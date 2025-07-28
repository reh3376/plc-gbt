/**
 * Data Synchronization Orchestrator
 * Phase 32.1 - Multi-System Integration
 *
 * Orchestrates data synchronization across Redis, Neo4j, PostgreSQL, and Qdrant
 * Ensures consistency with conflict resolution and change data capture
 */

import { QdrantClient } from '@qdrant/js-client-rest';
import { EventEmitter } from 'events';
import neo4j from 'neo4j-driver';
import { Client as PgClient } from 'pg';
import { createClient } from 'redis';
import { v4 as uuidv4 } from 'uuid';

export enum SyncOperationType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  BATCH = 'batch',
}

export enum ConflictResolutionStrategy {
  LAST_WRITE_WINS = 'last_write_wins',
  HIGHEST_VERSION = 'highest_version',
  MANUAL_RESOLUTION = 'manual_resolution',
  MERGE = 'merge',
}

export interface SyncChange {
  id: string;
  entityType: string;
  entityId: string;
  operation: SyncOperationType;
  data: Record<string, unknown>;
  version: number;
  timestamp: number;
  source: string;
}

export interface SyncConflict {
  id: string;
  entityType: string;
  entityId: string;
  changes: SyncChange[];
  detectedAt: number;
  strategy: ConflictResolutionStrategy;
  resolved: boolean;
  resolution?: SyncChange;
}

export interface SyncSession {
  id: string;
  startTime: number;
  endTime?: number;
  changesProcessed: number;
  conflictsDetected: number;
  conflictsResolved: number;
  errors: SyncError[];
  status: 'running' | 'completed' | 'failed';
}

export interface SyncError {
  timestamp: number;
  database: string;
  operation: string;
  error: string;
  entityId?: string;
}

export interface SyncOrchestratorConfig {
  conflictStrategy: ConflictResolutionStrategy;
  batchSize: number;
  syncInterval: number;
  enableCDC: boolean;
  databases: {
    redis: { host: string; port: number };
    postgres: {
      host: string;
      port: number;
      database: string;
      user: string;
      password: string;
    };
    neo4j: { uri: string; user: string; password: string };
    qdrant: { host: string; port: number };
  };
}

export class DataSyncOrchestrator extends EventEmitter {
  private config: SyncOrchestratorConfig;
  private syncTimer?: NodeJS.Timer;
  private changeQueue: SyncChange[] = [];
  private activeSessions: Map<string, SyncSession> = new Map();
  private conflictMap: Map<string, SyncConflict> = new Map();

  // Database clients
  private redisClient?: ReturnType<typeof createClient>;
  private pgClient?: PgClient;
  private neo4jDriver?: ReturnType<typeof neo4j.driver>;
  private qdrantClient?: QdrantClient;

  private isRunning: boolean = false;

  constructor(config: SyncOrchestratorConfig) {
    super();
    this.config = config;
  }

  /**
   * Start the synchronization orchestrator
   */
  public async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Sync orchestrator is already running');
    }

    // Connect to databases
    await this.connectDatabases();

    // Set up change data capture if enabled
    if (this.config.enableCDC) {
      await this.setupChangeDataCapture();
    }

    // Start synchronization timer
    this.syncTimer = setInterval(() => {
      this.performSync().catch((error) => {
        console.error('Sync error:', error);
        this.emit('sync:error', error);
      });
    }, this.config.syncInterval);

    this.isRunning = true;
    this.emit('orchestrator:started');
    console.log('Data sync orchestrator started');
  }

  /**
   * Stop the synchronization orchestrator
   */
  public async stop(): Promise<void> {
    if (!this.isRunning) return;

    // Stop sync timer
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }

    // Complete active sessions
    for (const [sessionId, session] of this.activeSessions) {
      session.status = 'failed';
      session.endTime = Date.now();
      this.emit('session:failed', session);
    }

    // Disconnect databases
    await this.disconnectDatabases();

    this.isRunning = false;
    this.emit('orchestrator:stopped');
    console.log('Data sync orchestrator stopped');
  }

  /**
   * Add a change to the synchronization queue
   */
  public queueChange(change: Omit<SyncChange, 'id' | 'timestamp'>): void {
    const fullChange: SyncChange = {
      ...change,
      id: uuidv4(),
      timestamp: Date.now(),
    };

    this.changeQueue.push(fullChange);
    this.emit('change:queued', fullChange);
  }

  /**
   * Manually trigger synchronization
   */
  public async triggerSync(): Promise<SyncSession> {
    return this.performSync();
  }

  /**
   * Get active sync sessions
   */
  public getActiveSessions(): SyncSession[] {
    return Array.from(this.activeSessions.values());
  }

  /**
   * Get unresolved conflicts
   */
  public getUnresolvedConflicts(): SyncConflict[] {
    return Array.from(this.conflictMap.values()).filter((c) => !c.resolved);
  }

  /**
   * Resolve a conflict manually
   */
  public async resolveConflict(
    conflictId: string,
    resolution: SyncChange
  ): Promise<void> {
    const conflict = this.conflictMap.get(conflictId);
    if (!conflict) {
      throw new Error(`Conflict ${conflictId} not found`);
    }

    conflict.resolution = resolution;
    conflict.resolved = true;

    // Apply resolution
    await this.applyChange(resolution);

    this.emit('conflict:resolved', conflict);
  }

  /**
   * Perform synchronization
   */
  private async performSync(): Promise<SyncSession> {
    const session: SyncSession = {
      id: uuidv4(),
      startTime: Date.now(),
      changesProcessed: 0,
      conflictsDetected: 0,
      conflictsResolved: 0,
      errors: [],
      status: 'running',
    };

    this.activeSessions.set(session.id, session);
    this.emit('session:started', session);

    try {
      // Process changes in batches
      while (this.changeQueue.length > 0) {
        const batch = this.changeQueue.splice(0, this.config.batchSize);

        for (const change of batch) {
          try {
            // Check for conflicts
            const conflicts = await this.detectConflicts(change);

            if (conflicts.length > 0) {
              session.conflictsDetected += conflicts.length;

              // Resolve conflicts
              for (const conflict of conflicts) {
                const resolved = await this.resolveConflictAutomatically(
                  conflict
                );
                if (resolved) {
                  session.conflictsResolved++;
                  await this.applyChange(conflict.resolution!);
                } else {
                  // Store unresolved conflict
                  this.conflictMap.set(conflict.id, conflict);
                  this.emit('conflict:detected', conflict);
                }
              }
            } else {
              // No conflicts, apply change
              await this.applyChange(change);
            }

            session.changesProcessed++;
          } catch (error) {
            const syncError: SyncError = {
              timestamp: Date.now(),
              database: 'unknown',
              operation: change.operation,
              error: error instanceof Error ? error.message : 'Unknown error',
              entityId: change.entityId,
            };
            session.errors.push(syncError);
            this.emit('sync:error', syncError);
          }
        }
      }

      session.status = 'completed';
      session.endTime = Date.now();
    } catch (error) {
      session.status = 'failed';
      session.endTime = Date.now();
      throw error;
    } finally {
      this.activeSessions.delete(session.id);
      this.emit('session:completed', session);
    }

    return session;
  }

  /**
   * Apply a change to all databases
   */
  private async applyChange(change: SyncChange): Promise<void> {
    const promises: Promise<void>[] = [];

    // Apply to Redis (cache)
    if (this.redisClient) {
      promises.push(this.applyToRedis(change));
    }

    // Apply to PostgreSQL (structured data)
    if (this.pgClient) {
      promises.push(this.applyToPostgreSQL(change));
    }

    // Apply to Neo4j (graph relationships)
    if (this.neo4jDriver) {
      promises.push(this.applyToNeo4j(change));
    }

    // Apply to Qdrant (vector embeddings)
    if (this.qdrantClient) {
      promises.push(this.applyToQdrant(change));
    }

    await Promise.all(promises);
    this.emit('change:applied', change);
  }

  /**
   * Apply change to Redis
   */
  private async applyToRedis(change: SyncChange): Promise<void> {
    const key = `${change.entityType}:${change.entityId}`;

    switch (change.operation) {
      case SyncOperationType.CREATE:
      case SyncOperationType.UPDATE:
        await this.redisClient!.set(
          key,
          JSON.stringify({
            ...change.data,
            _version: change.version,
            _lastModified: change.timestamp,
          })
        );
        break;

      case SyncOperationType.DELETE:
        await this.redisClient!.del(key);
        break;
    }
  }

  /**
   * Apply change to PostgreSQL
   */
  private async applyToPostgreSQL(change: SyncChange): Promise<void> {
    switch (change.operation) {
      case SyncOperationType.CREATE:
        await this.pgClient!.query(
          `INSERT INTO ${change.entityType} (id, data, version, last_modified) 
           VALUES ($1, $2, $3, $4)
           ON CONFLICT (id) DO UPDATE 
           SET data = $2, version = $3, last_modified = $4`,
          [
            change.entityId,
            change.data,
            change.version,
            new Date(change.timestamp),
          ]
        );
        break;

      case SyncOperationType.UPDATE:
        await this.pgClient!.query(
          `UPDATE ${change.entityType} 
           SET data = $1, version = $2, last_modified = $3
           WHERE id = $4`,
          [
            change.data,
            change.version,
            new Date(change.timestamp),
            change.entityId,
          ]
        );
        break;

      case SyncOperationType.DELETE:
        await this.pgClient!.query(
          `DELETE FROM ${change.entityType} WHERE id = $1`,
          [change.entityId]
        );
        break;
    }
  }

  /**
   * Apply change to Neo4j
   */
  private async applyToNeo4j(change: SyncChange): Promise<void> {
    const session = this.neo4jDriver!.session();

    try {
      switch (change.operation) {
        case SyncOperationType.CREATE:
        case SyncOperationType.UPDATE:
          await session.run(
            `MERGE (n:${change.entityType} {id: $id})
             SET n += $properties
             SET n._version = $version
             SET n._lastModified = $timestamp`,
            {
              id: change.entityId,
              properties: change.data,
              version: change.version,
              timestamp: change.timestamp,
            }
          );
          break;

        case SyncOperationType.DELETE:
          await session.run(
            `MATCH (n:${change.entityType} {id: $id})
             DETACH DELETE n`,
            { id: change.entityId }
          );
          break;
      }
    } finally {
      await session.close();
    }
  }

  /**
   * Apply change to Qdrant
   */
  private async applyToQdrant(change: SyncChange): Promise<void> {
    // Only handle entities with vector embeddings
    if (!change.data.embedding) return;

    const collectionName = change.entityType.toLowerCase();

    switch (change.operation) {
      case SyncOperationType.CREATE:
      case SyncOperationType.UPDATE:
        await this.qdrantClient!.upsert(collectionName, {
          points: [
            {
              id: change.entityId,
              vector: change.data.embedding as number[],
              payload: {
                ...change.data,
                _version: change.version,
                _lastModified: change.timestamp,
              },
            },
          ],
        });
        break;

      case SyncOperationType.DELETE:
        await this.qdrantClient!.delete(collectionName, {
          points: [change.entityId],
        });
        break;
    }
  }

  /**
   * Detect conflicts for a change
   */
  private async detectConflicts(change: SyncChange): Promise<SyncConflict[]> {
    const conflicts: SyncConflict[] = [];

    // Check version conflicts across databases
    const versions = await this.getEntityVersions(
      change.entityType,
      change.entityId
    );

    if (versions.length > 1) {
      // Version mismatch detected
      const conflict: SyncConflict = {
        id: uuidv4(),
        entityType: change.entityType,
        entityId: change.entityId,
        changes: [change, ...versions],
        detectedAt: Date.now(),
        strategy: this.config.conflictStrategy,
        resolved: false,
      };
      conflicts.push(conflict);
    }

    return conflicts;
  }

  /**
   * Get entity versions from all databases
   */
  private async getEntityVersions(
    entityType: string,
    entityId: string
  ): Promise<SyncChange[]> {
    const versions: SyncChange[] = [];

    // Get from Redis
    if (this.redisClient) {
      const redisData = await this.redisClient.get(`${entityType}:${entityId}`);
      if (redisData) {
        const parsed = JSON.parse(redisData);
        versions.push({
          id: uuidv4(),
          entityType,
          entityId,
          operation: SyncOperationType.UPDATE,
          data: parsed,
          version: parsed._version || 0,
          timestamp: parsed._lastModified || 0,
          source: 'redis',
        });
      }
    }

    // Get from PostgreSQL
    if (this.pgClient) {
      const result = await this.pgClient.query(
        `SELECT data, version, last_modified FROM ${entityType} WHERE id = $1`,
        [entityId]
      );
      if (result.rows.length > 0) {
        const row = result.rows[0];
        versions.push({
          id: uuidv4(),
          entityType,
          entityId,
          operation: SyncOperationType.UPDATE,
          data: row.data,
          version: row.version,
          timestamp: row.last_modified.getTime(),
          source: 'postgresql',
        });
      }
    }

    return versions;
  }

  /**
   * Automatically resolve a conflict based on strategy
   */
  private async resolveConflictAutomatically(
    conflict: SyncConflict
  ): Promise<boolean> {
    switch (conflict.strategy) {
      case ConflictResolutionStrategy.LAST_WRITE_WINS:
        // Pick the change with the latest timestamp
        conflict.resolution = conflict.changes.reduce((latest, change) =>
          change.timestamp > latest.timestamp ? change : latest
        );
        conflict.resolved = true;
        return true;

      case ConflictResolutionStrategy.HIGHEST_VERSION:
        // Pick the change with the highest version
        conflict.resolution = conflict.changes.reduce((highest, change) =>
          change.version > highest.version ? change : highest
        );
        conflict.resolved = true;
        return true;

      case ConflictResolutionStrategy.MERGE:
        // Merge all changes (simple merge strategy)
        const mergedData = conflict.changes.reduce(
          (merged, change) => ({
            ...merged,
            ...change.data,
          }),
          {}
        );

        conflict.resolution = {
          id: uuidv4(),
          entityType: conflict.entityType,
          entityId: conflict.entityId,
          operation: SyncOperationType.UPDATE,
          data: mergedData,
          version: Math.max(...conflict.changes.map((c) => c.version)) + 1,
          timestamp: Date.now(),
          source: 'conflict_resolution',
        };
        conflict.resolved = true;
        return true;

      case ConflictResolutionStrategy.MANUAL_RESOLUTION:
        // Cannot resolve automatically
        return false;

      default:
        return false;
    }
  }

  /**
   * Set up change data capture
   */
  private async setupChangeDataCapture(): Promise<void> {
    // Set up PostgreSQL logical replication
    if (this.pgClient) {
      // This would typically involve setting up logical replication slots
      // and listening for changes
      console.log('CDC setup for PostgreSQL (placeholder)');
    }

    // Set up Redis keyspace notifications
    if (this.redisClient) {
      await this.redisClient.configSet('notify-keyspace-events', 'KEA');
      // Subscribe to keyspace events
      console.log('CDC setup for Redis (placeholder)');
    }

    // Neo4j and Qdrant would have their own CDC mechanisms
  }

  /**
   * Connect to all databases
   */
  private async connectDatabases(): Promise<void> {
    // Redis
    this.redisClient = createClient({
      socket: {
        host: this.config.databases.redis.host,
        port: this.config.databases.redis.port,
      },
    });
    await this.redisClient.connect();

    // PostgreSQL
    this.pgClient = new PgClient(this.config.databases.postgres);
    await this.pgClient.connect();

    // Neo4j
    this.neo4jDriver = neo4j.driver(
      this.config.databases.neo4j.uri,
      neo4j.auth.basic(
        this.config.databases.neo4j.user,
        this.config.databases.neo4j.password
      )
    );
    await this.neo4jDriver.verifyConnectivity();

    // Qdrant
    this.qdrantClient = new QdrantClient({
      host: this.config.databases.qdrant.host,
      port: this.config.databases.qdrant.port,
    });

    console.log('All databases connected for sync orchestrator');
  }

  /**
   * Disconnect from all databases
   */
  private async disconnectDatabases(): Promise<void> {
    if (this.redisClient) {
      await this.redisClient.quit();
    }

    if (this.pgClient) {
      await this.pgClient.end();
    }

    if (this.neo4jDriver) {
      await this.neo4jDriver.close();
    }

    console.log('All databases disconnected');
  }
}
