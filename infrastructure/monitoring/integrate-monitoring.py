#!/usr/bin/env python3
"""
AFAS Monitoring Integration Script
Integrates monitoring into existing AFAS services by adding metrics endpoints and logging.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

class MonitoringIntegrator:
    """Integrates monitoring into AFAS services."""
    
    def __init__(self, services_dir: Path):
        self.services_dir = services_dir
        self.shared_dir = services_dir.parent / "shared"
        
    def get_services(self) -> List[Path]:
        """Get list of service directories."""
        services = []
        for item in self.services_dir.iterdir():
            if item.is_dir() and (item / "src" / "main.py").exists():
                services.append(item)
        return services
    
    def check_shared_utils(self) -> bool:
        """Check if shared monitoring utilities exist."""
        metrics_file = self.shared_dir / "utils" / "metrics.py"
        logging_file = self.shared_dir / "utils" / "logging_config.py"
        
        if not metrics_file.exists():
            print_error(f"Shared metrics utility not found: {metrics_file}")
            return False
            
        if not logging_file.exists():
            print_error(f"Shared logging utility not found: {logging_file}")
            return False
            
        return True
    
    def integrate_service(self, service_path: Path) -> bool:
        """Integrate monitoring into a single service."""
        service_name = service_path.name
        main_py = service_path / "src" / "main.py"
        
        if not main_py.exists():
            print_warning(f"main.py not found in {service_name}")
            return False
        
        # Read current content
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check if already integrated
        if 'prometheus_client' in content and '/metrics' in content:
            print_success(f"✓ Monitoring already integrated in {service_name}")
            return True
        
        # Backup original file
        backup_file = main_py.with_suffix('.py.backup')
        with open(backup_file, 'w') as f:
            f.write(content)
        
        # Add monitoring integration
        updated_content = self.add_monitoring_imports(content, service_name)
        updated_content = self.add_metrics_endpoint(updated_content)
        updated_content = self.add_monitoring_middleware(updated_content, service_name)
        
        # Write updated content
        with open(main_py, 'w') as f:
            f.write(updated_content)
        
        print_success(f"✓ Monitoring integrated into {service_name}")
        return True
    
    def add_monitoring_imports(self, content: str, service_name: str) -> str:
        """Add monitoring imports to the service."""
        
        # Find FastAPI import line
        fastapi_import_pattern = r'from fastapi import ([^\\n]+)'
        match = re.search(fastapi_import_pattern, content)
        
        if match:
            # Add Response to FastAPI imports if not present
            imports = match.group(1)
            if 'Response' not in imports:
                new_imports = imports.rstrip() + ', Response'
                content = content.replace(match.group(0), f'from fastapi import {new_imports}')
        
        # Add monitoring imports after other imports
        monitoring_imports = f'''
# Monitoring imports
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import sys
from pathlib import Path

# Add shared utilities to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.append(str(shared_path))

try:
    from utils.metrics import MetricsCollector
    from utils.logging_config import setup_logging as enhanced_setup_logging
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Warning: Monitoring utilities not available")

# Initialize monitoring
if MONITORING_AVAILABLE:
    metrics_collector = MetricsCollector("{service_name}")
else:
    metrics_collector = None
'''
        
        # Find a good place to insert monitoring imports (after other imports)
        import_end_patterns = [
            r'from dotenv import load_dotenv\n',
            r'import uvicorn\n',
            r'from fastapi import [^\\n]+\n'
        ]
        
        insertion_point = 0
        for pattern in import_end_patterns:
            match = re.search(pattern, content)
            if match:
                insertion_point = max(insertion_point, match.end())
        
        if insertion_point > 0:
            content = content[:insertion_point] + monitoring_imports + content[insertion_point:]
        else:
            # Insert at the beginning if no good insertion point found
            content = monitoring_imports + content
        
        return content
    
    def add_metrics_endpoint(self, content: str) -> str:
        """Add /metrics endpoint to the service."""
        
        metrics_endpoint = '''
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if MONITORING_AVAILABLE:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    else:
        return {"error": "Monitoring not available", "status": "disabled"}
'''
        
        # Find a good place to insert the metrics endpoint
        # Look for existing endpoints or health check
        health_pattern = r'@app\.get\("/health"\)[^}]+}'
        root_pattern = r'@app\.get\("/"\)[^}]+}'
        
        insertion_point = None
        
        # Try to insert after health endpoint
        health_match = re.search(health_pattern, content, re.DOTALL)
        if health_match:
            insertion_point = health_match.end()
        else:
            # Try to insert after root endpoint
            root_match = re.search(root_pattern, content, re.DOTALL)
            if root_match:
                insertion_point = root_match.end()
        
        if insertion_point:
            content = content[:insertion_point] + metrics_endpoint + content[insertion_point:]
        else:
            # Insert before the main execution block
            main_pattern = r'if __name__ == "__main__":'
            main_match = re.search(main_pattern, content)
            if main_match:
                content = content[:main_match.start()] + metrics_endpoint + '\\n' + content[main_match.start():]
            else:
                # Append at the end
                content += metrics_endpoint
        
        return content
    
    def add_monitoring_middleware(self, content: str, service_name: str) -> str:
        """Add monitoring middleware to track requests."""
        
        middleware_code = f'''
# Monitoring middleware
@app.middleware("http")
async def monitoring_middleware(request, call_next):
    """Middleware to track HTTP requests and performance."""
    if MONITORING_AVAILABLE and metrics_collector:
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    else:
        return await call_next(request)
'''
        
        # Add time import if not present
        if 'import time' not in content:
            content = 'import time\\n' + content
        
        # Find app creation
        app_pattern = r'app = FastAPI\([^)]*\)'
        app_match = re.search(app_pattern, content, re.DOTALL)
        
        if app_match:
            # Insert middleware after app creation and CORS setup
            cors_pattern = r'app\.add_middleware\([^)]*CORSMiddleware[^}]*\}'
            cors_match = re.search(cors_pattern, content, re.DOTALL)
            
            if cors_match:
                insertion_point = cors_match.end()
            else:
                insertion_point = app_match.end()
            
            content = content[:insertion_point] + '\\n' + middleware_code + content[insertion_point:]
        
        return content
    
    def update_root_endpoint(self, content: str) -> str:
        """Update root endpoint to include monitoring status."""
        
        # Find root endpoint
        root_pattern = r'@app\.get\("/"\)[^{]*{[^}]*}'
        root_match = re.search(root_pattern, content, re.DOTALL)
        
        if root_match:
            # Add monitoring_enabled to the response
            root_content = root_match.group(0)
            if '"monitoring_enabled"' not in root_content:
                # Insert monitoring status into the return dict
                return_pattern = r'return\\s*{([^}]*)}'
                return_match = re.search(return_pattern, root_content)
                
                if return_match:
                    current_dict = return_match.group(1)
                    new_dict = current_dict.rstrip() + ',\\n        "monitoring_enabled": MONITORING_AVAILABLE'
                    new_root = root_content.replace(return_match.group(1), new_dict)
                    content = content.replace(root_content, new_root)
        
        return content
    
    def create_requirements_update(self, service_path: Path):
        """Update requirements.txt to include monitoring dependencies."""
        requirements_file = service_path / "requirements.txt"
        
        monitoring_deps = [
            "prometheus-client>=0.17.0",
            "structlog>=23.1.0"
        ]
        
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                current_deps = f.read()
            
            new_deps = []
            for dep in monitoring_deps:
                if dep.split('>=')[0] not in current_deps:
                    new_deps.append(dep)
            
            if new_deps:
                with open(requirements_file, 'a') as f:
                    f.write('\\n# Monitoring dependencies\\n')
                    for dep in new_deps:
                        f.write(f'{dep}\\n')
                
                print_status(f"Added monitoring dependencies to {service_path.name}/requirements.txt")
        else:
            # Create requirements.txt with monitoring dependencies
            with open(requirements_file, 'w') as f:
                f.write('# Monitoring dependencies\\n')
                for dep in monitoring_deps:
                    f.write(f'{dep}\\n')
            
            print_status(f"Created requirements.txt for {service_path.name}")
    
    def integrate_all_services(self):
        """Integrate monitoring into all AFAS services."""
        print_status("Starting AFAS monitoring integration...")
        
        # Check prerequisites
        if not self.check_shared_utils():
            print_error("Shared monitoring utilities not found. Please run setup-monitoring.sh first.")
            return False
        
        services = self.get_services()
        if not services:
            print_error("No services found in services directory")
            return False
        
        print_status(f"Found {len(services)} services to integrate")
        
        success_count = 0
        for service in services:
            print_status(f"Integrating monitoring into {service.name}...")
            
            try:
                if self.integrate_service(service):
                    self.create_requirements_update(service)
                    success_count += 1
                else:
                    print_warning(f"Failed to integrate {service.name}")
            except Exception as e:
                print_error(f"Error integrating {service.name}: {str(e)}")
        
        print_success(f"Successfully integrated monitoring into {success_count}/{len(services)} services")
        
        if success_count > 0:
            print_status("\\nNext steps:")
            print_status("1. Install monitoring dependencies: pip install -r requirements.txt")
            print_status("2. Start monitoring stack: cd infrastructure/monitoring && ./setup-monitoring.sh")
            print_status("3. Restart AFAS services: ./start-all.sh")
            print_status("4. Check metrics: http://localhost:9090/targets")
            print_status("5. View dashboards: http://localhost:3001")
        
        return success_count == len(services)

def main():
    """Main execution function."""
    print("🌾 AFAS Monitoring Integration")
    print("==============================")
    
    # Find services directory
    current_dir = Path(__file__).parent
    services_dir = current_dir.parent.parent / "services"
    
    if not services_dir.exists():
        print_error(f"Services directory not found: {services_dir}")
        sys.exit(1)
    
    # Create integrator and run
    integrator = MonitoringIntegrator(services_dir)
    
    if integrator.integrate_all_services():
        print_success("\\n🎉 Monitoring integration completed successfully!")
    else:
        print_error("\\n❌ Monitoring integration completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()