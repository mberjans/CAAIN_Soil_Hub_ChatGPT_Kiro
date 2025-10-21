#!/usr/bin/env python3
"""
Simple test script to verify the equipment assessment service implementation.
"""

import sys
import os
from uuid import uuid4

# Add the fertilizer application service to the Python path
sys.path.insert(0, '/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/services/fertilizer-application/src')

def test_equipment_assessment_service():
    """Test just the service implementation directly."""
    
    print("Testing Equipment Assessment Service...")
    
    try:
        # Import the service directly
        from services.equipment_assessment_service import EquipmentAssessmentService
        from models.equipment_models import FarmInfrastructure, EquipmentItem
        from models.application_models import EquipmentAssessmentRequest, EquipmentSpecification
        from enum import Enum
        
        # Test creating the service instance
        service = EquipmentAssessmentService()
        print("✓ Service instantiated successfully")
        
        # Create an internal model test
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
        import asyncio
        
        async def run_test():
            result = await service.assess_farm_equipment_and_infrastructure(farm_infrastructure)
            return result
        
        result = asyncio.run(run_test())
        print("✓ Internal assessment method works")
        print(f"  - Overall assessment score: {result.overall_assessment_score}")
        print(f"  - Number of equipment suitability results: {len(result.equipment_suitability)}")
        print(f"  - Number of upgrade recommendations: {len(result.upgrade_recommendations)}")
        print(f"  - Number of identified gaps: {len(result.identified_gaps)}")
        
        print("\n✓ Basic service functionality works!")
        return True
        
    except Exception as e:
        print(f"✗ Error in basic testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_equipment_assessment_service()
    if success:
        print("\n✓ Equipment Assessment Service has basic functionality working!")
    else:
        print("\n✗ Equipment Assessment Service has issues!")
        sys.exit(1)