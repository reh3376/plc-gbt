/**
 * WebSocket Server Implementation
 * Phase 32.1 - Multi-System Integration
 *
 * Main server for real-time PLC data streaming with multi-database integration
 */

import { QdrantClient } from '@qdrant/js-client-rest';
import { EventEmitter } from 'events';
import { createServer } from 'http';
import neo4j from 'neo4j-driver';
import { Client as PgClient } from 'pg';
import { createClient } from 'redis';
import { v4 as uuidv4 } from 'uuid';
import { WebSocketServer } from 'ws';

import { WebSocketConnectionManager } from './connection-manager';
import { PLCDataSimulator } from './plc-data-simulator';
import {
  AlertSeverity,
  CommandRequest,
  CommandResult,
  ConnectionConfig,
  ControlLoopData,
  PLCDataPoint,
  SubscriptionRequest,
  SystemAlert,
  SystemEventType,
  WebSocketMessage,
  WebSocketMessageType,
} from './types';

export interface ServerConfig {
  port: number;
  redis: {
    host: string;
    port: number;
  };
  postgres: {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
  };
  neo4j: {
    uri: string;
    user: string;
    password: string;
  };
  qdrant: {
    host: string;
    port: number;
  };
}

export class PLCWebSocketServer extends EventEmitter {
  private server: WebSocketServer;
  private httpServer: ReturnType<typeof createServer>;
  private connectionManager: WebSocketConnectionManager;
  private dataSimulator: PLCDataSimulator;

  // Database clients
  private redisClient?: ReturnType<typeof createClient>;
  private pgClient?: PgClient;
  private neo4jDriver?: ReturnType<typeof neo4j.driver>;
  private qdrantClient?: QdrantClient;

  private config: ServerConfig;
  private isRunning: boolean = false;

  constructor(config: ServerConfig) {
    super();
    this.config = config;

    // Create HTTP server
    this.httpServer = createServer();

    // Create WebSocket server
    this.server = new WebSocketServer({
      server: this.httpServer,
      perMessageDeflate: {
        zlibDeflateOptions: {
          chunkSize: 1024,
          memLevel: 7,
          level: 3,
        },
        zlibInflateOptions: {
          chunkSize: 10 * 1024,
        },
        clientNoContextTakeover: true,
        serverNoContextTakeover: true,
        serverMaxWindowBits: 10,
        concurrencyLimit: 10,
        threshold: 1024,
      },
    });

    // Initialize connection manager
    this.connectionManager = new WebSocketConnectionManager({
      heartbeatInterval: 30000,
      connectionTimeout: 60000,
      maxClientsPerIP: 10,
      enableAuthentication: true,
      maxMessageSize: 1024 * 1024, // 1MB
    });

    // Initialize data simulator
    this.dataSimulator = new PLCDataSimulator();

    this.setupEventHandlers();
  }

  /**
   * Start the WebSocket server
   */
  public async start(): Promise<void> {
    try {
      // Connect to databases
      await this.connectDatabases();

      // Set up WebSocket connection handler
      this.server.on('connection', async (ws, req) => {
        console.log('New WebSocket connection from:', req.socket.remoteAddress);

        // Parse connection config from headers or query params
        const config: ConnectionConfig = {
          clientId: (req.headers['x-client-id'] as string) || uuidv4(),
          authToken: req.headers['authorization'] as string,
          subscriptions: [],
          heartbeatInterval: 30000,
        };

        try {
          // Add connection to manager
          const connection = await this.connectionManager.addConnection(
            ws,
            config
          );

          // Set up message handler
          ws.on('message', async (data) => {
            await this.handleMessage(connection.id, data.toString());
          });
        } catch (error) {
          console.error('Failed to add connection:', error);
          ws.close(1008, 'Connection setup failed');
        }
      });

      // Start HTTP server
      this.httpServer.listen(this.config.port, () => {
        console.log(`WebSocket server listening on port ${this.config.port}`);
        this.isRunning = true;
        this.emit('server:started');
      });

      // Start data simulation
      this.startDataStreaming();
    } catch (error) {
      console.error('Failed to start server:', error);
      throw error;
    }
  }

  /**
   * Stop the WebSocket server
   */
  public async stop(): Promise<void> {
    console.log('Shutting down WebSocket server...');

    this.isRunning = false;

    // Stop data streaming
    this.dataSimulator.stop();

    // Shutdown connection manager
    await this.connectionManager.shutdown();

    // Close WebSocket server
    await new Promise<void>((resolve) => {
      this.server.close(() => resolve());
    });

    // Close HTTP server
    await new Promise<void>((resolve) => {
      this.httpServer.close(() => resolve());
    });

    // Disconnect databases
    await this.disconnectDatabases();

    this.emit('server:stopped');
    console.log('WebSocket server shutdown complete');
  }

  /**
   * Handle incoming WebSocket messages
   */
  private async handleMessage(
    connectionId: string,
    data: string
  ): Promise<void> {
    try {
      const message = JSON.parse(data) as WebSocketMessage;

      switch (message.type) {
        case WebSocketMessageType.PLC_DATA_SUBSCRIBE:
          await this.handleSubscribe(
            connectionId,
            message.payload as SubscriptionRequest
          );
          break;

        case WebSocketMessageType.PLC_DATA_UNSUBSCRIBE:
          await this.handleUnsubscribe(
            connectionId,
            message.payload as string[]
          );
          break;

        case WebSocketMessageType.CONTROL_LOOP_SUBSCRIBE:
          await this.handleControlLoopSubscribe(
            connectionId,
            message.payload as SubscriptionRequest
          );
          break;

        case WebSocketMessageType.EXECUTE_COMMAND:
          await this.handleCommand(
            connectionId,
            message.payload as CommandRequest
          );
          break;

        default:
          console.warn(`Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error('Failed to handle message:', error);

      // Send error response
      await this.connectionManager.sendMessage(connectionId, {
        id: uuidv4(),
        type: WebSocketMessageType.CONNECTION_ERROR,
        timestamp: Date.now(),
        payload: {
          error: 'Failed to process message',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      });
    }
  }

  /**
   * Handle PLC data subscription
   */
  private async handleSubscribe(
    connectionId: string,
    request: SubscriptionRequest
  ): Promise<void> {
    // Add subscriptions
    this.connectionManager.addSubscription(connectionId, request);

    // Store subscription in Redis for persistence
    if (this.redisClient) {
      const key = `subscription:${connectionId}`;
      await this.redisClient.sAdd(key, ...request.topics);
      await this.redisClient.expire(key, 86400); // 24 hours
    }

    console.log(`Client ${connectionId} subscribed to:`, request.topics);
  }

  /**
   * Handle PLC data unsubscription
   */
  private async handleUnsubscribe(
    connectionId: string,
    topics: string[]
  ): Promise<void> {
    // Remove subscriptions
    this.connectionManager.removeSubscription(connectionId, topics);

    // Remove from Redis
    if (this.redisClient) {
      const key = `subscription:${connectionId}`;
      await this.redisClient.sRem(key, ...topics);
    }

    console.log(`Client ${connectionId} unsubscribed from:`, topics);
  }

  /**
   * Handle control loop subscription
   */
  private async handleControlLoopSubscribe(
    connectionId: string,
    request: SubscriptionRequest
  ): Promise<void> {
    // Add control loop specific subscriptions
    const controlLoopTopics = request.topics.map(
      (topic) => `control-loop:${topic}`
    );

    this.connectionManager.addSubscription(connectionId, {
      ...request,
      topics: controlLoopTopics,
    });

    console.log(
      `Client ${connectionId} subscribed to control loops:`,
      request.topics
    );
  }

  /**
   * Handle command execution
   */
  private async handleCommand(
    connectionId: string,
    request: CommandRequest
  ): Promise<void> {
    const startTime = Date.now();

    try {
      // Execute command based on type
      let result: unknown;

      switch (request.command) {
        case 'get-plc-status':
          result = await this.getPLCStatus(request.parameters);
          break;

        case 'set-control-loop-mode':
          result = await this.setControlLoopMode(request.parameters);
          break;

        case 'query-historical-data':
          result = await this.queryHistoricalData(request.parameters);
          break;

        default:
          throw new Error(`Unknown command: ${request.command}`);
      }

      // Send command result
      await this.connectionManager.sendMessage(connectionId, {
        id: uuidv4(),
        type: WebSocketMessageType.COMMAND_RESULT,
        timestamp: Date.now(),
        payload: {
          success: true,
          result,
          executionTime: Date.now() - startTime,
        } as CommandResult,
      });
    } catch (error) {
      // Send command error
      await this.connectionManager.sendMessage(connectionId, {
        id: uuidv4(),
        type: WebSocketMessageType.COMMAND_ERROR,
        timestamp: Date.now(),
        payload: {
          success: false,
          error:
            error instanceof Error ? error.message : 'Command execution failed',
          executionTime: Date.now() - startTime,
        } as CommandResult,
      });
    }
  }

  /**
   * Start real-time data streaming
   */
  private startDataStreaming(): void {
    // Stream PLC data
    this.dataSimulator.on('plc-data', async (data: PLCDataPoint) => {
      // Cache in Redis
      if (this.redisClient) {
        const key = `plc:${data.tagName}:latest`;
        await this.redisClient.set(key, JSON.stringify(data), { EX: 300 });
      }

      // Broadcast to subscribers
      await this.connectionManager.broadcast(`plc:${data.tagName}`, {
        id: uuidv4(),
        type: WebSocketMessageType.PLC_DATA_UPDATE,
        timestamp: Date.now(),
        payload: data,
      });
    });

    // Stream control loop data
    this.dataSimulator.on('control-loop', async (data: ControlLoopData) => {
      // Store in PostgreSQL for historical analysis
      if (this.pgClient) {
        await this.pgClient.query(
          `INSERT INTO control_loop_data 
           (loop_id, timestamp, setpoint, process_variable, control_variable, mode, status)
           VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [
            data.loopId,
            new Date(),
            data.setpoint,
            data.processVariable,
            data.controlVariable,
            data.mode,
            data.status,
          ]
        );
      }

      // Broadcast to subscribers
      await this.connectionManager.broadcast(`control-loop:${data.loopId}`, {
        id: uuidv4(),
        type: WebSocketMessageType.CONTROL_LOOP_UPDATE,
        timestamp: Date.now(),
        payload: data,
      });
    });

    // Start simulation
    this.dataSimulator.start();
  }

  /**
   * Connect to all databases
   */
  private async connectDatabases(): Promise<void> {
    // Redis
    this.redisClient = createClient({
      socket: {
        host: this.config.redis.host,
        port: this.config.redis.port,
      },
    });
    await this.redisClient.connect();
    console.log('Connected to Redis');

    // PostgreSQL
    this.pgClient = new PgClient(this.config.postgres);
    await this.pgClient.connect();
    console.log('Connected to PostgreSQL');

    // Neo4j
    this.neo4jDriver = neo4j.driver(
      this.config.neo4j.uri,
      neo4j.auth.basic(this.config.neo4j.user, this.config.neo4j.password)
    );
    await this.neo4jDriver.verifyConnectivity();
    console.log('Connected to Neo4j');

    // Qdrant
    this.qdrantClient = new QdrantClient({
      host: this.config.qdrant.host,
      port: this.config.qdrant.port,
    });
    console.log('Connected to Qdrant');
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
  }

  /**
   * Set up event handlers
   */
  private setupEventHandlers(): void {
    // Handle connection events
    this.connectionManager.on('connection:added', (connection) => {
      console.log(`Client connected: ${connection.id}`);

      // Send system event
      this.connectionManager.broadcast('system:events', {
        id: uuidv4(),
        type: WebSocketMessageType.SYSTEM_EVENT,
        timestamp: Date.now(),
        payload: {
          type: SystemEventType.PLC_CONNECTED,
          source: connection.id,
          details: { clientId: connection.id },
        },
      });
    });

    this.connectionManager.on('connection:removed', (connection) => {
      console.log(`Client disconnected: ${connection.id}`);
    });
  }

  // Command implementations
  private async getPLCStatus(
    params: Record<string, unknown>
  ): Promise<unknown> {
    // Implementation would query actual PLC status
    return {
      plcId: params.plcId,
      status: 'online',
      cpuUsage: 45,
      memoryUsage: 62,
      programStatus: 'running',
    };
  }

  private async setControlLoopMode(
    params: Record<string, unknown>
  ): Promise<unknown> {
    // Implementation would set actual control loop mode
    return {
      loopId: params.loopId,
      previousMode: 'auto',
      newMode: params.mode,
      success: true,
    };
  }

  private async queryHistoricalData(
    params: Record<string, unknown>
  ): Promise<unknown> {
    // Implementation would query PostgreSQL for historical data
    return {
      tagName: params.tagName,
      startTime: params.startTime,
      endTime: params.endTime,
      dataPoints: [],
    };
  }
}

// Export for use
export { PLCDataSimulator, WebSocketConnectionManager };
