#!/usr/bin/env python3
"""
Test script to verify the equipment assessment service implementation.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add the fertilizer application service to the Python path
sys.path.insert(0, '/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-application/src')

# Import directly from the modules
from models.application_models import EquipmentAssessmentRequest, EquipmentSpecification, EquipmentType
from models.equipment_models import EquipmentItem, EquipmentAssessmentResult, EquipmentSuitability, EquipmentUpgradeRecommendation, FarmInfrastructure
from services.equipment_assessment_service import EquipmentAssessmentService
from enum import Enum


def test_equipment_assessment_service():
    """Test the equipment assessment service implementation."""
    
    print("Testing Equipment Assessment Service...")
    
    try:
        # Create an instance of the service
        service = EquipmentAssessmentService()
        print("✓ Service instantiated successfully")
        
        # Test the internal method first
        from models.equipment_models import FarmInfrastructure
        
        farm_infrastructure = FarmInfrastructure(
            farm_location_id=uuid4(),
            total_acres=500.0,
            field_layout_complexity=0.5,
            access_road_quality=0.7,
            storage_capacity_tons=100.0,
            labor_availability_score=0.6,
            existing_equipment=[]
        )
        
        # Test the internal assessment method
        result = asyncio.run(service.assess_farm_equipment_and_infrastructure(farm_infrastructure))
        print("✓ Internal assessment method works")
        print(f"  - Overall assessment score: {result.overall_assessment_score}")
        print(f"  - Number of equipment suitability results: {len(result.equipment_suitability)}")
        print(f"  - Number of upgrade recommendations: {len(result.upgrade_recommendations)}")
        print(f"  - Number of identified gaps: {len(result.identified_gaps)}")
        
        # Test the API-compatible method
        from models.application_models import EquipmentType
        
        equipment_specs = [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=500.0,
                capacity_unit="lbs",
                application_width=60.0
            )
        ]
        
        request = EquipmentAssessmentRequest(
            farm_size_acres=500.0,
            field_count=5,
            average_field_size=100.0,
            current_equipment=equipment_specs,
            labor_availability="medium"
        )
        
        response = asyncio.run(service.assess_farm_equipment(request))
        print("✓ API-compatible assessment method works")
        print(f"  - Request ID: {response.request_id}")
        print(f"  - Farm assessment acres: {response.farm_assessment['farm_size_acres']}")
        print(f"  - Number of equipment assessments: {len(response.equipment_assessments)}")
        print(f"  - Number of upgrade priorities: {len(response.upgrade_priorities)}")
        print(f"  - Processing time: {response.processing_time_ms:.2f} ms")
        
        print("\n✓ All tests passed! Equipment Assessment Service is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Error in testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_equipment_assessment_service()
    if success:
        print("\nEquipment Assessment Service implementation is successful!")
    else:
        print("\nEquipment Assessment Service implementation has errors!")
        sys.exit(1)