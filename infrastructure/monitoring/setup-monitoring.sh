#!/bin/bash

# AFAS Monitoring Infrastructure Setup Script
# Sets up local monitoring stack with Prometheus, Grafana, and log aggregation

set -e

echo "🔧 Setting up AFAS Monitoring Infrastructure..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Create necessary directories
create_directories() {
    print_status "Creating monitoring directories..."
    
    # Create log directories
    mkdir -p ../../logs/question-router
    mkdir -p ../../logs/recommendation-engine
    mkdir -p ../../logs/ai-agent
    mkdir -p ../../logs/data-integration
    mkdir -p ../../logs/image-analysis
    mkdir -p ../../logs/user-management
    mkdir -p ../../logs/frontend
    
    # Create monitoring data directories
    mkdir -p ./data/prometheus
    mkdir -p ./data/grafana
    mkdir -p ./data/loki
    mkdir -p ./data/alertmanager
    
    # Set permissions
    chmod 755 ./data/*
    
    print_success "Directories created successfully"
}

# Install Python monitoring dependencies
install_python_deps() {
    print_status "Installing Python monitoring dependencies..."
    
    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Using virtual environment: $VIRTUAL_ENV"
    else
        print_warning "No virtual environment detected. Consider using one."
    fi
    
    # Install monitoring packages
    pip install prometheus-client structlog
    
    print_success "Python dependencies installed"
}

# Start monitoring stack
start_monitoring_stack() {
    print_status "Starting monitoring stack..."
    
    # Pull latest images
    docker-compose -f docker-compose.monitoring.yml pull
    
    # Start services
    docker-compose -f docker-compose.monitoring.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check if services are running
    if docker-compose -f docker-compose.monitoring.yml ps | grep -q "Up"; then
        print_success "Monitoring stack started successfully"
    else
        print_error "Some services failed to start"
        docker-compose -f docker-compose.monitoring.yml logs
        exit 1
    fi
}

# Configure Grafana dashboards
configure_grafana() {
    print_status "Configuring Grafana dashboards..."
    
    # Wait for Grafana to be ready
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
            break
        fi
        print_status "Waiting for Grafana to be ready... (attempt $((attempt + 1))/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Grafana failed to start within expected time"
        exit 1
    fi
    
    # Import dashboards (they should be auto-provisioned)
    print_success "Grafana is ready and dashboards should be auto-provisioned"
}

# Verify monitoring setup
verify_setup() {
    print_status "Verifying monitoring setup..."
    
    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        print_success "✓ Prometheus is healthy (http://localhost:9090)"
    else
        print_error "✗ Prometheus is not responding"
    fi
    
    # Check Grafana
    if curl -s http://localhost:3001/api/health > /dev/null; then
        print_success "✓ Grafana is healthy (http://localhost:3001)"
        print_status "  Default login: admin / afas_admin_2024"
    else
        print_error "✗ Grafana is not responding"
    fi
    
    # Check Alertmanager
    if curl -s http://localhost:9093/-/healthy > /dev/null; then
        print_success "✓ Alertmanager is healthy (http://localhost:9093)"
    else
        print_error "✗ Alertmanager is not responding"
    fi
    
    # Check Loki
    if curl -s http://localhost:3100/ready > /dev/null; then
        print_success "✓ Loki is healthy (http://localhost:3100)"
    else
        print_error "✗ Loki is not responding"
    fi
    
    # Check exporters
    services=("node-exporter:9100" "postgres-exporter:9187" "mongodb-exporter:9216" "redis-exporter:9121")
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s http://localhost:$port/metrics > /dev/null; then
            print_success "✓ $name is healthy (http://localhost:$port)"
        else
            print_warning "⚠ $name is not responding (may need database connection)"
        fi
    done
}

# Create monitoring integration script
create_integration_script() {
    print_status "Creating monitoring integration script..."
    
    cat > ./integrate-monitoring.py << 'EOF'
#!/usr/bin/env python3
"""
AFAS Monitoring Integration Script
Integrates monitoring into existing AFAS services
"""

import os
import sys
from pathlib import Path

def integrate_metrics_into_service(service_path):
    """Add metrics integration to a service."""
    
    # Add metrics endpoint to FastAPI service
    main_py = service_path / "src" / "main.py"
    
    if main_py.exists():
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check if metrics are already integrated
        if 'prometheus_client' in content:
            print(f"✓ Metrics already integrated in {service_path.name}")
            return
        
        # Add metrics imports and endpoint
        metrics_code = '''
# Metrics integration
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from shared.utils.metrics import MetricsCollector
from shared.utils.logging_config import setup_logging

# Initialize metrics collector
metrics_collector = MetricsCollector("{service_name}")

# Setup logging
setup_logging("{service_name}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
'''.format(service_name=service_path.name)
        
        # Insert after FastAPI app creation
        if 'app = FastAPI(' in content:
            content = content.replace(
                'app = FastAPI(',
                f'{metrics_code}\napp = FastAPI('
            )
            
            with open(main_py, 'w') as f:
                f.write(content)
            
            print(f"✓ Metrics integrated into {service_path.name}")
        else:
            print(f"⚠ Could not integrate metrics into {service_path.name} - FastAPI app not found")
    else:
        print(f"⚠ main.py not found in {service_path.name}")

def main():
    """Integrate monitoring into all AFAS services."""
    
    services_dir = Path("../../services")
    
    if not services_dir.exists():
        print("❌ Services directory not found")
        sys.exit(1)
    
    services = [d for d in services_dir.iterdir() if d.is_dir()]
    
    for service in services:
        integrate_metrics_into_service(service)
    
    print("\n🎉 Monitoring integration complete!")
    print("\nNext steps:")
    print("1. Restart your AFAS services")
    print("2. Check metrics at http://localhost:9090/targets")
    print("3. View dashboards at http://localhost:3001")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x ./integrate-monitoring.py
    print_success "Integration script created"
}

# Main execution
main() {
    echo "🌾 AFAS Monitoring Infrastructure Setup"
    echo "======================================"
    
    check_docker
    create_directories
    install_python_deps
    start_monitoring_stack
    configure_grafana
    create_integration_script
    verify_setup
    
    echo ""
    echo "🎉 Monitoring infrastructure setup complete!"
    echo ""
    echo "📊 Access Points:"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3001 (admin / afas_admin_2024)"
    echo "  • Alertmanager: http://localhost:9093"
    echo "  • Loki: http://localhost:3100"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Run './integrate-monitoring.py' to add metrics to services"
    echo "  2. Start your AFAS services with monitoring enabled"
    echo "  3. Check Prometheus targets at http://localhost:9090/targets"
    echo "  4. View agricultural dashboards in Grafana"
    echo ""
    echo "📝 Log Files:"
    echo "  • Service logs: ../../logs/<service>/"
    echo "  • Monitoring logs: docker-compose logs -f"
    echo ""
    echo "⚠️  Remember to configure database connections for exporters"
}

# Run main function
main "$@"