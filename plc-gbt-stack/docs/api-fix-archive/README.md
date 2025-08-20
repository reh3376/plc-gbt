# API Fix Archive

## Purpose
This directory contains archived versions of API-related files that were replaced during the MCP Browser Automation & OpenAPI Schema Integration Fix implementation.

## Files Archived

### `fake-openapi-schema-client.ts`
- **Original Location**: `plc-gbt-stack/ui/nextjs/src/lib/mcp/openapi-schema-client.ts`
- **Archived Date**: January 20, 2025
- **Reason**: Replaced with real Docker MCP integration
- **Issues**: 
  - Violated AI Task Orchestrator methodology by using hardcoded schemas
  - Contained 27 hardcoded component schemas instead of MCP server calls
  - Used fake validation instead of real MCP Docker server validation
  - Expected server on incorrect port 3001 instead of Docker MCP port 8811

### Replacement Implementation
- **New File**: `plc-gbt-stack/ui/nextjs/src/lib/mcp/real-openapi-mcp-client.ts`
- **Features**:
  - Connects to actual Docker MCP server on port 8811
  - Real schema validation via MCP endpoints
  - Proper error handling and retry logic
  - Strict TypeScript compliance (zero `any` types)
  - Compatible interface with existing code

## Important Notes
- **DO NOT USE** archived files for active development
- These files are kept for reference and rollback purposes only
- All new development should use the real MCP client implementations
- See `MCP_BROWSER_AUTOMATION_FIX_ROADMAP.md` for complete implementation details

## Related Documentation
- [MCP Browser Automation Fix Roadmap](../MCP_BROWSER_AUTOMATION_FIX_ROADMAP.md)
- [API Creation Methodology](../API_CREATION_METHODOLOGY.md)
- [AI Task Orchestrator TypeScript Guide](../AI_TASK_ORCHESTRATOR_TS_GUIDE.md)
