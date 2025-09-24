# Installation Guide

This guide provides step-by-step instructions for installing and setting up the PLC-GBT platform.

## Prerequisites

- Python 3.12 or higher
- Node.js 20.x or higher
- Docker and Docker Compose
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/reh3376/plc-gbt.git
   cd plc-gbt
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install development dependencies**
   ```bash
   cd plc-gbt-stack
   pip install -e .[dev]
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start required services**
   ```bash
   docker-compose up -d
   ```

## Detailed Installation

### Python Dependencies

The project uses `uv` for fast dependency management:

```bash
pip install uv
uv pip install -r requirements.txt
```

### Database Setup

1. **PostgreSQL**
   ```bash
   docker run -d --name plc-postgres \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=plc_gbt \
     -p 5432:5432 \
     postgres:14
   ```

2. **Neo4j**
   ```bash
   docker run -d --name plc-neo4j \
     -e NEO4J_AUTH=neo4j/password \
     -p 7474:7474 -p 7687:7687 \
     neo4j:5
   ```

3. **Redis**
   ```bash
   docker run -d --name plc-redis \
     -p 6379:6379 \
     redis:7-alpine
   ```

4. **Qdrant**
   ```bash
   docker run -d --name plc-qdrant \
     -p 6333:6333 \
     qdrant/qdrant
   ```

### Frontend Setup

```bash
cd plc-gbt-stack/ui/nextjs
npm install
npm run dev
```

### API Server

```bash
cd plc-gbt-stack/api
uvicorn main:app --reload
```

## Verification

Run the test suite to verify installation:

```bash
pytest
```

## Troubleshooting

### Common Issues

1. **Python version error**: Ensure Python 3.12+ is installed
2. **Docker not running**: Start Docker Desktop or Docker daemon
3. **Port conflicts**: Check if required ports are already in use
4. **Permission errors**: Use `sudo` for Docker commands if needed

### Getting Help

- Check the [documentation](docs/)
- Open an [issue](https://github.com/reh3376/plc-gbt/issues)
- Join our community discussions

## Next Steps

- Read the [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- Review the [Architecture](docs/architecture-decisions.md)
- Check the [Roadmap](docs/roadmap.md)
