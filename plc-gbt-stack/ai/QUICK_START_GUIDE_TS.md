# 🚀 AI Task Orchestrator - TypeScript Quick Start Guide (60 seconds)

## Prerequisites
```bash
# Install TypeScript and dependencies
cd plc-gbt-stack/ai
npm install
npm run build
```

## 🎯 60-Second Quick Start

### 1. Basic Task Analysis and Implementation

```typescript
import { createOrchestrator } from '@plc-gbt/orchestrator';

// 1. Create orchestrator (5 seconds)
const orchestrator = createOrchestrator();

// 2. Analyze your task (10 seconds)
const analysis = await orchestrator.analyzeTask("Create PLC data parser for L5X files");

// 3. View analysis results (5 seconds)
console.log(`Complexity: ${analysis.complexity}`);
console.log(`Requirements: ${analysis.requirements.length}`);
console.log(`Estimated hours: ${analysis.estimatedEffort.hours}`);

// 4. Get implementation guide (10 seconds)
const guidePath = await orchestrator.createImplementationGuide(analysis);
console.log(`Guide created: ${guidePath}`);

// 5. Validate your implementation (20 seconds)
const myCode = `
function parseL5X(filePath: string): Promise<ParsedData> {
    // Your implementation here
    const data = fs.readFileSync(filePath, 'utf-8');
    return { status: 'parsed', data };
}
`;

const result = await orchestrator.validateImplementation(myCode);
console.log(`Validation: ${result.passed ? '✅ PASSED' : '❌ FAILED'}`);
console.log(`Score: ${result.score}/100`);

// 6. Create summary (10 seconds)
const summary = await orchestrator.createSummaryDocument();
console.log(`Summary saved: ${summary}`);
```

## 📊 Choose Your Path

Based on your task type, jump to the appropriate section:

### 🔧 Small Scripts & Utilities
```typescript
// Quick validation for simple scripts
const orchestrator = createOrchestrator({ enableMemory: false });
const analysis = await orchestrator.analyzeTask("Create CSV to JSON converter");
// Creates guide with ~50-100 lines of code template
```

### 🔌 API Service Endpoints
```typescript
// API development with OpenAPI schema validation
const orchestrator = createOrchestrator({
    enableMemory: true,
    enableProductionChecks: true,
    enableOpenAPIValidation: true
});
const analysis = await orchestrator.analyzeTask("Create REST API for sensor data");
// Generates OpenAPI schemas and endpoint templates with Zod validation
```

### 📊 Data Processing Pipelines
```typescript
// Data pipeline with validation
const orchestrator = createOrchestrator({ enableMemory: true });
const analysis = await orchestrator.analyzeTask("Build ETL pipeline for PLC logs");
// Includes data validation schemas and error handling patterns
```

### 🎛️ Control System Algorithms
```typescript
// Control systems with mathematical validation
const orchestrator = createOrchestrator({
    enableControlAnalysis: true,
    enableMathValidation: true
});
const analysis = await orchestrator.analyzeTask("Implement PID controller with anti-windup");
// Provides control theory guidance and TypeScript implementation patterns
```

### 🏭 Industrial Integrations
```typescript
// Industrial protocol integration
const orchestrator = createOrchestrator({ enableMemory: true });
const analysis = await orchestrator.analyzeTask("Create OPC UA client for PLC communication");
// Includes protocol-specific types and safety checks
```

## 🔥 Advanced Features (2 minutes)

### Progress Monitoring
```typescript
// Real-time progress tracking
orchestrator.progressMonitor.addCallback((update) => {
    console.log(`[${update.percentage.toFixed(0)}%] ${update.status}`);
});
```

### Memory System Integration
```typescript
// Leverage similar implementations
if (analysis.memoryInsights) {
    const similar = analysis.memoryInsights.similarTasks || [];
    console.log(`Found ${similar.length} similar implementations`);
}
```

### Production Readiness
```typescript
// Get deployment checklist
const checklist = await orchestrator.getProductionChecklist(myCode);
console.log(`Production ready: ${checklist.overallReadiness}`);
checklist.blockingIssues.forEach(issue => {
    console.log(`⚠️  ${issue}`);
});
```

### Type-Safe Control System Validation
```typescript
// Validate control implementations with full type safety
if (analysis.isControlSystemTask()) {
    const controlResult = await orchestrator.controlHandler.validateControlImplementation(myCode);
    console.log(`Safety score: ${controlResult.safetyScore}%`);
}
```

## 💡 Common Patterns

### Pattern 1: Quick Script Development
```typescript
// Minimal setup for simple scripts
const orchestrator = createOrchestrator({ enableMemory: false });
const analysis = await orchestrator.analyzeTask("Parse CSV and calculate statistics");
const guide = await orchestrator.createImplementationGuide(analysis);
// Implement using the guide...
const result = await orchestrator.validateImplementation(code);
```

### Pattern 2: Full Development Cycle with OpenAPI
```typescript
// Complete workflow with OpenAPI schema enforcement
import { ValidationTier } from '@plc-gbt/orchestrator';

const orchestrator = createOrchestrator({
    enableMemory: true,
    enableMathValidation: true,
    enableProductionChecks: true,
    enableOpenAPIValidation: true
});

// Full cycle with schema-first development
const analysis = await orchestrator.analyzeTask(taskDescription);
const schemas = await orchestrator.generateOpenAPISchemas(analysis);
const guide = await orchestrator.createImplementationGuide(analysis);
// ... implement code with generated types ...
const validation = await orchestrator.validateImplementation(
    code, 
    ValidationTier.PRODUCTION
);
const checklist = await orchestrator.getProductionChecklist(code);
const summary = await orchestrator.createSummaryDocument();
await orchestrator.cleanup();
```

### Pattern 3: Iterative Development with Type Safety
```typescript
// Validate as you code with full type inference
const orchestrator = createOrchestrator();
const analysis = await orchestrator.analyzeTask("Build data pipeline");

// Validate incrementally with type-safe results
for (const moduleCode of [parserCode, transformerCode, loaderCode]) {
    const result = await orchestrator.validateImplementation(
        moduleCode, 
        ValidationTier.SYNTAX
    );
    if (!result.passed) {
        console.log(`Fix issues:`, result.issues);
        // TypeScript knows the shape of result.issues
    }
}
```

## 🛠️ Configuration Options

### Environment-Based (.env file)
```bash
# .env file in project root
ENVIRONMENT=development
ENABLE_MEMORY=true
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
ENABLE_OPENAPI_VALIDATION=true
```

### Programmatic Configuration with Type Safety
```typescript
import { OrchestratorConfig } from '@plc-gbt/orchestrator';

const config: OrchestratorConfig = {
    // Features
    enableMemory: true,
    enableMathValidation: true,
    enableControlAnalysis: true,
    enableProductionChecks: false,
    enableOpenAPIValidation: true,
    
    // Performance
    maxWorkers: 8,
    timeoutSeconds: 600,
    cacheTTL: 3600,
    
    // Logging
    logLevel: 'DEBUG',
    logFile: 'orchestrator.log'
};

const orchestrator = createOrchestrator(config);
```

## 📝 Output Examples

### Task Analysis Output (Type-Safe)
```typescript
interface TaskAnalysis {
    taskId: string;
    complexity: 'simple' | 'moderate' | 'complex' | 'extensive';
    requirements: string[];
    risks: string[];
    dependencies: string[];
    estimatedEffort: {
        hours: number;
        days: number;
    };
}

// Usage with full type inference
const analysis = await orchestrator.analyzeTask(description);
// TypeScript knows all properties and their types
```

### Validation Output with Zod Schemas
```typescript
import { z } from 'zod';

// Generated validation schema
const ValidationResultSchema = z.object({
    tier: z.enum(['SYNTAX', 'REQUIREMENTS', 'PRODUCTION']),
    score: z.number().min(0).max(100),
    passed: z.boolean(),
    issues: z.array(z.object({
        severity: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
        message: z.string(),
        line: z.number().optional()
    }))
});

// Type-safe validation
const result = await orchestrator.validateImplementation(code);
// result is fully typed based on the schema
```

### Production Checklist with Types
```typescript
interface ProductionChecklist {
    overallReadiness: boolean;
    blockingIssues: string[];
    checks: {
        logging: boolean;
        errorHandling: boolean;
        security: boolean;
        monitoring: boolean;
        documentation: boolean;
    };
}

const checklist = await orchestrator.getProductionChecklist(code);
// Full IntelliSense support for all properties
```

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Missing Type Definitions
```typescript
// Solution: Use generated types from OpenAPI schemas
import type { components } from './api/types.gen';
type UserData = components['schemas']['UserData'];
```

### Pitfall 2: Async/Await Errors
```typescript
// Solution: Always use try-catch with async operations
try {
    const analysis = await orchestrator.analyzeTask(task);
} catch (error) {
    console.error('Analysis failed:', error);
    // TypeScript narrows error type properly
}
```

### Pitfall 3: Schema Validation Mismatches
```typescript
// Solution: Use Zod schemas from OpenAPI definitions
import { UserSchema } from './schemas.gen';

const userData = await fetchUserData();
const validatedData = UserSchema.parse(userData);
// validatedData is now type-safe
```

## 🎉 Next Steps

1. **Explore the Full Guide**: See [AI_TASK_ORCHESTRATOR_TS_GUIDE.md](../docs/AI_TASK_ORCHESTRATOR_TS_GUIDE.md)
2. **Check Examples**: Run `npm run example` for TypeScript examples
3. **Read API Docs**: Generated TypeDoc documentation at `docs/api`
4. **Type Definitions**: Explore `@types` for all interfaces

## 🆘 Quick Help

```typescript
// Get type information
import type { AITaskOrchestrator } from '@plc-gbt/orchestrator';

// View available methods with IntelliSense
const orchestrator: AITaskOrchestrator = createOrchestrator();
// orchestrator. <- Full IntelliSense support

// Check configuration types
import type { OrchestratorConfig } from '@plc-gbt/orchestrator';

// Runtime type checking
console.log('Memory enabled:', orchestrator.memoryCoordinator !== null);
console.log('Math validation:', orchestrator.mathValidator !== null);
console.log('Control analysis:', orchestrator.controlHandler !== null);
```

## 🔗 OpenAPI Schema Integration

```typescript
// MANDATORY: All API schemas must use OpenAPI MCP
const orchestrator = createOrchestrator({
    enableOpenAPIValidation: true
});

// Generate schemas from OpenAPI definitions
const schemas = await orchestrator.generateSchemasFromOpenAPI({
    apiPath: '/api/control-loops',
    outputPath: './src/schemas'
});

// Use generated types and validators
import { ControlLoopSchema } from './schemas';
const validated = ControlLoopSchema.parse(data);
```

---

**Ready to build with TypeScript?** You now have everything needed to start using the AI Task Orchestrator with full type safety! 🚀
