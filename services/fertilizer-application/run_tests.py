#!/usr/bin/env python3
"""
Test Runner for Comprehensive Fertilizer Application Testing Suite
TICKET-023_fertilizer-application-method-11.1

This script runs the comprehensive testing suite with proper configuration
and generates detailed reports for all test categories.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import argparse


class TestRunner:
    """Comprehensive test runner for fertilizer application service."""
    
    def __init__(self, project_root: str = None):
        """Initialize test runner."""
        self.project_root = project_root or os.path.dirname(os.path.abspath(__file__))
        self.test_dir = os.path.join(self.project_root, "tests")
        self.reports_dir = os.path.join(self.project_root, "test_reports")
        self.src_dir = os.path.join(self.project_root, "src")
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Test categories and their configurations
        self.test_categories = {
            "unit": {
                "description": "Unit tests for individual components",
                "pattern": "test_*.py",
                "exclude": ["test_comprehensive", "test_performance", "test_load", "test_stress"],
                "markers": ["unit", "fast"]
            },
            "integration": {
                "description": "Integration tests for service interactions",
                "pattern": "test_*integration*.py",
                "markers": ["integration"]
            },
            "performance": {
                "description": "Performance and load tests",
                "pattern": "test_performance*.py",
                "markers": ["performance", "load_test"]
            },
            "agricultural_validation": {
                "description": "Agricultural domain validation tests",
                "pattern": "test_agricultural*.py",
                "markers": ["agricultural_validation", "expert_review"]
            },
            "comprehensive": {
                "description": "Comprehensive end-to-end tests",
                "pattern": "test_comprehensive*.py",
                "markers": ["comprehensive"]
            }
        }
    
    def run_category_tests(self, category: str, verbose: bool = True) -> Dict[str, Any]:
        """Run tests for a specific category."""
        if category not in self.test_categories:
            raise ValueError(f"Unknown test category: {category}")
        
        config = self.test_categories[category]
        print(f"\n{'='*60}")
        print(f"Running {category.upper()} tests")
        print(f"Description: {config['description']}")
        print(f"{'='*60}")
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            self.test_dir,
            "-v" if verbose else "-q",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            f"--html={self.reports_dir}/{category}_report.html",
            f"--self-contained-html",
            f"--junitxml={self.reports_dir}/{category}_results.xml",
            f"--cov={self.src_dir}",
            f"--cov-report=html:{self.reports_dir}/{category}_coverage",
            f"--cov-report=xml:{self.reports_dir}/{category}_coverage.xml",
            f"--cov-report=term-missing"
        ]
        
        # Add markers if specified
        if "markers" in config:
            markers = " or ".join(config["markers"])
            cmd.extend(["-m", markers])
        
        # Add pattern if specified
        if "pattern" in config:
            cmd.extend(["-k", config["pattern"]])
        
        # Add excludes if specified
        if "exclude" in config:
            for exclude in config["exclude"]:
                cmd.extend(["--ignore", f"tests/{exclude}.py"])
        
        # Run the tests
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse results
            test_results = {
                "category": category,
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "total_tests": self._count_tests(result.stdout),
                "passed_tests": self._count_passed_tests(result.stdout),
                "failed_tests": self._count_failed_tests(result.stdout),
                "skipped_tests": self._count_skipped_tests(result.stdout)
            }
            
            print(f"Tests completed in {duration:.2f} seconds")
            print(f"Return code: {result.returncode}")
            print(f"Total tests: {test_results['total_tests']}")
            print(f"Passed: {test_results['passed_tests']}")
            print(f"Failed: {test_results['failed_tests']}")
            print(f"Skipped: {test_results['skipped_tests']}")
            
            if result.stderr:
                print(f"\nErrors/Warnings:\n{result.stderr}")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            return {
                "category": category,
                "success": False,
                "returncode": -1,
                "duration": 600,
                "stdout": "",
                "stderr": "Test execution timed out after 10 minutes",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0
            }
        except Exception as e:
            return {
                "category": category,
                "success": False,
                "returncode": -1,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0
            }
    
    def _count_tests(self, output: str) -> int:
        """Count total tests from pytest output."""
        lines = output.split('\n')
        for line in lines:
            if 'collected' in line and 'item' in line:
                try:
                    return int(line.split()[1])
                except (IndexError, ValueError):
                    pass
        return 0
    
    def _count_passed_tests(self, output: str) -> int:
        """Count passed tests from pytest output."""
        return output.count('PASSED')
    
    def _count_failed_tests(self, output: str) -> int:
        """Count failed tests from pytest output."""
        return output.count('FAILED')
    
    def _count_skipped_tests(self, output: str) -> int:
        """Count skipped tests from pytest output."""
        return output.count('SKIPPED')
    
    def run_all_tests(self, categories: List[str] = None, verbose: bool = True) -> Dict[str, Any]:
        """Run all test categories."""
        if categories is None:
            categories = list(self.test_categories.keys())
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE FERTILIZER APPLICATION TESTING SUITE")
        print("TICKET-023_fertilizer-application-method-11.1")
        print(f"{'='*80}")
        
        start_time = time.time()
        results = {}
        
        for category in categories:
            if category in self.test_categories:
                results[category] = self.run_category_tests(category, verbose)
            else:
                print(f"Warning: Unknown test category '{category}'")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate overall statistics
        total_tests = sum(r.get("total_tests", 0) for r in results.values())
        total_passed = sum(r.get("passed_tests", 0) for r in results.values())
        total_failed = sum(r.get("failed_tests", 0) for r in results.values())
        total_skipped = sum(r.get("skipped_tests", 0) for r in results.values())
        
        overall_success = all(r.get("success", False) for r in results.values())
        
        # Create comprehensive report
        comprehensive_report = {
            "start_time": start_time,
            "categories": results,
            "overall_success": overall_success,
            "total_tests": total_tests,
            "passed_tests": total_passed,
            "failed_tests": total_failed,
            "skipped_tests": total_skipped,
            "coverage_percentage": 0.0,  # Will be calculated separately
            "performance_metrics": {},
            "end_time": end_time,
            "duration": total_duration
        }
        
        # Save comprehensive report
        report_file = os.path.join(self.reports_dir, "comprehensive_report.json")
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*80}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total execution time: {total_duration:.2f} seconds")
        print(f"Overall success: {'✓ PASSED' if overall_success else '✗ FAILED'}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Skipped: {total_skipped}")
        print(f"Success rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        print(f"\nDetailed reports saved to: {self.reports_dir}")
        print(f"Comprehensive report: {report_file}")
        
        return comprehensive_report
    
    def run_coverage_analysis(self) -> float:
        """Run coverage analysis across all tests."""
        print(f"\n{'='*60}")
        print("RUNNING COVERAGE ANALYSIS")
        print(f"{'='*60}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            self.test_dir,
            "--cov={}".format(self.src_dir),
            "--cov-report=html:{}".format(os.path.join(self.reports_dir, "coverage")),
            "--cov-report=xml:{}".format(os.path.join(self.reports_dir, "coverage.xml")),
            "--cov-report=term-missing",
            "--cov-fail-under=80",
            "-q"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Extract coverage percentage from output
            coverage_percentage = 0.0
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line and '%' in line:
                    try:
                        coverage_percentage = float(line.split()[-1].replace('%', ''))
                        break
                    except (IndexError, ValueError):
                        pass
            
            print(f"Coverage analysis completed")
            print(f"Coverage percentage: {coverage_percentage:.1f}%")
            
            return coverage_percentage
            
        except Exception as e:
            print(f"Coverage analysis failed: {e}")
            return 0.0


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Comprehensive Fertilizer Application Test Runner")
    parser.add_argument("--categories", nargs="+", 
                       choices=["unit", "integration", "performance", "agricultural_validation", "comprehensive"],
                       help="Test categories to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run coverage analysis")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    runner = TestRunner(args.project_root)
    
    if args.coverage:
        coverage = runner.run_coverage_analysis()
        return 0 if coverage >= 80.0 else 1
    
    # Run tests
    report = runner.run_all_tests(args.categories, args.verbose)
    
    # Return appropriate exit code
    return 0 if report["overall_success"] else 1


if __name__ == "__main__":
    sys.exit(main())