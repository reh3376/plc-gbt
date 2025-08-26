#!/usr/bin/env tsx

/**
 * 🤖 MCP Docker Server Connectivity Validation
 *
 * AI Task Orchestrator TypeScript Methodology Compliance:
 * - Zero `any` types - strict TypeScript throughout
 * - Comprehensive MCP server validation
 * - Playwright MCP integration testing
 * - Production-ready connectivity validation
 */

import { execSync } from 'child_process';

interface MCPValidationConfig {
  readonly mcpServerPort: number;
  readonly playwrightServerPort: number;
  readonly timeoutMs: number;
  readonly retryAttempts: number;
  readonly healthCheckEndpoints: readonly string[];
}

interface MCPValidationResult {
  readonly serverAccessible: boolean;
  readonly playwrightIntegration: boolean;
  readonly dockerNetworking: boolean;
  readonly healthChecks: readonly HealthCheckResult[];
  readonly overallStatus: 'ready' | 'partial' | 'failed';
  readonly recommendations: readonly string[];
}

interface HealthCheckResult {
  readonly endpoint: string;
  readonly status: 'success' | 'failed' | 'timeout';
  readonly responseTime: number;
  readonly error?: string;
}

// 🎯 AI Task Orchestrator MCP Configuration
const MCP_CONFIG: MCPValidationConfig = {
  mcpServerPort: 8811,
  playwrightServerPort: 3000,
  timeoutMs: 10000,
  retryAttempts: 3,
  healthCheckEndpoints: [
    'http://localhost:8811',
    'http://localhost:8811/health',
    'http://localhost:8811/mcp',
    'http://host.docker.internal:8811', // Docker networking test
    'http://localhost:3000', // Development server
    'http://host.docker.internal:3000', // Docker networking for Playwright
  ],
};

class MCPConnectivityValidator {
  private readonly config: MCPValidationConfig;

  constructor(config: MCPValidationConfig) {
    this.config = config;
  }

  /**
   * Execute comprehensive MCP connectivity validation
   */
  public async validateMCPConnectivity(): Promise<MCPValidationResult> {
    console.log('🤖 Starting MCP Docker Server Connectivity Validation');
    console.log('━'.repeat(70));

    try {
      // 1. Check MCP Docker Container Status
      const containerStatus = await this.validateMCPContainer();

      // 2. Test Network Connectivity
      const healthChecks = await this.performHealthChecks();

      // 3. Validate Docker Networking
      const dockerNetworking = await this.validateDockerNetworking();

      // 4. Test Playwright Integration
      const playwrightIntegration = await this.validatePlaywrightIntegration();

      // 5. Generate Results and Recommendations
      const result = this.generateValidationResult(
        containerStatus,
        healthChecks,
        dockerNetworking,
        playwrightIntegration
      );

      this.displayResults(result);
      return result;
    } catch (error) {
      console.error('💥 MCP validation failed:', error);
      throw error;
    }
  }

  /**
   * Validate MCP Docker container is running
   */
  private async validateMCPContainer(): Promise<boolean> {
    console.log('🐳 Checking MCP Docker container status...');

    try {
      // Check for mcp/docker container
      const mcpContainer = execSync(
        'docker ps --filter "ancestor=mcp/docker" --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"',
        { encoding: 'utf8', stdio: 'pipe' }
      );

      if (mcpContainer.trim()) {
        console.log('✅ MCP Docker container found:');
        console.log(`   ${mcpContainer.trim()}`);
        return true;
      }

      // Check for any container on port 8811
      const portContainer = execSync(
        'docker ps --filter "publish=8811" --format "{{.Names}}\t{{.Image}}\t{{.Ports}}"',
        { encoding: 'utf8', stdio: 'pipe' }
      );

      if (portContainer.trim()) {
        console.log('✅ Container found on MCP port 8811:');
        console.log(`   ${portContainer.trim()}`);
        return true;
      }

      console.log('❌ No MCP Docker container found');
      return false;
    } catch (error) {
      console.log('❌ Error checking Docker containers:', error);
      return false;
    }
  }

  /**
   * Perform health checks on all MCP endpoints
   */
  private async performHealthChecks(): Promise<readonly HealthCheckResult[]> {
    console.log('🏥 Performing MCP health checks...');

    const results: HealthCheckResult[] = [];

    for (const endpoint of this.config.healthCheckEndpoints) {
      const result = await this.testEndpoint(endpoint);
      results.push(result);

      const statusIcon =
        result.status === 'success' ? '✅' : result.status === 'timeout' ? '⏱️' : '❌';
      console.log(`${statusIcon} ${endpoint} (${result.responseTime}ms)`);

      if (result.error) {
        console.log(`   └─ ${result.error}`);
      }
    }

    return results;
  }

  /**
   * Validate Docker networking for MCP integration
   */
  private async validateDockerNetworking(): Promise<boolean> {
    console.log('🔗 Validating Docker networking...');

    try {
      // Test host.docker.internal resolution
      const hostDockerTest = await this.testEndpoint('http://host.docker.internal:8811');

      if (hostDockerTest.status === 'success') {
        console.log('✅ Docker networking (host.docker.internal) working');
        return true;
      }

      // Test if we're in a Docker container ourselves
      const inContainer = await this.isRunningInContainer();
      if (inContainer) {
        console.log('ℹ️  Running inside Docker container - host.docker.internal expected to work');

        // Test internal Docker networking
        const internalTest = await this.testEndpoint('http://mcp-server:8811');
        if (internalTest.status === 'success') {
          console.log('✅ Internal Docker networking working');
          return true;
        }
      }

      console.log('⚠️  Docker networking validation incomplete');
      return false;
    } catch (error) {
      console.log('❌ Docker networking validation failed:', error);
      return false;
    }
  }

  /**
   * Validate Playwright MCP integration readiness
   */
  private async validatePlaywrightIntegration(): Promise<boolean> {
    console.log('🎭 Validating Playwright MCP integration...');

    try {
      // Check if development server is accessible
      const devServerTest = await this.testEndpoint(
        `http://localhost:${this.config.playwrightServerPort}`
      );

      if (devServerTest.status !== 'success') {
        console.log('⚠️  Development server not accessible');
        console.log('   Start with: npm run dev (in plc-gbt-stack/ui/nextjs)');
        return false;
      }

      // Check Docker networking for Playwright
      const dockerPlaywrightTest = await this.testEndpoint(
        `http://host.docker.internal:${this.config.playwrightServerPort}`
      );

      if (dockerPlaywrightTest.status === 'success') {
        console.log('✅ Playwright Docker networking ready');
        return true;
      }

      console.log('⚠️  Playwright Docker networking not working');
      console.log('   This may impact automated testing');
      return false;
    } catch (error) {
      console.log('❌ Playwright integration validation failed:', error);
      return false;
    }
  }

  /**
   * Test individual endpoint connectivity
   */
  private async testEndpoint(url: string): Promise<HealthCheckResult> {
    const startTime = Date.now();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeoutMs);

      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'User-Agent': 'PLC-GBT-MCP-Validator/1.0',
        },
      });

      clearTimeout(timeoutId);
      const responseTime = Date.now() - startTime;

      return {
        endpoint: url,
        status: response.ok ? 'success' : 'failed',
        responseTime,
        error: response.ok ? undefined : `HTTP ${response.status} ${response.statusText}`,
      };
    } catch (error) {
      const responseTime = Date.now() - startTime;

      if (error instanceof Error && error.name === 'AbortError') {
        return {
          endpoint: url,
          status: 'timeout',
          responseTime,
          error: `Timeout after ${this.config.timeoutMs}ms`,
        };
      }

      return {
        endpoint: url,
        status: 'failed',
        responseTime,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Check if we're running inside a Docker container
   */
  private async isRunningInContainer(): Promise<boolean> {
    try {
      // Check for Docker-specific files
      const { execSync } = await import('child_process');

      // Check for .dockerenv file
      try {
        execSync('test -f /.dockerenv', { stdio: 'pipe' });
        return true;
      } catch {
        // Check cgroup for Docker
        try {
          const cgroup = execSync('cat /proc/1/cgroup', { encoding: 'utf8', stdio: 'pipe' });
          return cgroup.includes('docker') || cgroup.includes('containerd');
        } catch {
          return false;
        }
      }
    } catch {
      return false;
    }
  }

  /**
   * Generate comprehensive validation result
   */
  private generateValidationResult(
    containerStatus: boolean,
    healthChecks: readonly HealthCheckResult[],
    dockerNetworking: boolean,
    playwrightIntegration: boolean
  ): MCPValidationResult {
    const serverAccessible = healthChecks.some(
      check => check.endpoint.includes('localhost:8811') && check.status === 'success'
    );

    // Determine overall status
    let overallStatus: 'ready' | 'partial' | 'failed';
    if (serverAccessible && dockerNetworking && playwrightIntegration) {
      overallStatus = 'ready';
    } else if (serverAccessible || dockerNetworking) {
      overallStatus = 'partial';
    } else {
      overallStatus = 'failed';
    }

    // Generate recommendations
    const recommendations: string[] = [];

    if (!containerStatus) {
      recommendations.push(
        'Start MCP Docker container: docker run -d -p 8811:8811 mcp/docker:0.0.17'
      );
    }

    if (!serverAccessible) {
      recommendations.push('Verify MCP server is accessible on port 8811');
    }

    if (!dockerNetworking) {
      recommendations.push('Enable Docker Desktop or verify Docker networking configuration');
    }

    if (!playwrightIntegration) {
      recommendations.push('Start development server: npm run dev (in plc-gbt-stack/ui/nextjs)');
      recommendations.push('Verify host.docker.internal resolution in Docker environment');
    }

    return {
      serverAccessible,
      playwrightIntegration,
      dockerNetworking,
      healthChecks,
      overallStatus,
      recommendations,
    };
  }

  /**
   * Display validation results
   */
  private displayResults(result: MCPValidationResult): void {
    console.log('━'.repeat(70));
    console.log('📊 MCP CONNECTIVITY VALIDATION RESULTS');
    console.log('━'.repeat(70));

    // Overall status
    const statusIcon =
      result.overallStatus === 'ready' ? '✅' : result.overallStatus === 'partial' ? '⚠️' : '❌';
    console.log(`${statusIcon} Overall Status: ${result.overallStatus.toUpperCase()}`);
    console.log();

    // Component status
    console.log('🔍 Component Status:');
    console.log(`   ${result.serverAccessible ? '✅' : '❌'} MCP Server Accessible`);
    console.log(`   ${result.dockerNetworking ? '✅' : '❌'} Docker Networking`);
    console.log(`   ${result.playwrightIntegration ? '✅' : '❌'} Playwright Integration`);
    console.log();

    // Health check summary
    const successCount = result.healthChecks.filter(h => h.status === 'success').length;
    console.log(`🏥 Health Checks: ${successCount}/${result.healthChecks.length} passed`);
    console.log();

    // Recommendations
    if (result.recommendations.length > 0) {
      console.log('💡 Recommendations:');
      result.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. ${rec}`);
      });
      console.log();
    }

    // Ready status
    if (result.overallStatus === 'ready') {
      console.log('🎉 MCP connectivity is ready for Node Properties Modal development!');
      console.log('🚀 You can proceed with Playwright MCP testing');
    } else {
      console.log('⚠️  MCP connectivity issues detected');
      console.log('🔧 Please address recommendations before proceeding');
    }
  }
}

// 🚀 Execute MCP validation if called directly
if (require.main === module) {
  const validator = new MCPConnectivityValidator(MCP_CONFIG);

  validator
    .validateMCPConnectivity()
    .then(result => {
      const exitCode = result.overallStatus === 'ready' ? 0 : 1;
      process.exit(exitCode);
    })
    .catch(error => {
      console.error('💥 MCP validation failed:', error.message);
      process.exit(1);
    });
}

export { MCPConnectivityValidator, type MCPValidationResult };
