/**
 * User Agent Testing Framework - Phase 31
 * Refactored for reduced complexity and improved maintainability
 */

// Main framework export
export { default as UserAgentTestingFramework } from './refactored-user-agent-testing';

// Component exports
export * from './types';
export * from './executors';
export * from './utils';

// Legacy export for compatibility (use refactored version)
export { default as LegacyUserAgentTestingFramework } from './user-agent-testing'; 