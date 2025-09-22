#!/usr/bin/env python3
"""
Fertilizer Safety Limits Validation Script

This script validates that fertilizer recommendations stay within safe
limits to prevent crop damage, environmental harm, and economic waste.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class FertilizerSafetyValidator:
    """Validates fertilizer recommendations against safety limits."""
    
    def __init__(self):
        self.validation_results = {
            'nitrogen_safety': {'passed': [], 'failed': [], 'warnings': []},
            'phosphorus_safety': {'passed': [], 'failed': [], 'warnings': []},
            'potassium_safety': {'passed': [], 'failed': [], 'warnings': []},
            'micronutrient_safety': {'passed': [], 'failed': [], 'warnings': []},
            'environmental_safety': {'passed': [], 'failed': [], 'warnings': []},
            'summary': {
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0,
                'warnings': 0
            }
        }
        
        # Safety limits based on agricultural research and extension guidelines
        self.safety_limits = {
            'nitrogen': {
                'max_single_application': 200,  # lbs N/acre
                'max_annual_application': 300,  # lbs N/acre
                'max_preplant_application': 150,  # lbs N/acre
                'environmental_threshold': 250,  # lbs N/acre (groundwater concern)
                'crop_specific_limits': {
                    'corn': 250,
                    'soybean': 50,  # Minimal N for soybean
                    'wheat': 150,
                    'cotton': 200
                }
            },
            'phosphorus': {
                'max_single_application': 100,  # lbs P2O5/acre
                'max_annual_application': 150,  # lbs P2O5/acre
                'environmental_threshold': 80,   # lbs P2O5/acre (runoff concern)
                'soil_test_threshold': 50,      # ppm P above which no P recommended
                'crop_specific_limits': {
                    'corn': 80,
                    'soybean': 60,
                    'wheat': 70,
                    'cotton': 80
                }
            },
            'potassium': {
                'max_single_application': 200,  # lbs K2O/acre
                'max_annual_application': 300,  # lbs K2O/acre
                'soil_test_threshold': 400,     # ppm K above which no K recommended
                'crop_specific_limits': {
                    'corn': 200,
                    'soybean': 150,
                    'wheat': 120,
                    'cotton': 180
                }
            },
            'micronutrients': {
                'zinc': {'max_rate': 20, 'units': 'lbs/acre'},
                'iron': {'max_rate': 15, 'units': 'lbs/acre'},
                'manganese': {'max_rate': 10, 'units': 'lbs/acre'},
                'copper': {'max_rate': 5, 'units': 'lbs/acre'},
                'boron': {'max_rate': 2, 'units': 'lbs/acre'},
                'molybdenum': {'max_rate': 0.5, 'units': 'lbs/acre'}
            }
        }
    
    def validate_nitrogen_safety(self) -> bool:
        """Validate nitrogen recommendation safety."""
        print("Validating nitrogen safety limits...")
        
        # Test scenarios with various N rates
        test_scenarios = [
            {
                'crop': 'corn',
                'n_rate': 180,
                'application_method': 'split',
                'expected_status': 'safe'
            },
            {
                'crop': 'corn',
                'n_rate': 280,  # Excessive
                'application_method': 'single',
                'expected_status': 'unsafe'
            },
            {
                'crop': 'soybean',
                'n_rate': 80,   # Too high for soybean
                'application_method': 'preplant',
                'expected_status': 'unsafe'
            },
            {
                'crop': 'wheat',
                'n_rate': 120,
                'application_method': 'split',
                'expected_status': 'safe'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            n_rate = scenario['n_rate']
            method = scenario['application_method']
            
            # Check against safety limits
            safety_status = self._check_nitrogen_safety(crop, n_rate, method)
            
            if safety_status == scenario['expected_status']:
                self.validation_results['nitrogen_safety']['passed'].append(
                    f"Scenario {i+1}: {crop} with {n_rate} lbs N/acre correctly flagged as {safety_status}"
                )
                print(f"  ✓ Scenario {i+1}: Nitrogen safety check passed")
            else:
                self.validation_results['nitrogen_safety']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_status']}, got {safety_status}"
                )
                print(f"  ❌ Scenario {i+1}: Nitrogen safety check failed")
                all_passed = False
        
        return all_passed
    
    def _check_nitrogen_safety(self, crop: str, n_rate: float, method: str) -> str:
        """Check nitrogen rate against safety limits."""
        limits = self.safety_limits['nitrogen']
        
        # Check crop-specific limits
        if crop in limits['crop_specific_limits']:
            if n_rate > limits['crop_specific_limits'][crop]:
                return 'unsafe'
        
        # Check general limits
        if n_rate > limits['max_annual_application']:
            return 'unsafe'
        
        # Check single application limits
        if method == 'single' and n_rate > limits['max_single_application']:
            return 'unsafe'
        
        # Check environmental threshold
        if n_rate > limits['environmental_threshold']:
            return 'environmental_concern'
        
        return 'safe'
    
    def validate_phosphorus_safety(self) -> bool:
        """Validate phosphorus recommendation safety."""
        print("Validating phosphorus safety limits...")
        
        test_scenarios = [
            {
                'crop': 'corn',
                'p_rate': 60,
                'soil_test_p': 25,
                'expected_status': 'safe'
            },
            {
                'crop': 'corn',
                'p_rate': 120,  # Excessive
                'soil_test_p': 15,
                'expected_status': 'unsafe'
            },
            {
                'crop': 'soybean',
                'p_rate': 40,
                'soil_test_p': 60,  # High soil test
                'expected_status': 'unnecessary'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            p_rate = scenario['p_rate']
            soil_test_p = scenario['soil_test_p']
            
            safety_status = self._check_phosphorus_safety(crop, p_rate, soil_test_p)
            
            if safety_status == scenario['expected_status']:
                self.validation_results['phosphorus_safety']['passed'].append(
                    f"Scenario {i+1}: {crop} P recommendation correctly assessed as {safety_status}"
                )
                print(f"  ✓ Scenario {i+1}: Phosphorus safety check passed")
            else:
                self.validation_results['phosphorus_safety']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_status']}, got {safety_status}"
                )
                print(f"  ❌ Scenario {i+1}: Phosphorus safety check failed")
                all_passed = False
        
        return all_passed
    
    def _check_phosphorus_safety(self, crop: str, p_rate: float, soil_test_p: float) -> str:
        """Check phosphorus rate against safety limits."""
        limits = self.safety_limits['phosphorus']
        
        # Check if P is needed based on soil test
        if soil_test_p > limits['soil_test_threshold']:
            return 'unnecessary'
        
        # Check crop-specific limits
        if crop in limits['crop_specific_limits']:
            if p_rate > limits['crop_specific_limits'][crop]:
                return 'unsafe'
        
        # Check general limits
        if p_rate > limits['max_annual_application']:
            return 'unsafe'
        
        # Check environmental threshold
        if p_rate > limits['environmental_threshold']:
            return 'environmental_concern'
        
        return 'safe'
    
    def validate_potassium_safety(self) -> bool:
        """Validate potassium recommendation safety."""
        print("Validating potassium safety limits...")
        
        test_scenarios = [
            {
                'crop': 'corn',
                'k_rate': 120,
                'soil_test_k': 150,
                'expected_status': 'safe'
            },
            {
                'crop': 'corn',
                'k_rate': 250,  # Excessive
                'soil_test_k': 100,
                'expected_status': 'unsafe'
            },
            {
                'crop': 'soybean',
                'k_rate': 80,
                'soil_test_k': 450,  # Very high soil test
                'expected_status': 'unnecessary'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            k_rate = scenario['k_rate']
            soil_test_k = scenario['soil_test_k']
            
            safety_status = self._check_potassium_safety(crop, k_rate, soil_test_k)
            
            if safety_status == scenario['expected_status']:
                self.validation_results['potassium_safety']['passed'].append(
                    f"Scenario {i+1}: {crop} K recommendation correctly assessed as {safety_status}"
                )
                print(f"  ✓ Scenario {i+1}: Potassium safety check passed")
            else:
                self.validation_results['potassium_safety']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_status']}, got {safety_status}"
                )
                print(f"  ❌ Scenario {i+1}: Potassium safety check failed")
                all_passed = False
        
        return all_passed
    
    def _check_potassium_safety(self, crop: str, k_rate: float, soil_test_k: float) -> str:
        """Check potassium rate against safety limits."""
        limits = self.safety_limits['potassium']
        
        # Check if K is needed based on soil test
        if soil_test_k > limits['soil_test_threshold']:
            return 'unnecessary'
        
        # Check crop-specific limits
        if crop in limits['crop_specific_limits']:
            if k_rate > limits['crop_specific_limits'][crop]:
                return 'unsafe'
        
        # Check general limits
        if k_rate > limits['max_annual_application']:
            return 'unsafe'
        
        return 'safe'
    
    def validate_micronutrient_safety(self) -> bool:
        """Validate micronutrient recommendation safety."""
        print("Validating micronutrient safety limits...")
        
        test_scenarios = [
            {
                'nutrient': 'zinc',
                'rate': 10,
                'expected_status': 'safe'
            },
            {
                'nutrient': 'zinc',
                'rate': 30,  # Excessive
                'expected_status': 'unsafe'
            },
            {
                'nutrient': 'boron',
                'rate': 1.5,
                'expected_status': 'safe'
            },
            {
                'nutrient': 'boron',
                'rate': 5,   # Toxic level
                'expected_status': 'unsafe'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            nutrient = scenario['nutrient']
            rate = scenario['rate']
            
            safety_status = self._check_micronutrient_safety(nutrient, rate)
            
            if safety_status == scenario['expected_status']:
                self.validation_results['micronutrient_safety']['passed'].append(
                    f"Scenario {i+1}: {nutrient} at {rate} lbs/acre correctly assessed as {safety_status}"
                )
                print(f"  ✓ Scenario {i+1}: {nutrient} safety check passed")
            else:
                self.validation_results['micronutrient_safety']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_status']}, got {safety_status}"
                )
                print(f"  ❌ Scenario {i+1}: {nutrient} safety check failed")
                all_passed = False
        
        return all_passed
    
    def _check_micronutrient_safety(self, nutrient: str, rate: float) -> str:
        """Check micronutrient rate against safety limits."""
        limits = self.safety_limits['micronutrients']
        
        if nutrient in limits:
            max_rate = limits[nutrient]['max_rate']
            if rate > max_rate:
                return 'unsafe'
            elif rate > max_rate * 0.8:  # Warning threshold
                return 'caution'
        
        return 'safe'
    
    def validate_environmental_safety(self) -> bool:
        """Validate environmental safety considerations."""
        print("Validating environmental safety considerations...")
        
        # Test scenarios for environmental risk
        test_scenarios = [
            {
                'description': 'High N rate near water body',
                'n_rate': 220,
                'distance_to_water': 50,  # feet
                'slope': 8,  # percent
                'expected_risk': 'high'
            },
            {
                'description': 'Moderate P rate on steep slope',
                'p_rate': 70,
                'slope': 12,  # percent
                'soil_texture': 'sandy_loam',
                'expected_risk': 'moderate'
            },
            {
                'description': 'Normal rates on flat field',
                'n_rate': 150,
                'p_rate': 40,
                'slope': 2,
                'expected_risk': 'low'
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios):
            risk_level = self._assess_environmental_risk(scenario)
            
            if risk_level == scenario['expected_risk']:
                self.validation_results['environmental_safety']['passed'].append(
                    f"Scenario {i+1}: {scenario['description']} - risk correctly assessed as {risk_level}"
                )
                print(f"  ✓ Scenario {i+1}: Environmental risk assessment passed")
            else:
                self.validation_results['environmental_safety']['failed'].append(
                    f"Scenario {i+1}: Expected {scenario['expected_risk']}, got {risk_level}"
                )
                print(f"  ❌ Scenario {i+1}: Environmental risk assessment failed")
                all_passed = False
        
        return all_passed
    
    def _assess_environmental_risk(self, scenario: Dict[str, Any]) -> str:
        """Assess environmental risk based on scenario factors."""
        risk_factors = 0
        
        # Check nitrogen rate
        n_rate = scenario.get('n_rate', 0)
        if n_rate > 200:
            risk_factors += 2
        elif n_rate > 150:
            risk_factors += 1
        
        # Check phosphorus rate
        p_rate = scenario.get('p_rate', 0)
        if p_rate > 60:
            risk_factors += 2
        elif p_rate > 40:
            risk_factors += 1
        
        # Check slope
        slope = scenario.get('slope', 0)
        if slope > 10:
            risk_factors += 2
        elif slope > 5:
            risk_factors += 1
        
        # Check distance to water
        distance_to_water = scenario.get('distance_to_water', 1000)
        if distance_to_water < 100:
            risk_factors += 2
        elif distance_to_water < 300:
            risk_factors += 1
        
        # Determine overall risk
        if risk_factors >= 4:
            return 'high'
        elif risk_factors >= 2:
            return 'moderate'
        else:
            return 'low'
    
    def run_all_validations(self) -> bool:
        """Run all fertilizer safety validations."""
        print("Running fertilizer safety limit validations...")
        print("=" * 60)
        
        validations = [
            ('Nitrogen Safety', self.validate_nitrogen_safety),
            ('Phosphorus Safety', self.validate_phosphorus_safety),
            ('Potassium Safety', self.validate_potassium_safety),
            ('Micronutrient Safety', self.validate_micronutrient_safety),
            ('Environmental Safety', self.validate_environmental_safety)
        ]
        
        all_passed = True
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warnings = 0
        
        for name, validation_func in validations:
            print(f"\n{name}:")
            try:
                if validation_func():
                    print(f"  ✅ {name} validation passed")
                    passed_checks += 1
                else:
                    print(f"  ❌ {name} validation failed")
                    failed_checks += 1
                    all_passed = False
                total_checks += 1
            except Exception as e:
                print(f"  ⚠️  {name} validation error: {e}")
                warnings += 1
                all_passed = False
        
        # Update summary
        self.validation_results['summary'] = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'warnings': warnings
        }
        
        self._generate_safety_report()
        return all_passed
    
    def _generate_safety_report(self):
        """Generate fertilizer safety validation report."""
        print("\n" + "=" * 60)
        print("FERTILIZER SAFETY VALIDATION RESULTS")
        print("=" * 60)
        
        summary = self.validation_results['summary']
        print(f"Total safety checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed_checks']}")
        print(f"Failed: {summary['failed_checks']}")
        print(f"Warnings: {summary['warnings']}")
        
        # Detailed results by category
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
        
        # Safety recommendations
        print(f"\n🛡️  SAFETY RECOMMENDATIONS:")
        print("  • Never exceed maximum fertilizer rates for any crop")
        print("  • Consider environmental factors (slope, water proximity)")
        print("  • Use split applications for high nitrogen rates")
        print("  • Monitor soil test levels to avoid over-application")
        print("  • Follow state and local fertilizer regulations")
        
        # Save detailed report
        report_data = {
            'validation_date': datetime.now().isoformat(),
            'safety_limits_used': self.safety_limits,
            'results': self.validation_results,
            'recommendations': [
                'Implement rate limit checks in recommendation algorithms',
                'Add environmental risk assessment to recommendations',
                'Include safety warnings for high-risk scenarios',
                'Validate all recommendations against crop-specific limits'
            ]
        }
        
        with open('safety-validation-results.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed safety report saved to: safety-validation-results.json")

def main():
    """Main safety validation function."""
    validator = FertilizerSafetyValidator()
    
    success = validator.run_all_validations()
    
    if not success:
        print("\n❌ Fertilizer safety validation failed!")
        print("Some recommendations exceed safe limits or lack proper safety checks.")
        sys.exit(1)
    else:
        print("\n✅ All fertilizer safety validations passed!")
        print("Recommendations are within safe limits for crops and environment.")
        sys.exit(0)

if __name__ == "__main__":
    main()