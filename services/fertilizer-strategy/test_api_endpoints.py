#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, 'src')

from src.services.environmental_optimization_service import SustainabilityOptimizationService
from uuid import uuid4

async def test_api():
    print('Testing API endpoints...')
    
    # Test the service directly
    service = SustainabilityOptimizationService()
    
    field_id = uuid4()
    field_data = {
        'soil_type': 'clay_loam',
        'organic_matter_percent': 3.5,
        'ph': 6.2,
        'field_size_acres': 40.0
    }
    
    fertilizer_options = [
        {'type': 'nitrogen', 'form': 'urea', 'cost_per_unit': 0.45},
        {'type': 'phosphorus', 'form': 'DAP', 'cost_per_unit': 0.65},
        {'type': 'potassium', 'form': 'MOP', 'cost_per_unit': 0.35}
    ]
    
    result = await service.optimize_sustainability(
        field_id=field_id,
        field_data=field_data,
        fertilizer_options=fertilizer_options,
        optimization_method='genetic_algorithm'
    )
    
    print(f'✓ API test successful! Optimization score: {result.optimization_score:.3f}')
    print(f'✓ Environmental impact calculated: {result.environmental_impact.nutrient_runoff_risk}')
    print(f'✓ Sustainability metrics calculated: {result.sustainability_metrics.sustainability_score:.3f}')
    print(f'✓ Recommendations generated: {len(result.recommendations)} recommendations')

if __name__ == "__main__":
    asyncio.run(test_api())
