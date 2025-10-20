"""Test fertilizer explanation service"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services/recommendation_engine/src'))

from services.fertilizer_explanation_service import FertilizerExplanationService

# Test basic initialization
service = FertilizerExplanationService()
print('✓ FertilizerExplanationService initialized successfully')

# Test explanation generation
recommendation = {
    'fertilizer_name': 'Urea 46-0-0',
    'fertilizer_type': 'synthetic',
    'suitability_score': 0.85,
    'cost_analysis': {'cost_per_acre': 45.50},
    'soil_health_score': 0.65,
    'confidence_score': 0.80
}

priorities = {
    'cost_effectiveness': 0.8,
    'soil_health': 0.6
}

constraints = {
    'budget_per_acre': 50.00
}

explanation = service.generate_recommendation_explanation(
    recommendation=recommendation,
    priorities=priorities,
    constraints=constraints
)

print('✓ Generated explanation successfully')
print(f'  - Explanation ID: {explanation.get("explanation_id")}')
print(f'  - Language: {explanation.get("language")}')
print(f'  - Summary: {explanation.get("summary", {}).get("one_sentence_summary")}')
print(f'  - Plain text: {explanation.get("plain_text_summary")}')

print('\n✓ All tests passed!')
