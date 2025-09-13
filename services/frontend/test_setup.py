#!/usr/bin/env python3
"""
Test script to verify AFAS Frontend setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Python imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ HTTPX imported successfully")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    base_path = Path(__file__).parent
    required_files = [
        "src/main.py",
        "src/streamlit_app.py",
        "src/templates/dashboard.html",
        "src/templates/crop_selection.html",
        "src/templates/soil_fertility.html",
        "src/templates/fertilizer_strategy.html",
        "src/static/css/agricultural.css",
        "src/static/js/agricultural.js",
        "start_fastapi.py",
        "start_streamlit.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_exist = False
    
    return all_exist

def test_fastapi_app():
    """Test that FastAPI app can be created"""
    print("\n🚀 Testing FastAPI application...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Import without starting server
        from main import app
        print("✅ FastAPI app created successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/crop-selection", "/soil-fertility", "/fertilizer-strategy", "/health"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        return False

def test_templates():
    """Test that templates are valid HTML"""
    print("\n📄 Testing HTML templates...")
    
    templates_path = Path(__file__).parent / "src" / "templates"
    template_files = list(templates_path.glob("*.html"))
    
    if not template_files:
        print("❌ No template files found")
        return False
    
    for template_file in template_files:
        try:
            content = template_file.read_text()
            if "<!DOCTYPE html>" in content and "<html" in content:
                print(f"✅ {template_file.name} - Valid HTML structure")
            else:
                print(f"❌ {template_file.name} - Invalid HTML structure")
                return False
        except Exception as e:
            print(f"❌ {template_file.name} - Error reading: {e}")
            return False
    
    return True

def test_static_files():
    """Test that static files exist and are valid"""
    print("\n🎨 Testing static files...")
    
    static_path = Path(__file__).parent / "src" / "static"
    
    # Test CSS
    css_file = static_path / "css" / "agricultural.css"
    if css_file.exists():
        content = css_file.read_text()
        if ":root" in content and "--primary-green" in content:
            print("✅ agricultural.css - Valid CSS with agricultural theme")
        else:
            print("❌ agricultural.css - Missing agricultural theme variables")
            return False
    else:
        print("❌ agricultural.css - File missing")
        return False
    
    # Test JavaScript
    js_file = static_path / "js" / "agricultural.js"
    if js_file.exists():
        content = js_file.read_text()
        if "AgriculturalCalculator" in content and "calculateSoilHealthScore" in content:
            print("✅ agricultural.js - Valid JavaScript with agricultural functions")
        else:
            print("❌ agricultural.js - Missing agricultural functions")
            return False
    else:
        print("❌ agricultural.js - File missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🌱 AFAS Frontend Setup Test\n")
    
    tests = [
        ("Python Imports", test_imports),
        ("File Structure", test_file_structure),
        ("FastAPI Application", test_fastapi_app),
        ("HTML Templates", test_templates),
        ("Static Files", test_static_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Frontend setup is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start FastAPI: python start_fastapi.py")
        print("3. Start Streamlit: python start_streamlit.py")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)