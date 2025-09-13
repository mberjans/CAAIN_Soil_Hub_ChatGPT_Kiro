#!/usr/bin/env python3
"""
Deployment Readiness Check Script

This script validates that the AFAS system is ready for deployment
by checking all critical components and configurations.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess

class DeploymentReadinessChecker:
    """Checks if the system is ready for deployment."""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'total_checks': 0,
            'deployment_ready': False
        }
        
    def check_service_structure(self) -> bool:
        """Check that all required services exist with proper structure."""
        print("Checking service structure...")
        
        required_services = [
            'question-router',
            'recommendation-engine',
            'ai-agent',
            'data-integration',
            'image-analysis',
            'user-management',
            'frontend'
        ]
        
        services_dir = Path("services")
        if not services_dir.exists():
            self.results['errors'].append("Services directory not found")
            return False
        
        missing_services = []
        for service in required_services:
            service_path = services_dir / service
            if not service_path.exists():
                missing_services.append(service)
                continue
                
            # Check for required files
            required_files = ['src/main.py', 'requirements.txt']
            for req_file in required_files:
                if not (service_path / req_file).exists():
                    self.results['warnings'].append(
                        f"Service {service} missing {req_file}"
                    )
        
        if missing_services:
            self.results['errors'].append(
                f"Missing services: {', '.join(missing_services)}"
            )
            return False
        
        self.results['passed'].append("All required services present")
        return True
    
    def check_configuration_files(self) -> bool:
        """Check that configuration files are present and valid."""
        print("Checking configuration files...")
        
        config_files = [
            '.env.example',
            'README.md',
            '.gitignore'
        ]
        
        missing_configs = []
        for config_file in config_files:
            if not Path(config_file).exists():
                missing_configs.append(config_file)
        
        if missing_configs:
            self.results['warnings'].append(
                f"Missing configuration files: {', '.join(missing_configs)}"
            )
        
        # Check for sensitive files that shouldn't be committed
        sensitive_files = ['.env', 'secrets.json', 'api_keys.txt']
        committed_sensitive = []
        for sensitive_file in sensitive_files:
            if Path(sensitive_file).exists():
                committed_sensitive.append(sensitive_file)
        
        if committed_sensitive:
            self.results['errors'].append(
                f"Sensitive files found in repository: {', '.join(committed_sensitive)}"
            )
            return False
        
        self.results['passed'].append("Configuration files validated")
        return True
    
    def check_dependencies(self) -> bool:
        """Check that all dependencies are properly specified."""
        print("Checking dependencies...")
        
        services_dir = Path("services")
        dependency_issues = []
        
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir():
                requirements_file = service_dir / "requirements.txt"
                if requirements_file.exists():
                    try:
                        with open(requirements_file, 'r') as f:
                            content = f.read()
                            
                        # Check for pinned versions
                        lines = content.strip().split('\n')
                        unpinned = []
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '==' not in line and '>=' not in line:
                                    unpinned.append(line)
                        
                        if unpinned:
                            dependency_issues.append(
                                f"{service_dir.name}: unpinned dependencies {unpinned}"
                            )
                            
                    except Exception as e:
                        dependency_issues.append(
                            f"{service_dir.name}: error reading requirements.txt - {e}"
                        )
        
        if dependency_issues:
            self.results['warnings'].extend(dependency_issues)
        
        self.results['passed'].append("Dependencies checked")
        return True
    
    def check_test_coverage(self) -> bool:
        """Check that adequate test coverage exists."""
        print("Checking test coverage...")
        
        tests_dir = Path("tests")
        if not tests_dir.exists():
            self.results['errors'].append("Tests directory not found")
            return False
        
        required_test_dirs = ['unit', 'integration', 'agricultural']
        missing_test_dirs = []
        
        for test_dir in required_test_dirs:
            if not (tests_dir / test_dir).exists():
                missing_test_dirs.append(test_dir)
        
        if missing_test_dirs:
            self.results['warnings'].append(
                f"Missing test directories: {', '.join(missing_test_dirs)}"
            )
        
        # Check for agricultural test files
        agricultural_tests_dir = tests_dir / "agricultural"
        if agricultural_tests_dir.exists():
            agricultural_test_files = list(agricultural_tests_dir.glob("test_*.py"))
            if len(agricultural_test_files) < 3:
                self.results['warnings'].append(
                    "Insufficient agricultural test coverage"
                )
        
        self.results['passed'].append("Test structure validated")
        return True
    
    def check_documentation(self) -> bool:
        """Check that required documentation exists."""
        print("Checking documentation...")
        
        required_docs = [
            'README.md',
            '.kiro/specs/technical-architecture.md',
            '.kiro/specs/implementation-plan.md'
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.results['warnings'].append(
                f"Missing documentation: {', '.join(missing_docs)}"
            )
        
        # Check README content
        readme_path = Path("README.md")
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            
            required_sections = [
                'Getting Started',
                'Installation',
                'Usage'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section.lower() not in readme_content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                self.results['warnings'].append(
                    f"README missing sections: {', '.join(missing_sections)}"
                )
        
        self.results['passed'].append("Documentation checked")
        return True
    
    def check_security_configuration(self) -> bool:
        """Check security configuration."""
        print("Checking security configuration...")
        
        # Check for security-related files
        security_files = [
            '.github/workflows/security.yml',
            'scripts/validate_agricultural_logic.py'
        ]
        
        missing_security = []
        for sec_file in security_files:
            if not Path(sec_file).exists():
                missing_security.append(sec_file)
        
        if missing_security:
            self.results['warnings'].append(
                f"Missing security files: {', '.join(missing_security)}"
            )
        
        # Check for common security issues
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            security_patterns = ['.env', '*.key', 'secrets/', 'credentials.json']
            missing_patterns = []
            
            for pattern in security_patterns:
                if pattern not in gitignore_content:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                self.results['warnings'].append(
                    f"Gitignore missing security patterns: {', '.join(missing_patterns)}"
                )
        
        self.results['passed'].append("Security configuration checked")
        return True
    
    def check_agricultural_validation(self) -> bool:
        """Check that agricultural validation is in place."""
        print("Checking agricultural validation...")
        
        # Check for agricultural validation workflow
        ag_workflow = Path(".github/workflows/agricultural-validation.yml")
        if not ag_workflow.exists():
            self.results['errors'].append(
                "Agricultural validation workflow not found"
            )
            return False
        
        # Check for agricultural test files
        ag_tests_dir = Path("tests/agricultural")
        if ag_tests_dir.exists():
            ag_test_files = list(ag_tests_dir.glob("test_*.py"))
            if len(ag_test_files) == 0:
                self.results['warnings'].append(
                    "No agricultural test files found"
                )
        else:
            self.results['warnings'].append(
                "Agricultural tests directory not found"
            )
        
        # Check for agricultural validation script
        ag_validation_script = Path("scripts/validate_agricultural_logic.py")
        if not ag_validation_script.exists():
            self.results['warnings'].append(
                "Agricultural validation script not found"
            )
        
        self.results['passed'].append("Agricultural validation checked")
        return True
    
    def run_all_checks(self) -> bool:
        """Run all deployment readiness checks."""
        print("Running deployment readiness checks...")
        print("=" * 50)
        
        checks = [
            self.check_service_structure,
            self.check_configuration_files,
            self.check_dependencies,
            self.check_test_coverage,
            self.check_documentation,
            self.check_security_configuration,
            self.check_agricultural_validation
        ]
        
        all_passed = True
        critical_failed = False
        
        for check in checks:
            self.results['total_checks'] += 1
            if not check():
                all_passed = False
                # Some checks are critical for deployment
                if check in [self.check_service_structure, self.check_agricultural_validation]:
                    critical_failed = True
        
        # Determine deployment readiness
        self.results['deployment_ready'] = all_passed and not critical_failed
        
        self._print_results()
        return self.results['deployment_ready']
    
    def _print_results(self):
        """Print deployment readiness results."""
        print("\n" + "=" * 50)
        print("DEPLOYMENT READINESS RESULTS")
        print("=" * 50)
        
        print(f"Total checks: {self.results['total_checks']}")
        print(f"Passed: {len(self.results['passed'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        print(f"Errors: {len(self.results['errors'])}")
        
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
        
        print(f"\n🚀 DEPLOYMENT READY: {'YES' if self.results['deployment_ready'] else 'NO'}")
        
        # Save results to file
        with open('deployment-readiness-report.json', 'w') as f:
            json.dump(self.results, f, indent=2)

def main():
    """Main deployment readiness check function."""
    checker = DeploymentReadinessChecker()
    
    ready = checker.run_all_checks()
    
    if not ready:
        print("\n❌ System is NOT ready for deployment!")
        sys.exit(1)
    else:
        print("\n✅ System is ready for deployment!")
        sys.exit(0)

if __name__ == "__main__":
    main()