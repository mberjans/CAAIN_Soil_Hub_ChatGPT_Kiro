#!/bin/bash

# AFAS Monitoring Status Script
# Quick status check for monitoring infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

check_service() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        print_success "✓ $service_name is running ($url)"
        return 0
    else
        print_error "✗ $service_name is not responding ($url)"
        return 1
    fi
}

check_docker_service() {
    local container_name=$1
    
    if docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        if [ "$status" = "running" ]; then
            print_success "✓ $container_name container is running"
            return 0
        else
            print_error "✗ $container_name container is $status"
            return 1
        fi
    else
        print_error "✗ $container_name container not found"
        return 1
    fi
}

check_log_files() {
    local logs_dir="../../logs"
    
    if [ -d "$logs_dir" ]; then
        local log_count=$(find "$logs_dir" -name "*.log" | wc -l)
        if [ "$log_count" -gt 0 ]; then
            print_success "✓ Found $log_count log files in $logs_dir"
            
            # Show recent log activity
            local recent_logs=$(find "$logs_dir" -name "*.log" -mmin -10 | wc -l)
            if [ "$recent_logs" -gt 0 ]; then
                print_success "  → $recent_logs log files updated in last 10 minutes"
            else
                print_warning "  → No recent log activity (last 10 minutes)"
            fi
        else
            print_warning "⚠ No log files found in $logs_dir"
        fi
    else
        print_error "✗ Logs directory not found: $logs_dir"
    fi
}

check_prometheus_targets() {
    local prometheus_url="http://localhost:9090"
    
    if curl -s --max-time 5 "$prometheus_url/api/v1/targets" > /dev/null 2>&1; then
        local targets_data=$(curl -s "$prometheus_url/api/v1/targets")
        local up_count=$(echo "$targets_data" | jq -r '.data.activeTargets[] | select(.health=="up") | .labels.job' 2>/dev/null | wc -l)
        local down_count=$(echo "$targets_data" | jq -r '.data.activeTargets[] | select(.health!="up") | .labels.job' 2>/dev/null | wc -l)
        
        if [ "$up_count" -gt 0 ]; then
            print_success "✓ Prometheus has $up_count targets up"
            if [ "$down_count" -gt 0 ]; then
                print_warning "  → $down_count targets are down"
            fi
        else
            print_error "✗ No Prometheus targets are up"
        fi
    else
        print_error "✗ Cannot check Prometheus targets"
    fi
}

show_quick_stats() {
    print_status "\n📊 Quick Statistics"
    print_status "==================="
    
    # Docker containers
    local running_containers=$(docker ps --filter "name=afas-" --format "{{.Names}}" | wc -l)
    print_status "Running monitoring containers: $running_containers"
    
    # Service endpoints
    local services=("question-router:8000" "recommendation-engine:8001" "ai-agent:8002" "data-integration:8003" "image-analysis:8004" "user-management:8005")
    local running_services=0
    
    for service in "${services[@]}"; do
        local name=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        if curl -s --max-time 2 "http://localhost:$port/health" > /dev/null 2>&1; then
            running_services=$((running_services + 1))
        fi
    done
    
    print_status "AFAS services responding: $running_services/${#services[@]}"
    
    # Log files
    if [ -d "../../logs" ]; then
        local total_logs=$(find "../../logs" -name "*.log" | wc -l)
        local total_size=$(find "../../logs" -name "*.log" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
        print_status "Log files: $total_logs files, $total_size total"
    fi
}

show_access_urls() {
    print_status "\n🔗 Access URLs"
    print_status "==============="
    print_status "• Prometheus:    http://localhost:9090"
    print_status "• Grafana:       http://localhost:3001 (admin/afas_admin_2024)"
    print_status "• Alertmanager:  http://localhost:9093"
    print_status "• Loki:          http://localhost:3100"
    print_status ""
    print_status "• Node Exporter: http://localhost:9100/metrics"
    print_status "• DB Exporters:  http://localhost:9187, 9216, 9121"
}

main() {
    echo "🌾 AFAS Monitoring Status Check"
    echo "==============================="
    
    print_status "\n🐳 Docker Containers"
    print_status "===================="
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # Check monitoring containers
    local containers=("afas-prometheus" "afas-grafana" "afas-alertmanager" "afas-loki" "afas-promtail")
    local running_count=0
    
    for container in "${containers[@]}"; do
        if check_docker_service "$container"; then
            running_count=$((running_count + 1))
        fi
    done
    
    print_status "\n🌐 Service Health"
    print_status "=================="
    
    # Check monitoring services
    local services_healthy=0
    
    if check_service "Prometheus" "http://localhost:9090/-/healthy"; then
        services_healthy=$((services_healthy + 1))
    fi
    
    if check_service "Grafana" "http://localhost:3001/api/health"; then
        services_healthy=$((services_healthy + 1))
    fi
    
    if check_service "Alertmanager" "http://localhost:9093/-/healthy"; then
        services_healthy=$((services_healthy + 1))
    fi
    
    if check_service "Loki" "http://localhost:3100/ready"; then
        services_healthy=$((services_healthy + 1))
    fi
    
    print_status "\n🎯 Prometheus Targets"
    print_status "====================="
    check_prometheus_targets
    
    print_status "\n📝 Log Collection"
    print_status "=================="
    check_log_files
    
    # Show statistics
    show_quick_stats
    
    # Show access URLs
    show_access_urls
    
    print_status "\n🔧 Management Commands"
    print_status "======================"
    print_status "• Start monitoring:  ./setup-monitoring.sh"
    print_status "• Stop monitoring:   docker-compose -f docker-compose.monitoring.yml down"
    print_status "• View logs:         docker-compose -f docker-compose.monitoring.yml logs -f"
    print_status "• Test monitoring:   ./test-monitoring.py"
    print_status "• Integrate services: ./integrate-monitoring.py"
    
    # Overall status
    print_status "\n📋 Overall Status"
    print_status "=================="
    
    if [ "$running_count" -eq "${#containers[@]}" ] && [ "$services_healthy" -ge 3 ]; then
        print_success "🎉 Monitoring infrastructure is healthy!"
    elif [ "$running_count" -gt 0 ] || [ "$services_healthy" -gt 0 ]; then
        print_warning "⚠️  Monitoring infrastructure is partially working"
        print_status "   Run './setup-monitoring.sh' to fix issues"
    else
        print_error "❌ Monitoring infrastructure is not running"
        print_status "   Run './setup-monitoring.sh' to start monitoring"
    fi
}

# Run main function
main "$@"