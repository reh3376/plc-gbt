/**
 * Retry Policy Implementation
 * Phase 32.1 - Multi-System Integration
 *
 * Implements various retry strategies including exponential backoff,
 * linear retry, and custom policies for resilient operations
 */

export enum RetryStrategy {
  EXPONENTIAL = 'exponential',
  LINEAR = 'linear',
  FIXED = 'fixed',
  CUSTOM = 'custom',
}

export interface RetryConfig {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  strategy: RetryStrategy;
  backoffMultiplier: number;
  jitter: boolean;
  retryableErrors?: string[];
  onRetry?: (attempt: number, error: Error) => void;
}

export interface RetryResult<T> {
  success: boolean;
  result?: T;
  error?: Error;
  attempts: number;
  totalTime: number;
}

export class RetryPolicy {
  private config: RetryConfig;

  constructor(config: Partial<RetryConfig> = {}) {
    this.config = {
      maxAttempts: 3,
      initialDelay: 1000,
      maxDelay: 30000,
      strategy: RetryStrategy.EXPONENTIAL,
      backoffMultiplier: 2,
      jitter: true,
      ...config,
    };
  }

  /**
   * Execute an operation with retry logic
   */
  public async execute<T>(
    operation: () => Promise<T>
  ): Promise<RetryResult<T>> {
    const startTime = Date.now();
    let lastError: Error | undefined;

    for (let attempt = 1; attempt <= this.config.maxAttempts; attempt++) {
      try {
        const result = await operation();

        return {
          success: true,
          result,
          attempts: attempt,
          totalTime: Date.now() - startTime,
        };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');

        // Check if error is retryable
        if (!this.isRetryableError(lastError)) {
          return {
            success: false,
            error: lastError,
            attempts: attempt,
            totalTime: Date.now() - startTime,
          };
        }

        // Call onRetry callback if provided
        if (this.config.onRetry) {
          this.config.onRetry(attempt, lastError);
        }

        // Don't delay after last attempt
        if (attempt < this.config.maxAttempts) {
          const delay = this.calculateDelay(attempt);
          await this.sleep(delay);
        }
      }
    }

    return {
      success: false,
      error: lastError || new Error('Max attempts reached'),
      attempts: this.config.maxAttempts,
      totalTime: Date.now() - startTime,
    };
  }

  /**
   * Check if an error is retryable
   */
  private isRetryableError(error: Error): boolean {
    // If no specific retryable errors defined, retry all
    if (
      !this.config.retryableErrors ||
      this.config.retryableErrors.length === 0
    ) {
      return true;
    }

    // Check if error message contains any retryable error patterns
    return this.config.retryableErrors.some((pattern) =>
      error.message.includes(pattern)
    );
  }

  /**
   * Calculate delay for next retry attempt
   */
  private calculateDelay(attempt: number): number {
    let delay: number;

    switch (this.config.strategy) {
      case RetryStrategy.EXPONENTIAL:
        delay =
          this.config.initialDelay *
          Math.pow(this.config.backoffMultiplier, attempt - 1);
        break;

      case RetryStrategy.LINEAR:
        delay = this.config.initialDelay * attempt;
        break;

      case RetryStrategy.FIXED:
        delay = this.config.initialDelay;
        break;

      default:
        delay = this.config.initialDelay;
    }

    // Apply max delay cap
    delay = Math.min(delay, this.config.maxDelay);

    // Apply jitter if enabled
    if (this.config.jitter) {
      delay = this.applyJitter(delay);
    }

    return Math.round(delay);
  }

  /**
   * Apply jitter to delay to prevent thundering herd
   */
  private applyJitter(delay: number): number {
    // Random jitter between 0.5x and 1.5x the delay
    const jitterFactor = 0.5 + Math.random();
    return delay * jitterFactor;
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * Bulkhead Pattern Implementation
 * Isolates resources to prevent cascading failures
 */
export class Bulkhead {
  private activeRequests: number = 0;
  private queuedRequests: (() => void)[] = [];

  constructor(private maxConcurrent: number, private maxQueued: number = 0) {}

  /**
   * Execute operation with bulkhead protection
   */
  public async execute<T>(operation: () => Promise<T>): Promise<T> {
    // Check if we can execute immediately
    if (this.activeRequests < this.maxConcurrent) {
      return this.executeOperation(operation);
    }

    // Check if we can queue
    if (this.maxQueued > 0 && this.queuedRequests.length < this.maxQueued) {
      return new Promise((resolve, reject) => {
        this.queuedRequests.push(() => {
          this.executeOperation(operation).then(resolve).catch(reject);
        });
      });
    }

    // Reject if bulkhead is full
    throw new Error('Bulkhead capacity exceeded');
  }

  /**
   * Execute the operation and manage counters
   */
  private async executeOperation<T>(operation: () => Promise<T>): Promise<T> {
    this.activeRequests++;

    try {
      const result = await operation();
      return result;
    } finally {
      this.activeRequests--;

      // Process queued requests
      if (this.queuedRequests.length > 0) {
        const nextRequest = this.queuedRequests.shift();
        if (nextRequest) {
          nextRequest();
        }
      }
    }
  }

  /**
   * Get current bulkhead metrics
   */
  public getMetrics(): {
    activeRequests: number;
    queuedRequests: number;
    availableCapacity: number;
  } {
    return {
      activeRequests: this.activeRequests,
      queuedRequests: this.queuedRequests.length,
      availableCapacity: this.maxConcurrent - this.activeRequests,
    };
  }
}

/**
 * Timeout wrapper for operations
 */
export class TimeoutWrapper {
  constructor(private timeoutMs: number) {}

  /**
   * Execute operation with timeout
   */
  public async execute<T>(operation: () => Promise<T>): Promise<T> {
    return Promise.race([
      operation(),
      new Promise<T>((_, reject) =>
        setTimeout(
          () =>
            reject(new Error(`Operation timed out after ${this.timeoutMs}ms`)),
          this.timeoutMs
        )
      ),
    ]);
  }
}

/**
 * Combined resilience wrapper that applies multiple patterns
 */
export class ResilienceWrapper {
  constructor(
    private circuitBreaker?: {
      execute: <T>(op: () => Promise<T>) => Promise<T>;
    },
    private retryPolicy?: RetryPolicy,
    private bulkhead?: Bulkhead,
    private timeout?: TimeoutWrapper
  ) {}

  /**
   * Execute operation with all resilience patterns applied
   */
  public async execute<T>(operation: () => Promise<T>): Promise<T> {
    // Wrap operation with timeout if configured
    let wrappedOperation = operation;
    if (this.timeout) {
      const timeoutWrapper = this.timeout;
      wrappedOperation = () => timeoutWrapper.execute(operation);
    }

    // Wrap with retry policy if configured
    if (this.retryPolicy) {
      const retryWrapper = this.retryPolicy;
      const previousOperation = wrappedOperation;
      wrappedOperation = async () => {
        const result = await retryWrapper.execute(previousOperation);
        if (!result.success) {
          throw result.error || new Error('Operation failed after retries');
        }
        return result.result!;
      };
    }

    // Wrap with bulkhead if configured
    if (this.bulkhead) {
      const bulkheadWrapper = this.bulkhead;
      const previousOperation = wrappedOperation;
      wrappedOperation = () => bulkheadWrapper.execute(previousOperation);
    }

    // Wrap with circuit breaker if configured
    if (this.circuitBreaker) {
      return this.circuitBreaker.execute(wrappedOperation);
    }

    return wrappedOperation();
  }
}
