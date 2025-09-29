#!/usr/bin/env python3
"""
CAAIN Soil Hub - Production Deployment Script
Comprehensive production deployment automation for crop taxonomy service
"""

import os
import sys
import json
import yaml
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests


class ProductionDeployment:
    """Comprehensive production deployment automation."""
    
    def __init__(self, config_path: str = "production-config.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.service_path = Path("services/crop-taxonomy")
        self.deployment_log = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load production deployment configuration."""
        default_config = {
            'deployment': {
                'environment': 'production',
                'version': '1.0.0',
                'rollback_enabled': True,
                'health_check_timeout': 300
            },
            'services': {
                'crop_taxonomy': {
                    'port': 8000,
                    'replicas': 2,
                    'health_endpoint': '/api/v1/health'
                },
                'postgres': {
                    'port': 5432,
                    'database': 'crop_taxonomy'
                },
                'redis': {
                    'port': 6379
                },
                'nginx': {
                    'port': 80,
                    'ssl_port': 443
                }
            },
            'monitoring': {
                'prometheus_port': 9090,
                'grafana_port': 3000,
                'alertmanager_port': 9093
            },
            'backup': {
                'enabled': True,
                'retention_days': 30
            },
            'notifications': {
                'webhook_url': None,
                'email': None
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> bool:
        """Run shell command with error handling."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.service_path,
                capture_output=True,
                text=True,
                check=True
            )
            self.log(f"Command successful: {' '.join(command)}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(command)} - {e.stderr}", "ERROR")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites."""
        self.log("Checking deployment prerequisites...")
        
        prerequisites = [
            ("Docker", ["docker", "--version"]),
            ("Docker Compose", ["docker-compose", "--version"]),
            ("Python", ["python", "--version"]),
            ("Git", ["git", "--version"])
        ]
        
        for name, command in prerequisites:
            if not self.run_command(command):
                self.log(f"Prerequisite check failed: {name}", "ERROR")
                return False
            self.log(f"Prerequisite check passed: {name}")
        
        # Check required files
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".env.production",
            "nginx.conf"
        ]
        
        for file_name in required_files:
            file_path = self.service_path / file_name
            if not file_path.exists():
                self.log(f"Required file missing: {file_name}", "ERROR")
                return False
            self.log(f"Required file found: {file_name}")
        
        return True
    
    def run_security_audit(self) -> bool:
        """Run security audit before deployment."""
        self.log("Running security audit...")
        
        security_script = self.service_path / "security-audit.py"
        if security_script.exists():
            if self.run_command(["python", "security-audit.py"]):
                self.log("Security audit passed")
                return True
            else:
                self.log("Security audit failed", "ERROR")
                return False
        else:
            self.log("Security audit script not found", "WARNING")
            return True
    
    def run_tests(self) -> bool:
        """Run comprehensive tests."""
        self.log("Running comprehensive tests...")
        
        # Run unit tests
        if not self.run_command(["python", "-m", "pytest", "tests/", "-v", "--tb=short"]):
            self.log("Unit tests failed", "ERROR")
            return False
        
        # Run agricultural validation tests
        agricultural_tests = self.service_path / "tests" / "agricultural"
        if agricultural_tests.exists():
            if not self.run_command(["python", "-m", "pytest", "tests/agricultural/", "-v"]):
                self.log("Agricultural validation tests failed", "ERROR")
                return False
        
        self.log("All tests passed")
        return True
    
    def build_docker_images(self) -> bool:
        """Build Docker images for production."""
        self.log("Building Docker images...")
        
        # Build main service image
        if not self.run_command(["docker-compose", "build", "crop-taxonomy"]):
            self.log("Failed to build crop-taxonomy image", "ERROR")
            return False
        
        # Build monitoring images
        monitoring_compose = self.service_path / "docker-compose.monitoring.yml"
        if monitoring_compose.exists():
            if not self.run_command(["docker-compose", "-f", "docker-compose.monitoring.yml", "build"]):
                self.log("Failed to build monitoring images", "ERROR")
                return False
        
        self.log("Docker images built successfully")
        return True
    
    def setup_monitoring(self) -> bool:
        """Set up monitoring infrastructure."""
        self.log("Setting up monitoring infrastructure...")
        
        monitoring_script = self.service_path / "monitoring-setup.py"
        if monitoring_script.exists():
            if self.run_command(["python", "monitoring-setup.py"]):
                self.log("Monitoring setup completed")
                return True
            else:
                self.log("Monitoring setup failed", "ERROR")
                return False
        else:
            self.log("Monitoring setup script not found", "WARNING")
            return True
    
    def deploy_services(self) -> bool:
        """Deploy services to production."""
        self.log("Deploying services...")
        
        # Stop existing services
        self.run_command(["docker-compose", "down"])
        
        # Start services
        if not self.run_command(["docker-compose", "up", "-d"]):
            self.log("Failed to start services", "ERROR")
            return False
        
        # Start monitoring services
        monitoring_compose = self.service_path / "docker-compose.monitoring.yml"
        if monitoring_compose.exists():
            if not self.run_command(["docker-compose", "-f", "docker-compose.monitoring.yml", "up", "-d"]):
                self.log("Failed to start monitoring services", "ERROR")
                return False
        
        self.log("Services deployed successfully")
        return True
    
    def wait_for_services(self) -> bool:
        """Wait for services to be ready."""
        self.log("Waiting for services to be ready...")
        
        timeout = self.config['deployment']['health_check_timeout']
        start_time = time.time()
        
        services = [
            ("crop-taxonomy", "http://localhost:8000/api/v1/health"),
            ("postgres", "http://localhost:5432"),
            ("redis", "http://localhost:6379")
        ]
        
        for service_name, health_url in services:
            self.log(f"Checking {service_name} health...")
            
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        self.log(f"{service_name} is healthy")
                        break
                except requests.RequestException:
                    pass
                
                time.sleep(5)
            else:
                self.log(f"{service_name} health check timeout", "ERROR")
                return False
        
        self.log("All services are ready")
        return True
    
    def run_database_migrations(self) -> bool:
        """Run database migrations."""
        self.log("Running database migrations...")
        
        # Wait for database to be ready
        time.sleep(10)
        
        # Run migrations
        if not self.run_command(["docker-compose", "exec", "-T", "crop-taxonomy", "python", "-m", "alembic", "upgrade", "head"]):
            self.log("Database migrations failed", "ERROR")
            return False
        
        self.log("Database migrations completed")
        return True
    
    def setup_backup_system(self) -> bool:
        """Set up backup system."""
        self.log("Setting up backup system...")
        
        backup_script = self.service_path / "backup-system.py"
        if backup_script.exists():
            # Create initial backup
            if self.run_command(["python", "backup-system.py", "backup"]):
                self.log("Initial backup created")
                return True
            else:
                self.log("Initial backup failed", "ERROR")
                return False
        else:
            self.log("Backup system script not found", "WARNING")
            return True
    
    def run_smoke_tests(self) -> bool:
        """Run smoke tests after deployment."""
        self.log("Running smoke tests...")
        
        smoke_tests = [
            ("Health Check", "http://localhost:8000/api/v1/health"),
            ("Service Info", "http://localhost:8000/api/v1/info"),
            ("Taxonomy Endpoint", "http://localhost:8000/api/v1/taxonomy/crops"),
            ("Search Endpoint", "http://localhost:8000/api/v1/search/crops")
        ]
        
        for test_name, url in smoke_tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"Smoke test passed: {test_name}")
                else:
                    self.log(f"Smoke test failed: {test_name} - Status: {response.status_code}", "ERROR")
                    return False
            except requests.RequestException as e:
                self.log(f"Smoke test failed: {test_name} - {e}", "ERROR")
                return False
        
        self.log("All smoke tests passed")
        return True
    
    def send_deployment_notification(self, success: bool) -> bool:
        """Send deployment notification."""
        if not self.config['notifications']['webhook_url']:
            return True
        
        try:
            message = "Production deployment completed successfully" if success else "Production deployment failed"
            payload = {
                "text": message,
                "status": "success" if success else "error",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": self.config['deployment']['version']
            }
            
            response = requests.post(
                self.config['notifications']['webhook_url'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("Deployment notification sent")
                return True
            else:
                self.log(f"Failed to send notification: {response.status_code}", "WARNING")
                return False
                
        except requests.RequestException as e:
            self.log(f"Notification failed: {e}", "WARNING")
            return False
    
    def save_deployment_log(self) -> None:
        """Save deployment log to file."""
        log_file = Path("deployment-log.json")
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": self.config['deployment']['version'],
            "environment": self.config['deployment']['environment'],
            "log": self.deployment_log
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.log(f"Deployment log saved to: {log_file}")
    
    def deploy(self) -> bool:
        """Run complete production deployment."""
        self.log("Starting production deployment...")
        self.log("=" * 60)
        
        deployment_steps = [
            ("Check Prerequisites", self.check_prerequisites),
            ("Run Security Audit", self.run_security_audit),
            ("Run Tests", self.run_tests),
            ("Build Docker Images", self.build_docker_images),
            ("Setup Monitoring", self.setup_monitoring),
            ("Deploy Services", self.deploy_services),
            ("Wait for Services", self.wait_for_services),
            ("Run Database Migrations", self.run_database_migrations),
            ("Setup Backup System", self.setup_backup_system),
            ("Run Smoke Tests", self.run_smoke_tests)
        ]
        
        for step_name, step_function in deployment_steps:
            self.log(f"Executing: {step_name}")
            
            if not step_function():
                self.log(f"Deployment failed at step: {step_name}", "ERROR")
                self.send_deployment_notification(False)
                self.save_deployment_log()
                return False
            
            self.log(f"Step completed: {step_name}")
        
        # Deployment successful
        self.log("=" * 60)
        self.log("Production deployment completed successfully!")
        self.log("=" * 60)
        
        self.send_deployment_notification(True)
        self.save_deployment_log()
        
        # Print deployment summary
        self.print_deployment_summary()
        
        return True
    
    def print_deployment_summary(self) -> None:
        """Print deployment summary."""
        print("\n" + "=" * 60)
        print("🚀 DEPLOYMENT SUMMARY")
        print("=" * 60)
        print(f"Version: {self.config['deployment']['version']}")
        print(f"Environment: {self.config['deployment']['environment']}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Service Status:")
        print(f"  • Crop Taxonomy Service: http://localhost:8000")
        print(f"  • API Documentation: http://localhost:8000/docs")
        print(f"  • Health Check: http://localhost:8000/api/v1/health")
        print(f"  • Prometheus: http://localhost:9090")
        print(f"  • Grafana: http://localhost:3000")
        print("\n🔧 Next Steps:")
        print("  1. Monitor service health and performance")
        print("  2. Verify all endpoints are working correctly")
        print("  3. Check monitoring dashboards")
        print("  4. Test backup and recovery procedures")
        print("  5. Update DNS and SSL certificates for production domain")
        print("\n📚 Documentation:")
        print("  • User Guide: docs/user-guide.md")
        print("  • Administrator Guide: docs/administrator-guide.md")
        print("  • Launch Plan: docs/launch-plan.md")
        print("=" * 60)


def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CAAIN Soil Hub Production Deployment')
    parser.add_argument('--config', default='production-config.yml',
                       help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without actual deployment')
    
    args = parser.parse_args()
    
    deployment = ProductionDeployment(args.config)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual deployment will be performed")
        print("=" * 60)
        
        # Run checks only
        checks = [
            ("Check Prerequisites", deployment.check_prerequisites),
            ("Run Security Audit", deployment.run_security_audit),
            ("Run Tests", deployment.run_tests),
        ]
        
        for check_name, check_function in checks:
            print(f"Executing: {check_name}")
            if check_function():
                print(f"✅ {check_name} passed")
            else:
                print(f"❌ {check_name} failed")
                sys.exit(1)
        
        print("\n✅ All checks passed - Ready for deployment!")
        sys.exit(0)
    
    # Run actual deployment
    success = deployment.deploy()
    
    if not success:
        print("\n❌ Production deployment failed!")
        sys.exit(1)
    else:
        print("\n✅ Production deployment successful!")
        sys.exit(0)


if __name__ == "__main__":
    main()