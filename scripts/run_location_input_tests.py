#!/usr/bin/env python3
"""
Location Input Test Runner
TICKET-008_farm-location-input-15.1 - Automated test runner for comprehensive location input testing

This script provides a comprehensive test runner for the location input testing suite
with support for different test categories, performance monitoring, and reporting.
"""

import argparse
import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LocationInputTestRunner:
    """Comprehensive test runner for location input functionality"""
    
    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Test categories
        self.test_categories = {
            "unit": "Unit tests for individual components",
            "integration": "Integration tests with external services",
            "performance": "Performance and load tests",
            "geographic": "Geographic accuracy tests",
            "comprehensive": "Comprehensive test suite",
            "mobile": "Mobile-specific tests",
            "regression": "Regression tests",
            "all": "All test categories"
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            "max_response_time_ms": 2000,
            "min_throughput_ops_per_sec": 100,
            "max_memory_usage_mb": 500,
            "max_cpu_usage_percent": 80,
            "max_error_rate_percent": 5,
            "concurrent_users_target": 1000
        }
    
    def setup_environment(self) -> bool:
        """Set up test environment"""
        try:
            # Set environment variables
            os.environ.update({
                'TESTING': 'true',
                'LOG_LEVEL': 'INFO',
                'PYTHONPATH': str(project_root)
            })
            
            # Check if test directory exists
            if not self.test_dir.exists():
                logger.error(f"Test directory not found: {self.test_dir}")
                return False
            
            # Check for required test files
            required_files = [
                "comprehensive_location_input_test_suite.py",
                "test_location_input_performance.py",
                "test_location_input_geographic_accuracy.py",
                "test_location_input_integration.py",
                "conftest.py"
            ]
            
            missing_files = []
            for file in required_files:
                if not (self.test_dir / file).exists():
                    missing_files.append(file)
            
            if missing_files:
                logger.error(f"Missing required test files: {missing_files}")
                return False
            
            logger.info("Test environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def run_pytest_command(self, test_path: str, category: str, **kwargs) -> Dict[str, Any]:
        """Run pytest command and return results"""
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        # Add category-specific options
        if category == "performance":
            cmd.extend(["--maxfail=3", "--timeout=300"])
        elif category == "integration":
            cmd.extend(["--maxfail=5", "--timeout=600"])
        elif category == "comprehensive":
            cmd.extend(["--maxfail=10", "--timeout=900"])
        
        # Add coverage if requested
        if kwargs.get("coverage", False):
            cmd.extend([
                "--cov=services/location-validation",
                "--cov-report=xml",
                "--cov-report=html"
            ])
        
        # Add parallel execution if requested
        if kwargs.get("parallel", False):
            cmd.extend(["-n", "auto"])
        
        # Add output file
        output_file = f"test-results-{category}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        cmd.extend(["--junitxml", output_file])
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 1800)  # 30 minutes default
            )
            end_time = time.time()
            
            return {
                "category": category,
                "command": " ".join(cmd),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": end_time - start_time,
                "output_file": output_file,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Test timeout for category: {category}")
            return {
                "category": category,
                "command": " ".join(cmd),
                "returncode": -1,
                "stdout": "",
                "stderr": "Test timeout",
                "duration": kwargs.get("timeout", 1800),
                "output_file": output_file,
                "success": False,
                "timeout": True
            }
        except Exception as e:
            logger.error(f"Error running tests for category {category}: {e}")
            return {
                "category": category,
                "command": " ".join(cmd),
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0,
                "output_file": output_file,
                "success": False,
                "error": str(e)
            }
    
    def run_unit_tests(self, **kwargs) -> Dict[str, Any]:
        """Run unit tests"""
        logger.info("Running unit tests...")
        return self.run_pytest_command(
            str(self.test_dir / "comprehensive_location_input_test_suite.py"),
            "unit",
            coverage=kwargs.get("coverage", True),
            parallel=kwargs.get("parallel", True)
        )
    
    def run_integration_tests(self, **kwargs) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("Running integration tests...")
        return self.run_pytest_command(
            str(self.test_dir / "test_location_input_integration.py"),
            "integration",
            coverage=kwargs.get("coverage", True),
            timeout=600
        )
    
    def run_performance_tests(self, **kwargs) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("Running performance tests...")
        return self.run_pytest_command(
            str(self.test_dir / "test_location_input_performance.py"),
            "performance",
            timeout=900
        )
    
    def run_geographic_tests(self, **kwargs) -> Dict[str, Any]:
        """Run geographic accuracy tests"""
        logger.info("Running geographic accuracy tests...")
        return self.run_pytest_command(
            str(self.test_dir / "test_location_input_geographic_accuracy.py"),
            "geographic",
            timeout=600
        )
    
    def run_comprehensive_tests(self, **kwargs) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("Running comprehensive test suite...")
        return self.run_pytest_command(
            str(self.test_dir / "comprehensive_location_input_test_suite.py"),
            "comprehensive",
            coverage=kwargs.get("coverage", True),
            timeout=1200
        )
    
    def run_mobile_tests(self, **kwargs) -> Dict[str, Any]:
        """Run mobile-specific tests"""
        logger.info("Running mobile tests...")
        return self.run_pytest_command(
            str(self.test_dir),
            "mobile",
            extra_args=["-k", "mobile"]
        )
    
    def run_regression_tests(self, **kwargs) -> Dict[str, Any]:
        """Run regression tests"""
        logger.info("Running regression tests...")
        return self.run_pytest_command(
            str(self.test_dir),
            "regression",
            extra_args=["-k", "regression"]
        )
    
    def run_all_tests(self, **kwargs) -> Dict[str, Any]:
        """Run all tests"""
        logger.info("Running all tests...")
        return self.run_pytest_command(
            str(self.test_dir),
            "all",
            coverage=kwargs.get("coverage", True),
            parallel=kwargs.get("parallel", True),
            timeout=1800
        )
    
    def run_tests(self, categories: List[str], **kwargs) -> Dict[str, Any]:
        """Run tests for specified categories"""
        self.start_time = time.time()
        results = {}
        
        # Map category names to methods
        category_methods = {
            "unit": self.run_unit_tests,
            "integration": self.run_integration_tests,
            "performance": self.run_performance_tests,
            "geographic": self.run_geographic_tests,
            "comprehensive": self.run_comprehensive_tests,
            "mobile": self.run_mobile_tests,
            "regression": self.run_regression_tests,
            "all": self.run_all_tests
        }
        
        for category in categories:
            if category not in category_methods:
                logger.warning(f"Unknown test category: {category}")
                continue
            
            logger.info(f"Starting {category} tests...")
            result = category_methods[category](**kwargs)
            results[category] = result
            
            if result["success"]:
                logger.info(f"✅ {category} tests passed in {result['duration']:.2f}s")
            else:
                logger.error(f"❌ {category} tests failed")
                if result.get("timeout"):
                    logger.error("Test timeout occurred")
                if result.get("error"):
                    logger.error(f"Error: {result['error']}")
        
        self.end_time = time.time()
        self.results = results
        return results
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive test report"""
        if not self.results:
            logger.warning("No test results to report")
            return ""
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        total_duration_tests = sum(result["duration"] for result in self.results.values())
        
        # Generate report content
        report_lines = [
            "# Location Input Test Suite Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total Test Categories: {total_tests}",
            f"- Passed: {passed_tests}",
            f"- Failed: {failed_tests}",
            f"- Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "- Success Rate: 0%",
            f"- Total Duration: {total_duration:.2f}s",
            f"- Test Execution Time: {total_duration_tests:.2f}s",
            "",
            "## Test Results by Category",
            ""
        ]
        
        for category, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            duration = result["duration"]
            
            report_lines.extend([
                f"### {category.title()} Tests",
                f"- Status: {status}",
                f"- Duration: {duration:.2f}s",
                f"- Command: `{result['command']}`",
                ""
            ])
            
            if not result["success"]:
                if result.get("timeout"):
                    report_lines.append("- ⚠️ Test timeout occurred")
                if result.get("error"):
                    report_lines.append(f"- ❌ Error: {result['error']}")
                if result["stderr"]:
                    report_lines.append(f"- Error Output: {result['stderr'][:500]}...")
                report_lines.append("")
        
        # Add performance analysis if performance tests were run
        if "performance" in self.results and self.results["performance"]["success"]:
            report_lines.extend([
                "## Performance Analysis",
                "",
                "### Performance Thresholds",
                f"- Max Response Time: {self.performance_thresholds['max_response_time_ms']}ms",
                f"- Min Throughput: {self.performance_thresholds['min_throughput_ops_per_sec']} ops/sec",
                f"- Max Memory Usage: {self.performance_thresholds['max_memory_usage_mb']}MB",
                f"- Max CPU Usage: {self.performance_thresholds['max_cpu_usage_percent']}%",
                f"- Max Error Rate: {self.performance_thresholds['max_error_rate_percent']}%",
                f"- Concurrent Users Target: {self.performance_thresholds['concurrent_users_target']}",
                ""
            ])
        
        # Add recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])
        
        if failed_tests > 0:
            report_lines.append("- 🔧 Review failed tests and fix issues")
        
        if total_duration > 1800:  # 30 minutes
            report_lines.append("- ⚡ Consider optimizing test execution time")
        
        if passed_tests == total_tests:
            report_lines.append("- 🎉 All tests passed! Ready for deployment")
        
        report_lines.extend([
            "",
            "## Test Files Generated",
            ""
        ])
        
        for category, result in self.results.items():
            if result.get("output_file"):
                report_lines.append(f"- {result['output_file']}")
        
        report_content = "\n".join(report_lines)
        
        # Write report to file
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            logger.info(f"Test report written to: {output_file}")
        
        return report_content
    
    def print_summary(self):
        """Print test summary to console"""
        if not self.results:
            logger.warning("No test results to summarize")
            return
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("LOCATION INPUT TEST SUITE SUMMARY")
        print("="*60)
        print(f"Total Categories: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "Success Rate: 0%")
        
        if self.end_time and self.start_time:
            print(f"Total Duration: {self.end_time - self.start_time:.2f}s")
        
        print("\nTest Results:")
        for category, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            duration = result["duration"]
            print(f"  {category.title():<15} {status:<10} ({duration:.2f}s)")
        
        print("="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Location Input Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python scripts/run_location_input_tests.py --categories all
  
  # Run specific test categories
  python scripts/run_location_input_tests.py --categories unit integration performance
  
  # Run with coverage and parallel execution
  python scripts/run_location_input_tests.py --categories all --coverage --parallel
  
  # Run and generate report
  python scripts/run_location_input_tests.py --categories all --report test-report.md
        """
    )
    
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["unit", "integration", "performance", "geographic", "comprehensive", "mobile", "regression", "all"],
        default=["all"],
        help="Test categories to run"
    )
    
    parser.add_argument(
        "--test-dir",
        default="tests",
        help="Directory containing test files"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage reports"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--report",
        help="Generate test report file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Test timeout in seconds (default: 1800)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    runner = LocationInputTestRunner(test_dir=args.test_dir)
    
    # Setup environment
    if not runner.setup_environment():
        logger.error("Failed to setup test environment")
        sys.exit(1)
    
    # Run tests
    logger.info(f"Starting test execution for categories: {', '.join(args.categories)}")
    results = runner.run_tests(
        args.categories,
        coverage=args.coverage,
        parallel=args.parallel,
        timeout=args.timeout
    )
    
    # Print summary
    runner.print_summary()
    
    # Generate report if requested
    if args.report:
        report_content = runner.generate_report(args.report)
        if args.verbose:
            print("\n" + report_content)
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result["success"])
    if failed_tests > 0:
        logger.error(f"{failed_tests} test categories failed")
        sys.exit(1)
    else:
        logger.info("All test categories passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()