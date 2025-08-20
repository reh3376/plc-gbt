# MCP Docker Server Setup Guide

## Overview

The PLC-GBT project uses a Model Context Protocol (MCP) Docker server for centralized OpenAPI schema management. This server is **MANDATORY** for production environments to ensure API consistency and type safety.

## Current Status

⚠️ **Development Mode**: The MCP server connection is currently disabled in development mode to prevent console errors. For production deployment, you must set up the actual MCP Docker server.

## Setting Up MCP Docker Server

### Option 1: Use Existing n8n-mcp Service (Recommended for Development)

If you're using the existing n8n-mcp service, you can configure it as your MCP server:

```bash
# In your .env file
NEXT_PUBLIC_MCP_SERVER_URL=http://localhost:8765
```

### Option 2: Deploy Dedicated MCP OpenAPI Server (Recommended for Production)

Create a dedicated MCP server for OpenAPI schema management:

1. **Create Docker Compose Service**

Add to your `docker-compose.yml`:

```yaml
services:
  mcp-openapi-server:
    image: mcp/openapi-server:latest  # Replace with actual image
    container_name: plc-mcp-openapi
    restart: unless-stopped
    ports:
      - "8811:8811"
    environment:
      - PORT=8811
      - AUTH_TOKEN=${MCP_AUTH_TOKEN}
      - LOG_LEVEL=info
    volumes:
      - ./schemas:/app/schemas
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8811/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

2. **Configure Environment Variables**

```bash
# .env file
NEXT_PUBLIC_MCP_SERVER_URL=http://localhost:8811
MCP_AUTH_TOKEN=your-secure-token-here
```

3. **Start the Service**

```bash
docker-compose up -d mcp-openapi-server
```

## Fallback Mode Behavior

When the MCP server is not available, the application operates in fallback mode:

- **Development**: Errors are suppressed, validation uses local schemas
- **Production**: Warnings are logged, but the app continues to function
- **API Development**: Manual schema definitions are temporarily allowed

⚠️ **Important**: Fallback mode violates the API Creation Methodology and should only be used during development or when the MCP server is temporarily unavailable.

## Verification

To verify your MCP server is running correctly:

```bash
# Check health endpoint
curl http://localhost:8811/health

# Expected response
{"status": "healthy", "version": "1.0.0"}
```

## Troubleshooting

### Connection Errors in Console

If you see "Health check failed: Failed to fetch" errors:

1. **Check if MCP server is running**: `docker ps | grep mcp`
2. **Verify port availability**: `lsof -i :8811`
3. **Check Docker logs**: `docker logs plc-mcp-openapi`
4. **Ensure environment variable is set**: Check `NEXT_PUBLIC_MCP_SERVER_URL`

### Fallback Mode Warnings

If you see "MCP server not available - validation will use fallback mode":

- This is expected in development without MCP server
- For production, ensure MCP server is properly deployed
- Check network connectivity between Next.js app and MCP server

## API Development Requirements

Per the [API Creation Methodology](./API_CREATION_METHODOLOGY.md), all API development MUST use the MCP Docker server when available:

1. **Schema Definition**: Define all schemas in the MCP server
2. **Type Generation**: Run `pnpm api:gen` to generate types from MCP
3. **Runtime Validation**: Use generated Zod schemas for validation
4. **No Manual Types**: Never create manual TypeScript interfaces for APIs

## Production Deployment Checklist

- [ ] MCP Docker server deployed and accessible
- [ ] `NEXT_PUBLIC_MCP_SERVER_URL` configured correctly
- [ ] Health check endpoint responding
- [ ] All API schemas migrated to MCP server
- [ ] Type generation pipeline connected to MCP
- [ ] CI/CD updated to validate against MCP schemas
- [ ] Monitoring configured for MCP server uptime

## Related Documentation

- [API Creation Methodology](./API_CREATION_METHODOLOGY.md)
- [AI Task Orchestrator Guide](./AI_TASK_ORCHESTRATOR_TS_GUIDE.md)
- [Docker Compose Configuration](../docker-compose.yml)
