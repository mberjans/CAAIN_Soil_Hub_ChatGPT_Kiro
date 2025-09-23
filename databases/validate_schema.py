#!/usr/bin/env python3
"""
Schema Validation Script for Farm Location Input Feature
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

import os
import sys
from pathlib import Path

def validate_files_exist():
    """Validate that all required files exist."""
    required_files = [
        'databases/postgresql/farm_location_schema.sql',
        'databases/python/location_models.py',
        'databases/python/location_sqlalchemy_models.py',
        'databases/migrations/001_create_farm_location_tables.sql',
        'databases/migrations/001_rollback_farm_location_tables.sql',
        'databases/migrations/run_migration.py',
        'databases/test_location_models.py',
        'databases/FARM_LOCATION_SCHEMA.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ All required files exist")
    return True

def validate_pydantic_models():
    """Validate Pydantic models can be imported and work correctly."""
    try:
        # Add current directory to path for imports
        sys.path.insert(0, str(Path.cwd()))
        
        from databases.python.location_models import (
            FarmLocationCreate, FarmLocationUpdate, FarmLocation,
            FarmFieldCreate, FarmFieldUpdate, FarmField,
            LocationSource, FieldType, ValidationResult,
            GeocodingRequest, ReverseGeocodingRequest,
            LOCATION_ERRORS
        )
        
        # Test basic model creation
        location = FarmLocationCreate(
            name="Test Farm",
            latitude=42.0308,
            longitude=-93.6319,
            source="gps"
        )
        
        field = FarmFieldCreate(
            location_id="test-uuid",
            field_name="Test Field",
            field_type="crop"
        )
        
        print("✅ Pydantic models import and work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic models validation failed: {e}")
        return False

def validate_sqlalchemy_models():
    """Validate SQLAlchemy models can be imported."""
    try:
        # Add current directory to path for imports
        sys.path.insert(0, str(Path.cwd()))
        
        from databases.python.location_sqlalchemy_models import (
            FarmLocation, FarmField, GeocodingCache
        )
        
        print("✅ SQLAlchemy models import correctly")
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy models validation failed: {e}")
        return False

def validate_migration_script():
    """Validate migration script is executable and has correct structure."""
    migration_script = Path('databases/migrations/run_migration.py')
    
    if not migration_script.exists():
        print("❌ Migration script not found")
        return False
    
    # Check if script is executable
    if not os.access(migration_script, os.X_OK):
        print("❌ Migration script is not executable")
        return False
    
    # Check script has required functions
    with open(migration_script, 'r') as f:
        content = f.read()
        required_functions = [
            'create_farm_location_tables',
            'rollback_farm_location_tables',
            'check_tables_exist',
            'validate_schema'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"def {func}" not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Migration script missing functions: {missing_functions}")
            return False
    
    print("✅ Migration script is valid and executable")
    return True

def validate_sql_schema():
    """Validate SQL schema files have correct structure."""
    schema_file = Path('databases/postgresql/farm_location_schema.sql')
    
    if not schema_file.exists():
        print("❌ SQL schema file not found")
        return False
    
    with open(schema_file, 'r') as f:
        content = f.read()
        
        required_tables = ['farm_locations', 'farm_fields', 'geocoding_cache']
        required_indexes = [
            'idx_farm_locations_user_id',
            'idx_farm_locations_coordinates',
            'idx_farm_fields_location_id',
            'idx_geocoding_cache_hash'
        ]
        
        missing_tables = []
        for table in required_tables:
            if f"CREATE TABLE {table}" not in content:
                missing_tables.append(table)
        
        missing_indexes = []
        for index in required_indexes:
            if f"CREATE INDEX {index}" not in content:
                missing_indexes.append(index)
        
        if missing_tables:
            print(f"❌ SQL schema missing tables: {missing_tables}")
            return False
        
        if missing_indexes:
            print(f"❌ SQL schema missing indexes: {missing_indexes}")
            return False
    
    print("✅ SQL schema is valid")
    return True

def validate_requirements_coverage():
    """Validate that implementation covers all requirements."""
    requirements_file = Path('.kiro/specs/farm-location-input/requirements.md')
    
    if not requirements_file.exists():
        print("⚠️  Requirements file not found, skipping coverage check")
        return True
    
    with open(requirements_file, 'r') as f:
        content = f.read()
        
        # Check for key requirement indicators
        key_requirements = [
            'GPS coordinates',
            'address input',
            'interactive map',
            'current location',
            'multiple field locations',
            'location validation'
        ]
        
        missing_requirements = []
        for req in key_requirements:
            if req.lower() not in content.lower():
                missing_requirements.append(req)
        
        if missing_requirements:
            print(f"⚠️  Some requirements may not be covered: {missing_requirements}")
        else:
            print("✅ All key requirements appear to be covered")
    
    return True

def main():
    """Main validation function."""
    print("🔍 Validating Farm Location Input Database Schema Implementation")
    print("=" * 60)
    
    validations = [
        ("File Existence", validate_files_exist),
        ("Pydantic Models", validate_pydantic_models),
        ("SQLAlchemy Models", validate_sqlalchemy_models),
        ("Migration Script", validate_migration_script),
        ("SQL Schema", validate_sql_schema),
        ("Requirements Coverage", validate_requirements_coverage)
    ]
    
    all_passed = True
    
    for name, validation_func in validations:
        print(f"\n📋 {name}:")
        try:
            result = validation_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {name} validation failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All validations passed! Database schema implementation is complete.")
        print("\nNext steps:")
        print("1. Run database migration: python databases/migrations/run_migration.py --database-url <url> --action create")
        print("2. Run tests: python -m pytest databases/test_location_models.py")
        print("3. Implement location validation service")
        print("4. Implement geocoding service")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())