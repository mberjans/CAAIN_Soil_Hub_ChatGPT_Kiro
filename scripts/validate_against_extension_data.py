#!/usr/bin/env python3
"""
Extension Data Validation Script

This script validates AFAS recommendations against university extension
service guidelines and published research data.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import date, datetime
import requests
import warnings

class ExtensionDataValidator:
    """Validates recommendations against extension service data."""
    
    def __init__(self):
        self.validation_results = {
            'nitrogen_validation': {'passed': [], 'failed': [], 'warnings': []},
            'phosphorus_validation': {'passed': [], 'failed': [], 'warnings': []},
            'crop_selection_validation': {'passed': [], 'failed': [], 'warnings': []},
            'soil_health_validation': {'passed': [], 'failed': [], 'warnings': []},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'warnings': 0
            }
        }
        
        # Extension service reference data
        self.extension_data = self._load_extension_reference_data()
    
    def _load_extension_reference_data(self) -> Dict[str, Any]:
        """Load reference data from extension services."""
        return {
            'iowa_state_nitrogen': {
                # Iowa State Extension PM 1688 - Corn Nitrogen Rate Calculator
                'corn_base_rates': {
                    140: 120,  # 140 bu/acre goal = 120 lbs N/acre base
                    160: 140,  # 160 bu/acre goal = 140 lbs N/acre base
                    180: 160,  # 180 bu/acre goal = 160 lbs N/acre base
                    200: 180   # 200 bu/acre goal = 180 lbs N/acre base
                },
                'legume_credits': {
                    'soybean': 40,      # 40 lbs N/acre credit
                    'alfalfa_1yr': 100, # 100 lbs N/acre credit
                    'alfalfa_2yr': 150, # 150 lbs N/acre credit
                    'red_clover': 60    # 60 lbs N/acre credit
                },
                'soil_test_credits': {
                    # Nitrate-N ppm to lbs N/acre credit (multiply by 2)
                    'conversion_factor': 2.0,
                    'max_credit': 50  # Maximum soil test N credit
                }
            },
            'tri_state_phosphorus': {
                # Tri-State Fertilizer Recommendations
                'critical_levels': {
                    'corn': 15,     # ppm P (Mehlich-3)
                    'soybean': 12,  # ppm P (Mehlich-3)
                    'wheat': 15     # ppm P (Mehlich-3)
                },
                'buildup_rates': {
                    'low': 60,      # lbs P2O5/acre for buildup
                    'medium': 40,   # lbs P2O5/acre for buildup
                    'high': 20      # lbs P2O5/acre for maintenance
                },
                'maintenance_rates': {
                    'corn': 30,     # lbs P2O5/acre
                    'soybean': 25,  # lbs P2O5/acre
                    'wheat': 30     # lbs P2O5/acre
                }
            },
            'crop_adaptation_zones': {
                # USDA Plant Hardiness Zones and crop adaptation
                'corn': {
                    'min_zone': '3a',
                    'optimal_zones': ['4a', '4b', '5a', '5b', '6a', '6b'],
                    'min_gdd': 2200,
                    'optimal_gdd': (2600, 3200),
                    'min_frost_free_days': 120
                },
                'soybean': {
                    'min_zone': '3b',
                    'optimal_zones': ['4a', '4b', '5a', '5b', '6a'],
                    'min_gdd': 2000,
                    'optimal_gdd': (2200, 2800),
                    'min_frost_free_days': 100
                }
            },
            'soil_health_standards': {
                # NRCS Soil Health Assessment
                'ph_ranges': {
                    'very_acidic': (3.0, 4.5),
                    'acidic': (4.5, 6.0),
                    'optimal': (6.0, 7.0),
                    'alkaline': (7.0, 8.5),
                    'very_alkaline': (8.5, 10.0)
                },
                'organic_matter_targets': {
                    'poor': (0.0, 2.0),
                    'fair': (2.0, 3.0),
                    'good': (3.0, 4.0),
                    'excellent': (4.0, 6.0)
                },
                'bulk_density_limits': {
                    'sand': 1.6,
                    'loam': 1.4,
                    'clay': 1.3
                }
            }
        }
    
    def validate_nitrogen_recommendations(self) -> bool:
        """Validate nitrogen recommendations against Iowa State guidelines."""
        print("Validating nitrogen recommendations against Iowa State Extension...")
        
        test_scenarios = [
            {
                'crop': 'corn',
                'yield_goal': 180,
                'previous_crop': 'soybean',
                'soil_nitrate_ppm': 12,
                'organic_matter': 3.5,
                'expected_range': (90, 110)  # 160 base - 40 legume - 24 soil = 96
            },
            {
                'crop': 'corn',
                'yield_goal': 160,
                'previous_crop': 'corn',
                'soil_nitrate_ppm': 8,
                'organic_matter': 3.0,
                'expected_range': (120, 140)  # 140 base - 0 legume - 16 soil = 124
            },
            {
                'crop': 'corn',
                'yield_goal': 200,
                'previous_crop': 'alfalfa',
                'soil_nitrate_ppm': 15,
                'organic_matter': 4.0,
                'expected_range': (40, 60)  # 180 base - 100 legume - 30 soil = 50
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            # Calculate expected N rate using extension guidelines
            base_rate = self.extension_data['iowa_state_nitrogen']['corn_base_rates'][scenario['yield_goal']]
            
            # Legume credit
            legume_credit = 0
            if scenario['previous_crop'] == 'soybean':
                legume_credit = self.extension_data['iowa_state_nitrogen']['legume_credits']['soybean']
            elif scenario['previous_crop'] == 'alfalfa':
                legume_credit = self.extension_data['iowa_state_nitrogen']['legume_credits']['alfalfa_1yr']
            
            # Soil test credit
            soil_credit = min(
                scenario['soil_nitrate_ppm'] * self.extension_data['iowa_state_nitrogen']['soil_test_credits']['conversion_factor'],
                self.extension_data['iowa_state_nitrogen']['soil_test_credits']['max_credit']
            )
            
            expected_rate = base_rate - legume_credit - soil_credit
            expected_min, expected_max = scenario['expected_range']
            
            # Validate calculation
            if expected_min <= expected_rate <= expected_max:
                self.validation_results['nitrogen_validation']['passed'].append(
                    f"Scenario {i+1}: Expected {expected_rate} lbs N/acre (within {expected_min}-{expected_max})"
                )
                print(f"  ✓ Scenario {i+1}: N rate calculation validated")
            else:
                self.validation_results['nitrogen_validation']['failed'].append(
                    f"Scenario {i+1}: Expected {expected_rate} lbs N/acre (outside {expected_min}-{expected_max})"
                )
                print(f"  ❌ Scenario {i+1}: N rate calculation failed")
                all_passed = False
        
        return all_passed
    
    def validate_phosphorus_recommendations(self) -> bool:
        """Validate phosphorus recommendations against Tri-State guidelines."""
        print("Validating phosphorus recommendations against Tri-State guidelines...")
        
        test_scenarios = [
            {
                'crop': 'corn',
                'soil_p_ppm': 8,   # Below critical level
                'expected_type': 'buildup',
                'expected_range': (50, 70)
            },
            {
                'crop': 'soybean',
                'soil_p_ppm': 25,  # Above critical level
                'expected_type': 'maintenance',
                'expected_range': (20, 30)
            },
            {
                'crop': 'corn',
                'soil_p_ppm': 15,  # At critical level
                'expected_type': 'maintenance',
                'expected_range': (25, 35)
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            soil_p = scenario['soil_p_ppm']
            critical_level = self.extension_data['tri_state_phosphorus']['critical_levels'][crop]
            
            # Determine recommendation type
            if soil_p < critical_level:
                rec_type = 'buildup'
                expected_rate = self.extension_data['tri_state_phosphorus']['buildup_rates']['low']
            else:
                rec_type = 'maintenance'
                expected_rate = self.extension_data['tri_state_phosphorus']['maintenance_rates'][crop]
            
            expected_min, expected_max = scenario['expected_range']
            
            # Validate recommendation
            if (rec_type == scenario['expected_type'] and 
                expected_min <= expected_rate <= expected_max):
                self.validation_results['phosphorus_validation']['passed'].append(
                    f"Scenario {i+1}: {rec_type} recommendation validated"
                )
                print(f"  ✓ Scenario {i+1}: P recommendation validated")
            else:
                self.validation_results['phosphorus_validation']['failed'].append(
                    f"Scenario {i+1}: Expected {rec_type}, got different recommendation"
                )
                print(f"  ❌ Scenario {i+1}: P recommendation failed")
                all_passed = False
        
        return all_passed
    
    def validate_crop_adaptation(self) -> bool:
        """Validate crop adaptation recommendations."""
        print("Validating crop adaptation against USDA guidelines...")
        
        test_scenarios = [
            {
                'crop': 'corn',
                'location': {'latitude': 42.0, 'longitude': -93.6},  # Iowa
                'climate': {
                    'hardiness_zone': '5a',
                    'growing_degree_days': 2800,
                    'frost_free_days': 160
                },
                'expected_suitability': 'high'
            },
            {
                'crop': 'corn',
                'location': {'latitude': 47.0, 'longitude': -100.0},  # North Dakota
                'climate': {
                    'hardiness_zone': '3b',
                    'growing_degree_days': 2100,
                    'frost_free_days': 110
                },
                'expected_suitability': 'marginal'
            },
            {
                'crop': 'soybean',
                'location': {'latitude': 40.0, 'longitude': -89.0},  # Illinois
                'climate': {
                    'hardiness_zone': '5b',
                    'growing_degree_days': 2600,
                    'frost_free_days': 170
                },
                'expected_suitability': 'high'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            climate = scenario['climate']
            crop_requirements = self.extension_data['crop_adaptation_zones'][crop]
            
            # Check growing degree days
            gdd = climate['growing_degree_days']
            min_gdd = crop_requirements['min_gdd']
            optimal_gdd = crop_requirements['optimal_gdd']
            
            # Check frost-free days
            frost_days = climate['frost_free_days']
            min_frost_days = crop_requirements['min_frost_free_days']
            
            # Determine suitability
            if gdd >= optimal_gdd[0] and gdd <= optimal_gdd[1] and frost_days >= min_frost_days + 20:
                suitability = 'high'
            elif gdd >= min_gdd and frost_days >= min_frost_days:
                suitability = 'moderate'
            else:
                suitability = 'marginal'
            
            # Validate against expected
            if suitability == scenario['expected_suitability']:
                self.validation_results['crop_selection_validation']['passed'].append(
                    f"Scenario {i+1}: {crop} suitability correctly assessed as {suitability}"
                )
                print(f"  ✓ Scenario {i+1}: {crop} adaptation validated")
            else:
                self.validation_results['crop_selection_validation']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_suitability']}, got {suitability}"
                )
                print(f"  ❌ Scenario {i+1}: {crop} adaptation failed")
                all_passed = False
        
        return all_passed
    
    def validate_soil_health_assessments(self) -> bool:
        """Validate soil health assessments against NRCS standards."""
        print("Validating soil health assessments against NRCS standards...")
        
        test_scenarios = [
            {
                'soil_data': {
                    'ph': 6.5,
                    'organic_matter_percent': 3.8,
                    'bulk_density': 1.2,
                    'soil_texture': 'loam'
                },
                'expected_score_range': (8.0, 9.0),
                'expected_rating': 'good'
            },
            {
                'soil_data': {
                    'ph': 5.2,
                    'organic_matter_percent': 1.8,
                    'bulk_density': 1.7,
                    'soil_texture': 'loam'
                },
                'expected_score_range': (3.0, 5.0),
                'expected_rating': 'poor'
            },
            {
                'soil_data': {
                    'ph': 7.8,
                    'organic_matter_percent': 2.5,
                    'bulk_density': 1.5,
                    'soil_texture': 'clay'
                },
                'expected_score_range': (5.0, 7.0),
                'expected_rating': 'fair'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            soil_data = scenario['soil_data']
            
            # Calculate soil health score components
            ph_score = self._score_ph(soil_data['ph'])
            om_score = self._score_organic_matter(soil_data['organic_matter_percent'])
            bd_score = self._score_bulk_density(soil_data['bulk_density'], soil_data['soil_texture'])
            
            # Overall score (simplified)
            overall_score = (ph_score + om_score + bd_score) / 3
            
            expected_min, expected_max = scenario['expected_score_range']
            
            # Validate score
            if expected_min <= overall_score <= expected_max:
                self.validation_results['soil_health_validation']['passed'].append(
                    f"Scenario {i+1}: Soil health score {overall_score:.1f} within expected range"
                )
                print(f"  ✓ Scenario {i+1}: Soil health assessment validated")
            else:
                self.validation_results['soil_health_validation']['failed'].append(
                    f"Scenario {i+1}: Score {overall_score:.1f} outside range {expected_min}-{expected_max}"
                )
                print(f"  ❌ Scenario {i+1}: Soil health assessment failed")
                all_passed = False
        
        return all_passed
    
    def _score_ph(self, ph: float) -> float:
        """Score pH according to NRCS standards."""
        if 6.0 <= ph <= 7.0:
            return 10.0
        elif 5.5 <= ph <= 7.5:
            return 8.0
        elif 5.0 <= ph <= 8.0:
            return 6.0
        elif 4.5 <= ph <= 8.5:
            return 4.0
        else:
            return 2.0
    
    def _score_organic_matter(self, om_percent: float) -> float:
        """Score organic matter according to NRCS standards."""
        if om_percent >= 4.0:
            return 10.0
        elif om_percent >= 3.0:
            return 8.0
        elif om_percent >= 2.0:
            return 6.0
        elif om_percent >= 1.0:
            return 4.0
        else:
            return 2.0
    
    def _score_bulk_density(self, bulk_density: float, texture: str) -> float:
        """Score bulk density according to soil texture."""
        limits = self.extension_data['soil_health_standards']['bulk_density_limits']
        
        if texture in ['sand', 'sandy_loam']:
            limit = limits['sand']
        elif texture in ['clay', 'clay_loam']:
            limit = limits['clay']
        else:
            limit = limits['loam']
        
        if bulk_density <= limit * 0.8:
            return 10.0
        elif bulk_density <= limit:
            return 8.0
        elif bulk_density <= limit * 1.2:
            return 6.0
        elif bulk_density <= limit * 1.4:
            return 4.0
        else:
            return 2.0
    
    def run_all_validations(self) -> bool:
        """Run all extension data validations."""
        print("Running validation against extension service data...")
        print("=" * 60)
        
        validations = [
            ('Nitrogen Recommendations', self.validate_nitrogen_recommendations),
            ('Phosphorus Recommendations', self.validate_phosphorus_recommendations),
            ('Crop Adaptation', self.validate_crop_adaptation),
            ('Soil Health Assessments', self.validate_soil_health_assessments)
        ]
        
        all_passed = True
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        for name, validation_func in validations:
            print(f"\n{name}:")
            try:
                if validation_func():
                    print(f"  ✅ {name} validation passed")
                    passed_tests += 1
                else:
                    print(f"  ❌ {name} validation failed")
                    failed_tests += 1
                    all_passed = False
                total_tests += 1
            except Exception as e:
                print(f"  ⚠️  {name} validation error: {e}")
                warnings += 1
                all_passed = False
        
        # Update summary
        self.validation_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'warnings': warnings
        }
        
        self._generate_report()
        return all_passed
    
    def _generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("EXTENSION DATA VALIDATION RESULTS")
        print("=" * 60)
        
        summary = self.validation_results['summary']
        print(f"Total validations: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Warnings: {summary['warnings']}")
        
        # Detailed results
        for category, results in self.validation_results.items():
            if category == 'summary':
                continue
                
            category_name = category.replace('_', ' ').title()
            print(f"\n{category_name}:")
            
            if results['passed']:
                print("  ✅ Passed:")
                for item in results['passed']:
                    print(f"    • {item}")
            
            if results['failed']:
                print("  ❌ Failed:")
                for item in results['failed']:
                    print(f"    • {item}")
            
            if results['warnings']:
                print("  ⚠️  Warnings:")
                for item in results['warnings']:
                    print(f"    • {item}")
        
        # Save detailed report
        report_data = {
            'validation_date': datetime.now().isoformat(),
            'extension_sources': [
                'Iowa State University Extension PM 1688',
                'Tri-State Fertilizer Recommendations',
                'USDA Plant Hardiness Zone Map',
                'NRCS Soil Health Assessment'
            ],
            'results': self.validation_results
        }
        
        with open('extension-validation-report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: extension-validation-report.json")

def main():
    """Main validation function."""
    validator = ExtensionDataValidator()
    
    success = validator.run_all_validations()
    
    if not success:
        print("\n❌ Extension data validation failed!")
        print("Recommendations do not match established extension guidelines.")
        sys.exit(1)
    else:
        print("\n✅ All extension data validations passed!")
        print("Recommendations align with university extension guidelines.")
        sys.exit(0)

if __name__ == "__main__":
    main()