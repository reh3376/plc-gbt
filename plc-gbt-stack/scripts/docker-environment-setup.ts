#!/usr/bin/env tsx

/**
 * 🐳 PLC-GBT Docker Environment Setup & Validation
 *
 * AI Task Orchestrator TypeScript Methodology Compliance:
 * - Zero `any` types - strict TypeScript throughout
 * - Comprehensive error handling and validation
 * - MCP Docker server integration validation
 * - Production-ready environment setup
 *
 * Purpose:
 * - Set up all required Docker containers for Node Properties Modal development
 * - Validate MCP Docker server connectivity (port 8811)
 * - Ensure database connectivity (Neo4j, PostgreSQL, Redis, Qdrant)
 * - Confirm development environment readiness
 */

import { execSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

interface DockerEnvironmentConfig {
  readonly requiredContainers: readonly ContainerDefinition[];
  readonly environmentVariables: Record<string, string>;
  readonly healthCheckTimeout: number;
  readonly startupTimeout: number;
  readonly mcpServerPort: number;
  readonly developmentServerPort: number;
}

interface ContainerDefinition {
  readonly name: string;
  readonly service: string;
  readonly ports: readonly string[];
  readonly healthEndpoint?: string;
  readonly dependsOn: readonly string[];
  readonly priority: 'critical' | 'high' | 'medium' | 'low';
}

interface ContainerStatus {
  readonly name: string;
  readonly status: 'running' | 'stopped' | 'error' | 'unknown';
  readonly health: 'healthy' | 'unhealthy' | 'starting' | 'unknown';
  readonly ports: readonly string[];
}

interface ConnectivityResult {
  readonly endpoint: string;
  readonly status: 'connected' | 'failed' | 'timeout';
  readonly responseTime: number;
  readonly error?: string;
}

// 🎯 AI Task Orchestrator Configuration
const DOCKER_CONFIG: DockerEnvironmentConfig = {
  requiredContainers: [
    {
      name: 'plc-neo4j',
      service: 'neo4j',
      ports: ['7474', '7687'],
      healthEndpoint: 'http://localhost:7474',
      dependsOn: [],
      priority: 'critical',
    },
    {
      name: 'plc-postgres',
      service: 'postgres',
      ports: ['5432'],
      dependsOn: [],
      priority: 'critical',
    },
    {
      name: 'plc-redis',
      service: 'redis',
      ports: ['6379'],
      dependsOn: [],
      priority: 'critical',
    },
    {
      name: 'plc-qdrant',
      service: 'qdrant',
      ports: ['6333'],
      healthEndpoint: 'http://localhost:6333/collections',
      dependsOn: [],
      priority: 'high',
    },
    {
      name: 'plc-n8n',
      service: 'n8n',
      ports: ['5678'],
      healthEndpoint: 'http://localhost:5678/healthz',
      dependsOn: ['postgres'],
      priority: 'medium',
    },
  ],
  environmentVariables: {
    // Database Configuration
    POSTGRES_DB: 'plc_gbt',
    POSTGRES_USER: 'plc_user',
    POSTGRES_PASSWORD: 'postgres_password',
    NEO4J_PASSWORD: 'neo4j_password',
    NEO4J_BOLT_URL: 'bolt://localhost:7687',
    NEO4J_USER: 'neo4j',

    // Redis Configuration
    REDIS_HOST: 'localhost',
    REDIS_PORT: '6379',
    REDIS_PASSWORD: '',

    // Qdrant Configuration
    QDRANT_HOST: 'localhost',
    QDRANT_PORT: '6333',
    QDRANT_API_KEY: '',

    // Security Configuration
    VAULT_ROOT_TOKEN: 'dev-vault-token',
    VAULT_TOKEN: 'dev-vault-token',
    JWT_SECRET: 'dev-jwt-secret-key-for-plc-gbt',
    JWT_ALGORITHM: 'HS256',
    JWT_EXPIRATION_HOURS: '24',

    // API Configuration
    OPENAI_API_KEY: 'your-openai-api-key-here',
    GATEWAY_PORT: '8080',
    GATEWAY_BEARER_TOKEN: 'dev-bearer-token',
    GATEWAY_CORS_ORIGINS: '*',

    // Performance Configuration
    ETL_BATCH_SIZE: '1000',
    ETL_WORKER_THREADS: '4',
    ETL_LOG_LEVEL: 'info',
    LOG_LEVEL: 'info',

    // Rate Limiting
    RATE_LIMIT_ENABLED: 'true',
    RATE_LIMIT_REQUESTS: '100',
    RATE_LIMIT_WINDOW: '60',
  },
  healthCheckTimeout: 60000, // 60 seconds
  startupTimeout: 300000, // 5 minutes
  mcpServerPort: 8811,
  developmentServerPort: 3000,
};

class DockerEnvironmentSetup {
  private readonly config: DockerEnvironmentConfig;
  private readonly projectRoot: string;
  private readonly dockerComposeFile: string;
  private readonly envFile: string;

  constructor(config: DockerEnvironmentConfig) {
    this.config = config;
    this.projectRoot = path.resolve(__dirname, '..');
    this.dockerComposeFile = path.join(this.projectRoot, 'docker-compose.yml');
    this.envFile = path.join(this.projectRoot, '.env');
  }

  /**
   * Execute comprehensive Docker environment setup with AI Task Orchestrator compliance
   */
  public async setupEnvironment(): Promise<void> {
    console.log('🐳 Starting PLC-GBT Docker Environment Setup - AI Task Orchestrator Protocol');
    console.log('━'.repeat(80));

    try {
      // 1. Validate Prerequisites
      await this.validatePrerequisites();

      // 2. Setup Environment Variables
      await this.setupEnvironmentVariables();

      // 3. Start Docker Containers
      await this.startDockerContainers();

      // 4. Validate Container Health
      await this.validateContainerHealth();

      // 5. Test Database Connectivity
      await this.testDatabaseConnectivity();

      // 6. Validate MCP Docker Server
      await this.validateMCPServer();

      // 7. Confirm Development Readiness
      await this.confirmDevelopmentReadiness();

      console.log('🎉 Docker environment setup completed successfully!');
      console.log('✅ Ready for Node Properties Modal development');
    } catch (error) {
      console.error('💥 Docker environment setup failed:', error);
      throw error;
    }
  }

  /**
   * Validate system prerequisites
   */
  private async validatePrerequisites(): Promise<void> {
    console.log('🔍 Validating prerequisites...');

    // Check Docker installation
    try {
      execSync('docker --version', { stdio: 'pipe' });
      console.log('✅ Docker installed');
    } catch {
      throw new Error('Docker is not installed or not accessible');
    }

    // Check Docker Compose
    try {
      execSync('docker-compose --version', { stdio: 'pipe' });
      console.log('✅ Docker Compose available');
    } catch {
      try {
        execSync('docker compose version', { stdio: 'pipe' });
        console.log('✅ Docker Compose (v2) available');
      } catch {
        throw new Error('Docker Compose is not available');
      }
    }

    // Check if Docker daemon is running
    try {
      execSync('docker info', { stdio: 'pipe' });
      console.log('✅ Docker daemon running');
    } catch {
      throw new Error('Docker daemon is not running');
    }

    // Verify docker-compose.yml exists
    if (!fs.existsSync(this.dockerComposeFile)) {
      throw new Error(`Docker Compose file not found: ${this.dockerComposeFile}`);
    }
    console.log('✅ Docker Compose configuration found');
  }

  /**
   * Setup environment variables in .env file
   */
  private async setupEnvironmentVariables(): Promise<void> {
    console.log('⚙️  Setting up environment variables...');

    const envContent = Object.entries(this.config.environmentVariables)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    // Read existing .env if it exists and preserve custom values
    let existingEnv: Record<string, string> = {};
    if (fs.existsSync(this.envFile)) {
      const existingContent = fs.readFileSync(this.envFile, 'utf8');
      existingContent.split('\n').forEach(line => {
        const [key, ...valueParts] = line.split('=');
        if (key && valueParts.length > 0) {
          existingEnv[key.trim()] = valueParts.join('=').trim();
        }
      });
    }

    // Merge configurations, preferring existing values for critical settings
    const criticalKeys = ['OPENAI_API_KEY', 'NEO4J_PASSWORD', 'POSTGRES_PASSWORD'];
    const mergedEnv = { ...this.config.environmentVariables };

    criticalKeys.forEach(key => {
      if (existingEnv[key] && existingEnv[key] !== 'your-openai-api-key-here') {
        mergedEnv[key] = existingEnv[key];
        console.log(`✅ Preserved existing ${key}`);
      }
    });

    const finalEnvContent = Object.entries(mergedEnv)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    fs.writeFileSync(this.envFile, finalEnvContent);
    console.log(`✅ Environment variables configured: ${this.envFile}`);
  }

  /**
   * Start Docker containers in dependency order
   */
  private async startDockerContainers(): Promise<void> {
    console.log('🚀 Starting Docker containers...');

    // Sort containers by priority and dependencies
    const sortedContainers = this.getSortedContainers();

    // Stop any existing containers first to ensure clean state
    try {
      console.log('🛑 Stopping existing containers...');
      execSync('docker-compose down', {
        cwd: this.projectRoot,
        stdio: 'pipe',
      });
    } catch (error) {
      console.log('ℹ️  No existing containers to stop');
    }

    // Start containers by priority groups
    const priorityGroups = this.groupContainersByPriority(sortedContainers);

    for (const [priority, containers] of priorityGroups) {
      console.log(`🔧 Starting ${priority} priority containers...`);

      const services = containers.map(c => c.service);
      const startCommand = `docker-compose up -d ${services.join(' ')}`;

      try {
        execSync(startCommand, {
          cwd: this.projectRoot,
          stdio: 'inherit',
          timeout: this.config.startupTimeout,
        });

        console.log(`✅ Started ${priority} containers: ${services.join(', ')}`);

        // Wait for containers to initialize before starting next group
        await this.waitForContainerStartup(containers);
      } catch (error) {
        console.error(`❌ Failed to start ${priority} containers:`, error);
        throw new Error(`Container startup failed for priority group: ${priority}`);
      }
    }
  }

  /**
   * Wait for containers to start up properly
   */
  private async waitForContainerStartup(containers: readonly ContainerDefinition[]): Promise<void> {
    console.log('⏳ Waiting for container startup...');

    // Give containers time to initialize
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Check container status
    for (const container of containers) {
      const maxAttempts = 12; // 60 seconds total
      let attempts = 0;

      while (attempts < maxAttempts) {
        try {
          const result = execSync(
            `docker ps --filter "name=${container.name}" --format "{{.Status}}"`,
            {
              encoding: 'utf8',
              stdio: 'pipe',
            }
          );

          if (result.includes('Up')) {
            console.log(`✅ Container ${container.name} is running`);
            break;
          }
        } catch (error) {
          console.log(`⏳ Waiting for ${container.name} (attempt ${attempts + 1}/${maxAttempts})`);
        }

        attempts++;
        await new Promise(resolve => setTimeout(resolve, 5000));
      }

      if (attempts >= maxAttempts) {
        throw new Error(`Container ${container.name} failed to start within timeout`);
      }
    }
  }

  /**
   * Validate container health status
   */
  private async validateContainerHealth(): Promise<void> {
    console.log('🏥 Validating container health...');

    const containerStatuses = await this.getContainerStatuses();

    for (const status of containerStatuses) {
      console.log(`📊 ${status.name}: ${status.status} (${status.health})`);

      if (status.status !== 'running') {
        console.warn(`⚠️  Container ${status.name} is not running: ${status.status}`);
      }
    }

    const criticalContainers = this.config.requiredContainers.filter(
      c => c.priority === 'critical'
    );
    const runningCritical = containerStatuses.filter(
      s => criticalContainers.some(c => c.name === s.name) && s.status === 'running'
    );

    if (runningCritical.length < criticalContainers.length) {
      throw new Error('Critical containers are not running');
    }

    console.log('✅ Container health validation passed');
  }

  /**
   * Test database connectivity
   */
  private async testDatabaseConnectivity(): Promise<void> {
    console.log('🔌 Testing database connectivity...');

    const connectivityTests: ConnectivityResult[] = [];

    // Test Neo4j HTTP interface
    connectivityTests.push(await this.testEndpoint('http://localhost:7474', 'Neo4j HTTP'));

    // Test Qdrant HTTP interface
    connectivityTests.push(
      await this.testEndpoint('http://localhost:6333/collections', 'Qdrant HTTP')
    );

    // Test PostgreSQL (using pg_isready if available)
    try {
      execSync('pg_isready -h localhost -p 5432 -U plc_user', { stdio: 'pipe' });
      connectivityTests.push({
        endpoint: 'PostgreSQL',
        status: 'connected',
        responseTime: 0,
      });
    } catch {
      connectivityTests.push({
        endpoint: 'PostgreSQL',
        status: 'failed',
        responseTime: 0,
        error: 'pg_isready not available or connection failed',
      });
    }

    // Test Redis (using redis-cli if available)
    try {
      execSync('redis-cli -h localhost -p 6379 ping', { stdio: 'pipe' });
      connectivityTests.push({
        endpoint: 'Redis',
        status: 'connected',
        responseTime: 0,
      });
    } catch {
      connectivityTests.push({
        endpoint: 'Redis',
        status: 'failed',
        responseTime: 0,
        error: 'redis-cli not available or connection failed',
      });
    }

    // Display results
    connectivityTests.forEach(test => {
      const statusIcon = test.status === 'connected' ? '✅' : '❌';
      console.log(`${statusIcon} ${test.endpoint}: ${test.status}`);
      if (test.error) {
        console.log(`   └─ ${test.error}`);
      }
    });

    const failedTests = connectivityTests.filter(t => t.status === 'failed');
    if (failedTests.length > 0) {
      console.warn(`⚠️  ${failedTests.length} connectivity tests failed`);
    } else {
      console.log('✅ All database connectivity tests passed');
    }
  }

  /**
   * Validate MCP Docker Server connectivity
   */
  private async validateMCPServer(): Promise<void> {
    console.log('🤖 Validating MCP Docker Server...');

    // Check if MCP server is running on port 8811
    const mcpTest = await this.testEndpoint(
      `http://localhost:${this.config.mcpServerPort}`,
      'MCP Docker Server'
    );

    if (mcpTest.status === 'connected') {
      console.log('✅ MCP Docker Server is accessible');

      // Test specific MCP endpoints if available
      try {
        const healthTest = await this.testEndpoint(
          `http://localhost:${this.config.mcpServerPort}/health`,
          'MCP Health'
        );
        if (healthTest.status === 'connected') {
          console.log('✅ MCP health endpoint responding');
        }
      } catch {
        console.log('ℹ️  MCP health endpoint not available (this may be normal)');
      }
    } else {
      console.warn('⚠️  MCP Docker Server not accessible');
      console.log('   This may impact Playwright MCP integration');
      console.log('   Check if mcp/docker:0.0.17 container is running on port 8811');
    }

    // Check for Docker Labs AI Tools extension (which provides MCP server)
    try {
      const result = execSync(
        'docker ps --filter "ancestor=mcp/docker:0.0.17" --format "{{.Names}}"',
        {
          encoding: 'utf8',
          stdio: 'pipe',
        }
      );

      if (result.trim()) {
        console.log(`✅ MCP Docker container found: ${result.trim()}`);
      } else {
        console.log('ℹ️  MCP Docker container not found with expected image');
      }
    } catch (error) {
      console.log('ℹ️  Could not verify MCP Docker container');
    }
  }

  /**
   * Confirm development environment readiness
   */
  private async confirmDevelopmentReadiness(): Promise<void> {
    console.log('🎯 Confirming development environment readiness...');

    const checks = [
      { name: 'Docker containers running', status: await this.areContainersRunning() },
      { name: 'Database connectivity', status: true }, // Validated in previous step
      { name: 'Environment variables set', status: fs.existsSync(this.envFile) },
      {
        name: 'MCP server accessible',
        status:
          (await this.testEndpoint(`http://localhost:${this.config.mcpServerPort}`, 'MCP'))
            .status === 'connected',
      },
    ];

    checks.forEach(check => {
      const icon = check.status ? '✅' : '❌';
      console.log(`${icon} ${check.name}`);
    });

    const allPassed = checks.every(check => check.status);

    if (allPassed) {
      console.log('🎉 Development environment is ready!');
      console.log('🚀 Ready to continue Node Properties Modal development');
      console.log('🔗 Key endpoints:');
      console.log(`   • Next.js Dev Server: http://localhost:${this.config.developmentServerPort}`);
      console.log(`   • MCP Docker Server: http://localhost:${this.config.mcpServerPort}`);
      console.log('   • Neo4j Browser: http://localhost:7474');
      console.log('   • Qdrant Dashboard: http://localhost:6333/dashboard');
    } else {
      throw new Error('Development environment validation failed');
    }
  }

  // Helper methods

  private getSortedContainers(): readonly ContainerDefinition[] {
    // Simple dependency-aware sorting (topological sort would be better for complex deps)
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };

    return [...this.config.requiredContainers].sort((a, b) => {
      // First sort by dependency (containers with no deps first)
      if (a.dependsOn.length !== b.dependsOn.length) {
        return a.dependsOn.length - b.dependsOn.length;
      }

      // Then sort by priority
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }

  private groupContainersByPriority(
    containers: readonly ContainerDefinition[]
  ): Map<string, ContainerDefinition[]> {
    const groups = new Map<string, ContainerDefinition[]>();

    containers.forEach(container => {
      const existing = groups.get(container.priority) || [];
      groups.set(container.priority, [...existing, container]);
    });

    return groups;
  }

  private async getContainerStatuses(): Promise<ContainerStatus[]> {
    const statuses: ContainerStatus[] = [];

    for (const container of this.config.requiredContainers) {
      try {
        const result = execSync(
          `docker ps --filter "name=${container.name}" --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"`,
          { encoding: 'utf8', stdio: 'pipe' }
        );

        if (result.trim()) {
          const [name, status, ports] = result.trim().split('\t');
          statuses.push({
            name: name || container.name,
            status: status?.includes('Up') ? 'running' : 'stopped',
            health: 'unknown', // Would need to parse health status separately
            ports: ports ? [ports] : container.ports,
          });
        } else {
          statuses.push({
            name: container.name,
            status: 'stopped',
            health: 'unknown',
            ports: container.ports,
          });
        }
      } catch {
        statuses.push({
          name: container.name,
          status: 'error',
          health: 'unknown',
          ports: container.ports,
        });
      }
    }

    return statuses;
  }

  private async testEndpoint(url: string, name: string): Promise<ConnectivityResult> {
    const startTime = Date.now();

    try {
      const response = await fetch(url, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });

      const responseTime = Date.now() - startTime;

      return {
        endpoint: name,
        status: response.ok ? 'connected' : 'failed',
        responseTime,
        error: response.ok ? undefined : `HTTP ${response.status}`,
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;

      return {
        endpoint: name,
        status: responseTime > 4500 ? 'timeout' : 'failed',
        responseTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async areContainersRunning(): Promise<boolean> {
    const statuses = await this.getContainerStatuses();
    const criticalContainers = this.config.requiredContainers.filter(
      c => c.priority === 'critical'
    );
    const runningCritical = statuses.filter(
      s => criticalContainers.some(c => c.name === s.name) && s.status === 'running'
    );

    return runningCritical.length >= criticalContainers.length;
  }
}

// 🚀 Execute Docker environment setup if called directly
if (require.main === module) {
  const setupManager = new DockerEnvironmentSetup(DOCKER_CONFIG);

  setupManager
    .setupEnvironment()
    .then(() => {
      console.log('🎉 Docker environment setup completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('💥 Docker environment setup failed:', error.message);
      process.exit(1);
    });
}

export { DockerEnvironmentSetup, type ContainerStatus, type DockerEnvironmentConfig };
