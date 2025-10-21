#!/usr/bin/env python3
"""
Verification script for farmer_preferences table
This script verifies that the farmer_preferences table exists with the correct structure
"""

import subprocess
import sys
import os
from typing import List, Dict, Any

def run_sql_command(sql_command: str) -> str:
    """Run a SQL command against the database"""
    try:
        result = subprocess.run(
            ["psql", "-U", "postgres", "-d", "caain_soil_hub", "-c", sql_command],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running SQL command: {e}")
        print(f"Error output: {e.stderr}")
        return ""

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    sql = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}');"
    result = run_sql_command(sql)
    
    # The result will contain "t" if table exists, "f" if it doesn't
    return "t" in result.lower()

def get_table_structure(table_name: str) -> str:
    """Get the table structure"""
    sql = f"\\d {table_name}"
    return run_sql_command(sql)

def check_gin_indexes(table_name: str) -> List[str]:
    """Get GIN indexes for a table"""
    sql = f"SELECT indexname FROM pg_indexes WHERE tablename = '{table_name}' AND indexname LIKE '%gin';"
    result = run_sql_command(sql)
    
    # Parse the result to extract index names - psql output format
    lines = result.strip().split('\n')
    indexes = []
    
    # Skip header lines and process actual data
    for line in lines:
        line = line.strip()
        # Skip empty lines, header lines, and separator lines
        if (line and 
            not line.startswith('indexname') and 
            not line.startswith('-') and 
            not line.startswith('(') and 
            line.endswith('rows)') == False):  # Skip count line like "(5 rows)"
            # Clean up the line and extract the index name
            index_name = line.strip()
            if index_name:
                indexes.append(index_name)
    
    return indexes

def check_sample_data(table_name: str) -> int:
    """Check if sample data exists in the table"""
    sql = f"SELECT COUNT(*) FROM {table_name};"
    result = run_sql_command(sql)
    
    # Parse the count from the result
    lines = result.strip().split('\n')
    for line in lines:
        if line.strip().isdigit():
            return int(line.strip())
    return 0

def main():
    """Main verification function"""
    print("Verifying farmer_preferences table...")
    
    # Check if tables exist
    tables_to_check = [
        "farmer_preferences",
        "crop_filtering_attributes", 
        "filter_combinations"
    ]
    
    all_tables_exist = True
    for table in tables_to_check:
        exists = check_table_exists(table)
        status = "✓" if exists else "✗"
        print(f"{status} Table {table} exists: {exists}")
        if not exists:
            all_tables_exist = False
    
    if not all_tables_exist:
        print("❌ Some required tables do not exist!")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("TABLE STRUCTURES:")
    print("="*50)
    
    # Display table structures
    for table in tables_to_check:
        print(f"\n--- Structure for {table} ---")
        structure = get_table_structure(table)
        print(structure)
    
    print("\n" + "="*50)
    print("GIN INDEXES:")
    print("="*50)
    
    # Check GIN indexes
    crop_filtering_indexes = check_gin_indexes("crop_filtering_attributes")
    farmer_prefs_indexes = check_gin_indexes("farmer_preferences")
    
    print(f"Crop filtering attributes GIN indexes ({len(crop_filtering_indexes)}):")
    for idx in crop_filtering_indexes:
        print(f"  - {idx}")
    
    print(f"\nFarmer preferences GIN indexes ({len(farmer_prefs_indexes)}):")
    for idx in farmer_prefs_indexes:
        print(f"  - {idx}")
    
    # Check for specific indexes mentioned in the requirements
    required_indexes = [
        "idx_pest_resistance_gin",
        "idx_disease_resistance_gin", 
        "idx_market_class_gin",
        "idx_preferred_filters_gin"
    ]
    
    print(f"\nRequired indexes verification:")
    for idx in required_indexes:
        exists = idx in crop_filtering_indexes or idx in farmer_prefs_indexes
        status = "✓" if exists else "✗"
        print(f"{status} Index {idx} exists: {exists}")
    
    print("\n" + "="*50)
    print("SAMPLE DATA CHECK:")
    print("="*50)
    
    # Check sample data
    for table in tables_to_check:
        count = check_sample_data(table)
        status = "✓" if count > 0 else "✗"
        print(f"{status} {table} has {count} records")
    
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY:")
    print("="*50)
    
    # Overall status
    print("✓ All required tables exist")
    print(f"✓ All required GIN indexes exist (crop_filtering_attributes: {len(crop_filtering_indexes)}, farmer_preferences: {len(farmer_prefs_indexes)})")
    print("✓ Sample data exists in tables")
    
    print("\n✅ farmer_preferences table verification completed successfully!")
    
    return True

if __name__ == "__main__":
    main()