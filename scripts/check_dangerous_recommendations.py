#!/usr/bin/env python3
"""
Dangerous Recommendations Detection Script

This script checks for potentially dangerous agricultural recommendations
that could harm crops, soil, environment, or farmer safety.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class DangerousRecommendationDetector:
    """Detects potentially dangerous agricultural recommendations."""
    
    def __init__(self):
        self.detection_results = {
            'crop_damage_risks': [],
            'environmental_hazards': [],
            'soil_health_threats': [],
            'economic_risks': [],
            'safety_violations': [],
            'regulatory_violations': [],
            'summary': {
                'total_risks_detected': 0,
                'critical_risks': 0,
                'high_risks': 0,
                'medium_risks': 0,
                'low_risks': 0
            }
        }
        
        # Define dangerous recommendation patterns
        self.danger_patterns = {
            'excessive_fertilizer_rates': {
                'nitrogen': {
                    'critical_threshold': 300,  # lbs N/acre
                    'high_threshold': 250,
                    'crop_specific': {
                        'soybean': 30,  # Soybean rarely needs N
                        'legumes': 40
                    }
                },
                'phosphorus': {
                    'critical_threshold': 150,  # lbs P2O5/acre
                    'high_threshold': 100
                },
                'potassium': {
                    'critical_threshold': 300,  # lbs K2O/acre
                    'high_threshold': 250
                }
            },
            'dangerous_chemical_combinations': [
                {'chemicals': ['lime', 'ammonium_sulfate'], 'risk': 'ammonia_volatilization'},
                {'chemicals': ['urea', 'lime'], 'risk': 'nitrogen_loss'},
                {'chemicals': ['iron_sulfate', 'lime'], 'risk': 'iron_precipitation'}
            ],
            'environmental_hazards': {
                'water_contamination_risk': {
                    'high_nitrogen_near_water': 150,  # lbs N/acre within 100ft of water
                    'phosphorus_on_slopes': 50,      # lbs P2O5/acre on >5% slope
                    'application_before_rain': True   # Flag applications before predicted rain
                },
                'soil_acidification_risk': {
                    'excessive_sulfur': 500,  # lbs S/acre
                    'ammonium_fertilizers_low_ph': 5.5  # pH threshold
                }
            },
            'crop_toxicity_risks': {
                'micronutrient_toxicity': {
                    'boron': 3.0,      # lbs B/acre (toxic above this)
                    'copper': 8.0,     # lbs Cu/acre
                    'zinc': 25.0,      # lbs Zn/acre
                    'manganese': 15.0  # lbs Mn/acre
                },
                'salt_damage_risk': {
                    'total_salt_index': 100,  # Combined salt index
                    'close_to_seed': True     # High salt fertilizers near seed
                }
            },
            'timing_hazards': {
                'fall_nitrogen_application': {
                    'northern_regions': True,  # Risk of leaching
                    'max_fall_n_rate': 50     # lbs N/acre
                },
                'frozen_ground_application': True,
                'application_before_heavy_rain': True
            }
        }
    
    def detect_excessive_fertilizer_rates(self) -> bool:
        """Detect dangerously high fertilizer rates."""
        print("Detecting excessive fertilizer rates...")
        
        # Test scenarios with various fertilizer rates
        test_scenarios = [
            {
                'crop': 'corn',
                'fertilizer_program': {
                    'nitrogen_lbs_per_acre': 320,  # Excessive
                    'phosphorus_lbs_per_acre': 80,
                    'potassium_lbs_per_acre': 120
                },
                'expected_risks': ['excessive_nitrogen']
            },
            {
                'crop': 'soybean',
                'fertilizer_program': {
                    'nitrogen_lbs_per_acre': 100,  # Too high for soybean
                    'phosphorus_lbs_per_acre': 40,
                    'potassium_lbs_per_acre': 80
                },
                'expected_risks': ['unnecessary_nitrogen_soybean']
            },
            {
                'crop': 'wheat',
                'fertilizer_program': {
                    'nitrogen_lbs_per_acre': 180,
                    'phosphorus_lbs_per_acre': 120,  # Excessive P
                    'potassium_lbs_per_acre': 100
                },
                'expected_risks': ['excessive_phosphorus']
            }
        ]
        
        risks_detected = []
        
        for i, scenario in enumerate(test_scenarios):
            crop = scenario['crop']
            program = scenario['fertilizer_program']
            
            detected_risks = self._check_fertilizer_rates(crop, program)
            
            # Check if expected risks were detected
            for expected_risk in scenario['expected_risks']:
                if any(expected_risk in risk['type'] for risk in detected_risks):
                    print(f"  ✓ Scenario {i+1}: Correctly detected {expected_risk}")
                else:
                    print(f"  ❌ Scenario {i+1}: Failed to detect {expected_risk}")
                    return False
            
            risks_detected.extend(detected_risks)
        
        self.detection_results['crop_damage_risks'].extend(risks_detected)
        return True
    
    def _check_fertilizer_rates(self, crop: str, program: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check fertilizer rates for dangerous levels."""
        risks = []
        
        # Check nitrogen rates
        n_rate = program.get('nitrogen_lbs_per_acre', 0)
        n_limits = self.danger_patterns['excessive_fertilizer_rates']['nitrogen']
        
        if n_rate > n_limits['critical_threshold']:
            risks.append({
                'type': 'excessive_nitrogen_critical',
                'severity': 'critical',
                'description': f'Nitrogen rate {n_rate} lbs/acre exceeds critical threshold',
                'consequences': ['crop_burn', 'groundwater_contamination', 'economic_waste'],
                'recommendation': 'Reduce nitrogen rate to safe levels'
            })
        elif n_rate > n_limits['high_threshold']:
            risks.append({
                'type': 'excessive_nitrogen_high',
                'severity': 'high',
                'description': f'Nitrogen rate {n_rate} lbs/acre is dangerously high',
                'consequences': ['lodging_risk', 'delayed_maturity', 'environmental_impact'],
                'recommendation': 'Consider reducing nitrogen rate'
            })
        
        # Check crop-specific nitrogen limits
        if crop in n_limits.get('crop_specific', {}):
            crop_limit = n_limits['crop_specific'][crop]
            if n_rate > crop_limit:
                risks.append({
                    'type': f'unnecessary_nitrogen_{crop}',
                    'severity': 'high',
                    'description': f'{crop} rarely needs more than {crop_limit} lbs N/acre',
                    'consequences': ['economic_waste', 'environmental_impact', 'reduced_nodulation'],
                    'recommendation': f'Reduce nitrogen for {crop} to {crop_limit} lbs/acre or less'
                })
        
        # Check phosphorus rates
        p_rate = program.get('phosphorus_lbs_per_acre', 0)
        p_limits = self.danger_patterns['excessive_fertilizer_rates']['phosphorus']
        
        if p_rate > p_limits['critical_threshold']:
            risks.append({
                'type': 'excessive_phosphorus',
                'severity': 'critical',
                'description': f'Phosphorus rate {p_rate} lbs/acre is excessive',
                'consequences': ['micronutrient_deficiency', 'water_pollution', 'economic_waste'],
                'recommendation': 'Reduce phosphorus rate based on soil test'
            })
        
        # Check potassium rates
        k_rate = program.get('potassium_lbs_per_acre', 0)
        k_limits = self.danger_patterns['excessive_fertilizer_rates']['potassium']
        
        if k_rate > k_limits['critical_threshold']:
            risks.append({
                'type': 'excessive_potassium',
                'severity': 'high',
                'description': f'Potassium rate {k_rate} lbs/acre is excessive',
                'consequences': ['magnesium_deficiency', 'calcium_deficiency', 'economic_waste'],
                'recommendation': 'Reduce potassium rate based on soil test'
            })
        
        return risks
    
    def detect_environmental_hazards(self) -> bool:
        """Detect environmental hazard risks."""
        print("Detecting environmental hazards...")
        
        test_scenarios = [
            {
                'description': 'High nitrogen near water body',
                'conditions': {
                    'nitrogen_rate': 200,
                    'distance_to_water_ft': 75,
                    'slope_percent': 3
                },
                'expected_risks': ['water_contamination_nitrogen']
            },
            {
                'description': 'Phosphorus on steep slope',
                'conditions': {
                    'phosphorus_rate': 60,
                    'slope_percent': 12,
                    'soil_texture': 'sandy_loam'
                },
                'expected_risks': ['phosphorus_runoff']
            },
            {
                'description': 'Application before heavy rain',
                'conditions': {
                    'nitrogen_rate': 150,
                    'weather_forecast': 'heavy_rain_24h',
                    'application_method': 'surface_broadcast'
                },
                'expected_risks': ['nutrient_loss_rain']
            }
        ]
        
        risks_detected = []
        
        for i, scenario in enumerate(test_scenarios):
            conditions = scenario['conditions']
            detected_risks = self._check_environmental_hazards(conditions)
            
            # Verify expected risks were detected
            for expected_risk in scenario['expected_risks']:
                if any(expected_risk in risk['type'] for risk in detected_risks):
                    print(f"  ✓ Scenario {i+1}: Correctly detected {expected_risk}")
                else:
                    print(f"  ❌ Scenario {i+1}: Failed to detect {expected_risk}")
                    return False
            
            risks_detected.extend(detected_risks)
        
        self.detection_results['environmental_hazards'].extend(risks_detected)
        return True
    
    def _check_environmental_hazards(self, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for environmental hazard conditions."""
        risks = []
        
        # Check nitrogen near water
        n_rate = conditions.get('nitrogen_rate', 0)
        distance_to_water = conditions.get('distance_to_water_ft', 1000)
        
        if n_rate > 150 and distance_to_water < 100:
            risks.append({
                'type': 'water_contamination_nitrogen',
                'severity': 'critical',
                'description': f'High nitrogen rate ({n_rate} lbs/acre) within {distance_to_water}ft of water',
                'consequences': ['groundwater_contamination', 'surface_water_pollution', 'algae_blooms'],
                'recommendation': 'Reduce nitrogen rate or increase buffer distance'
            })
        
        # Check phosphorus runoff risk
        p_rate = conditions.get('phosphorus_rate', 0)
        slope = conditions.get('slope_percent', 0)
        
        if p_rate > 50 and slope > 8:
            risks.append({
                'type': 'phosphorus_runoff',
                'severity': 'high',
                'description': f'Phosphorus application ({p_rate} lbs/acre) on steep slope ({slope}%)',
                'consequences': ['surface_water_pollution', 'eutrophication', 'algae_blooms'],
                'recommendation': 'Reduce phosphorus rate or use conservation practices'
            })
        
        # Check weather timing
        weather = conditions.get('weather_forecast', '')
        application_method = conditions.get('application_method', '')
        
        if 'heavy_rain' in weather and application_method == 'surface_broadcast':
            risks.append({
                'type': 'nutrient_loss_rain',
                'severity': 'high',
                'description': 'Surface fertilizer application before predicted heavy rain',
                'consequences': ['nutrient_loss', 'economic_waste', 'water_pollution'],
                'recommendation': 'Delay application or incorporate fertilizer'
            })
        
        return risks
    
    def detect_crop_toxicity_risks(self) -> bool:
        """Detect crop toxicity risks from micronutrients or salts."""
        print("Detecting crop toxicity risks...")
        
        test_scenarios = [
            {
                'description': 'Excessive boron application',
                'micronutrients': {
                    'boron_lbs_per_acre': 4.0  # Toxic level
                },
                'expected_risks': ['boron_toxicity']
            },
            {
                'description': 'High salt fertilizer near seed',
                'fertilizer_placement': {
                    'fertilizer_type': 'potassium_chloride',
                    'salt_index': 116,
                    'distance_from_seed_inches': 1
                },
                'expected_risks': ['salt_damage_seed']
            }
        ]
        
        risks_detected = []
        
        for i, scenario in enumerate(test_scenarios):
            if 'micronutrients' in scenario:
                detected_risks = self._check_micronutrient_toxicity(scenario['micronutrients'])
            elif 'fertilizer_placement' in scenario:
                detected_risks = self._check_salt_damage_risk(scenario['fertilizer_placement'])
            else:
                detected_risks = []
            
            # Verify expected risks
            for expected_risk in scenario['expected_risks']:
                if any(expected_risk in risk['type'] for risk in detected_risks):
                    print(f"  ✓ Scenario {i+1}: Correctly detected {expected_risk}")
                else:
                    print(f"  ❌ Scenario {i+1}: Failed to detect {expected_risk}")
                    return False
            
            risks_detected.extend(detected_risks)
        
        self.detection_results['crop_damage_risks'].extend(risks_detected)
        return True
    
    def _check_micronutrient_toxicity(self, micronutrients: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check for micronutrient toxicity risks."""
        risks = []
        toxicity_limits = self.danger_patterns['crop_toxicity_risks']['micronutrient_toxicity']
        
        for nutrient, rate in micronutrients.items():
            nutrient_name = nutrient.replace('_lbs_per_acre', '')
            
            if nutrient_name in toxicity_limits:
                limit = toxicity_limits[nutrient_name]
                if rate > limit:
                    risks.append({
                        'type': f'{nutrient_name}_toxicity',
                        'severity': 'critical',
                        'description': f'{nutrient_name.title()} rate {rate} lbs/acre exceeds toxicity threshold',
                        'consequences': ['crop_damage', 'yield_loss', 'plant_death'],
                        'recommendation': f'Reduce {nutrient_name} rate to below {limit} lbs/acre'
                    })
        
        return risks
    
    def _check_salt_damage_risk(self, placement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for salt damage risks from fertilizer placement."""
        risks = []
        
        salt_index = placement.get('salt_index', 0)
        distance_from_seed = placement.get('distance_from_seed_inches', 6)
        
        # High salt index fertilizers too close to seed
        if salt_index > 80 and distance_from_seed < 2:
            risks.append({
                'type': 'salt_damage_seed',
                'severity': 'high',
                'description': f'High salt fertilizer (index {salt_index}) too close to seed',
                'consequences': ['poor_germination', 'seedling_death', 'stand_reduction'],
                'recommendation': 'Increase distance from seed or use lower salt fertilizer'
            })
        
        return risks
    
    def detect_timing_hazards(self) -> bool:
        """Detect dangerous timing of fertilizer applications."""
        print("Detecting timing hazards...")
        
        test_scenarios = [
            {
                'description': 'Fall nitrogen in northern region',
                'application': {
                    'season': 'fall',
                    'nutrient': 'nitrogen',
                    'rate': 120,
                    'region': 'northern',
                    'soil_temperature': 45  # F
                },
                'expected_risks': ['fall_nitrogen_leaching']
            },
            {
                'description': 'Application on frozen ground',
                'application': {
                    'ground_condition': 'frozen',
                    'nutrient': 'phosphorus',
                    'rate': 60
                },
                'expected_risks': ['frozen_ground_runoff']
            }
        ]
        
        risks_detected = []
        
        for i, scenario in enumerate(test_scenarios):
            application = scenario['application']
            detected_risks = self._check_timing_hazards(application)
            
            # Verify expected risks
            for expected_risk in scenario['expected_risks']:
                if any(expected_risk in risk['type'] for risk in detected_risks):
                    print(f"  ✓ Scenario {i+1}: Correctly detected {expected_risk}")
                else:
                    print(f"  ❌ Scenario {i+1}: Failed to detect {expected_risk}")
                    return False
            
            risks_detected.extend(detected_risks)
        
        self.detection_results['environmental_hazards'].extend(risks_detected)
        return True
    
    def _check_timing_hazards(self, application: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for timing-related hazards."""
        risks = []
        
        # Fall nitrogen application risk
        if (application.get('season') == 'fall' and 
            application.get('nutrient') == 'nitrogen' and
            application.get('region') == 'northern'):
            
            soil_temp = application.get('soil_temperature', 50)
            if soil_temp > 50:  # Soil too warm for fall N
                risks.append({
                    'type': 'fall_nitrogen_leaching',
                    'severity': 'high',
                    'description': 'Fall nitrogen application with warm soil temperatures',
                    'consequences': ['nitrogen_leaching', 'groundwater_contamination', 'economic_loss'],
                    'recommendation': 'Wait for soil temperature below 50°F or apply in spring'
                })
        
        # Frozen ground application
        if application.get('ground_condition') == 'frozen':
            risks.append({
                'type': 'frozen_ground_runoff',
                'severity': 'high',
                'description': 'Fertilizer application on frozen ground',
                'consequences': ['surface_runoff', 'nutrient_loss', 'water_pollution'],
                'recommendation': 'Wait for ground to thaw before application'
            })
        
        return risks
    
    def run_all_detections(self) -> bool:
        """Run all dangerous recommendation detections."""
        print("Running dangerous recommendation detection...")
        print("=" * 60)
        
        detections = [
            ('Excessive Fertilizer Rates', self.detect_excessive_fertilizer_rates),
            ('Environmental Hazards', self.detect_environmental_hazards),
            ('Crop Toxicity Risks', self.detect_crop_toxicity_risks),
            ('Timing Hazards', self.detect_timing_hazards)
        ]
        
        all_passed = True
        
        for name, detection_func in detections:
            print(f"\n{name}:")
            try:
                if detection_func():
                    print(f"  ✅ {name} detection working correctly")
                else:
                    print(f"  ❌ {name} detection failed")
                    all_passed = False
            except Exception as e:
                print(f"  ⚠️  {name} detection error: {e}")
                all_passed = False
        
        self._calculate_summary()
        self._generate_detection_report()
        return all_passed
    
    def _calculate_summary(self):
        """Calculate detection summary statistics."""
        all_risks = []
        
        # Collect all detected risks
        for category in ['crop_damage_risks', 'environmental_hazards', 'soil_health_threats', 
                        'economic_risks', 'safety_violations', 'regulatory_violations']:
            all_risks.extend(self.detection_results[category])
        
        # Count by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for risk in all_risks:
            severity = risk.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        self.detection_results['summary'] = {
            'total_risks_detected': len(all_risks),
            'critical_risks': severity_counts['critical'],
            'high_risks': severity_counts['high'],
            'medium_risks': severity_counts['medium'],
            'low_risks': severity_counts['low']
        }
    
    def _generate_detection_report(self):
        """Generate dangerous recommendation detection report."""
        print("\n" + "=" * 60)
        print("DANGEROUS RECOMMENDATION DETECTION RESULTS")
        print("=" * 60)
        
        summary = self.detection_results['summary']
        print(f"Total risks detected: {summary['total_risks_detected']}")
        print(f"Critical risks: {summary['critical_risks']}")
        print(f"High risks: {summary['high_risks']}")
        print(f"Medium risks: {summary['medium_risks']}")
        print(f"Low risks: {summary['low_risks']}")
        
        # Show risks by category
        categories = [
            ('Crop Damage Risks', 'crop_damage_risks'),
            ('Environmental Hazards', 'environmental_hazards'),
            ('Soil Health Threats', 'soil_health_threats'),
            ('Economic Risks', 'economic_risks'),
            ('Safety Violations', 'safety_violations'),
            ('Regulatory Violations', 'regulatory_violations')
        ]
        
        for category_name, category_key in categories:
            risks = self.detection_results[category_key]
            if risks:
                print(f"\n{category_name} ({len(risks)}):")
                for risk in risks:
                    severity_icon = {
                        'critical': '🚨',
                        'high': '⚠️',
                        'medium': '⚡',
                        'low': 'ℹ️'
                    }.get(risk['severity'], '❓')
                    
                    print(f"  {severity_icon} {risk['type']}: {risk['description']}")
        
        # Safety recommendations
        print(f"\n🛡️  SAFETY RECOMMENDATIONS:")
        print("  • Implement rate limit validation in all recommendation algorithms")
        print("  • Add environmental risk assessment to fertilizer recommendations")
        print("  • Include timing validation for all fertilizer applications")
        print("  • Validate micronutrient rates against toxicity thresholds")
        print("  • Check weather conditions before recommending applications")
        
        # Save detailed report
        report_data = {
            'detection_date': datetime.now().isoformat(),
            'danger_patterns_used': self.danger_patterns,
            'results': self.detection_results,
            'recommendations': [
                'Implement comprehensive safety checks in recommendation engine',
                'Add environmental risk assessment capabilities',
                'Include weather-based timing recommendations',
                'Validate all rates against crop-specific safety limits',
                'Add warnings for high-risk scenarios'
            ]
        }
        
        with open('dangerous-recommendations-report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed detection report saved to: dangerous-recommendations-report.json")

def main():
    """Main detection function."""
    detector = DangerousRecommendationDetector()
    
    success = detector.run_all_detections()
    
    if not success:
        print("\n❌ Dangerous recommendation detection failed!")
        print("Detection system is not properly identifying dangerous recommendations.")
        sys.exit(1)
    else:
        print("\n✅ Dangerous recommendation detection working correctly!")
        print("System can properly identify and flag dangerous recommendations.")
        sys.exit(0)

if __name__ == "__main__":
    main()