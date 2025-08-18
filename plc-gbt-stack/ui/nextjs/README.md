This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🐳 Docker Environment & Automation

**⚠️ CRITICAL FOR CODING AGENTS & BROWSER AUTOMATION**: When working with Docker containers, browser automation, or MCP testing tools, use the Docker networking address:

- **✅ For Browser Automation**: `http://host.docker.internal:3000`
- **✅ For API Calls from Docker**: `http://host.docker.internal:3000/api/v1/...`
- **✅ For WebSocket Connections**: `ws://host.docker.internal:3000/ws`

**Examples:**
```typescript
// Playwright MCP browser navigation
await mcp.browser_navigate('http://host.docker.internal:3000')

// API testing from containerized environments
const response = await fetch('http://host.docker.internal:3000/api/v1/health')

// WebSocket connections from Docker services
const ws = new WebSocket('ws://host.docker.internal:3000/ws/workflow')
```

This ensures proper networking when the development server runs on the host while automation tools run in Docker containers.

## 🚨 CRITICAL: API Development Standards

**MANDATORY FOR ALL DEVELOPERS**: This project enforces strict API development standards with ZERO tolerance for manual type definitions.

### Required Reading Before ANY API Work:
- 📘 **[API Creation Methodology](../docs/API_CREATION_METHODOLOGY.md)** - Complete methodology (MUST READ)
- 📋 **[API Development Checklist](../docs/API_DEVELOPMENT_AGENT_CHECKLIST.md)** - Quick reference for agents
- 🔧 **[AI Task Orchestrator Guide](../docs/AI_TASK_ORCHESTRATOR_TS_GUIDE.md)** - Overall development framework

### Key Rules:
1. **ALL API schemas defined using OpenAPI Schema MCP** - No exceptions
2. **ALL types generated from OpenAPI** - Never manually write API types
3. **ALL requests/responses validated with Zod** - No unvalidated JSON
4. **Zero `any` types allowed** - Use `unknown` with type guards

### Quick Start:
```bash
# 1. Define schema in openapi-schema-client.ts
# 2. Generate types and Zod schemas
pnpm api:gen

# 3. Use ONLY generated types
import type { components } from '@/api/types.gen'
import { WorkflowSchema } from '@/api/zod-schemas'
```

**Violations of these rules will cause immediate build failures.**

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
