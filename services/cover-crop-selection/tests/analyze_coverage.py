#!/usr/bin/env python3
"""
Coverage Analysis Script for Cover Crop Selection Service

This script analyzes the current test coverage and identifies areas that need
additional testing to reach the 90% coverage target.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def load_coverage_data():
    """Load coverage data from coverage.json."""
    coverage_file = Path(__file__).parent.parent / "coverage.json"
    
    if not coverage_file.exists():
        print("❌ Coverage file not found. Run tests with coverage first:")
        print("   python tests/run_comprehensive_tests.py --mode coverage")
        return None
        
    with open(coverage_file, 'r') as f:
        return json.load(f)
        

def analyze_file_coverage(coverage_data):
    """Analyze coverage by file and identify low-coverage areas."""
    print("📊 Coverage Analysis by File")
    print("=" * 80)
    
    files_by_coverage = []
    
    for file_path, file_data in coverage_data.get("files", {}).items():
        if not file_path.startswith("src/"):
            continue
            
        summary = file_data.get("summary", {})
        percent_covered = summary.get("percent_covered", 0)
        covered_lines = summary.get("covered_lines", 0) 
        total_lines = summary.get("num_statements", 0)
        missing_lines = summary.get("missing_lines", 0)
        
        files_by_coverage.append({
            "file": file_path,
            "percent": percent_covered,
            "covered": covered_lines,
            "total": total_lines,
            "missing": missing_lines
        })
    
    # Sort by coverage percentage (lowest first)
    files_by_coverage.sort(key=lambda x: x["percent"])
    
    print(f"{'File':<50} {'Coverage':<10} {'Lines':<15} {'Status'}")
    print("-" * 80)
    
    low_coverage_files = []
    
    for file_info in files_by_coverage:
        file_path = file_info["file"]
        percent = file_info["percent"]
        covered = file_info["covered"]
        total = file_info["total"]
        
        if percent < 90:
            status = "🔴 LOW" if percent < 75 else "🟡 MED"
            low_coverage_files.append(file_info)
        else:
            status = "✅ GOOD"
            
        print(f"{file_path:<50} {percent:>6.1f}% {covered:>6}/{total:<6} {status}")
    
    print("\n" + "=" * 80)
    print(f"📈 Summary: {len(low_coverage_files)} files need improvement")
    
    return low_coverage_files


def identify_critical_missing_coverage(coverage_data, low_coverage_files):
    """Identify critical missing coverage areas."""
    print("\n🎯 Critical Areas Needing Coverage")
    print("=" * 80)
    
    critical_areas = defaultdict(list)
    
    for file_info in low_coverage_files:
        file_path = file_info["file"]
        file_data = coverage_data["files"][file_path]
        missing_lines = file_data.get("summary", {}).get("missing_lines", [])
        
        if not missing_lines:
            continue
            
        # Try to read the source file to understand what's missing
        try:
            src_file = Path(__file__).parent.parent / file_path
            if src_file.exists():
                with open(src_file, 'r') as f:
                    lines = f.readlines()
                    
                # Analyze missing lines to categorize them
                for line_num in missing_lines[:10]:  # Show first 10 missing lines
                    if line_num <= len(lines):
                        line_content = lines[line_num - 1].strip()
                        
                        # Categorize the missing line
                        if "def " in line_content:
                            critical_areas["functions"].append((file_path, line_num, line_content))
                        elif "class " in line_content:
                            critical_areas["classes"].append((file_path, line_num, line_content))
                        elif "if " in line_content or "elif " in line_content:
                            critical_areas["conditions"].append((file_path, line_num, line_content))
                        elif "except " in line_content or "raise " in line_content:
                            critical_areas["error_handling"].append((file_path, line_num, line_content))
                        else:
                            critical_areas["other"].append((file_path, line_num, line_content))
                            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
    
    # Report critical areas
    for category, items in critical_areas.items():
        if items:
            print(f"\n🔍 {category.replace('_', ' ').title()} ({len(items)} items):")
            for file_path, line_num, content in items[:5]:  # Show top 5
                print(f"   {file_path}:{line_num} - {content[:60]}...")
    
    return critical_areas


def generate_coverage_improvement_plan(low_coverage_files, critical_areas):
    """Generate a plan to improve test coverage to 90%."""
    print("\n📋 Coverage Improvement Plan")
    print("=" * 80)
    
    total_missing = sum(file_info["missing"] for file_info in low_coverage_files)
    print(f"Target: 90% coverage (currently 74.3%)")
    print(f"Missing: ~{total_missing} lines need coverage")
    
    print("\n🎯 Priority Actions:")
    
    # Priority 1: Core service functions
    service_files = [f for f in low_coverage_files if "service" in f["file"]]
    if service_files:
        print("\n1. Core Service Coverage (HIGH PRIORITY)")
        for file_info in service_files:
            needed = int(file_info["total"] * 0.9 - file_info["covered"])
            print(f"   - {file_info['file']}: Add ~{needed} lines of test coverage")
    
    # Priority 2: API routes
    api_files = [f for f in low_coverage_files if "api" in f["file"] or "route" in f["file"]]
    if api_files:
        print("\n2. API Coverage (MEDIUM PRIORITY)")
        for file_info in api_files:
            needed = int(file_info["total"] * 0.9 - file_info["covered"])
            print(f"   - {file_info['file']}: Add ~{needed} lines of test coverage")
    
    # Priority 3: Utility functions
    util_files = [f for f in low_coverage_files if "util" in f["file"] or "helper" in f["file"]]
    if util_files:
        print("\n3. Utility Coverage (LOW PRIORITY)")
        for file_info in util_files:
            needed = int(file_info["total"] * 0.9 - file_info["covered"])
            print(f"   - {file_info['file']}: Add ~{needed} lines of test coverage")
    
    print("\n📝 Recommended Test Types:")
    if critical_areas.get("functions"):
        print("   - Add unit tests for uncovered functions")
    if critical_areas.get("conditions"):
        print("   - Add branch tests for conditional logic")
    if critical_areas.get("error_handling"):
        print("   - Add exception and error handling tests")
    if critical_areas.get("classes"):
        print("   - Add class instantiation and method tests")
    
    print("\n⚡ Quick Wins (to reach 85% coverage):")
    print("   - Focus on core service methods with business logic")
    print("   - Add error case testing for API endpoints")
    print("   - Test utility functions and helpers")
    
    print("\n🏆 Long-term (to reach 90% coverage):")
    print("   - Comprehensive edge case testing")
    print("   - Integration testing for complex workflows")
    print("   - Performance testing with coverage tracking")


def main():
    """Main coverage analysis function."""
    print("🔍 Cover Crop Selection Service - Coverage Analysis")
    print("=" * 80)
    
    # Load coverage data
    coverage_data = load_coverage_data()
    if not coverage_data:
        return 1
    
    # Show overall summary
    totals = coverage_data.get("totals", {})
    overall_percent = totals.get("percent_covered", 0)
    covered_lines = totals.get("covered_lines", 0)
    total_lines = totals.get("num_statements", 0)
    
    print(f"📊 Overall Coverage: {overall_percent:.1f}% ({covered_lines}/{total_lines} lines)")
    
    if overall_percent >= 90:
        print("🎯 ✅ EXCELLENT: Target coverage achieved!")
        return 0
    elif overall_percent >= 85:
        print("👍 GOOD: Close to target, minor improvements needed")
    elif overall_percent >= 75:
        print("⚠️  MODERATE: Significant improvements needed")
    else:
        print("🔴 LOW: Major coverage improvements required")
    
    # Analyze by file
    low_coverage_files = analyze_file_coverage(coverage_data)
    
    # Identify critical areas
    critical_areas = identify_critical_missing_coverage(coverage_data, low_coverage_files)
    
    # Generate improvement plan
    generate_coverage_improvement_plan(low_coverage_files, critical_areas)
    
    print("\n" + "=" * 80)
    print("💡 Next Steps:")
    print("   1. Run: python tests/analyze_coverage.py")
    print("   2. Focus on highest-impact areas first")
    print("   3. Re-run tests: python tests/run_comprehensive_tests.py --mode coverage")
    print("   4. Iterate until >90% coverage achieved")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())