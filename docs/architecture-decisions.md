# Architecture Decision Records (ADR)

This document captures key architectural decisions made during the PLC-Savvy GPT project development.

## ADR-001: Docker-based Microservices Architecture

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need to deploy multiple services (Neo4j, Qdrant, Gateway, ETL) in a coordinated manner  
**Decision**: Use Docker Compose to orchestrate microservices  
**Consequences**: 
- ✅ Easy deployment and scaling
- ✅ Service isolation and independent updates
- ✅ Consistent development/production environments
- ❌ Additional complexity in networking and service discovery

## ADR-002: Neo4j as Knowledge Graph Database

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need to store complex relationships between PLC components (programs, routines, AOIs, UDTs)  
**Decision**: Use Neo4j Enterprise for the knowledge graph  
**Consequences**: 
- ✅ Native graph queries with Cypher
- ✅ Excellent visualization capabilities
- ✅ ACID compliance and clustering support
- ❌ Licensing costs for enterprise features
- ❌ Additional learning curve for Cypher query language

## ADR-003: Qdrant for Vector Storage

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need high-performance vector similarity search for document embeddings  
**Decision**: Use Qdrant as the vector database  
**Alternatives Considered**: LanceDB, pgvector  
**Consequences**: 
- ✅ High performance and scalability
- ✅ Built-in filtering and metadata support
- ✅ REST and gRPC APIs
- ❌ Relatively new compared to alternatives

## ADR-004: FastAPI for Gateway Service

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need REST API for ChatGPT Actions integration  
**Decision**: Use FastAPI for the gateway service  
**Consequences**: 
- ✅ Automatic OpenAPI documentation generation
- ✅ High performance with async support
- ✅ Built-in data validation with Pydantic
- ✅ Easy integration with ChatGPT Actions

## ADR-005: Python for ETL and Services

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need to process PDFs, L5X files, and integrate with multiple APIs  
**Decision**: Use Python 3.12 for all custom services  
**Consequences**: 
- ✅ Rich ecosystem of libraries (pdfplumber, lxml, openai, neo4j)
- ✅ Team familiarity and rapid development
- ✅ Strong typing support with modern Python
- ❌ Potential performance limitations for CPU-intensive tasks

## ADR-006: OpenAI text-embedding-3-large for Embeddings

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need high-quality embeddings for semantic search  
**Decision**: Use OpenAI's text-embedding-3-large model (3072 dimensions)  
**Consequences**: 
- ✅ State-of-the-art embedding quality
- ✅ Consistent with fine-tuning model ecosystem
- ❌ API dependency and costs
- ❌ Vendor lock-in to OpenAI

## ADR-007: RAG (Retrieval-Augmented Generation) Architecture

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need to combine structured knowledge graph with unstructured document search  
**Decision**: Implement hybrid RAG combining vector similarity + graph neighborhood queries  
**Consequences**: 
- ✅ Best of both worlds: semantic search + structured relationships
- ✅ More accurate and contextual responses
- ❌ Increased complexity in query orchestration
- ❌ Higher latency due to multiple data sources

## ADR-008: Bearer Token Authentication

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need secure API access for ChatGPT Actions  
**Decision**: Use Bearer token authentication for gateway API  
**Consequences**: 
- ✅ Simple to implement and use
- ✅ Compatible with ChatGPT Actions security model
- ❌ Token management and rotation required
- ❌ Less sophisticated than OAuth for complex scenarios

## ADR-009: Health Check Strategy

**Date**: 2025-06-30  
**Status**: Accepted  
**Context**: Need reliable container health monitoring  
**Decision**: Implement custom health checks using native tools available in each container  
**Consequences**: 
- ✅ Proper service dependency management
- ✅ Reliable container orchestration
- ❌ Container-specific health check implementations needed

## Future Decisions to Make

- **Vector Database Selection**: Final choice between Qdrant, LanceDB, pgvector
- **Master KG Hosting**: On-premises vs private cloud deployment
- **Monitoring Stack**: Prometheus + Grafana vs alternatives
- **Backup Strategy**: Frequency, retention, and disaster recovery procedures

---

*This document will be updated as new architectural decisions are made.* 