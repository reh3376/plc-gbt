#!/bin/bash

# AI Enhancement Framework - Setup Verification Script
# Comprehensive verification of complete framework installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNING_CHECKS++))
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_CHECKS++))
}

# Test function wrapper
run_check() {
    local test_name="$1"
    local test_function="$2"
    
    ((TOTAL_CHECKS++))
    print_status "Checking: $test_name"
    
    if $test_function; then
        print_success "$test_name"
        return 0
    else
        print_error "$test_name"
        return 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            echo "  Python $PYTHON_VERSION found"
            return 0
        else
            echo "  Python $PYTHON_VERSION is too old (need 3.8+)"
            return 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        echo "  Warning: Using 'python' command (version $PYTHON_VERSION)"
        echo "  Consider using 'python3' explicitly"
        return 0
    else
        echo "  Python not found"
        return 1
    fi
}

# Check virtual environment
check_virtual_env() {
    if [ -d "ai-enhancement-env" ]; then
        echo "  Virtual environment directory exists"
        
        if [ -f "ai-enhancement-env/bin/activate" ]; then
            echo "  Activation script found"
            return 0
        elif [ -f "ai-enhancement-env/Scripts/activate" ]; then
            echo "  Windows activation script found"
            return 0
        else
            echo "  Virtual environment appears corrupted"
            return 1
        fi
    else
        echo "  Virtual environment not found"
        return 1
    fi
}

# Check Docker installation
check_docker() {
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version 2>/dev/null)
        echo "  $DOCKER_VERSION"
        
        if docker system info >/dev/null 2>&1; then
            echo "  Docker daemon is running"
            return 0
        else
            echo "  Docker daemon is not running"
            return 1
        fi
    else
        echo "  Docker not found"
        return 1
    fi
}

# Check Docker Compose
check_docker_compose() {
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version 2>/dev/null)
        echo "  $COMPOSE_VERSION"
        return 0
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version --short 2>/dev/null)
        echo "  Docker Compose plugin v$COMPOSE_VERSION"
        return 0
    else
        echo "  Docker Compose not found"
        return 1
    fi
}

# Check configuration files
check_config_files() {
    local missing_files=()
    
    # Check required configuration files
    [ ! -f ".env" ] && missing_files+=(".env")
    [ ! -f ".cursorrules" ] && missing_files+=(".cursorrules")
    [ ! -f "docker/docker-compose.yml" ] && missing_files+=("docker/docker-compose.yml")
    [ ! -f "docker/Dockerfile" ] && missing_files+=("docker/Dockerfile")
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        echo "  All required configuration files present"
        return 0
    else
        echo "  Missing files: ${missing_files[*]}"
        return 1
    fi
}

# Check Docker services
check_docker_services() {
    if [ ! -f "docker/docker-compose.yml" ]; then
        echo "  docker-compose.yml not found"
        return 1
    fi
    
    # Check if services are defined
    SERVICES=$(docker-compose -f docker/docker-compose.yml config --services 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "  Services defined: $(echo $SERVICES | tr '\n' ' ')"
        
        # Check if services are running
        RUNNING_SERVICES=$(docker-compose -f docker/docker-compose.yml ps --services --filter "status=running" 2>/dev/null)
        if [ -n "$RUNNING_SERVICES" ]; then
            echo "  Running services: $(echo $RUNNING_SERVICES | tr '\n' ' ')"
            return 0
        else
            echo "  No services currently running"
            return 1
        fi
    else
        echo "  Invalid docker-compose.yml file"
        return 1
    fi
}

# Check individual service health
check_service_health() {
    local service="$1"
    local port="$2"
    local health_check="$3"
    
    if curl -f -s "http://localhost:$port$health_check" >/dev/null 2>&1; then
        echo "  $service is healthy (port $port)"
        return 0
    else
        echo "  $service is not responding (port $port)"
        return 1
    fi
}

# Check Redis
check_redis() {
    check_service_health "Redis" "6379" ""
    return $?
}

# Check Neo4j
check_neo4j() {
    check_service_health "Neo4j" "7474" ""
    return $?
}

# Check PostgreSQL
check_postgresql() {
    if command_exists pg_isready; then
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            echo "  PostgreSQL is ready"
            return 0
        else
            echo "  PostgreSQL is not ready"
            return 1
        fi
    else
        # Fallback: try to connect via docker
        if docker-compose -f docker/docker-compose.yml exec -T postgresql pg_isready >/dev/null 2>&1; then
            echo "  PostgreSQL is ready (via Docker)"
            return 0
        else
            echo "  PostgreSQL is not ready"
            return 1
        fi
    fi
}

# Check Qdrant
check_qdrant() {
    check_service_health "Qdrant" "6333" "/health"
    return $?
}

# Check network connectivity
check_network() {
    if docker network ls | grep -q "ai_enhancement_network"; then
        echo "  AI Enhancement network exists"
        return 0
    else
        echo "  AI Enhancement network not found"
        return 1
    fi
}

# Check volumes
check_volumes() {
    local volumes=$(docker volume ls -q | grep "ai_framework" | wc -l)
    if [ "$volumes" -gt 0 ]; then
        echo "  Found $volumes AI Framework volumes"
        return 0
    else
        echo "  No AI Framework volumes found"
        return 1
    fi
}

# Check Python dependencies
check_python_dependencies() {
    if [ -f "requirements.txt" ]; then
        # Try to activate virtual environment and check packages
        if [ -f "ai-enhancement-env/bin/activate" ]; then
            source ai-enhancement-env/bin/activate
            
            # Check a few key packages
            local missing_packages=()
            
            python -c "import redis" 2>/dev/null || missing_packages+=("redis")
            python -c "import neo4j" 2>/dev/null || missing_packages+=("neo4j")
            python -c "import psycopg2" 2>/dev/null || missing_packages+=("psycopg2")
            python -c "import qdrant_client" 2>/dev/null || missing_packages+=("qdrant-client")
            
            if [ ${#missing_packages[@]} -eq 0 ]; then
                echo "  Key Python packages are installed"
                return 0
            else
                echo "  Missing packages: ${missing_packages[*]}"
                return 1
            fi
        else
            echo "  Cannot activate virtual environment"
            return 1
        fi
    else
        echo "  requirements.txt not found"
        return 1
    fi
}

# Check IDE configuration
check_ide_config() {
    local score=0
    local total=0
    
    # Check VSCode/Cursor settings
    if [ -f ".vscode/settings.json" ]; then
        ((score++))
        echo "  VSCode/Cursor settings found"
    fi
    ((total++))
    
    # Check cursorrules
    if [ -f ".cursorrules" ]; then
        ((score++))
        echo "  Cursor rules found"
    fi
    ((total++))
    
    # Check if Python interpreter is configured
    if [ -f ".vscode/settings.json" ] && grep -q "python.defaultInterpreterPath" ".vscode/settings.json"; then
        ((score++))
        echo "  Python interpreter configured"
    fi
    ((total++))
    
    if [ "$score" -eq "$total" ]; then
        return 0
    else
        echo "  IDE configuration incomplete ($score/$total)"
        return 1
    fi
}

# Performance benchmark
run_performance_test() {
    print_status "Running performance tests..."
    
    # Test Docker startup time
    if [ -f "docker/docker-compose.yml" ]; then
        print_status "Testing service startup time..."
        
        START_TIME=$(date +%s)
        docker-compose -f docker/docker-compose.yml up -d >/dev/null 2>&1
        
        # Wait for services to be healthy
        sleep 30
        
        END_TIME=$(date +%s)
        STARTUP_TIME=$((END_TIME - START_TIME))
        
        if [ "$STARTUP_TIME" -lt 60 ]; then
            print_success "Service startup time: ${STARTUP_TIME}s (Good)"
        elif [ "$STARTUP_TIME" -lt 120 ]; then
            print_warning "Service startup time: ${STARTUP_TIME}s (Acceptable)"
        else
            print_error "Service startup time: ${STARTUP_TIME}s (Slow)"
        fi
    fi
    
    # Test memory usage
    MEMORY_USAGE=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep -E "(redis|neo4j|postgres|qdrant)" | awk '{print $2}' | sed 's/MiB.*//' | awk '{sum += $1} END {print sum}')
    
    if [ ! -z "$MEMORY_USAGE" ]; then
        if [ "$MEMORY_USAGE" -lt 2000 ]; then
            print_success "Total memory usage: ${MEMORY_USAGE}MiB (Good)"
        elif [ "$MEMORY_USAGE" -lt 4000 ]; then
            print_warning "Total memory usage: ${MEMORY_USAGE}MiB (High)"
        else
            print_error "Total memory usage: ${MEMORY_USAGE}MiB (Very High)"
        fi
    fi
}

# Generate report
generate_report() {
    echo ""
    echo "==========================================="
    echo "AI Enhancement Framework - Setup Report"
    echo "==========================================="
    echo ""
    echo "Total Checks: $TOTAL_CHECKS"
    echo "Passed: $PASSED_CHECKS"
    echo "Failed: $FAILED_CHECKS"
    echo "Warnings: $WARNING_CHECKS"
    echo ""
    
    local success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    
    if [ "$success_rate" -ge 90 ]; then
        print_success "Setup Status: EXCELLENT ($success_rate%)"
        echo "Your AI Enhancement Framework setup is ready for production use!"
    elif [ "$success_rate" -ge 75 ]; then
        print_warning "Setup Status: GOOD ($success_rate%)"
        echo "Your setup is functional but has some issues to address."
    elif [ "$success_rate" -ge 50 ]; then
        print_warning "Setup Status: PARTIAL ($success_rate%)"
        echo "Your setup needs significant attention before use."
    else
        print_error "Setup Status: INCOMPLETE ($success_rate%)"
        echo "Your setup requires major fixes before use."
    fi
    
    echo ""
    
    # Recommendations
    if [ "$FAILED_CHECKS" -gt 0 ]; then
        echo "Recommendations:"
        echo "1. Review failed checks above"
        echo "2. Run ./scripts/setup.sh to fix installation issues"
        echo "3. Check Docker Desktop is running"
        echo "4. Verify all configuration files exist"
        echo "5. Run this script again after fixes"
    fi
    
    # Next steps
    if [ "$success_rate" -ge 75 ]; then
        echo ""
        echo "Next Steps:"
        echo "1. Start development: cursor . (or your preferred editor)"
        echo "2. Activate Python environment: source ai-enhancement-env/bin/activate"
        echo "3. Test AI features with your OpenAI API key in .env"
        echo "4. View services: docker-compose -f docker/docker-compose.yml ps"
    fi
}

# Main function
main() {
    echo "==========================================="
    echo "AI Enhancement Framework"
    echo "Setup Verification"
    echo "==========================================="
    echo ""
    
    # Core system checks
    print_status "=== Core System Checks ==="
    run_check "Python Installation" check_python
    run_check "Virtual Environment" check_virtual_env
    run_check "Docker Installation" check_docker
    run_check "Docker Compose" check_docker_compose
    
    echo ""
    
    # Configuration checks
    print_status "=== Configuration Checks ==="
    run_check "Configuration Files" check_config_files
    run_check "IDE Configuration" check_ide_config
    
    echo ""
    
    # Service checks
    print_status "=== Service Checks ==="
    run_check "Docker Services" check_docker_services
    run_check "Network Configuration" check_network
    run_check "Volume Configuration" check_volumes
    
    echo ""
    
    # Individual service health
    print_status "=== Service Health Checks ==="
    run_check "Redis Service" check_redis
    run_check "Neo4j Service" check_neo4j
    run_check "PostgreSQL Service" check_postgresql
    run_check "Qdrant Service" check_qdrant
    
    echo ""
    
    # Dependency checks
    print_status "=== Dependency Checks ==="
    run_check "Python Dependencies" check_python_dependencies
    
    echo ""
    
    # Performance tests
    if [ "$1" = "--performance" ]; then
        run_performance_test
    fi
    
    # Generate final report
    generate_report
}

# Show usage
if [ "$1" = "--help" ]; then
    echo "AI Enhancement Framework - Setup Verification"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --performance    Include performance tests"
    echo "  --help          Show this help message"
    echo ""
    echo "This script verifies that all components of the AI Enhancement"
    echo "Framework are properly installed and configured."
    exit 0
fi

# Execute main function
main "$@" 