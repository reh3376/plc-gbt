# MCP Browser Automation & OpenAPI Schema Integration Fix Roadmap

**Created**: January 20, 2025  
**Purpose**: Methodically fix MCP browser automation tools and establish proper OpenAPI Schema MCP integration  
**Methodology**: AI Task Orchestrator TypeScript Guide  
**Critical Issue**: Automated testing blocked due to fake OpenAPI Schema MCP implementation violating core methodology  

## 🚨 CRITICAL FINDING: Core Methodology Violation

The current implementation violates the fundamental requirement stated in `API_CREATION_METHODOLOGY.md`:

> **MANDATORY RULE**: All API definitions, JSON schemas, and UI schemas MUST use the OpenAPI Schema MCP from MCP_Docker server. **NO EXCEPTIONS**. As specified in the API_CREATION_METHODOLOGY.md file

### Root Cause Analysis
1. **Fake MCP Client**: The `openapi-schema-client.ts` is a mock implementation with hardcoded schemas
2. **No Real MCP Connection**: The client pretends to connect but doesn't actually reach MCP Docker
3. **Hardcoded Schemas**: All schemas are embedded in the file instead of retrieved from MCP Docker
4. **Browser Automation Blocked**: MCP browser tools require proper MCP Docker connection to function

## 📋 Phase 1: Diagnostic & Infrastructure Assessment
**Status**: 🔄 IN PROGRESS  
**Objective**: Understand current state and identify all broken connections

### Sub-Phase 1.1: MCP Docker Service Analysis
- [x] Check all running Docker containers
- [x] Verify MCP-related services status
- [x] Identify missing or misconfigured services
- [x] Document current Docker network configuration

**Findings:**
- ✅ Database services running: plc-redis, plc-postgres, plc-neo4j, plc-qdrant
- ✅ MCP browser container running: mcp-browser (Playwright v1.53.2)
- ✅ N8N-MCP service running on port 3000
- ✅ **Docker MCP service running on port 8811 (includes OpenAPI Schema tools)**
- ✅ Network: plc-gbt-stack_plc-database-network exists and databases are connected

### Sub-Phase 1.2: MCP Configuration Audit
- [x] Review `.cursor/mcp.json` configuration
- [x] Check for OpenAPI Schema MCP server configuration
- [x] Identify MCP server endpoints and ports
- [x] Document authentication requirements

**Findings:**
- ✅ N8N-MCP configured in `.cursor/mcp.json` (port 3000)
- ✅ **Docker MCP service (`mcp/docker:0.0.17`) running on port 8811**
- ⚠️ **OpenAPI Schema tools exist in Docker MCP but not being used**
- ⚠️ Fake client expects server at `http://localhost:3001/mcp` (but dev server runs on 3000)
- ❌ **Current implementation uses fake hardcoded schemas instead of Docker MCP**

### Sub-Phase 1.3: Current Implementation Analysis
- [x] Audit `openapi-schema-client.ts` fake implementation
- [x] Identify all hardcoded schemas that need migration
- [x] Map current API endpoints using fake validation
- [x] Document all components dependent on fake MCP

**Findings:**
- 📊 **27 hardcoded component schemas** in fake implementation
- 📊 **14 API endpoints** defined with fake validation
- ⚠️ All schemas are hardcoded in `loadOpenAPISchemasSync()` method
- ⚠️ No actual network connection - just logs fake success
- ⚠️ Validation is done locally, not through MCP server

**Hardcoded Schemas Requiring Migration:**
1. **Workflow Schemas**: WorkflowNode, WorkflowEdge, WorkflowMetadata, WorkflowData
2. **Node Property Schemas**: NodePropertySchema, PropertyField, PropertyGroup, PropertyConstraints
3. **Industrial Node Types**: IndustrialNodeType (54 types), PropertyFieldType, ValidationSeverity
4. **Support Schemas**: SupportEmailRequest, SupportEmailResponse, ErrorResponse
5. **Validation Schemas**: ValidationResult, ConnectionTestResult, NodeConfigurationValidation*

**API Endpoints Using Fake Validation:**
1. GET /api/v1/files
2. PUT /api/v1/files/{id}/move
3. PUT /api/v1/files/{id}/rename
4. GET /api/v1/workflows
5. POST /api/v1/workflows
6. PUT /api/v1/workflows/{id}
7. PUT /api/v1/workflows/{id}/execute
8. GET /api/v1/workflows/{id}/status
9. GET /api/v1/node-properties/{nodeType}
10. POST /api/v1/node-properties/{nodeType}/validate
11. POST /api/v1/node-properties/{nodeType}/test-connection
12. POST /api/v1/support/send-email

## 📋 Phase 2: MCP Docker Infrastructure Setup
**Status**: ⏳ PENDING  
**Objective**: Establish proper MCP Docker services and connections

### Sub-Phase 2.1: OpenAPI Schema MCP Server Setup
- [ ] Deploy OpenAPI Schema MCP server container
- [ ] Configure proper networking (plc-internal-network)
- [ ] Set up authentication tokens
- [ ] Verify server health endpoints

### Sub-Phase 2.2: MCP Browser Automation Server Setup
- [ ] Verify Playwright container configuration
- [ ] Establish MCP browser service connection
- [ ] Configure browser automation endpoints
- [ ] Test basic browser commands

### Sub-Phase 2.3: Network Integration
- [ ] Connect all MCP services to shared network
- [ ] Configure service discovery
- [ ] Set up inter-service communication
- [ ] Test connectivity between services

## 📋 Phase 3: Real OpenAPI Schema MCP Client Implementation
**Status**: ⏳ PENDING  
**Objective**: Replace fake client with real MCP Docker integration

### Sub-Phase 3.1: MCP Client Development
- [ ] Create real MCP Docker client connection
- [ ] Implement proper authentication
- [ ] Add connection retry logic
- [ ] Implement health check monitoring

### Sub-Phase 3.2: Schema Migration
- [ ] Connect to real OpenAPI Schema MCP server
- [ ] Retrieve actual schemas from MCP Docker
- [ ] Validate retrieved schemas match expected format
- [ ] Replace all hardcoded schemas with MCP calls

### Sub-Phase 3.3: Validation Implementation
- [ ] Implement real-time schema validation via MCP
- [ ] Add request/response validation endpoints
- [ ] Implement schema versioning support
- [ ] Add comprehensive error handling

## 📋 Phase 4: API Integration Migration
**Status**: ⏳ PENDING  
**Objective**: Update all API routes to use real MCP validation

### Sub-Phase 4.1: API Route Updates
- [ ] Update node properties API routes
- [ ] Update workflow management API routes
- [ ] Update file operations API routes
- [ ] Update support/help API routes

### Sub-Phase 4.2: Type Generation Pipeline
- [ ] Set up automated type generation from MCP
- [ ] Configure openapi-typescript integration
- [ ] Implement Zod schema generation
- [ ] Add CI/CD validation checks

### Sub-Phase 4.3: Frontend Integration
- [ ] Update all frontend API clients
- [ ] Implement runtime validation hooks
- [ ] Add type-safe API method generation
- [ ] Update error handling patterns

## 📋 Phase 5: Browser Automation Restoration
**Status**: ⏳ PENDING  
**Objective**: Enable MCP browser automation for testing

### Sub-Phase 5.1: MCP Browser Client Setup
- [ ] Establish connection to MCP browser service
- [ ] Configure browser navigation endpoints
- [ ] Set up element interaction methods
- [ ] Implement screenshot/snapshot capabilities

### Sub-Phase 5.2: Playwright MCP Integration
- [ ] Connect Playwright to MCP Docker
- [ ] Configure test runner integration
- [ ] Set up automated test execution
- [ ] Implement test result reporting

### Sub-Phase 5.3: Test Migration
- [ ] Update existing Playwright tests for MCP
- [ ] Add proper Docker networking (host.docker.internal)
- [ ] Implement two-phase testing protocol
- [ ] Validate >95% automated test success rate

## 📋 Phase 6: Validation & Testing
**Status**: ⏳ PENDING  
**Objective**: Ensure all systems working correctly

### Sub-Phase 6.1: Integration Testing
- [ ] Test OpenAPI Schema MCP validation
- [ ] Test browser automation functionality
- [ ] Verify API request/response validation
- [ ] Test type generation pipeline

### Sub-Phase 6.2: Performance Validation
- [ ] Measure MCP connection latency
- [ ] Test schema validation performance
- [ ] Verify browser automation speed
- [ ] Optimize connection pooling

### Sub-Phase 6.3: Documentation Updates
- [ ] Update API Creation Methodology docs
- [ ] Document MCP Docker setup process
- [ ] Create troubleshooting guide
- [ ] Update developer onboarding

## 🎯 Success Criteria

1. **OpenAPI Schema MCP**: Real connection to MCP Docker server established
2. **Schema Validation**: All API schemas retrieved from MCP, not hardcoded
3. **Browser Automation**: MCP browser tools fully functional
4. **Type Safety**: Zero manual API type definitions
5. **Testing**: >95% automated test success rate achieved
6. **Documentation**: Complete setup and usage documentation

## 🚨 Critical Path Items

1. **BLOCKER**: Cannot proceed with automated testing until MCP connection fixed
2. **DEPENDENCY**: All API development blocked until real OpenAPI Schema MCP working
3. **RISK**: Current fake implementation may have introduced schema drift

## 📊 Progress Tracking

| Phase | Status | Completion | Blocking Issues |
|-------|--------|------------|-----------------|
| Phase 1 | ✅ COMPLETE | 100% | Diagnostic complete - OpenAPI MCP server missing |
| Phase 2 | 🔄 NEXT | 0% | Need to create OpenAPI Schema MCP Docker service |
| Phase 3 | ⏳ PENDING | 0% | Waiting on Phase 2 |
| Phase 4 | ⏳ PENDING | 0% | Waiting on Phase 3 |
| Phase 5 | ⏳ PENDING | 0% | Waiting on Phase 4 |
| Phase 6 | ⏳ PENDING | 0% | Waiting on Phase 5 |

## 🔄 Next Immediate Actions

### 🚨 **CRITICAL DISCOVERY: Docker MCP Already Has OpenAPI Tools!**

The Docker MCP server (`mcp/docker:0.0.17`) is already running on port 8811 and should include OpenAPI schema management tools. This changes our approach:

1. **Verify Docker MCP OpenAPI Tools** (IMMEDIATE)
   - Check what OpenAPI tools are available in Docker MCP
   - Test OpenAPI schema validation functionality
   - Document available MCP commands

2. **Update Client to Use Docker MCP** (Phase 3.1)
   - Change fake client URL from `localhost:3001` to Docker MCP at `localhost:8811`
   - Use Docker MCP's actual OpenAPI tools
   - Remove fake schema implementations
   - Note: Dev server runs on port 3000, not 3001

3. **Test Browser Automation Tools** (Phase 2.2)
   - Verify mcp_MCP_DOCKER_browser_* tools are working
   - Test with proper Docker MCP connection
   - Document any configuration needed

4. **Migrate to Real MCP Validation** (Phase 3.2)
   - Replace hardcoded schemas with Docker MCP calls
   - Implement proper request/response validation
   - Update all API endpoints

## 📝 Notes

- This is a critical infrastructure issue that blocks all automated testing
- The fake OpenAPI Schema MCP client has created technical debt
- Proper MCP Docker integration is mandatory per AI Task Orchestrator methodology
- No workarounds should be attempted - fix the root cause

### Port Clarification:
- **Port 3000**: Next.js dev server (actual application)
- **Port 3001**: Where fake openapi-schema-client.ts expects MCP server (incorrect)
- **Port 8811**: Docker MCP server (mcp/docker:0.0.17) - the real MCP service
- **Port 3000**: N8N-MCP service (different from OpenAPI MCP)

---

**Remember**: We NEVER give up when confronted with a difficult task. We adapt, and overcome.
