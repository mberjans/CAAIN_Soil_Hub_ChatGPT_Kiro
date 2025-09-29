#!/usr/bin/env python3
"""
Test script to verify agricultural validation imports work correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from services.agricultural_validation_service import AgriculturalValidationService
    print("✅ AgriculturalValidationService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AgriculturalValidationService: {e}")

try:
    from services.expert_review_service import ExpertReviewService
    print("✅ ExpertReviewService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ExpertReviewService: {e}")

try:
    from services.validation_metrics_service import ValidationMetricsService
    print("✅ ValidationMetricsService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ValidationMetricsService: {e}")

try:
    from models.validation_models import ValidationRequest, ExpertReviewRequest
    print("✅ Validation models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import validation models: {e}")

try:
    from models.crop_variety_models import VarietyRecommendation
    print("✅ VarietyRecommendation imported successfully")
except ImportError as e:
    print(f"❌ Failed to import VarietyRecommendation: {e}")

try:
    from models.service_models import VarietyRecommendationRequest
    print("✅ VarietyRecommendationRequest imported successfully")
except ImportError as e:
    print(f"❌ Failed to import VarietyRecommendationRequest: {e}")

print("\n🎉 All imports successful! Agricultural validation system is ready.")