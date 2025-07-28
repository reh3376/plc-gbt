/**
 * WebSocket Connection Manager
 * Phase 32.1 - Multi-System Integration
 *
 * Manages WebSocket client connections with authentication, heartbeat monitoring,
 * and subscription management. Implements resilience patterns for connection stability.
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { WebSocket } from 'ws';
import {
  AlertSeverity,
  ConnectionConfig,
  SubscriptionRequest,
  SystemAlert,
  WebSocketMessage,
  WebSocketMessageType,
} from './types';

export interface ClientConnection {
  id: string;
  websocket: WebSocket;
  config: ConnectionConfig;
  subscriptions: Set<string>;
  lastHeartbeat: number;
  isAlive: boolean;
  metadata: Record<string, unknown>;
}

export interface ConnectionManagerConfig {
  heartbeatInterval: number;
  connectionTimeout: number;
  maxClientsPerIP: number;
  enableAuthentication: boolean;
  maxMessageSize: number;
}

export class WebSocketConnectionManager extends EventEmitter {
  private connections: Map<string, ClientConnection> = new Map();
  private heartbeatTimer?: NodeJS.Timer;
  private config: ConnectionManagerConfig;

  constructor(config: Partial<ConnectionManagerConfig> = {}) {
    super();

    this.config = {
      heartbeatInterval: 30000, // 30 seconds
      connectionTimeout: 60000, // 60 seconds
      maxClientsPerIP: 10,
      enableAuthentication: true,
      maxMessageSize: 1024 * 1024, // 1MB
      ...config,
    };

    this.startHeartbeatMonitoring();
  }

  /**
   * Register a new WebSocket connection
   */
  public async addConnection(
    websocket: WebSocket,
    config: ConnectionConfig
  ): Promise<ClientConnection> {
    // Validate authentication if enabled
    if (this.config.enableAuthentication && !config.authToken) {
      throw new Error('Authentication required but no token provided');
    }

    const connection: ClientConnection = {
      id: config.clientId || uuidv4(),
      websocket,
      config,
      subscriptions: new Set(config.subscriptions || []),
      lastHeartbeat: Date.now(),
      isAlive: true,
      metadata: {},
    };

    // Set up WebSocket event handlers
    this.setupConnectionHandlers(connection);

    // Store connection
    this.connections.set(connection.id, connection);

    // Send connection acknowledgment
    await this.sendMessage(connection.id, {
      id: uuidv4(),
      type: WebSocketMessageType.CONNECTION_ACK,
      timestamp: Date.now(),
      payload: {
        connectionId: connection.id,
        heartbeatInterval: this.config.heartbeatInterval,
      },
    });

    this.emit('connection:added', connection);
    return connection;
  }

  /**
   * Remove a connection
   */
  public removeConnection(connectionId: string): void {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    // Clean up subscriptions
    connection.subscriptions.clear();

    // Close WebSocket if still open
    if (connection.websocket.readyState === WebSocket.OPEN) {
      connection.websocket.close(1000, 'Connection closed by server');
    }

    this.connections.delete(connectionId);
    this.emit('connection:removed', connection);
  }

  /**
   * Send message to specific client
   */
  public async sendMessage<T>(
    connectionId: string,
    message: WebSocketMessage<T>
  ): Promise<void> {
    const connection = this.connections.get(connectionId);
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }

    if (connection.websocket.readyState !== WebSocket.OPEN) {
      throw new Error(`Connection ${connectionId} is not open`);
    }

    const data = JSON.stringify(message);

    // Check message size
    if (data.length > this.config.maxMessageSize) {
      throw new Error(
        `Message size ${data.length} exceeds limit ${this.config.maxMessageSize}`
      );
    }

    return new Promise((resolve, reject) => {
      connection.websocket.send(data, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve();
        }
      });
    });
  }

  /**
   * Broadcast message to all connections with specific subscription
   */
  public async broadcast<T>(
    topic: string,
    message: WebSocketMessage<T>
  ): Promise<void> {
    const promises: Promise<void>[] = [];

    for (const [connectionId, connection] of this.connections) {
      if (connection.subscriptions.has(topic)) {
        promises.push(
          this.sendMessage(connectionId, message).catch((error) => {
            console.error(`Failed to send to ${connectionId}:`, error);
          })
        );
      }
    }

    await Promise.all(promises);
  }

  /**
   * Add subscription for a connection
   */
  public addSubscription(
    connectionId: string,
    request: SubscriptionRequest
  ): void {
    const connection = this.connections.get(connectionId);
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }

    request.topics.forEach((topic) => {
      connection.subscriptions.add(topic);
    });

    this.emit('subscription:added', { connectionId, topics: request.topics });
  }

  /**
   * Remove subscription for a connection
   */
  public removeSubscription(connectionId: string, topics: string[]): void {
    const connection = this.connections.get(connectionId);
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }

    topics.forEach((topic) => {
      connection.subscriptions.delete(topic);
    });

    this.emit('subscription:removed', { connectionId, topics });
  }

  /**
   * Get all active connections
   */
  public getConnections(): ClientConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get connection by ID
   */
  public getConnection(connectionId: string): ClientConnection | undefined {
    return this.connections.get(connectionId);
  }

  /**
   * Send system alert to all connections
   */
  public async broadcastSystemAlert(alert: SystemAlert): Promise<void> {
    const message: WebSocketMessage<SystemAlert> = {
      id: uuidv4(),
      type: WebSocketMessageType.SYSTEM_ALERT,
      timestamp: Date.now(),
      payload: alert,
    };

    const promises: Promise<void>[] = [];

    for (const connectionId of this.connections.keys()) {
      promises.push(
        this.sendMessage(connectionId, message).catch((error) => {
          console.error(`Failed to send alert to ${connectionId}:`, error);
        })
      );
    }

    await Promise.all(promises);
  }

  /**
   * Clean up and close all connections
   */
  public async shutdown(): Promise<void> {
    // Stop heartbeat monitoring
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    // Close all connections
    const promises: Promise<void>[] = [];

    for (const [connectionId, connection] of this.connections) {
      promises.push(
        this.sendMessage(connectionId, {
          id: uuidv4(),
          type: WebSocketMessageType.CONNECTION_CLOSE,
          timestamp: Date.now(),
          payload: { reason: 'Server shutting down' },
        }).catch(() => {
          // Ignore send errors during shutdown
        })
      );

      connection.websocket.close(1001, 'Server shutting down');
    }

    await Promise.all(promises);
    this.connections.clear();
    this.emit('shutdown');
  }

  /**
   * Set up WebSocket event handlers for a connection
   */
  private setupConnectionHandlers(connection: ClientConnection): void {
    const { websocket } = connection;

    websocket.on('pong', () => {
      connection.isAlive = true;
      connection.lastHeartbeat = Date.now();
    });

    websocket.on('close', () => {
      this.removeConnection(connection.id);
    });

    websocket.on('error', (error) => {
      console.error(`WebSocket error for ${connection.id}:`, error);
      this.emit('connection:error', { connectionId: connection.id, error });
    });
  }

  /**
   * Start heartbeat monitoring for all connections
   */
  private startHeartbeatMonitoring(): void {
    this.heartbeatTimer = setInterval(() => {
      const now = Date.now();

      for (const [connectionId, connection] of this.connections) {
        if (!connection.isAlive) {
          // Connection didn't respond to last ping
          console.warn(`Connection ${connectionId} failed heartbeat check`);
          this.removeConnection(connectionId);
          continue;
        }

        // Check if connection has been idle too long
        if (now - connection.lastHeartbeat > this.config.connectionTimeout) {
          console.warn(`Connection ${connectionId} timed out`);
          this.removeConnection(connectionId);
          continue;
        }

        // Send ping
        connection.isAlive = false;
        connection.websocket.ping();
      }
    }, this.config.heartbeatInterval);
  }
}
