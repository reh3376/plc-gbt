/**
 * Circuit Breaker Pattern Implementation
 * Phase 32.1 - Multi-System Integration
 *
 * Prevents cascading failures in distributed systems by monitoring
 * service health and breaking connections when failures exceed thresholds
 */

import { EventEmitter } from 'events';

export enum CircuitState {
  CLOSED = 'closed', // Normal operation
  OPEN = 'open', // Circuit broken, rejecting requests
  HALF_OPEN = 'half_open', // Testing if service recovered
}

export interface CircuitBreakerConfig {
  failureThreshold: number; // Number of failures before opening
  successThreshold: number; // Number of successes to close from half-open
  timeout: number; // Time in ms before trying half-open
  monitoringPeriod: number; // Time window for counting failures
  volumeThreshold: number; // Minimum requests before evaluating
}

export interface CircuitBreakerMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  rejectedRequests: number;
  state: CircuitState;
  lastStateChange: number;
  lastFailure?: number;
  consecutiveFailures: number;
  consecutiveSuccesses: number;
}

export class CircuitBreaker extends EventEmitter {
  private config: CircuitBreakerConfig;
  private state: CircuitState = CircuitState.CLOSED;
  private metrics: CircuitBreakerMetrics;
  private stateChangeTimer?: NodeJS.Timeout;
  private requestWindow: { timestamp: number; success: boolean }[] = [];

  constructor(
    private name: string,
    config: Partial<CircuitBreakerConfig> = {}
  ) {
    super();

    this.config = {
      failureThreshold: 5,
      successThreshold: 2,
      timeout: 60000, // 60 seconds
      monitoringPeriod: 60000, // 60 seconds
      volumeThreshold: 10,
      ...config,
    };

    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      rejectedRequests: 0,
      state: CircuitState.CLOSED,
      lastStateChange: Date.now(),
      consecutiveFailures: 0,
      consecutiveSuccesses: 0,
    };
  }

  /**
   * Execute a function through the circuit breaker
   */
  public async execute<T>(operation: () => Promise<T>): Promise<T> {
    // Check if we should allow the request
    if (!this.allowRequest()) {
      this.metrics.rejectedRequests++;
      this.emit('request:rejected', {
        circuit: this.name,
        state: this.state,
      });
      throw new Error(`Circuit breaker ${this.name} is OPEN`);
    }

    this.metrics.totalRequests++;
    const startTime = Date.now();

    try {
      const result = await operation();
      this.onSuccess();

      this.emit('request:success', {
        circuit: this.name,
        duration: Date.now() - startTime,
      });

      return result;
    } catch (error) {
      this.onFailure();

      this.emit('request:failure', {
        circuit: this.name,
        duration: Date.now() - startTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      });

      throw error;
    }
  }

  /**
   * Get current circuit breaker metrics
   */
  public getMetrics(): CircuitBreakerMetrics {
    return { ...this.metrics, state: this.state };
  }

  /**
   * Get current circuit state
   */
  public getState(): CircuitState {
    return this.state;
  }

  /**
   * Reset the circuit breaker
   */
  public reset(): void {
    this.changeState(CircuitState.CLOSED);
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      rejectedRequests: 0,
      state: CircuitState.CLOSED,
      lastStateChange: Date.now(),
      consecutiveFailures: 0,
      consecutiveSuccesses: 0,
    };
    this.requestWindow = [];

    if (this.stateChangeTimer) {
      clearTimeout(this.stateChangeTimer);
      this.stateChangeTimer = undefined;
    }

    this.emit('circuit:reset', { circuit: this.name });
  }

  /**
   * Check if request should be allowed
   */
  private allowRequest(): boolean {
    this.cleanRequestWindow();

    switch (this.state) {
      case CircuitState.CLOSED:
        return true;

      case CircuitState.OPEN:
        return false;

      case CircuitState.HALF_OPEN:
        // Allow limited requests to test recovery
        return true;

      default:
        return false;
    }
  }

  /**
   * Handle successful request
   */
  private onSuccess(): void {
    this.metrics.successfulRequests++;
    this.metrics.consecutiveSuccesses++;
    this.metrics.consecutiveFailures = 0;

    this.requestWindow.push({
      timestamp: Date.now(),
      success: true,
    });

    if (this.state === CircuitState.HALF_OPEN) {
      // Check if we should close the circuit
      if (this.metrics.consecutiveSuccesses >= this.config.successThreshold) {
        this.changeState(CircuitState.CLOSED);
      }
    }
  }

  /**
   * Handle failed request
   */
  private onFailure(): void {
    this.metrics.failedRequests++;
    this.metrics.consecutiveFailures++;
    this.metrics.consecutiveSuccesses = 0;
    this.metrics.lastFailure = Date.now();

    this.requestWindow.push({
      timestamp: Date.now(),
      success: false,
    });

    switch (this.state) {
      case CircuitState.CLOSED:
        // Check if we should open the circuit
        if (this.shouldOpen()) {
          this.changeState(CircuitState.OPEN);
        }
        break;

      case CircuitState.HALF_OPEN:
        // Single failure in half-open state reopens the circuit
        this.changeState(CircuitState.OPEN);
        break;
    }
  }

  /**
   * Check if circuit should open based on failure rate
   */
  private shouldOpen(): boolean {
    const recentRequests = this.requestWindow.filter(
      (req) => req.timestamp > Date.now() - this.config.monitoringPeriod
    );

    // Not enough volume to make a decision
    if (recentRequests.length < this.config.volumeThreshold) {
      return false;
    }

    const failures = recentRequests.filter((req) => !req.success).length;

    return failures >= this.config.failureThreshold;
  }

  /**
   * Change circuit state
   */
  private changeState(newState: CircuitState): void {
    if (this.state === newState) return;

    const oldState = this.state;
    this.state = newState;
    this.metrics.state = newState;
    this.metrics.lastStateChange = Date.now();

    // Clear any existing timer
    if (this.stateChangeTimer) {
      clearTimeout(this.stateChangeTimer);
      this.stateChangeTimer = undefined;
    }

    // Set up timer for OPEN -> HALF_OPEN transition
    if (newState === CircuitState.OPEN) {
      this.stateChangeTimer = setTimeout(() => {
        this.changeState(CircuitState.HALF_OPEN);
      }, this.config.timeout);
    }

    // Reset consecutive counters on state change
    if (newState === CircuitState.CLOSED) {
      this.metrics.consecutiveFailures = 0;
    }

    this.emit('state:changed', {
      circuit: this.name,
      oldState,
      newState,
      metrics: this.getMetrics(),
    });
  }

  /**
   * Clean old requests from the window
   */
  private cleanRequestWindow(): void {
    const cutoff = Date.now() - this.config.monitoringPeriod;
    this.requestWindow = this.requestWindow.filter(
      (req) => req.timestamp > cutoff
    );
  }
}

/**
 * Circuit Breaker Factory for managing multiple circuits
 */
export class CircuitBreakerFactory {
  private circuits: Map<string, CircuitBreaker> = new Map();

  /**
   * Get or create a circuit breaker
   */
  public getCircuit(
    name: string,
    config?: Partial<CircuitBreakerConfig>
  ): CircuitBreaker {
    if (!this.circuits.has(name)) {
      const circuit = new CircuitBreaker(name, config);
      this.circuits.set(name, circuit);
    }

    return this.circuits.get(name)!;
  }

  /**
   * Get all circuits
   */
  public getAllCircuits(): Map<string, CircuitBreaker> {
    return new Map(this.circuits);
  }

  /**
   * Get metrics for all circuits
   */
  public getAllMetrics(): Record<string, CircuitBreakerMetrics> {
    const metrics: Record<string, CircuitBreakerMetrics> = {};

    for (const [name, circuit] of this.circuits) {
      metrics[name] = circuit.getMetrics();
    }

    return metrics;
  }

  /**
   * Reset a specific circuit
   */
  public resetCircuit(name: string): void {
    const circuit = this.circuits.get(name);
    if (circuit) {
      circuit.reset();
    }
  }

  /**
   * Reset all circuits
   */
  public resetAllCircuits(): void {
    for (const circuit of this.circuits.values()) {
      circuit.reset();
    }
  }
}
