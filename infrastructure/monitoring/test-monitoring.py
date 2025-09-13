#!/usr/bin/env python3
"""
AFAS Monitoring Test Script
Tests the monitoring infrastructure to ensure all components are working correctly.
"""

import asyncio
import aiohttp
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_status(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

class MonitoringTester:
    """Tests AFAS monitoring infrastructure."""
    
    def __init__(self):
        self.monitoring_endpoints = {
            'prometheus': 'http://localhost:9090',
            'grafana': 'http://localhost:3001',
            'alertmanager': 'http://localhost:9093',
            'loki': 'http://localhost:3100'
        }
        
        self.service_endpoints = {
            'question-router': 'http://localhost:8000',
            'recommendation-engine': 'http://localhost:8001',
            'ai-agent': 'http://localhost:8002',
            'data-integration': 'http://localhost:8003',
            'image-analysis': 'http://localhost:8004',
            'user-management': 'http://localhost:8005',
            'frontend': 'http://localhost:3000'
        }
        
        self.exporter_endpoints = {
            'node-exporter': 'http://localhost:9100',
            'postgres-exporter': 'http://localhost:9187',
            'mongodb-exporter': 'http://localhost:9216',
            'redis-exporter': 'http://localhost:9121'
        }
    
    async def test_endpoint_health(self, session: aiohttp.ClientSession, name: str, url: str, 
                                 expected_paths: List[str] = None) -> Dict[str, Any]:
        """Test if an endpoint is healthy and responsive."""
        result = {
            'name': name,
            'url': url,
            'status': 'unknown',
            'response_time': None,
            'error': None,
            'paths_tested': {}
        }
        
        try:
            start_time = time.time()
            
            # Test main endpoint
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                result['response_time'] = time.time() - start_time
                result['status'] = 'healthy' if response.status == 200 else f'error_{response.status}'
                
                # Test additional paths if specified
                if expected_paths:
                    for path in expected_paths:
                        path_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
                        try:
                            async with session.get(path_url, timeout=aiohttp.ClientTimeout(total=5)) as path_response:
                                result['paths_tested'][path] = {
                                    'status': path_response.status,
                                    'healthy': path_response.status == 200
                                }
                        except Exception as e:
                            result['paths_tested'][path] = {
                                'status': 'error',
                                'error': str(e),
                                'healthy': False
                            }
                
        except asyncio.TimeoutError:
            result['status'] = 'timeout'
            result['error'] = 'Request timed out'
        except aiohttp.ClientConnectorError:
            result['status'] = 'connection_refused'
            result['error'] = 'Connection refused'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    async def test_prometheus_targets(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Prometheus targets to ensure services are being scraped."""
        result = {
            'targets_up': 0,
            'targets_down': 0,
            'targets': {}
        }
        
        try:
            async with session.get('http://localhost:9090/api/v1/targets') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for target in data.get('data', {}).get('activeTargets', []):
                        job = target.get('labels', {}).get('job', 'unknown')
                        health = target.get('health', 'unknown')
                        
                        result['targets'][job] = {
                            'health': health,
                            'last_scrape': target.get('lastScrape'),
                            'scrape_duration': target.get('scrapeDuration'),
                            'error': target.get('lastError', '')
                        }
                        
                        if health == 'up':
                            result['targets_up'] += 1
                        else:
                            result['targets_down'] += 1
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def test_grafana_datasources(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test Grafana datasources."""
        result = {
            'datasources': {},
            'healthy_count': 0,
            'total_count': 0
        }
        
        try:
            # Test with basic auth (admin:afas_admin_2024)
            auth = aiohttp.BasicAuth('admin', 'afas_admin_2024')
            
            async with session.get('http://localhost:3001/api/datasources', auth=auth) as response:
                if response.status == 200:
                    datasources = await response.json()
                    
                    for ds in datasources:
                        name = ds.get('name', 'unknown')
                        ds_type = ds.get('type', 'unknown')
                        url = ds.get('url', '')
                        
                        result['datasources'][name] = {
                            'type': ds_type,
                            'url': url,
                            'id': ds.get('id')
                        }
                        result['total_count'] += 1
                        
                        # Test datasource health
                        ds_id = ds.get('id')
                        if ds_id:
                            try:
                                async with session.get(f'http://localhost:3001/api/datasources/{ds_id}/health', auth=auth) as health_response:
                                    if health_response.status == 200:
                                        health_data = await health_response.json()
                                        result['datasources'][name]['health'] = health_data.get('status', 'unknown')
                                        if health_data.get('status') == 'success':
                                            result['healthy_count'] += 1
                            except:
                                result['datasources'][name]['health'] = 'error'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def test_service_metrics(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Test that AFAS services are exposing metrics."""
        result = {
            'services_with_metrics': 0,
            'total_services': len(self.service_endpoints),
            'services': {}
        }
        
        for service_name, base_url in self.service_endpoints.items():
            metrics_url = f"{base_url}/metrics"
            
            try:
                async with session.get(metrics_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        metrics_text = await response.text()
                        
                        # Check for AFAS-specific metrics
                        afas_metrics = [
                            'afas_http_requests_total',
                            'afas_questions_asked_total',
                            'afas_recommendations_generated_total'
                        ]
                        
                        found_metrics = []
                        for metric in afas_metrics:
                            if metric in metrics_text:
                                found_metrics.append(metric)
                        
                        result['services'][service_name] = {
                            'metrics_endpoint': 'available',
                            'afas_metrics_found': found_metrics,
                            'total_metrics_lines': len(metrics_text.split('\n'))
                        }
                        
                        if found_metrics:
                            result['services_with_metrics'] += 1
                    else:
                        result['services'][service_name] = {
                            'metrics_endpoint': f'error_{response.status}',
                            'afas_metrics_found': [],
                            'total_metrics_lines': 0
                        }
            
            except Exception as e:
                result['services'][service_name] = {
                    'metrics_endpoint': 'unavailable',
                    'error': str(e),
                    'afas_metrics_found': [],
                    'total_metrics_lines': 0
                }
        
        return result
    
    async def test_log_collection(self) -> Dict[str, Any]:
        """Test log collection and file structure."""
        result = {
            'log_directories': {},
            'total_log_files': 0,
            'services_with_logs': 0
        }
        
        logs_dir = Path('../../logs')
        
        if logs_dir.exists():
            for service_dir in logs_dir.iterdir():
                if service_dir.is_dir():
                    log_files = list(service_dir.glob('*.log'))
                    
                    result['log_directories'][service_dir.name] = {
                        'log_files': [f.name for f in log_files],
                        'file_count': len(log_files),
                        'total_size_mb': sum(f.stat().st_size for f in log_files) / (1024 * 1024)
                    }
                    
                    result['total_log_files'] += len(log_files)
                    if log_files:
                        result['services_with_logs'] += 1
        else:
            result['error'] = 'Logs directory not found'
        
        return result
    
    async def generate_test_metrics(self, session: aiohttp.ClientSession):
        """Generate some test metrics by making requests to services."""
        print_status("Generating test metrics by making sample requests...")
        
        test_requests = [
            ('question-router', '/health'),
            ('question-router', '/api/v1/questions/types'),
            ('recommendation-engine', '/health'),
            ('ai-agent', '/health'),
        ]
        
        for service, endpoint in test_requests:
            if service in self.service_endpoints:
                url = f"{self.service_endpoints[service]}{endpoint}"
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        print_status(f"  ✓ {service}{endpoint} -> {response.status}")
                except:
                    print_warning(f"  ✗ {service}{endpoint} -> failed")
        
        # Wait a bit for metrics to be scraped
        await asyncio.sleep(5)
    
    async def run_comprehensive_test(self):
        """Run comprehensive monitoring test suite."""
        print("🔍 AFAS Monitoring Test Suite")
        print("=============================")
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Monitoring Infrastructure
            print_status("\\n1. Testing monitoring infrastructure...")
            
            monitoring_results = {}
            for name, url in self.monitoring_endpoints.items():
                expected_paths = []
                if name == 'prometheus':
                    expected_paths = ['api/v1/targets', '-/healthy']
                elif name == 'grafana':
                    expected_paths = ['api/health']
                elif name == 'alertmanager':
                    expected_paths = ['-/healthy']
                elif name == 'loki':
                    expected_paths = ['ready']
                
                result = await self.test_endpoint_health(session, name, url, expected_paths)
                monitoring_results[name] = result
                
                if result['status'] == 'healthy':
                    print_success(f"  ✓ {name} is healthy ({result['response_time']:.2f}s)")
                else:
                    print_error(f"  ✗ {name} is {result['status']}: {result.get('error', 'Unknown error')}")
            
            # Test 2: Service Metrics Endpoints
            print_status("\\n2. Testing service metrics endpoints...")
            
            metrics_results = await self.test_service_metrics(session)
            print_status(f"  Services with metrics: {metrics_results['services_with_metrics']}/{metrics_results['total_services']}")
            
            for service, data in metrics_results['services'].items():
                if data['metrics_endpoint'] == 'available':
                    afas_count = len(data['afas_metrics_found'])
                    print_success(f"  ✓ {service}: {data['total_metrics_lines']} metrics, {afas_count} AFAS-specific")
                else:
                    print_warning(f"  ✗ {service}: {data['metrics_endpoint']}")
            
            # Test 3: Prometheus Targets
            print_status("\\n3. Testing Prometheus targets...")
            
            targets_result = await self.test_prometheus_targets(session)
            if 'error' not in targets_result:
                print_status(f"  Targets up: {targets_result['targets_up']}, down: {targets_result['targets_down']}")
                
                for job, data in targets_result['targets'].items():
                    if data['health'] == 'up':
                        print_success(f"  ✓ {job}: {data['health']} (scrape: {data['scrape_duration']})")
                    else:
                        print_error(f"  ✗ {job}: {data['health']} - {data['error']}")
            else:
                print_error(f"  Failed to get targets: {targets_result['error']}")
            
            # Test 4: Grafana Datasources
            print_status("\\n4. Testing Grafana datasources...")
            
            grafana_result = await self.test_grafana_datasources(session)
            if 'error' not in grafana_result:
                print_status(f"  Healthy datasources: {grafana_result['healthy_count']}/{grafana_result['total_count']}")
                
                for ds_name, data in grafana_result['datasources'].items():
                    health = data.get('health', 'unknown')
                    if health == 'success':
                        print_success(f"  ✓ {ds_name} ({data['type']}): healthy")
                    else:
                        print_warning(f"  ⚠ {ds_name} ({data['type']}): {health}")
            else:
                print_error(f"  Failed to test datasources: {grafana_result['error']}")
            
            # Test 5: Log Collection
            print_status("\\n5. Testing log collection...")
            
            log_result = await self.test_log_collection()
            if 'error' not in log_result:
                print_status(f"  Services with logs: {log_result['services_with_logs']}")
                print_status(f"  Total log files: {log_result['total_log_files']}")
                
                for service, data in log_result['log_directories'].items():
                    if data['file_count'] > 0:
                        print_success(f"  ✓ {service}: {data['file_count']} files ({data['total_size_mb']:.1f}MB)")
                    else:
                        print_warning(f"  ⚠ {service}: no log files")
            else:
                print_error(f"  Log collection test failed: {log_result['error']}")
            
            # Test 6: Generate Test Data
            print_status("\\n6. Generating test metrics...")
            await self.generate_test_metrics(session)
            
            # Test 7: Exporters
            print_status("\\n7. Testing database exporters...")
            
            for name, url in self.exporter_endpoints.items():
                result = await self.test_endpoint_health(session, name, url, ['metrics'])
                
                if result['status'] == 'healthy':
                    print_success(f"  ✓ {name} is healthy")
                else:
                    print_warning(f"  ⚠ {name} is {result['status']} (may need database connection)")
        
        # Summary
        print_status("\\n📊 Test Summary")
        print_status("================")
        
        # Calculate overall health
        healthy_monitoring = sum(1 for r in monitoring_results.values() if r['status'] == 'healthy')
        total_monitoring = len(monitoring_results)
        
        print_status(f"Monitoring Infrastructure: {healthy_monitoring}/{total_monitoring} healthy")
        print_status(f"Service Metrics: {metrics_results['services_with_metrics']}/{metrics_results['total_services']} available")
        
        if 'error' not in targets_result:
            print_status(f"Prometheus Targets: {targets_result['targets_up']} up, {targets_result['targets_down']} down")
        
        if 'error' not in grafana_result:
            print_status(f"Grafana Datasources: {grafana_result['healthy_count']}/{grafana_result['total_count']} healthy")
        
        if 'error' not in log_result:
            print_status(f"Log Collection: {log_result['services_with_logs']} services logging")
        
        # Recommendations
        print_status("\\n💡 Recommendations")
        print_status("===================")
        
        if healthy_monitoring < total_monitoring:
            print_warning("• Some monitoring services are not healthy. Check Docker containers.")
        
        if metrics_results['services_with_metrics'] < metrics_results['total_services']:
            print_warning("• Some services don't have metrics endpoints. Run integrate-monitoring.py")
        
        if 'error' not in targets_result and targets_result['targets_down'] > 0:
            print_warning("• Some Prometheus targets are down. Check service connectivity.")
        
        if 'error' not in log_result and log_result['services_with_logs'] == 0:
            print_warning("• No log files found. Check logging configuration.")
        
        print_status("\\n🔗 Useful Links")
        print_status("================")
        print_status("• Prometheus: http://localhost:9090")
        print_status("• Grafana: http://localhost:3001 (admin/afas_admin_2024)")
        print_status("• Alertmanager: http://localhost:9093")
        print_status("• Loki: http://localhost:3100")

def main():
    """Main execution function."""
    tester = MonitoringTester()
    asyncio.run(tester.run_comprehensive_test())

if __name__ == "__main__":
    main()