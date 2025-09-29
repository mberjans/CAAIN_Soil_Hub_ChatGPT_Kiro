#!/usr/bin/env python3
"""
Comprehensive Test Runner for Drought Management System

This script runs all tests for the drought management system including:
- Unit tests
- Integration tests
- Agricultural validation tests
- Performance tests

TICKET-014_drought-management-13.1: Comprehensive testing suite
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0

def run_unit_tests():
    """Run unit tests."""
    command = [
        "python", "-m", "pytest", 
        "tests/", 
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Unit Tests")

def run_integration_tests():
    """Run integration tests."""
    command = [
        "python", "-m", "pytest", 
        "tests/", 
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Integration Tests")

def run_agricultural_validation_tests():
    """Run agricultural validation tests."""
    command = [
        "python", "-m", "pytest", 
        "tests/test_agricultural_validation.py",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Agricultural Validation Tests")

def run_performance_tests():
    """Run performance tests."""
    command = [
        "python", "-m", "pytest", 
        "tests/test_performance.py",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Performance Tests")

def run_comprehensive_tests():
    """Run comprehensive test suite."""
    command = [
        "python", "-m", "pytest", 
        "tests/test_drought_management_comprehensive.py",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "Comprehensive Test Suite")

def run_all_tests():
    """Run all tests with coverage."""
    command = [
        "python", "-m", "pytest", 
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=80",
        "--tb=short",
        "-v"
    ]
    return run_command(command, "All Tests with Coverage")

def run_specific_test(test_file):
    """Run a specific test file."""
    command = [
        "python", "-m", "pytest", 
        f"tests/{test_file}",
        "--tb=short",
        "-v"
    ]
    return run_command(command, f"Specific Test: {test_file}")

def check_test_environment():
    """Check if test environment is properly set up."""
    print("Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} is installed")
    except ImportError:
        print("✗ pytest is not installed")
        return False
    
    # Check if required packages are installed
    required_packages = [
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "asyncio",
        "unittest.mock"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            return False
    
    # Check if test files exist
    test_files = [
        "test_drought_management_comprehensive.py",
        "test_agricultural_validation.py",
        "test_performance.py",
        "test_data_fixtures.py",
        "conftest.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(f"tests/{test_file}"):
            print(f"✓ {test_file} exists")
        else:
            print(f"✗ {test_file} is missing")
            return False
    
    print("✓ Test environment is properly set up")
    return True

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("DROUGHT MANAGEMENT SYSTEM - TEST REPORT")
    print("="*60)
    
    # Run all tests and generate report
    command = [
        "python", "-m", "pytest", 
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--junitxml=test-results.xml",
        "--tb=short",
        "-v"
    ]
    
    success = run_command(command, "Comprehensive Test Report Generation")
    
    if success:
        print("\n✓ Test report generated successfully")
        print("  - HTML coverage report: htmlcov/index.html")
        print("  - XML coverage report: coverage.xml")
        print("  - JUnit test results: test-results.xml")
    else:
        print("\n✗ Test report generation failed")
    
    return success

def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="Run drought management system tests")
    parser.add_argument("--test-type", choices=[
        "unit", "integration", "agricultural", "performance", 
        "comprehensive", "all", "specific", "report"
    ], default="all", help="Type of tests to run")
    parser.add_argument("--test-file", help="Specific test file to run (for specific test type)")
    parser.add_argument("--check-env", action="store_true", help="Check test environment setup")
    
    args = parser.parse_args()
    
    # Change to the drought management directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if args.check_env:
        if check_test_environment():
            print("\n✓ Environment check passed")
            return 0
        else:
            print("\n✗ Environment check failed")
            return 1
    
    print("DROUGHT MANAGEMENT SYSTEM - TEST RUNNER")
    print("="*60)
    
    success = True
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "agricultural":
        success = run_agricultural_validation_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "comprehensive":
        success = run_comprehensive_tests()
    elif args.test_type == "specific":
        if not args.test_file:
            print("Error: --test-file is required for specific test type")
            return 1
        success = run_specific_test(args.test_file)
    elif args.test_type == "report":
        success = generate_test_report()
    elif args.test_type == "all":
        success = run_all_tests()
    
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("✓ Drought management system is ready for production")
    else:
        print("✗ SOME TESTS FAILED")
        print("✗ Please review test failures before deployment")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())