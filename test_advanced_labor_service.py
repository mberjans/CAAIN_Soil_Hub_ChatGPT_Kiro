#!/usr/bin/env python3
"""
Simple test script to validate the Advanced Labor Analysis Service.
"""

import asyncio
from datetime import datetime
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'fertilizer-application'))

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements,
    FertilizerSpecification, EquipmentSpecification, ApplicationMethodType, EquipmentType
)
from src.services.advanced_labor_analysis_service import (
    AdvancedLaborAnalysisService
)


def test_advanced_labor_service():
    """Test the advanced labor analysis service functionality."""
    
    # Create sample data
    field_conditions = FieldConditions(
        field_size_acres=100.0,
        soil_type="loam",
        slope_percent=2.5,
        irrigation_available=False
    )

    crop_requirements = CropRequirements(
        crop_type="corn",
        growth_stage="V6",
        target_yield=180.0,
        nutrient_requirements={"nitrogen": 150.0, "phosphorus": 40.0, "potassium": 120.0}
    )

    fertilizer_specification = FertilizerSpecification(
        fertilizer_type="nitrogen",
        npk_ratio="30-0-0",
        form="liquid",
        cost_per_unit=0.80
    )

    equipment_specifications = [
        EquipmentSpecification(
            equipment_type=EquipmentType.SPRAYER,
            capacity=1000.0,
            application_width=60.0,
            fuel_efficiency=5.0
        ),
        EquipmentSpecification(
            equipment_type=EquipmentType.SPREADER,
            capacity=800.0,
            application_width=40.0,
            fuel_efficiency=4.0
        )
    ]

    application_methods = [
        ApplicationMethod(
            method_id="method_1",
            method_type=ApplicationMethodType.BROADCAST,
            recommended_equipment=equipment_specifications[1],
            application_rate=100.0,
            rate_unit="lbs/acre",
            application_timing="pre-plant",
            efficiency_score=0.75,
            cost_per_acre=45.0,
            labor_requirements="semi-skilled",
            environmental_impact="medium",
            pros=["Low cost", "Fast application"],
            cons=["Lower precision", "Weather dependent"]
        ),
        ApplicationMethod(
            method_id="method_2",
            method_type=ApplicationMethodType.BAND,
            recommended_equipment=equipment_specifications[0],
            application_rate=80.0,
            rate_unit="lbs/acre",
            application_timing="at-planting",
            efficiency_score=0.85,
            cost_per_acre=55.0,
            labor_requirements="skilled",
            environmental_impact="low",
            pros=["Higher efficiency", "Targeted application"],
            cons=["Higher cost", "Requires skilled labor"]
        )
    ]

    # Create service instance
    service = AdvancedLaborAnalysisService()

    # Test 1: Analyze labor efficiency
    print("Testing labor efficiency analysis...")
    efficiency_scores = asyncio.run(
        service.analyze_labor_efficiency(
            application_methods,
            field_conditions,
            crop_requirements,
            equipment_specifications
        )
    )
    
    print(f"  Efficiency scores calculated for {len(efficiency_scores)} methods")
    for method_id, score in efficiency_scores.items():
        print(f"    {method_id}: Overall Efficiency = {score.overall_efficiency:.3f}")
    
    # Test 2: Perform labor optimization
    print("\nTesting labor optimization...")
    optimization_result = asyncio.run(
        service.perform_labor_optimization(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications
        )
    )
    
    print(f"  Optimization completed in {optimization_result.optimization_time_ms:.2f}ms")
    print(f"  Recommended method: {optimization_result.recommended_labor_plan['recommended_method']['method_type']}")
    
    # Test 3: Calculate labor ROI
    print("\nTesting labor ROI calculation...")
    labor_roi = asyncio.run(
        service.calculate_labor_roi(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications
        )
    )
    
    print("  Labor ROI calculated:")
    for method_id, roi_data in labor_roi.items():
        print(f"    {method_id}: ROI = {roi_data['roi_percentage']:.2f}%")
    
    print("\nAll tests completed successfully!")
    return True


if __name__ == "__main__":
    test_advanced_labor_service()