#!/usr/bin/env python3
"""
Security Audit Script for CAAIN Soil Hub Crop Taxonomy Service
Performs comprehensive security checks and hardening validation
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml


class SecurityAuditor:
    """Comprehensive security audit for the crop taxonomy service."""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'critical_issues': [],
            'security_score': 0,
            'total_checks': 0
        }
        self.service_path = Path(__file__).parent
        self.src_path = self.service_path / "src"
        
    def check_dependencies_security(self) -> bool:
        """Check for known security vulnerabilities in dependencies."""
        print("🔍 Checking dependencies for security vulnerabilities...")
        
        try:
            # Check if safety is installed
            result = subprocess.run(['safety', 'check', '--json'], 
                                  capture_output=True, text=True, cwd=self.service_path)
            
            if result.returncode == 0:
                self.results['passed'].append("No known security vulnerabilities in dependencies")
                return True
            else:
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
                if vulnerabilities:
                    for vuln in vulnerabilities:
                        self.results['errors'].append(
                            f"Vulnerability in {vuln.get('package', 'unknown')}: {vuln.get('advisory', 'No details')}"
                        )
                    return False
                else:
                    self.results['passed'].append("Dependencies security check completed")
                    return True
                    
        except FileNotFoundError:
            self.results['warnings'].append("Safety tool not installed - install with: pip install safety")
            return False
        except Exception as e:
            self.results['errors'].append(f"Dependency security check failed: {e}")
            return False
    
    def check_secrets_exposure(self) -> bool:
        """Check for exposed secrets and sensitive information."""
        print("🔐 Checking for exposed secrets...")
        
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']',
            r'-----BEGIN PRIVATE KEY-----',
            r'-----BEGIN RSA PRIVATE KEY-----',
            r'sk_live_[a-zA-Z0-9]+',
            r'AKIA[0-9A-Z]{16}',
            r'[0-9a-f]{32}',
        ]
        
        exposed_secrets = []
        
        # Check Python files
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in sensitive_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        exposed_secrets.append(f"{py_file}: {matches}")
                        
            except Exception as e:
                self.results['warnings'].append(f"Could not check {py_file}: {e}")
        
        if exposed_secrets:
            for secret in exposed_secrets:
                self.results['critical_issues'].append(f"Potential secret exposure: {secret}")
            return False
        else:
            self.results['passed'].append("No exposed secrets found")
            return True
    
    def check_file_permissions(self) -> bool:
        """Check file permissions for security."""
        print("📁 Checking file permissions...")
        
        insecure_files = []
        
        # Check for world-writable files
        for file_path in self.src_path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                if stat.st_mode & 0o002:  # World writable
                    insecure_files.append(str(file_path))
        
        if insecure_files:
            for file_path in insecure_files:
                self.results['warnings'].append(f"World-writable file: {file_path}")
            return False
        else:
            self.results['passed'].append("File permissions are secure")
            return True
    
    def check_input_validation(self) -> bool:
        """Check for proper input validation."""
        print("✅ Checking input validation...")
        
        validation_issues = []
        
        # Check for SQL injection vulnerabilities
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for potential SQL injection patterns
                if 'f"SELECT' in content or 'f"INSERT' in content or 'f"UPDATE' in content:
                    validation_issues.append(f"{py_file}: Potential SQL injection vulnerability")
                    
                # Check for unsanitized user input
                if 'request.form' in content and 'escape' not in content:
                    validation_issues.append(f"{py_file}: Potential XSS vulnerability")
                    
            except Exception as e:
                self.results['warnings'].append(f"Could not check {py_file}: {e}")
        
        if validation_issues:
            for issue in validation_issues:
                self.results['warnings'].append(issue)
            return False
        else:
            self.results['passed'].append("Input validation appears secure")
            return True
    
    def check_authentication_security(self) -> bool:
        """Check authentication and authorization security."""
        print("🔑 Checking authentication security...")
        
        auth_issues = []
        
        # Check for hardcoded credentials
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for hardcoded passwords or tokens
                if 'password="' in content or 'token="' in content:
                    auth_issues.append(f"{py_file}: Potential hardcoded credentials")
                    
            except Exception as e:
                self.results['warnings'].append(f"Could not check {py_file}: {e}")
        
        # Check for proper session management
        session_files = list(self.src_path.rglob("*session*"))
        if not session_files:
            auth_issues.append("No session management files found")
        
        if auth_issues:
            for issue in auth_issues:
                self.results['warnings'].append(issue)
            return False
        else:
            self.results['passed'].append("Authentication security appears adequate")
            return True
    
    def check_https_configuration(self) -> bool:
        """Check HTTPS and SSL configuration."""
        print("🔒 Checking HTTPS configuration...")
        
        ssl_issues = []
        
        # Check for HTTPS enforcement
        nginx_conf = self.service_path / "nginx.conf"
        if nginx_conf.exists():
            with open(nginx_conf, 'r') as f:
                content = f.read()
                
            if 'ssl_certificate' not in content:
                ssl_issues.append("SSL certificate not configured in nginx.conf")
                
            if 'Strict-Transport-Security' not in content:
                ssl_issues.append("HSTS headers not configured")
        else:
            ssl_issues.append("nginx.conf not found")
        
        if ssl_issues:
            for issue in ssl_issues:
                self.results['warnings'].append(issue)
            return False
        else:
            self.results['passed'].append("HTTPS configuration appears secure")
            return True
    
    def check_cors_configuration(self) -> bool:
        """Check CORS configuration for security."""
        print("🌐 Checking CORS configuration...")
        
        cors_issues = []
        
        # Check main.py for CORS configuration
        main_py = self.src_path / "main.py"
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
                
            if 'allow_origins=["*"]' in content:
                cors_issues.append("CORS allows all origins (*) - should be restricted in production")
                
            if 'allow_credentials=True' in content and 'allow_origins=["*"]' in content:
                cors_issues.append("CORS allows credentials with wildcard origins - security risk")
        
        if cors_issues:
            for issue in cors_issues:
                self.results['critical_issues'].append(issue)
            return False
        else:
            self.results['passed'].append("CORS configuration appears secure")
            return True
    
    def check_logging_security(self) -> bool:
        """Check logging configuration for security."""
        print("📝 Checking logging security...")
        
        logging_issues = []
        
        # Check for sensitive data in logs
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for potential sensitive data logging
                if 'logger.info(password' in content or 'logger.debug(token' in content:
                    logging_issues.append(f"{py_file}: Potential sensitive data logging")
                    
            except Exception as e:
                self.results['warnings'].append(f"Could not check {py_file}: {e}")
        
        if logging_issues:
            for issue in logging_issues:
                self.results['warnings'].append(issue)
            return False
        else:
            self.results['passed'].append("Logging security appears adequate")
            return True
    
    def check_docker_security(self) -> bool:
        """Check Docker configuration for security."""
        print("🐳 Checking Docker security...")
        
        docker_issues = []
        
        # Check Dockerfile
        dockerfile = self.service_path / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile, 'r') as f:
                content = f.read()
                
            if 'USER root' in content and 'USER appuser' not in content:
                docker_issues.append("Dockerfile runs as root - security risk")
                
            if 'COPY . .' in content:
                docker_issues.append("Dockerfile copies all files - may include sensitive data")
                
            if 'RUN pip install --no-cache-dir -r requirements.txt' not in content:
                docker_issues.append("Dockerfile should use --no-cache-dir for pip install")
        else:
            docker_issues.append("Dockerfile not found")
        
        # Check docker-compose.yml
        compose_file = self.service_path / "docker-compose.yml"
        if compose_file.exists():
            with open(compose_file, 'r') as f:
                content = f.read()
                
            if 'privileged: true' in content:
                docker_issues.append("Docker compose uses privileged mode - security risk")
                
            if 'volumes:' in content and 'secrets:' not in content:
                docker_issues.append("Consider using Docker secrets for sensitive data")
        
        if docker_issues:
            for issue in docker_issues:
                self.results['warnings'].append(issue)
            return False
        else:
            self.results['passed'].append("Docker security configuration appears adequate")
            return True
    
    def calculate_security_score(self) -> int:
        """Calculate overall security score."""
        total_checks = self.results['total_checks']
        if total_checks == 0:
            return 0
            
        passed = len(self.results['passed'])
        warnings = len(self.results['warnings'])
        errors = len(self.results['errors'])
        critical = len(self.results['critical_issues'])
        
        # Weight different types of issues
        score = (passed * 10 - warnings * 5 - errors * 10 - critical * 20) / total_checks
        return max(0, min(100, score))
    
    def run_security_audit(self) -> Dict[str, Any]:
        """Run complete security audit."""
        print("🔒 Starting comprehensive security audit...")
        print("=" * 60)
        
        checks = [
            self.check_dependencies_security,
            self.check_secrets_exposure,
            self.check_file_permissions,
            self.check_input_validation,
            self.check_authentication_security,
            self.check_https_configuration,
            self.check_cors_configuration,
            self.check_logging_security,
            self.check_docker_security
        ]
        
        for check in checks:
            self.results['total_checks'] += 1
            try:
                check()
            except Exception as e:
                self.results['errors'].append(f"Security check failed: {e}")
        
        # Calculate security score
        self.results['security_score'] = self.calculate_security_score()
        
        self._print_results()
        return self.results
    
    def _print_results(self):
        """Print security audit results."""
        print("\n" + "=" * 60)
        print("🔒 SECURITY AUDIT RESULTS")
        print("=" * 60)
        
        print(f"Total checks: {self.results['total_checks']}")
        print(f"Security Score: {self.results['security_score']:.1f}/100")
        print(f"Passed: {len(self.results['passed'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        print(f"Errors: {len(self.results['errors'])}")
        print(f"Critical Issues: {len(self.results['critical_issues'])}")
        
        if self.results['passed']:
            print("\n✅ PASSED:")
            for item in self.results['passed']:
                print(f"  • {item}")
        
        if self.results['warnings']:
            print("\n⚠️  WARNINGS:")
            for item in self.results['warnings']:
                print(f"  • {item}")
        
        if self.results['errors']:
            print("\n❌ ERRORS:")
            for item in self.results['errors']:
                print(f"  • {item}")
        
        if self.results['critical_issues']:
            print("\n🚨 CRITICAL ISSUES:")
            for item in self.results['critical_issues']:
                print(f"  • {item}")
        
        # Security recommendations
        print("\n📋 SECURITY RECOMMENDATIONS:")
        if self.results['security_score'] < 70:
            print("  • Address critical issues before production deployment")
            print("  • Implement additional security hardening measures")
            print("  • Consider professional security audit")
        elif self.results['security_score'] < 85:
            print("  • Address warnings and errors")
            print("  • Implement monitoring and alerting")
            print("  • Regular security updates recommended")
        else:
            print("  • Security posture is good")
            print("  • Continue regular security monitoring")
            print("  • Maintain security best practices")
        
        # Save results
        with open('security-audit-report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: security-audit-report.json")


def main():
    """Main security audit function."""
    auditor = SecurityAuditor()
    results = auditor.run_security_audit()
    
    # Exit with error code if critical issues found
    if results['critical_issues'] or results['security_score'] < 50:
        print("\n❌ Security audit FAILED - Critical issues must be resolved!")
        sys.exit(1)
    elif results['security_score'] < 70:
        print("\n⚠️  Security audit WARNING - Issues should be addressed!")
        sys.exit(2)
    else:
        print("\n✅ Security audit PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()