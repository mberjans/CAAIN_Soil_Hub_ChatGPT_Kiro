#!/usr/bin/env python3
"""
AFAS Test Runner

Comprehensive test runner for the Autonomous Farm Advisory System.
Runs unit tests, integration tests, agricultural validation tests,
performance tests, and security tests.
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        elapsed = time.time() - start_time
        print(f"✅ SUCCESS ({elapsed:.2f}s)")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ FAILED ({elapsed:.2f}s)")
        
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        
        return False


def install_test_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    
    commands = [
        "pip install -r requirements-test.txt",
        "pip install pytest-html pytest-json-report pytest-benchmark"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing dependencies: {cmd}"):
            return False
    
    return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    cmd = "pytest tests/unit/"
    
    if verbose:
        cmd += " -v"
    
    if coverage:
        cmd += " --cov=services --cov-report=html --cov-report=term"
    
    cmd += " --tb=short"
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests."""
    cmd = "pytest tests/integration/"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --tb=short"
    
    return run_command(cmd, "Integration Tests")


def run_agricultural_tests(verbose=False):
    """Run agricultural accuracy tests."""
    cmd = "pytest tests/agricultural/ -m agricultural"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --tb=short"
    
    return run_command(cmd, "Agricultural Accuracy Tests")


def run_performance_tests(verbose=False):
    """Run performance tests."""
    cmd = "pytest tests/performance/ -m performance"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --tb=short --benchmark-only"
    
    return run_command(cmd, "Performance Tests")


def run_security_tests(verbose=False):
    """Run security tests."""
    cmd = "pytest tests/security/ -m security"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --tb=short"
    
    return run_command(cmd, "Security Tests")


def run_service_tests(service_name, verbose=False):
    """Run tests for a specific service."""
    service_path = f"services/{service_name}/tests/"
    
    if not Path(service_path).exists():
        print(f"❌ No tests found for service: {service_name}")
        return False
    
    cmd = f"pytest {service_path}"
    
    if verbose:
        cmd += " -v"
    
    cmd += " --tb=short"
    
    return run_command(cmd, f"Service Tests: {service_name}")


def run_all_tests(verbose=False, coverage=False, include_slow=False):
    """Run all test suites."""
    print("🚀 Running AFAS Comprehensive Test Suite")
    print(f"Verbose: {verbose}, Coverage: {coverage}, Include Slow: {include_slow}")
    
    results = {}
    
    # Install dependencies first
    if not install_test_dependencies():
        print("❌ Failed to install test dependencies")
        return False
    
    # Run test suites
    test_suites = [
        ("Unit Tests", lambda: run_unit_tests(verbose, coverage)),
        ("Integration Tests", lambda: run_integration_tests(verbose)),
        ("Agricultural Tests", lambda: run_agricultural_tests(verbose)),
        ("Security Tests", lambda: run_security_tests(verbose))
    ]
    
    # Add performance tests if including slow tests
    if include_slow:
        test_suites.append(("Performance Tests", lambda: run_performance_tests(verbose)))
    
    # Run individual service tests
    services = [
        "recommendation-engine",
        "data-integration", 
        "question-router",
        "ai-agent",
        "user-management",
        "image-analysis",
        "frontend"
    ]
    
    for service in services:
        if Path(f"services/{service}/tests/").exists():
            test_suites.append((f"Service: {service}", lambda s=service: run_service_tests(s, verbose)))
    
    # Execute all test suites
    for suite_name, test_func in test_suites:
        results[suite_name] = test_func()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for suite_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{suite_name:<30} {status}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"💥 {failed} test suite(s) failed!")
        return False


def run_quick_tests():
    """Run a quick subset of tests for development."""
    print("🏃 Running Quick Test Suite (Unit + Agricultural)")
    
    results = []
    
    # Install dependencies
    if not install_test_dependencies():
        return False
    
    # Run core tests
    results.append(run_unit_tests(verbose=True))
    results.append(run_agricultural_tests(verbose=True))
    
    success = all(results)
    
    if success:
        print("✅ Quick tests passed!")
    else:
        print("❌ Quick tests failed!")
    
    return success


def run_ci_tests():
    """Run tests suitable for CI/CD pipeline."""
    print("🤖 Running CI Test Suite")
    
    # Set CI-specific environment variables
    os.environ['CI'] = 'true'
    os.environ['PYTEST_TIMEOUT'] = '300'  # 5 minute timeout
    
    cmd = """
    pytest tests/unit/ tests/integration/ tests/agricultural/ tests/security/ \
    --tb=short \
    --maxfail=5 \
    --timeout=300 \
    --cov=services \
    --cov-report=xml \
    --cov-report=term \
    --junit-xml=test-results.xml \
    --html=test-report.html \
    --self-contained-html
    """
    
    return run_command(cmd, "CI Test Suite")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="AFAS Test Runner")
    
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["all", "unit", "integration", "agricultural", "performance", "security", "quick", "ci"],
        default="quick",
        help="Test suite to run (default: quick)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Include slow tests (performance, load tests)"
    )
    
    parser.add_argument(
        "--service", "-s",
        help="Run tests for specific service"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = False
    
    if args.service:
        success = run_service_tests(args.service, args.verbose)
    
    elif args.suite == "all":
        success = run_all_tests(args.verbose, args.coverage, args.slow)
    
    elif args.suite == "unit":
        success = run_unit_tests(args.verbose, args.coverage)
    
    elif args.suite == "integration":
        success = run_integration_tests(args.verbose)
    
    elif args.suite == "agricultural":
        success = run_agricultural_tests(args.verbose)
    
    elif args.suite == "performance":
        success = run_performance_tests(args.verbose)
    
    elif args.suite == "security":
        success = run_security_tests(args.verbose)
    
    elif args.suite == "quick":
        success = run_quick_tests()
    
    elif args.suite == "ci":
        success = run_ci_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()