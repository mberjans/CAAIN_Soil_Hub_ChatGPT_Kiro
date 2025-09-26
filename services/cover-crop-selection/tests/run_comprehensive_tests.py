"""
Comprehensive Test Runner for Cover Crop Selection Service

This script runs the complete test suite with proper coverage reporting,
performance benchmarking, and detailed result analysis. It provides
the infrastructure to achieve >90% test coverage matching the pH management
service standard.

Test Suite Components:
1. Existing tests (9 files, 4,593 lines)
2. Comprehensive API endpoints (1 file, ~1,200 lines)
3. Service layer comprehensive (1 file, ~1,500 lines)  
4. Performance & integration (1 file, ~1,000 lines)

Total: ~8,300 lines of test code covering all aspects
Target: >90% coverage with ~50-60 total test cases
"""

import pytest
import sys
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime
import json

# Add the src directory to the path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class CoverCropTestRunner:
    """Comprehensive test runner for cover crop selection service."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_categories": {},
            "coverage_report": {},
            "performance_metrics": {},
            "summary": {}
        }
        
    def run_test_category(self, category_name: str, test_files: list, markers: list = None):
        """Run a specific category of tests."""
        print(f"\\n{'='*60}")
        print(f"Running {category_name} Tests")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Build pytest command
        cmd = ["python", "-m", "pytest", "-v", "--tb=short"]
        
        # Add markers if specified
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])
                
        # Add test files
        for test_file in test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))
            else:
                print(f"Warning: Test file not found: {test_file}")
                
        # Add coverage if available
        try:
            import coverage
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
        except ImportError:
            print("Coverage not available - install with: pip install pytest-cov")
            
        # Run tests
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir.parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per category
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            self.results["test_categories"][category_name] = {
                "duration_seconds": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            # Print summary
            if result.returncode == 0:
                print(f"✅ {category_name} tests PASSED in {duration:.1f}s")
            else:
                print(f"❌ {category_name} tests FAILED in {duration:.1f}s")
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                print("STDERR:", result.stderr[-500:])
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {category_name} tests TIMED OUT after 5 minutes")
            self.results["test_categories"][category_name] = {
                "duration_seconds": 300,
                "return_code": -1,
                "error": "timeout",
                "success": False
            }
        except Exception as e:
            print(f"💥 {category_name} tests ERROR: {e}")
            self.results["test_categories"][category_name] = {
                "duration_seconds": 0,
                "return_code": -1,
                "error": str(e),
                "success": False
            }
            
    def run_existing_tests(self):
        """Run existing test suite."""
        existing_tests = [
            "test_api_endpoints.py",
            "test_benefit_tracking_system.py", 
            "test_climate_soil_integration.py",
            "test_cover_crop_service.py",
            "test_goal_based_api.py",
            "test_goal_based_basic.py",
            "test_goal_based_functionality.py",
            "test_rotation_integration.py",
            "test_timing_system.py"
        ]
        
        self.run_test_category("Existing Tests", existing_tests)
        
    def run_comprehensive_api_tests(self):
        """Run comprehensive API endpoint tests."""
        api_tests = ["test_comprehensive_api_endpoints.py"]
        self.run_test_category("Comprehensive API", api_tests)
        
    def run_service_layer_tests(self):
        """Run comprehensive service layer tests."""
        service_tests = ["test_service_layer_comprehensive.py"]
        self.run_test_category("Service Layer", service_tests)
        
    def run_performance_tests(self):
        """Run performance and integration tests."""
        performance_tests = ["test_performance_integration.py"]
        self.run_test_category("Performance & Integration", performance_tests)
        
    def run_agricultural_validation_tests(self):
        """Run agricultural accuracy validation tests."""
        ag_tests = ["test_agricultural_accuracy_validation.py"]
        self.run_test_category("Agricultural Validation", ag_tests)
        
    def run_unit_tests(self):
        """Run comprehensive unit tests."""
        unit_tests = ["test_cover_crop_service_comprehensive_unit.py"]
        self.run_test_category("Comprehensive Unit Tests", unit_tests)
        
    def run_quick_tests(self):
        """Run quick tests only (non-performance)."""
        quick_tests = [
            "test_api_endpoints.py",
            "test_cover_crop_service.py",
            "test_comprehensive_api_endpoints.py"
        ]
        self.run_test_category("Quick Tests", quick_tests)
        
    def run_coverage_analysis(self):
        """Run comprehensive coverage analysis."""
        print(f"\\n{'='*60}")
        print("Running Coverage Analysis")
        print(f"{'='*60}")
        
        coverage_cmd = [
            "python", "-m", "pytest", 
            "--cov=src",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json", 
            "--cov-report=term-missing",
            "--cov-fail-under=85",  # Aim for 85%+ coverage
            str(self.test_dir)
        ]
        
        try:
            result = subprocess.run(
                coverage_cmd,
                cwd=self.test_dir.parent,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for full coverage
            )
            
            # Try to read coverage.json if it exists
            coverage_file = self.test_dir.parent / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    self.results["coverage_report"] = coverage_data
                    
                # Extract summary statistics
                if "totals" in coverage_data:
                    totals = coverage_data["totals"] 
                    coverage_percent = totals.get("percent_covered", 0)
                    print(f"📊 Overall Coverage: {coverage_percent:.1f}%")
                    
                    if coverage_percent >= 90:
                        print("🎯 Excellent! Coverage target achieved (≥90%)")
                    elif coverage_percent >= 85:
                        print("👍 Good coverage (≥85%)")
                    elif coverage_percent >= 75:
                        print("⚠️  Moderate coverage (≥75%)")
                    else:
                        print("🔴 Low coverage (<75%)")
                        
            print(f"📄 HTML coverage report: {self.test_dir.parent / 'htmlcov' / 'index.html'}")
            
        except Exception as e:
            print(f"Coverage analysis error: {e}")
            
    def benchmark_performance(self):
        """Run performance benchmarks."""
        print(f"\\n{'='*60}")
        print("Performance Benchmarking")
        print(f"{'='*60}")
        
        # Run performance tests with special markers
        perf_cmd = [
            "python", "-m", "pytest", "-v",
            "-m", "not slow",  # Skip slow tests for benchmark
            "--tb=short",
            "test_performance_integration.py"
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                perf_cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            
            end_time = time.time()
            benchmark_time = end_time - start_time
            
            self.results["performance_metrics"] = {
                "benchmark_duration": benchmark_time,
                "benchmark_success": result.returncode == 0,
                "benchmark_output": result.stdout
            }
            
            print(f"⏱️  Performance benchmark completed in {benchmark_time:.1f}s")
            
            if result.returncode == 0:
                print("✅ Performance benchmarks PASSED")
            else:
                print("❌ Performance benchmarks had issues")
                
        except Exception as e:
            print(f"Performance benchmark error: {e}")
            
    def generate_summary_report(self):
        """Generate comprehensive test summary report."""
        print(f"\\n{'='*80}")
        print("COMPREHENSIVE TEST SUMMARY REPORT")
        print(f"{'='*80}")
        
        # Calculate totals
        total_categories = len(self.results["test_categories"])
        successful_categories = sum(1 for cat in self.results["test_categories"].values() 
                                  if cat.get("success", False))
        total_duration = sum(cat.get("duration_seconds", 0) 
                           for cat in self.results["test_categories"].values())
        
        print(f"📊 Test Categories: {successful_categories}/{total_categories} passed")
        print(f"⏱️  Total Duration: {total_duration:.1f} seconds")
        
        # Category details
        for category, results in self.results["test_categories"].items():
            status = "✅ PASS" if results.get("success") else "❌ FAIL"
            duration = results.get("duration_seconds", 0)
            print(f"   {category}: {status} ({duration:.1f}s)")
            
        # Coverage summary
        if "coverage_report" in self.results and "totals" in self.results["coverage_report"]:
            totals = self.results["coverage_report"]["totals"]
            coverage_percent = totals.get("percent_covered", 0)
            lines_covered = totals.get("covered_lines", 0)
            lines_total = totals.get("num_statements", 0)
            
            print(f"\\n📈 Coverage Summary:")
            print(f"   Overall: {coverage_percent:.1f}% ({lines_covered}/{lines_total} lines)")
            
            # Coverage target assessment
            if coverage_percent >= 90:
                print("   🎯 TARGET ACHIEVED: ≥90% coverage (matches pH management standard)")
            elif coverage_percent >= 85:
                print("   👍 GOOD: ≥85% coverage (close to target)")
            else:
                print("   🔴 NEEDS IMPROVEMENT: <85% coverage")
                
        # Performance summary
        if "performance_metrics" in self.results:
            perf = self.results["performance_metrics"]
            if perf.get("benchmark_success"):
                duration = perf.get("benchmark_duration", 0)
                print(f"\\n⚡ Performance: All benchmarks passed ({duration:.1f}s)")
            else:
                print("\\n⚠️  Performance: Some benchmarks had issues")
                
        # Final assessment
        print(f"\\n{'='*80}")
        
        if successful_categories == total_categories:
            if self.results.get("coverage_report", {}).get("totals", {}).get("percent_covered", 0) >= 90:
                print("🏆 EXCELLENT: All tests passed with ≥90% coverage!")
                print("✨ Test suite meets pH management service standard")
            else:
                print("🎯 GOOD: All tests passed, coverage improvement recommended")
        else:
            print("🔧 NEEDS WORK: Some test categories failed")
            
        print(f"{'='*80}")
        
        # Save detailed results
        results_file = self.test_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Detailed results saved to: {results_file}")
        
    def run_full_suite(self):
        """Run the complete comprehensive test suite."""
        print("🚀 Starting Comprehensive Cover Crop Selection Test Suite")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.run_existing_tests()
        self.run_unit_tests()
        self.run_comprehensive_api_tests()
        self.run_service_layer_tests()
        self.run_agricultural_validation_tests()
        self.run_performance_tests()
        
        # Run analysis
        self.run_coverage_analysis()
        self.benchmark_performance()
        
        # Generate final report
        self.generate_summary_report()
        
    def run_quick_suite(self):
        """Run quick test suite for development."""
        print("⚡ Running Quick Test Suite (Development Mode)")
        
        self.run_quick_tests()
        self.run_coverage_analysis()
        self.generate_summary_report()


def main():
    """Main test runner entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cover Crop Selection Test Runner")
    parser.add_argument("--mode", choices=["full", "quick", "coverage", "performance"], 
                       default="full", help="Test mode to run")
    parser.add_argument("--category", choices=["existing", "unit", "api", "service", "agricultural", "performance"],
                       help="Run specific test category only")
    
    args = parser.parse_args()
    
    runner = CoverCropTestRunner()
    
    if args.category:
        # Run specific category
        if args.category == "existing":
            runner.run_existing_tests()
        elif args.category == "unit":
            runner.run_unit_tests()
        elif args.category == "api":
            runner.run_comprehensive_api_tests()
        elif args.category == "service":
            runner.run_service_layer_tests()
        elif args.category == "agricultural":
            runner.run_agricultural_validation_tests()
        elif args.category == "performance":
            runner.run_performance_tests()
            
        runner.generate_summary_report()
        
    elif args.mode == "quick":
        runner.run_quick_suite()
    elif args.mode == "coverage":
        runner.run_coverage_analysis()
    elif args.mode == "performance":  
        runner.benchmark_performance()
    else:
        runner.run_full_suite()


if __name__ == "__main__":
    main()