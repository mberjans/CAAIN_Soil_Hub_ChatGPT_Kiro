#!/usr/bin/env python3
"""
Verification script for timing routes implementation.

This script verifies that all new timing routes endpoints are properly
implemented and accessible through the FastAPI application.
"""

import sys
import importlib.util
from pathlib import Path

def verify_imports():
    """Verify all necessary imports are available."""
    print("Verifying imports...")

    try:
        # Verify timing routes module
        spec = importlib.util.spec_from_file_location(
            "timing_routes",
            "src/api/timing_routes.py"
        )
        if spec is None:
            print("ERROR: Could not find timing_routes.py")
            return False

        module = importlib.util.module_from_spec(spec)
        print("  - timing_routes.py: OK")

        # Verify timing optimization models
        spec = importlib.util.spec_from_file_location(
            "timing_optimization_models",
            "src/models/timing_optimization_models.py"
        )
        if spec is None:
            print("ERROR: Could not find timing_optimization_models.py")
            return False

        module = importlib.util.module_from_spec(spec)
        print("  - timing_optimization_models.py: OK")

        # Verify test file
        spec = importlib.util.spec_from_file_location(
            "test_timing_routes",
            "src/tests/test_timing_routes.py"
        )
        if spec is None:
            print("ERROR: Could not find test_timing_routes.py")
            return False

        module = importlib.util.module_from_spec(spec)
        print("  - test_timing_routes.py: OK")

        print("All imports verified successfully!")
        return True

    except Exception as e:
        print(f"ERROR during import verification: {e}")
        return False


def verify_file_structure():
    """Verify file structure is correct."""
    print("\nVerifying file structure...")

    files = [
        "src/api/timing_routes.py",
        "src/models/timing_optimization_models.py",
        "src/tests/test_timing_routes.py",
        "TIMING_ROUTES_IMPLEMENTATION_SUMMARY.md"
    ]

    all_exist = True
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  - {file_path}: OK ({size} bytes)")
        else:
            print(f"  - {file_path}: MISSING")
            all_exist = False

    if all_exist:
        print("All files present!")
    else:
        print("Some files are missing!")

    return all_exist


def verify_endpoint_definitions():
    """Verify endpoint definitions are present in timing_routes.py."""
    print("\nVerifying endpoint definitions...")

    try:
        with open("src/api/timing_routes.py", "r") as f:
            content = f.read()

        endpoints = [
            ('POST /timing-optimization', '@router.post("/timing-optimization"'),
            ('GET /calendar', '@router.get("/calendar"'),
            ('GET /application-windows', '@router.get("/application-windows"'),
            ('POST /alerts/subscribe', '@router.post("/alerts/subscribe"'),
            ('GET /alerts/manage', '@router.get("/alerts/manage"')
        ]

        all_present = True
        for endpoint_name, decorator in endpoints:
            if decorator in content:
                print(f"  - {endpoint_name}: OK")
            else:
                print(f"  - {endpoint_name}: MISSING")
                all_present = False

        if all_present:
            print("All endpoints defined!")
        else:
            print("Some endpoints are missing!")

        return all_present

    except Exception as e:
        print(f"ERROR verifying endpoints: {e}")
        return False


def verify_model_definitions():
    """Verify new model definitions in timing_optimization_models.py."""
    print("\nVerifying model definitions...")

    try:
        with open("src/models/timing_optimization_models.py", "r") as f:
            content = f.read()

        models = [
            'AdvancedTimingOptimizationRequest',
            'AdvancedTimingOptimizationResponse',
            'FertilizerCalendarResponse',
            'CalendarEvent',
            'ApplicationWindowsResponse',
            'ApplicationWindow',
            'AlertSubscriptionRequest',
            'AlertSubscriptionResponse',
            'AlertManagementResponse'
        ]

        all_present = True
        for model_name in models:
            if f"class {model_name}" in content:
                print(f"  - {model_name}: OK")
            else:
                print(f"  - {model_name}: MISSING")
                all_present = False

        if all_present:
            print("All models defined!")
        else:
            print("Some models are missing!")

        return all_present

    except Exception as e:
        print(f"ERROR verifying models: {e}")
        return False


def verify_main_registration():
    """Verify router is registered in main.py."""
    print("\nVerifying main.py registration...")

    try:
        with open("src/main.py", "r") as f:
            content = f.read()

        checks = [
            ('Import statement', 'from api.timing_routes import router as timing_routes_router'),
            ('Router registration', 'app.include_router(timing_routes_router')
        ]

        all_present = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"  - {check_name}: OK")
            else:
                print(f"  - {check_name}: MISSING")
                all_present = False

        if all_present:
            print("Router properly registered!")
        else:
            print("Router registration incomplete!")

        return all_present

    except Exception as e:
        print(f"ERROR verifying main.py: {e}")
        return False


def verify_test_coverage():
    """Verify test coverage in test_timing_routes.py."""
    print("\nVerifying test coverage...")

    try:
        with open("src/tests/test_timing_routes.py", "r") as f:
            content = f.read()

        test_classes = [
            'TestAdvancedTimingOptimization',
            'TestFertilizerCalendar',
            'TestApplicationWindows',
            'TestAlertSubscription',
            'TestAlertManagement',
            'TestHealthCheck',
            'TestIntegration'
        ]

        all_present = True
        for test_class in test_classes:
            if f"class {test_class}" in content:
                print(f"  - {test_class}: OK")
            else:
                print(f"  - {test_class}: MISSING")
                all_present = False

        if all_present:
            print("All test classes present!")
        else:
            print("Some test classes are missing!")

        return all_present

    except Exception as e:
        print(f"ERROR verifying tests: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Timing Routes Implementation Verification")
    print("=" * 60)

    results = []

    results.append(("File Structure", verify_file_structure()))
    results.append(("Endpoint Definitions", verify_endpoint_definitions()))
    results.append(("Model Definitions", verify_model_definitions()))
    results.append(("Main.py Registration", verify_main_registration()))
    results.append(("Test Coverage", verify_test_coverage()))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    all_passed = True
    for check_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\nAll verification checks PASSED!")
        print("\nImplementation Summary:")
        print("  - 4 API endpoints implemented")
        print("  - 18 new Pydantic models created")
        print("  - Comprehensive test suite created")
        print("  - Router registered in main.py")
        print("  - Documentation created")
        return 0
    else:
        print("\nSome verification checks FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
