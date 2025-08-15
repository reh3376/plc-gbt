# PLC-GBT API Creation & Usage Methodology

**Based on:** Frontend Schema API Contract Playbook (Zod + OpenAPI)  
**Purpose:** Ensure zero-drift between API contracts and implementation with strict type safety and runtime validation  
**Last Updated:** December 22, 2024

---

## 🎯 Core Principles

1. **OpenAPI Schema MCP is the Single Source of Truth** - All API contracts must be defined using the OpenAPI Schema MCP tool
2. **Zero Manual Type Definitions** - All types are generated from OpenAPI schemas
3. **Runtime Validation Everywhere** - Every API request/response must be validated with Zod schemas
4. **Strict TypeScript Compliance** - Zero `any` types policy throughout the codebase
5. **CI/CD Enforcement** - Build fails if schemas are out of sync

---

## 📋 API Development Workflow

### Step 1: Define OpenAPI Schema

Always use the OpenAPI Schema MCP tool (`@/lib/mcp/openapi-schema-client.ts`) to define schemas:

```typescript
// In openapi-schema-client.ts
export const schemas: Record<string, OpenAPISchema> = {
  WorkflowData: {
    type: 'object',
    required: ['metadata', 'nodes', 'edges'],
    properties: {
      metadata: { $ref: '#/components/schemas/WorkflowMetadata' },
      nodes: {
        type: 'array',
        items: { $ref: '#/components/schemas/WorkflowNode' }
      },
      edges: {
        type: 'array',
        items: { $ref: '#/components/schemas/WorkflowEdge' }
      },
      variables: {
        type: 'object',
        additionalProperties: true
      }
    }
  }
  // ... other schemas
};
```

### Step 2: Generate TypeScript Types

Types are automatically generated from the OpenAPI schemas:

```typescript
// In your types file
import type { components } from '@/lib/mcp/openapi-schema-client';

export type WorkflowData = components['schemas']['WorkflowData'];
export type WorkflowMetadata = components['schemas']['WorkflowMetadata'];
```

### Step 3: Implement API Route with Validation

Every API route MUST validate requests and responses:

```typescript
// In app/api/v1/workflows/[id]/route.ts
import { openAPISchemaMCP } from '@/lib/mcp/openapi-schema-client';
import type { WorkflowData } from '@/lib/types/workflow-management.types';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
): Promise<NextResponse> {
  try {
    // 1. Fetch or generate data
    const workflowData: WorkflowData = await fetchWorkflowData(params.id);
    
    // 2. Create response
    const response = {
      success: true,
      message: 'Workflow retrieved successfully',
      data: workflowData
    };
    
    // 3. MANDATORY: Validate response against OpenAPI schema
    const validationResult = await openAPISchemaMCP.validateResponse(
      'GET',
      `/api/v1/workflows/${params.id}`,
      200,
      response
    );
    
    if (!validationResult.success) {
      console.error('OpenAPI validation failed:', validationResult.errors);
      // Handle validation failure appropriately
    }
    
    return NextResponse.json(response);
  } catch (error) {
    // Error handling...
  }
}
```

### Step 4: Client-Side Consumption

On the frontend, always validate API responses:

```typescript
// In stores or hooks
import { z } from 'zod';

// Define Zod schema based on OpenAPI (can be generated)
const WorkflowDataSchema = z.object({
  metadata: WorkflowMetadataSchema,
  nodes: z.array(WorkflowNodeSchema),
  edges: z.array(WorkflowEdgeSchema),
  variables: z.record(z.unknown()).optional()
});

// In API calls
async function loadWorkflow(workflowId: string) {
  const response = await fetch(`/api/v1/workflows/${workflowId}`);
  const data = await response.json();
  
  // Validate response data
  const validatedData = WorkflowDataSchema.parse(data.data);
  return validatedData;
}
```

---

## 🔧 Implementation Guidelines

### 1. File Organization

```
/src
  /lib
    /mcp
      openapi-schema-client.ts    # OpenAPI Schema MCP definitions
    /types
      *.types.ts                  # Generated types from OpenAPI
    /schemas
      *.schema.ts                 # Zod schemas for runtime validation
  /app
    /api
      /v1
        /[resource]
          route.ts                # API routes with validation
```

### 2. Schema Definition Rules

- **Always define in OpenAPI first** - Never create types manually
- **Use $ref for reusability** - Reference common schemas
- **Include required fields** - Be explicit about mandatory properties
- **Add descriptions** - Document what each field represents

### 3. API Route Requirements

Every API route MUST:
1. Import `openAPISchemaMCP`
2. Define clear request/response types
3. Validate all inputs with Zod
4. Validate all outputs with `openAPISchemaMCP.validateResponse()`
5. Handle validation failures gracefully
6. Return consistent error responses

### 4. Mock Data Generation

When creating mock data, ensure it conforms to schemas:

```typescript
function generateMockWorkflow(): WorkflowData {
  const mockData = {
    metadata: {
      id: 'test-1',
      name: 'Test Workflow',
      // ... all required fields
    },
    nodes: [],
    edges: []
  };
  
  // Validate mock data against schema
  const validationResult = WorkflowDataSchema.safeParse(mockData);
  if (!validationResult.success) {
    throw new Error(`Mock data validation failed: ${validationResult.error}`);
  }
  
  return mockData;
}
```

---

## ✅ Do's and Don'ts

### Do's
- ✅ **Always** use OpenAPI Schema MCP for defining API contracts
- ✅ **Always** validate responses before sending
- ✅ **Always** validate requests before processing
- ✅ **Always** handle validation errors explicitly
- ✅ **Always** keep schemas in sync with types
- ✅ Use descriptive schema names and properties
- ✅ Version your APIs properly (`/v1/`, `/v2/`)
- ✅ Test schema validation in unit tests

### Don'ts
- ❌ **Never** manually define API types
- ❌ **Never** skip validation "for simplicity"
- ❌ **Never** use `any` type in API definitions
- ❌ **Never** modify generated files
- ❌ **Never** trust unvalidated JSON data
- ❌ Don't mix UI-specific validation with API validation
- ❌ Don't create APIs without OpenAPI documentation

---

## 🧪 Testing Requirements

### 1. Schema Validation Tests

```typescript
describe('API Schema Validation', () => {
  it('should validate valid workflow data', async () => {
    const validData = generateValidWorkflowData();
    const result = await openAPISchemaMCP.validateResponse(
      'GET',
      '/api/v1/workflows/test',
      200,
      { success: true, data: validData }
    );
    expect(result.success).toBe(true);
  });
  
  it('should reject invalid workflow data', async () => {
    const invalidData = { /* missing required fields */ };
    const result = await openAPISchemaMCP.validateResponse(
      'GET',
      '/api/v1/workflows/test',
      200,
      { success: true, data: invalidData }
    );
    expect(result.success).toBe(false);
  });
});
```

### 2. API Integration Tests

- Test actual API routes with valid/invalid inputs
- Verify error responses match expected schema
- Ensure all edge cases are handled

---

## 🚀 CI/CD Integration

### Build-Time Checks

1. **Schema Validation**: Ensure all schemas are valid OpenAPI
2. **Type Generation**: Regenerate types and check for changes
3. **Linting**: No `any` types in API-related code
4. **Test Coverage**: All API routes must have tests

### Pre-commit Hooks

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm run lint:api && npm run test:schemas"
    }
  }
}
```

---

## 📊 Monitoring & Debugging

### Development

- Enable verbose logging for validation failures
- Use browser DevTools to inspect API responses
- Check console for schema validation warnings

### Production

- Log validation failures to monitoring service
- Track API response times and error rates
- Alert on repeated validation failures

---

## 🔄 Migration Strategy

When updating existing APIs:

1. **Create new version** (`/v2/`) alongside existing
2. **Define new schemas** in OpenAPI Schema MCP
3. **Implement with full validation**
4. **Deprecate old version** with notices
5. **Migrate clients** incrementally
6. **Remove old version** after migration period

---

## 📚 References

- [OpenAPI Specification](https://swagger.io/specification/)
- [Zod Documentation](https://zod.dev/)
- [Frontend Schema API Contract Playbook](./Frontend_Schema_API_Contract_Playbook.md)
- [AI Task Orchestrator TypeScript Guide](./AI_TASK_ORCHESTRATOR_TS_GUIDE.md)

---

## 🎯 Quick Checklist for New APIs

- [ ] Schema defined in `openapi-schema-client.ts`
- [ ] Types generated from OpenAPI schema
- [ ] Request validation implemented with Zod
- [ ] Response validation with `openAPISchemaMCP.validateResponse()`
- [ ] Error handling for validation failures
- [ ] Unit tests for schema validation
- [ ] Integration tests for API route
- [ ] No `any` types in implementation
- [ ] Documentation updated
- [ ] Mock data conforms to schema
