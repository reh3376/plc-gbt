# API Development Agent Checklist

**⚠️ CRITICAL**: This checklist is MANDATORY for all coding agents working on API development in PLC-GBT.

## 📋 Pre-Development Verification

Before writing ANY API code, verify:

- [ ] Have you read `plc-gbt-stack/docs/API_CREATION_METHODOLOGY.md`?
- [ ] Is MCP_Docker server accessible for OpenAPI Schema MCP?
- [ ] Is TypeScript configured with `strict: true` and `noExplicitAny: true`?
- [ ] Is ESLint rule `@typescript-eslint/no-explicit-any` enabled?
- [ ] Have you checked for existing reusable schemas?

## 🚀 Development Workflow Checklist

### 1. Schema Definition (MANDATORY FIRST STEP)
- [ ] Schema defined in `openapi-schema-client.ts` using OpenAPI Schema MCP
- [ ] All required fields listed in `required` array
- [ ] Proper formats specified (`uuid`, `email`, `date-time`)
- [ ] Validation constraints added (`minLength`, `maxLength`, `pattern`)
- [ ] NO manual type definitions created

### 2. Code Generation
- [ ] Run `pnpm api:gen` to generate types and Zod schemas
- [ ] Verify generated files in `src/api/types.gen.ts` and `src/api/zod-schemas.ts`
- [ ] NO modifications made to generated files

### 3. API Route Implementation
- [ ] Import `openAPISchemaMCP` from `@/lib/mcp/openapi-schema-client`
- [ ] Request body validated with generated Zod schema
- [ ] Response validated with `openAPISchemaMCP.validateResponse()`
- [ ] Standard error response format used
- [ ] NO `any` types in implementation

### 4. Client Implementation
- [ ] Type-safe API methods created in `lib/api/[resource].ts`
- [ ] All responses validated with generated Zod schemas
- [ ] Centralized error handling implemented
- [ ] Loading and error states handled in UI

### 5. Testing Requirements
- [ ] Unit tests for schema validation
- [ ] Integration tests for API routes
- [ ] E2E tests for critical user flows
- [ ] Error scenarios tested
- [ ] >95% test coverage achieved

## ❌ Common Violations to Avoid

```typescript
// ❌ NEVER DO THIS - Manual type definition
interface UserAPI {
  id: string;
  name: string;
}

// ❌ NEVER DO THIS - Manual Zod schema
const UserSchema = z.object({
  id: z.string(),
  name: z.string()
});

// ❌ NEVER DO THIS - Type assertion
const user = response.data as User;

// ❌ NEVER DO THIS - Unhandled errors
try {
  // api call
} catch (error) {
  console.log(error); // NO!
}
```

## ✅ Correct Patterns

```typescript
// ✅ CORRECT - Import generated types
import type { components } from '@/api/types.gen';
type User = components['schemas']['User'];

// ✅ CORRECT - Use generated Zod schemas
import { UserSchema } from '@/api/zod-schemas';
const validatedUser = UserSchema.parse(data);

// ✅ CORRECT - Validate responses in routes
await openAPISchemaMCP.validateResponse('GET', '/api/v1/users/123', 200, response);

// ✅ CORRECT - Proper error handling
catch (error) {
  const apiError = normalizeApiError(error);
  return NextResponse.json(apiError, { status: apiError.status });
}
```

## 📚 Resources

- **Full Methodology**: `plc-gbt-stack/docs/API_CREATION_METHODOLOGY.md`
- **Quick Start Guide**: Section 11 of API methodology document
- **End-to-End Example**: Section 12 of API methodology document
- **Common Pitfalls**: Section 9 of API methodology document

## 🚨 Final Reminder

**ZERO TOLERANCE POLICY**: Any manual API type definitions or schemas will cause immediate build failures. Always use the OpenAPI Schema MCP and generated types/schemas.

Remember: This methodology ensures zero schema drift, complete type safety, and production-ready APIs. Following it is not optional—it's mandatory.
