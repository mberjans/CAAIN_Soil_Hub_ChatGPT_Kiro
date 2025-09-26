#!/usr/bin/env python3
"""
Validation script for the climate zone section implementation in Streamlit app.
This script validates the structure and content of the updated streamlit_app.py
"""

import ast
import re

def validate_climate_zone_implementation():
    """Validate the climate zone implementation in streamlit_app.py"""
    
    print("🔍 Validating Climate Zone Implementation...")
    print("=" * 60)
    
    # Read the streamlit app file
    try:
        with open('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/frontend/src/streamlit_app.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ ERROR: streamlit_app.py not found!")
        return False
    
    # Validation checks
    checks = [
        ("Climate Zone Header", r'st\.header\("🌡️ Climate Zone Information"\)'),
        ("USDA Zone Selection", r'usda_zone = st\.selectbox'),
        ("Köppen Classification", r'koppen_climate = st\.text_input'),
        ("Frost Dates Section", r'st\.subheader\("🌨️ Frost Dates"\)'),
        ("Agricultural Assessment", r'st\.subheader\("🌾 Agricultural Assessment"\)'),
        ("Zone Confidence Metric", r'st\.metric\("Zone Confidence"'),
        ("Last Frost Metric", r'st\.metric\("Last Frost"'),
        ("First Frost Metric", r'st\.metric\("First Frost"'),
        ("Frost-Free Days Metric", r'st\.metric\("Frost-Free Days"'),
        ("Suitability Score", r'suitability_score = 8\.5'),
        ("Climate Zone Insights", r'st\.expander\("🔍 Climate Zone Insights"'),
        ("Progress Bar", r'st\.progress\(suitability_score / 10\.0\)'),
        ("Detection Status", r'st\.success\("✅ Verified"\)'),
    ]
    
    results = []
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"✅ {check_name}: Found")
            results.append(True)
        else:
            print(f"❌ {check_name}: Missing")
            results.append(False)
    
    # Check positioning - Climate zone should be between farm profile and current crop
    farm_profile_pos = content.find('st.header("🏡 Farm Profile")')
    climate_zone_pos = content.find('st.header("🌡️ Climate Zone Information")')
    current_crop_pos = content.find('st.header("🌾 Current Crop")')
    
    if farm_profile_pos < climate_zone_pos < current_crop_pos:
        print("✅ Section Positioning: Climate zone correctly positioned between Farm Profile and Current Crop")
        results.append(True)
    else:
        print("❌ Section Positioning: Climate zone not in correct position")
        results.append(False)
    
    # Check CSS additions
    css_checks = [
        ("Climate Zone Card CSS", r'\.climate-zone-card'),
        ("Frost Info CSS", r'\.frost-info'),
    ]
    
    for check_name, pattern in css_checks:
        if re.search(pattern, content):
            print(f"✅ {check_name}: Found")
            results.append(True)
        else:
            print(f"❌ {check_name}: Missing")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 SUCCESS: All climate zone features implemented correctly!")
        return True
    else:
        print("⚠️  WARNING: Some features are missing or incorrectly implemented")
        return False

def validate_mock_data():
    """Validate that the mock data matches requirements"""
    print("\n🧪 Validating Mock Data...")
    print("=" * 60)
    
    try:
        with open('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/frontend/src/streamlit_app.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ ERROR: streamlit_app.py not found!")
        return False
    
    mock_data_checks = [
        ("USDA Zone 5b", r'index=5.*# Default to Zone 5b'),
        ("Köppen Climate", r'Dfa - Hot-summer humid continental'),
        ("92% Confidence", r'92%'),
        ("April 15 Last Frost", r'April 15'),
        ("October 12 First Frost", r'October 12'),
        ("180 Frost-Free Days", r'180'),
        ("8.5 Suitability Score", r'suitability_score = 8\.5'),
    ]
    
    results = []
    for check_name, pattern in mock_data_checks:
        if re.search(pattern, content):
            print(f"✅ {check_name}: Found")
            results.append(True)
        else:
            print(f"❌ {check_name}: Missing")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"📊 Mock Data Results: {passed}/{total} checks passed")
    
    return passed == total

def main():
    """Main validation function"""
    print("🌱 CAAIN Soil Hub - Climate Zone Implementation Validator")
    print("=" * 70)
    
    # Validate implementation
    impl_success = validate_climate_zone_implementation()
    
    # Validate mock data
    data_success = validate_mock_data()
    
    # Overall summary
    print("\n" + "=" * 70)
    if impl_success and data_success:
        print("🎯 OVERALL STATUS: Implementation COMPLETE and VALIDATED!")
        print("📋 Next Steps:")
        print("   1. Test the Streamlit app locally")
        print("   2. Connect to backend climate zone detection API")
        print("   3. Replace mock data with real API calls")
        print("   4. Add error handling for API failures")
    else:
        print("⚠️  OVERALL STATUS: Implementation needs attention")
        if not impl_success:
            print("   - Fix missing implementation features")
        if not data_success:
            print("   - Fix mock data values")
    
    return impl_success and data_success

if __name__ == "__main__":
    main()