# AI Enhancement Framework - Troubleshooting Guide

## 📋 Overview

This comprehensive troubleshooting guide helps you resolve common issues when using the AI Enhancement Framework with Cursor IDE. Issues are organized by category with step-by-step solutions.

## 🚨 Emergency Quick Fixes

### Framework Not Working At All
```bash
# Complete reset and reinstall
pip uninstall ai-enhancement-framework
pip install --no-cache-dir ai-enhancement-framework[full]
python -c "from ai_enhancement_framework.core import AITaskOrchestrator; print('✅ Working!')"
```

### Cursor IDE Not Recognizing Framework
```bash
# Reset Cursor IDE configuration
rm -rf .vscode/settings.json
cursor .
# Then follow installation guide again
```

### Memory Services All Down
```bash
# Restart all Docker services
docker-compose down
docker-compose up -d
docker-compose ps  # Verify all services running
```

## 🔧 Installation Issues

### Issue: "Module not found" Error
**Error Message**: `ModuleNotFoundError: No module named 'ai_enhancement_framework'`

**Diagnosis**:
```bash
# Check Python version
python --version

# Check pip installation
pip list | grep ai-enhancement

# Check virtual environment
which python
```

**Solutions**:

#### Solution 1: Virtual Environment Issue
```bash
python -m venv ai-enhancement-env
source ai-enhancement-env/bin/activate  # Linux/macOS
# OR
ai-enhancement-env\Scripts\activate     # Windows

# Navigate to the AI Enhancement Framework directory
cd ai-enhancement-framework

# Install in virtual environment with development mode
pip install -e .[full]
```

#### Solution 2: Python Path Issue
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Solution 3: Permissions Issue
```bash
# Install with user flag
pip install --user ai-enhancement-framework[full]

# Or fix permissions (Linux/macOS)
sudo chown -R $(whoami) /usr/local/lib/python*/site-packages
```

### Issue: Dependencies Conflict
**Error Message**: `ERROR: pip's dependency resolver does not currently work with existing version conflicts`

**Solutions**:

#### Solution 1: Clean Install
```bash
# Create fresh virtual environment
rm -rf ai-enhancement-env
python -m venv ai-enhancement-env
source ai-enhancement-env/bin/activate
pip install --upgrade pip
pip install ai-enhancement-framework[full]
```

#### Solution 2: Specific Version Installation
```bash
# Install specific compatible versions
pip install ai-enhancement-framework==1.0.0
pip install --upgrade --force-reinstall ai-enhancement-framework[full]
```

### Issue: Docker Installation Problems
**Error Message**: `docker: command not found` or Docker services won't start

**Solutions**:

#### Solution 1: Install Docker (macOS)
```bash
# Using Homebrew
brew install --cask docker

# Start Docker Desktop manually
open /Applications/Docker.app
```

#### Solution 2: Install Docker (Linux)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Test installation
docker run hello-world
```

#### Solution 3: Docker Service Issues
```bash
# Check Docker service status
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Enable auto-start
sudo systemctl enable docker
```

## 🎮 Cursor IDE Integration Issues

### Issue: Cursor Not Detecting Framework
**Symptoms**: No AI enhancement features visible, framework commands not working

**Diagnosis**:
```bash
# Check Cursor settings
cat .vscode/settings.json

# Check Python interpreter
cursor --version
```

**Solutions**:

#### Solution 1: Python Interpreter Configuration
1. Open Cursor IDE
2. Press `Cmd/Ctrl + Shift + P`
3. Type "Python: Select Interpreter"
4. Choose your virtual environment Python

#### Solution 2: Workspace Settings Update
```json
{
  "ai.framework.enabled": true,
  "python.defaultInterpreterPath": "./ai-enhancement-env/bin/python",
  "ai.framework.auto_init": true
}
```

#### Solution 3: Framework Initialization
```bash
# Initialize in project directory
cd /path/to/your/project
python -m ai_enhancement_framework init --cursor
cursor .
```

### Issue: .cursorrules Not Loading
**Symptoms**: Framework not following project-specific configuration

**Solutions**:

#### Solution 1: File Format Check
```bash
# Validate YAML syntax
python -c "
import yaml
with open('.cursorrules', 'r') as f:
    try:
        yaml.safe_load(f)
        print('✅ YAML is valid')
    except yaml.YAMLError as e:
        print(f'❌ YAML error: {e}')
"
```

#### Solution 2: File Permissions
```bash
# Check file permissions
ls -la .cursorrules

# Fix permissions if needed
chmod 644 .cursorrules
```

#### Solution 3: Configuration Reset
```bash
# Backup current config
cp .cursorrules .cursorrules.backup

# Generate new config
python -m ai_enhancement_framework init --cursor --force

# Compare with backup
diff .cursorrules .cursorrules.backup
```

## 💾 Memory System Issues

### Issue: Redis Connection Failed
**Error Message**: `ConnectionError: Error connecting to Redis`

**Diagnosis**:
```bash
# Check Redis status
docker ps | grep redis
curl http://localhost:6379/ping

# Check Redis logs
docker logs redis
```

**Solutions**:

#### Solution 1: Start Redis Service
```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or via docker-compose
docker-compose up -d redis
```

#### Solution 2: Redis Configuration Issues
```bash
# Check Redis configuration
docker exec -it redis redis-cli CONFIG GET "*"

# Reset Redis configuration
docker stop redis
docker rm redis
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

#### Solution 3: Port Conflicts
```bash
# Check what's using port 6379
lsof -i :6379

# Use alternative port
docker run -d --name redis -p 6380:6379 redis:7-alpine

# Update framework configuration
export AI_FRAMEWORK_REDIS_URL="redis://localhost:6380"
```

### Issue: Neo4j Connection Problems
**Error Message**: `ServiceUnavailable: Unable to connect to Neo4j`

**Solutions**:

#### Solution 1: Start Neo4j Service
```bash
# Using Docker
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15-community

# Wait for startup (can take 30+ seconds)
sleep 30
curl http://localhost:7474
```

#### Solution 2: Authentication Issues
```bash
# Reset Neo4j password
docker exec -it neo4j cypher-shell -u neo4j -p neo4j
# Run: ALTER USER neo4j SET PASSWORD 'password'

# Update framework configuration
export AI_FRAMEWORK_NEO4J_USER="neo4j"
export AI_FRAMEWORK_NEO4J_PASSWORD="password"
```

#### Solution 3: Memory Issues
```bash
# Increase Neo4j memory limits
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_dbms_memory_heap_initial__size=512m \
  -e NEO4J_dbms_memory_heap_max__size=2G \
  neo4j:5.15-community
```

### Issue: PostgreSQL Connection Problems
**Error Message**: `OperationalError: could not connect to server`

**Solutions**:

#### Solution 1: Start PostgreSQL Service
```bash
# Using Docker
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_DB=ai_framework \
  -e POSTGRES_USER=ai_user \
  -e POSTGRES_PASSWORD=ai_password \
  postgres:15-alpine
```

#### Solution 2: Database Initialization
```bash
# Connect and initialize database
docker exec -it postgres psql -U ai_user -d ai_framework -c "
CREATE TABLE IF NOT EXISTS framework_data (
  id SERIAL PRIMARY KEY,
  key VARCHAR(255),
  data JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

#### Solution 3: Connection String Issues
```bash
# Test connection string
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://ai_user:ai_password@localhost:5432/ai_framework')
    print('✅ PostgreSQL connection successful')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
"
```

### Issue: Qdrant Vector Database Problems
**Error Message**: `ConnectionError: Cannot connect to Qdrant`

**Solutions**:

#### Solution 1: Start Qdrant Service
```bash
# Using Docker
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# Test connection
curl http://localhost:6333/collections
```

#### Solution 2: Initialize Collections
```bash
# Create collection for framework
curl -X PUT http://localhost:6333/collections/ai_framework \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

## 🔍 Analysis & Performance Issues

### Issue: Slow Analysis Performance
**Symptoms**: Code analysis taking >10 seconds, framework feels sluggish

**Diagnosis**:
```python
# Performance test
import time
from ai_enhancement_framework.core import UniversalCodeAnalyzer

analyzer = UniversalCodeAnalyzer()
start_time = time.time()
result = analyzer.analyze_content("def test(): pass")
analysis_time = time.time() - start_time
print(f"Analysis time: {analysis_time:.3f}s")
```

**Solutions**:

#### Solution 1: Reduce Analysis Depth
```bash
# Set lighter analysis mode
export AI_FRAMEWORK_ANALYSIS_DEPTH=basic
# or
export AI_FRAMEWORK_ANALYSIS_DEPTH=standard
```

#### Solution 2: Disable Heavy Features
```yaml
# In .cursorrules
assistant:
  code_analysis:
    security_analysis: false
    performance_analysis: false
    complexity_analysis: true  # Keep only essential
```

#### Solution 3: Optimize Memory Usage
```bash
# Limit memory usage
export AI_FRAMEWORK_MEMORY_LIMIT=512MB
export AI_FRAMEWORK_CACHE_SIZE=128MB
```

### Issue: High Memory Usage
**Symptoms**: System becoming slow, out of memory errors

**Solutions**:

#### Solution 1: Memory Monitoring
```python
# Monitor memory usage
from ai_enhancement_framework.core import memory_usage_monitor

async def check_memory():
    usage = await memory_usage_monitor()
    print(f"Memory usage: {usage}")
    
    if usage.total > 1000:  # MB
        print("⚠️ High memory usage detected")

import asyncio
asyncio.run(check_memory())
```

#### Solution 2: Enable Memory Cleanup
```yaml
# In configuration
memory:
  behavior:
    auto_cleanup: true
    cleanup_interval: 1800  # 30 minutes
    max_memory_usage: "1GB"
```

#### Solution 3: Disable Memory System
```bash
# Temporarily disable memory for testing
export AI_FRAMEWORK_MEMORY_ENABLED=false
```

### Issue: Hallucination Detection False Positives
**Symptoms**: Valid code being flagged as AI hallucinations

**Solutions**:

#### Solution 1: Adjust Detection Sensitivity
```yaml
# In configuration
code_analysis:
  hallucination_detection:
    sensitivity: "medium"  # high, medium, low
    ignore_patterns:
      - "# TODO:"
      - "# FIXME:"
```

#### Solution 2: Whitelist Known Patterns
```python
# Add to framework configuration
from ai_enhancement_framework.core import ConfigManager

config = ConfigManager()
config.add_hallucination_whitelist([
    "your_specific_pattern",
    "another_valid_pattern"
])
```

## 🔒 Security & Authentication Issues

### Issue: API Key Problems
**Symptoms**: OpenAI API calls failing, authentication errors

**Solutions**:

#### Solution 1: Check API Key
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### Solution 2: Update API Key
```bash
# Set API key properly
export OPENAI_API_KEY="your-api-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

### Issue: Docker Security Warnings
**Symptoms**: Security warnings about Docker containers

**Solutions**:

#### Solution 1: Use Official Images Only
```bash
# Verify image sources
docker images | grep -E "(redis|neo4j|postgres|qdrant)"

# Pull official images
docker pull redis:7-alpine
docker pull neo4j:5.15-community
docker pull postgres:15-alpine
docker pull qdrant/qdrant:latest
```

#### Solution 2: Network Security
```yaml
# docker-compose.yml security configuration
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    networks:
      - ai-framework
    ports:
      - "127.0.0.1:6379:6379"  # Bind to localhost only

networks:
  ai-framework:
    driver: bridge
    internal: false
```

## 📱 Platform-Specific Issues

### macOS Issues

#### Issue: Permission Denied Errors
```bash
# Fix Python permissions
sudo chown -R $(whoami) /usr/local/lib/python3.*/site-packages

# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local/Cellar
```

#### Issue: Apple Silicon Compatibility
```bash
# Force x86_64 architecture if needed
arch -x86_64 pip install ai-enhancement-framework[full]

# Or use native ARM64
pip install ai-enhancement-framework[full] --no-binary=:all:
```

### Linux Issues

#### Issue: Missing System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev python3-pip python3-venv \
  build-essential libpq-dev libssl-dev

# CentOS/RHEL/Fedora
sudo yum install python3-devel python3-pip gcc openssl-devel postgresql-devel
# OR
sudo dnf install python3-devel python3-pip gcc openssl-devel postgresql-devel
```

#### Issue: SELinux Problems
```bash
# Check SELinux status
getenforce

# Temporarily disable (not recommended for production)
sudo setenforce 0

# Or create SELinux policy
sudo setsebool -P container_manage_cgroup on
```

### Windows Issues

#### Issue: Windows Path Problems
```powershell
# Use PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned

# Fix path issues
$env:PATH += ";C:\Python311\Scripts"

# Install with user directory
pip install --user ai-enhancement-framework[full]
```

#### Issue: Docker Desktop Problems
```powershell
# Enable WSL 2
wsl --install

# Start Docker Desktop manually
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

## 🔄 Update & Maintenance Issues

### Issue: Framework Version Conflicts
**Symptoms**: Inconsistent behavior after updates

**Solutions**:

#### Solution 1: Clean Update
```bash
# Uninstall completely
pip uninstall ai-enhancement-framework -y
pip cache purge

# Fresh install
pip install ai-enhancement-framework[full]
```

#### Solution 2: Version Pinning
```bash
# Pin to specific version
pip install ai-enhancement-framework==1.0.0

# Or in requirements.txt
echo "ai-enhancement-framework==1.0.0" >> requirements.txt
```

### Issue: Configuration Migration Problems
**Symptoms**: Old configuration not working with new version

**Solutions**:

#### Solution 1: Configuration Migration
```bash
# Backup current config
cp .cursorrules .cursorrules.backup

# Generate new config with migration
python -m ai_enhancement_framework migrate-config --from=0.9.0 --to=1.0.0
```

#### Solution 2: Reset Configuration
```bash
# Reset to defaults
rm .cursorrules .vscode/settings.json
python -m ai_enhancement_framework init --cursor
```

## 📊 Diagnostic Tools

### Framework Health Check
```python
# Comprehensive health check
from ai_enhancement_framework.core import health_check

async def full_health_check():
    health = await health_check()
    
    print("=== AI Enhancement Framework Health Check ===")
    print(f"Overall Status: {health.status}")
    print(f"Framework Version: {health.version}")
    print(f"Python Version: {health.python_version}")
    
    print("\nServices Status:")
    for service, status in health.services.items():
        emoji = "✅" if status == "healthy" else "❌"
        print(f"  {emoji} {service}: {status}")
    
    print("\nConfiguration:")
    for key, value in health.config.items():
        print(f"  {key}: {value}")
    
    if health.warnings:
        print("\nWarnings:")
        for warning in health.warnings:
            print(f"  ⚠️ {warning}")
    
    if health.errors:
        print("\nErrors:")
        for error in health.errors:
            print(f"  ❌ {error}")

import asyncio
asyncio.run(full_health_check())
```

### Debug Information Collection
```bash
# Collect debug information
python -m ai_enhancement_framework debug-info > debug_report.txt

# System information
echo "=== System Information ===" >> debug_report.txt
uname -a >> debug_report.txt
python --version >> debug_report.txt
pip list | grep ai-enhancement >> debug_report.txt

# Docker information
echo "=== Docker Information ===" >> debug_report.txt
docker --version >> debug_report.txt
docker-compose --version >> debug_report.txt
docker ps >> debug_report.txt
```

### Log Analysis
```bash
# Check framework logs
tail -f ai_framework.log

# Check Docker logs
docker-compose logs -f

# Search for specific errors
grep -i "error" ai_framework.log
grep -i "warning" ai_framework.log
```

## 🆘 Getting Help

### Before Reporting Issues
1. **Run health check** - Use the diagnostic tools above
2. **Check logs** - Review framework and service logs
3. **Try clean install** - Fresh installation often resolves issues
4. **Verify configuration** - Ensure all configuration files are valid

### Information to Include in Bug Reports
```bash
# Collect this information for bug reports:

# 1. Framework version
python -c "import ai_enhancement_framework; print(ai_enhancement_framework.__version__)"

# 2. System information
uname -a
python --version
pip --version

# 3. Configuration files
cat .cursorrules
cat .vscode/settings.json

# 4. Error logs
tail -20 ai_framework.log

# 5. Docker status (if using services)
docker ps
docker-compose ps
```

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check online documentation for updates
- **Community Forum**: Get help from other users
- **Stack Overflow**: Tag questions with `ai-enhancement-framework`

## 📚 Related Documentation

- **[Installation Guide](CURSOR_INSTALLATION_HOW_TO.md)** - Initial setup instructions
- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Advanced configuration options
- **[Core Framework Documentation](../core/README.md)** - Framework architecture details
- **[User Guide](../docs/user_guide.md)** - Comprehensive usage guide

---

**Troubleshooting Guide Version**: 1.0.0  
**Framework Version**: 1.0.0  
**Last Updated**: January 18, 2025  
**Status**: Production Ready ✅ 