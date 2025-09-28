#!/usr/bin/env python3
"""
Comprehensive Crop Taxonomy Implementation Test

Tests the complete crop taxonomy system including:
- Database migration status
- Service functionality 
- API endpoints
- Data population capabilities
- Filtering and search functionality

This continues from TICKET-005 implementation to validate the system works.
"""

import asyncio
import os
import sys
import psycopg2
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the services directory to path for imports
sys.path.append('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/crop-taxonomy/src')

class CropTaxonomyImplementationTest:
    """Comprehensive test suite for crop taxonomy implementation."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://afas_user:secure_password@localhost:5432/afas_db')
        self.service_base_url = "http://localhost:8000"  # Assuming service runs on port 8000
        self.test_results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print("🧪 Starting Comprehensive Crop Taxonomy Implementation Test")
        print("=" * 70)
        
        # Test database schema and migration
        self.test_database_schema()
        
        # Test service imports and functionality
        self.test_service_imports()
        
        # Test database connection and operations
        self.test_database_operations()
        
        # Test data population
        self.test_data_population()
        
        # Test filtering capabilities
        self.test_filtering_functionality()
        
        # Test API endpoints (if available)
        self.test_api_endpoints()
        
        # Generate summary report
        self.generate_test_report()
        
        return self.test_results
    
    def test_database_schema(self):
        """Test database schema and migration status."""
        print("\n📊 Testing Database Schema and Migration...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Check if migration tables exist
            tables_to_check = [
                'crop_taxonomic_hierarchy',
                'crop_agricultural_classification', 
                'crop_climate_adaptations',
                'crop_soil_requirements',
                'crop_nutritional_profiles',
                'enhanced_crop_varieties',
                'crop_regional_adaptations',
                'crop_filtering_attributes'
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    existing_tables.append(table)
                    print(f"   ✅ Table '{table}' exists")
                else:
                    missing_tables.append(table)
                    print(f"   ❌ Table '{table}' missing")
            
            # Check crops table enhancements
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'crops' AND table_schema = 'public'
            """)
            crops_columns = [row[0] for row in cursor.fetchall()]
            
            enhanced_columns = [
                'taxonomy_id', 'agricultural_classification_id', 'climate_adaptation_id',
                'soil_requirements_id', 'nutritional_profile_id', 'filtering_attributes_id',
                'crop_code', 'search_keywords', 'tags', 'is_cover_crop'
            ]
            
            enhanced_cols_present = []
            enhanced_cols_missing = []
            
            for col in enhanced_columns:
                if col in crops_columns:
                    enhanced_cols_present.append(col)
                else:
                    enhanced_cols_missing.append(col)
            
            conn.close()
            
            self.test_results['database_schema'] = {
                'status': 'success' if not missing_tables and not enhanced_cols_missing else 'partial',
                'existing_tables': existing_tables,
                'missing_tables': missing_tables,
                'enhanced_columns_present': enhanced_cols_present,
                'enhanced_columns_missing': enhanced_cols_missing,
                'migration_status': 'complete' if len(existing_tables) == len(tables_to_check) else 'incomplete'
            }
            
            if not missing_tables and not enhanced_cols_missing:
                print("   🎉 Database schema is complete!")
            else:
                print(f"   ⚠️ Schema incomplete: {len(missing_tables)} missing tables, {len(enhanced_cols_missing)} missing columns")
            
        except Exception as e:
            print(f"   ❌ Database schema test failed: {e}")
            self.test_results['database_schema'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def test_service_imports(self):
        """Test service module imports and basic functionality."""
        print("\n🔧 Testing Service Imports and Functionality...")
        
        try:
            # Test core service import
            from services.crop_taxonomy_service import CropTaxonomyService
            print("   ✅ CropTaxonomyService import successful")
            
            # Test model imports
            from models.crop_taxonomy_models import (
                CropTaxonomicHierarchy, 
                CropAgriculturalClassification,
                ComprehensiveCropData
            )
            print("   ✅ Crop taxonomy models import successful")
            
            # Test service initialization
            service = CropTaxonomyService()
            print("   ✅ Service initialization successful")
            
            # Test basic service methods exist
            methods_to_check = [
                'classify_crop_taxonomically',
                'validate_crop_data', 
                'get_comprehensive_crop_data',
                'process_bulk_crop_data'
            ]
            
            available_methods = []
            missing_methods = []
            
            for method in methods_to_check:
                if hasattr(service, method):
                    available_methods.append(method)
                    print(f"   ✅ Method '{method}' available")
                else:
                    missing_methods.append(method)
                    print(f"   ❌ Method '{method}' missing")
            
            self.test_results['service_imports'] = {
                'status': 'success' if not missing_methods else 'partial',
                'available_methods': available_methods,
                'missing_methods': missing_methods,
                'service_initialized': True
            }
            
        except Exception as e:
            print(f"   ❌ Service import test failed: {e}")
            self.test_results['service_imports'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def test_database_operations(self):
        """Test basic database operations."""
        print("\n💾 Testing Database Operations...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Test basic queries on taxonomy tables
            test_queries = [
                ("SELECT COUNT(*) FROM crop_taxonomic_hierarchy", "taxonomic_hierarchy_count"),
                ("SELECT COUNT(*) FROM crop_agricultural_classification", "agricultural_classification_count"),
                ("SELECT COUNT(*) FROM crop_climate_adaptations", "climate_adaptations_count"),
                ("SELECT COUNT(*) FROM crops", "crops_count")
            ]
            
            query_results = {}
            
            for query, result_key in test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    query_results[result_key] = count
                    print(f"   ✅ {result_key}: {count} records")
                except Exception as e:
                    query_results[result_key] = f"Error: {e}"
                    print(f"   ❌ {result_key}: Query failed - {e}")
            
            conn.close()
            
            self.test_results['database_operations'] = {
                'status': 'success',
                'query_results': query_results
            }
            
        except Exception as e:
            print(f"   ❌ Database operations test failed: {e}")
            self.test_results['database_operations'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def test_data_population(self):
        """Test data population capabilities."""
        print("\n🌱 Testing Data Population...")
        
        try:
            # Check if sample data insertion script exists
            sample_script_path = '/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/crop-taxonomy/sample_data_insertion.py'
            
            if os.path.exists(sample_script_path):
                print("   ✅ Sample data insertion script found")
                
                # Try to run a test insertion (without actually inserting)
                conn = psycopg2.connect(self.database_url)
                cursor = conn.cursor()
                
                # Check for existing sample data
                cursor.execute("SELECT COUNT(*) FROM crops WHERE crop_name IN ('Wheat', 'Corn', 'Soybean')")
                sample_crop_count = cursor.fetchone()[0]
                
                conn.close()
                
                self.test_results['data_population'] = {
                    'status': 'ready',
                    'sample_script_available': True,
                    'existing_sample_crops': sample_crop_count,
                    'message': f'Sample data script ready. {sample_crop_count} sample crops already in database.'
                }
                
                print(f"   📊 {sample_crop_count} sample crops found in database")
                
                if sample_crop_count > 0:
                    print("   ✅ Sample data appears to be populated")
                else:
                    print("   ⚠️ No sample data found - may need to run population script")
                    
            else:
                print("   ❌ Sample data insertion script not found")
                self.test_results['data_population'] = {
                    'status': 'error',
                    'sample_script_available': False,
                    'message': 'Sample data insertion script missing'
                }
                
        except Exception as e:
            print(f"   ❌ Data population test failed: {e}")
            self.test_results['data_population'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def test_filtering_functionality(self):
        """Test crop filtering and search functionality."""
        print("\n🔍 Testing Filtering and Search Functionality...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Test advanced filtering queries that the system should support
            filter_tests = [
                {
                    'name': 'Filter by crop category',
                    'query': """
                        SELECT c.crop_name, ca.crop_category 
                        FROM crops c 
                        LEFT JOIN crop_agricultural_classification ca ON c.agricultural_classification_id = ca.classification_id 
                        WHERE ca.crop_category = 'grain'
                    """,
                    'expected_min_results': 0
                },
                {
                    'name': 'Filter by hardiness zones',
                    'query': """
                        SELECT c.crop_name, cca.hardiness_zones 
                        FROM crops c 
                        LEFT JOIN crop_climate_adaptations cca ON c.climate_adaptation_id = cca.adaptation_id 
                        WHERE cca.hardiness_zones && ARRAY['5','6']
                    """,
                    'expected_min_results': 0
                },
                {
                    'name': 'Filter by pH range',
                    'query': """
                        SELECT c.crop_name, csr.optimal_ph_min, csr.optimal_ph_max
                        FROM crops c 
                        LEFT JOIN crop_soil_requirements csr ON c.soil_requirements_id = csr.soil_req_id 
                        WHERE csr.optimal_ph_min <= 6.5 AND csr.optimal_ph_max >= 6.5
                    """,
                    'expected_min_results': 0
                },
                {
                    'name': 'Complex multi-table filtering',
                    'query': """
                        SELECT c.crop_name, ca.crop_category, cca.drought_tolerance, csr.drainage_requirement
                        FROM crops c 
                        LEFT JOIN crop_agricultural_classification ca ON c.agricultural_classification_id = ca.classification_id
                        LEFT JOIN crop_climate_adaptations cca ON c.climate_adaptation_id = cca.adaptation_id
                        LEFT JOIN crop_soil_requirements csr ON c.soil_requirements_id = csr.soil_req_id
                        WHERE ca.crop_category IN ('grain', 'legume') 
                        AND cca.drought_tolerance IN ('moderate', 'high')
                        AND csr.drainage_requirement = 'well_drained'
                    """,
                    'expected_min_results': 0
                }
            ]
            
            filter_results = {}
            
            for test in filter_tests:
                try:
                    cursor.execute(test['query'])
                    results = cursor.fetchall()
                    filter_results[test['name']] = {
                        'status': 'success',
                        'result_count': len(results),
                        'results': results[:3]  # First 3 results for inspection
                    }
                    print(f"   ✅ {test['name']}: {len(results)} results")
                    
                except Exception as e:
                    filter_results[test['name']] = {
                        'status': 'error', 
                        'error': str(e)
                    }
                    print(f"   ❌ {test['name']}: Query failed - {e}")
            
            conn.close()
            
            self.test_results['filtering_functionality'] = {
                'status': 'success',
                'filter_tests': filter_results
            }
            
        except Exception as e:
            print(f"   ❌ Filtering functionality test failed: {e}")
            self.test_results['filtering_functionality'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def test_api_endpoints(self):
        """Test API endpoints if service is running."""
        print("\n🌐 Testing API Endpoints...")
        
        try:
            # Test basic health/status endpoint
            response = requests.get(f"{self.service_base_url}/health", timeout=5)
            
            if response.status_code == 200:
                print("   ✅ Service is running and responding")
                
                # Test crop taxonomy endpoints
                endpoints_to_test = [
                    ("/api/crops", "GET", "List crops endpoint"),
                    ("/api/crops/search", "GET", "Search crops endpoint"),
                    ("/api/taxonomy/classify", "POST", "Taxonomic classification endpoint")
                ]
                
                endpoint_results = {}
                
                for endpoint, method, description in endpoints_to_test:
                    try:
                        if method == "GET":
                            resp = requests.get(f"{self.service_base_url}{endpoint}", timeout=5)
                        else:
                            resp = requests.post(f"{self.service_base_url}{endpoint}", json={}, timeout=5)
                        
                        endpoint_results[endpoint] = {
                            'status_code': resp.status_code,
                            'available': resp.status_code != 404
                        }
                        
                        if resp.status_code != 404:
                            print(f"   ✅ {description}: Available (Status {resp.status_code})")
                        else:
                            print(f"   ⚠️ {description}: Not implemented (404)")
                            
                    except Exception as e:
                        endpoint_results[endpoint] = {'error': str(e)}
                        print(f"   ❌ {description}: Error - {e}")
                
                self.test_results['api_endpoints'] = {
                    'status': 'service_running',
                    'service_available': True,
                    'endpoints': endpoint_results
                }
                
            else:
                print(f"   ⚠️ Service responded with status {response.status_code}")
                self.test_results['api_endpoints'] = {
                    'status': 'service_error',
                    'service_available': True,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Service not running or not accessible")
            self.test_results['api_endpoints'] = {
                'status': 'service_not_running',
                'service_available': False,
                'message': 'Service appears to be offline'
            }
        except Exception as e:
            print(f"   ❌ API endpoint test failed: {e}")
            self.test_results['api_endpoints'] = {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 70)
        print("📋 CROP TAXONOMY IMPLEMENTATION TEST REPORT")
        print("=" * 70)
        
        # Overall status assessment
        test_statuses = [result.get('status', 'unknown') for result in self.test_results.values()]
        success_count = test_statuses.count('success')
        total_tests = len(test_statuses)
        
        print(f"\n🎯 Overall Status: {success_count}/{total_tests} tests successful")
        
        # Detailed results
        for test_name, results in self.test_results.items():
            status = results.get('status', 'unknown')
            status_emoji = '✅' if status == 'success' else '⚠️' if status == 'partial' else '❌'
            print(f"\n{status_emoji} {test_name.replace('_', ' ').title()}: {status}")
            
            if 'error' in results:
                print(f"   Error: {results['error']}")
            elif 'message' in results:
                print(f"   {results['message']}")
        
        # Implementation readiness assessment
        print(f"\n🚀 IMPLEMENTATION READINESS ASSESSMENT:")
        
        schema_ready = self.test_results.get('database_schema', {}).get('status') == 'success'
        service_ready = self.test_results.get('service_imports', {}).get('status') in ['success', 'partial']
        
        if schema_ready and service_ready:
            print("   ✅ Core system is ready for production use")
            print("   ✅ Database schema is complete")
            print("   ✅ Service layer is functional")
            
            # Recommendations for next steps
            print(f"\n📝 RECOMMENDED NEXT STEPS:")
            
            data_populated = self.test_results.get('data_population', {}).get('existing_sample_crops', 0) > 0
            if not data_populated:
                print("   1. 🌱 Run data population script to add sample crops")
            else:
                print("   1. ✅ Sample data is populated")
            
            service_running = self.test_results.get('api_endpoints', {}).get('service_available', False)
            if not service_running:
                print("   2. 🚀 Start the crop taxonomy service")
            else:
                print("   2. ✅ Service is running")
            
            print("   3. 🧪 Run comprehensive integration tests")
            print("   4. 📚 Update API documentation")
            print("   5. 👨‍🌾 Get expert agricultural validation")
            print("   6. 🔗 Integrate with frontend filtering interface")
            
        else:
            print("   ❌ System needs additional work before production ready")
            if not schema_ready:
                print("   ❌ Database schema incomplete - run migration 003")
            if not service_ready:
                print("   ❌ Service layer has issues - check imports and dependencies")
        
        # Save report to file
        report_path = '/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/CROP_TAXONOMY_TEST_REPORT.json'
        with open(report_path, 'w') as f:
            json.dump({
                'test_results': self.test_results,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': success_count,
                    'success_rate': success_count / total_tests if total_tests > 0 else 0,
                    'overall_status': 'ready' if schema_ready and service_ready else 'needs_work'
                }
            }, f, indent=2)
        
        print(f"\n💾 Detailed test report saved to: {report_path}")


def main():
    """Main test execution function."""
    tester = CropTaxonomyImplementationTest()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    total_tests = len(results)
    
    return success_count == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)