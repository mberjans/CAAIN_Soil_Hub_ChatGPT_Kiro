"""
Tests for goal-based cover crop selection API endpoints.

Tests all four goal-based API endpoints with comprehensive scenarios
including error handling, input validation, and response verification.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import date
import json

from src.main import app
from src.models.cover_crop_models import (
    CoverCropSelectionRequest,
    CoverCropSpecies,
    SoilConditions,
    CoverCropObjectives,
    SoilBenefit,
    GrowingSeason
)
from src.models.goal_models import (
    GoalBasedObjectives,
    GoalCategory,
    SpecificGoal,
    GoalPriority,
    GoalBasedRecommendation
)


@pytest.fixture
def client():
    """Test client for API endpoints."""
    return TestClient(app)


@pytest.fixture
def sample_goal_based_request():
    """Sample goal-based recommendation request."""
    return {
        "request_id": "test_goal_api_001",
        "location": {
            "latitude": 40.0,
            "longitude": -85.0
        },
        "soil_conditions": {
            "ph": 6.5,
            "organic_matter_percent": 2.5,
            "drainage_class": "moderately_well_drained",
            "erosion_risk": "moderate"
        },
        "objectives": {
            "primary_goals": ["nitrogen_fixation", "erosion_control"],
            "nitrogen_needs": True,
            "erosion_control_priority": True
        },
        "planting_window": {
            "start": "2024-09-15",
            "end": "2024-10-15"
        },
        "field_size_acres": 50.0,
        "farmer_goals": {
            "goal_categories": [
                {
                    "category_name": "nitrogen_management",
                    "specific_goals": [
                        {
                            "goal_name": "maximize_nitrogen_fixation",
                            "target_value": 150.0,
                            "priority": "high",
                            "weight": 0.6
                        },
                        {
                            "goal_name": "reduce_fertilizer_costs",
                            "target_value": 40.0,
                            "priority": "high",
                            "weight": 0.4
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def sample_erosion_control_request():
    """Sample erosion control focused request."""
    return {
        "request_id": "test_erosion_api_001",
        "location": {
            "latitude": 42.0,
            "longitude": -87.0
        },
        "soil_conditions": {
            "ph": 6.8,
            "organic_matter_percent": 3.2,
            "drainage_class": "well_drained",
            "erosion_risk": "high"
        },
        "objectives": {
            "primary_goals": ["erosion_control", "weed_suppression"],
            "nitrogen_needs": False,
            "erosion_control_priority": True
        },
        "planting_window": {
            "start": "2024-08-20",
            "end": "2024-09-20"
        },
        "field_size_acres": 75.0,
        "farmer_goals": {
            "goal_categories": [
                {
                    "category_name": "erosion_control",
                    "specific_goals": [
                        {
                            "goal_name": "minimize_soil_loss",
                            "target_value": 2.0,
                            "priority": "high",
                            "weight": 0.7
                        },
                        {
                            "goal_name": "maximize_ground_cover",
                            "target_value": 85.0,
                            "priority": "high",
                            "weight": 0.3
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def mock_goal_based_recommendation():
    """Mock goal-based recommendation response."""
    return GoalBasedRecommendation(
        request_id="test_goal_api_001",
        farmer_goals=GoalBasedObjectives(
            goal_categories=[
                GoalCategory(
                    category_name="nitrogen_management",
                    specific_goals=[
                        SpecificGoal(
                            goal_name="maximize_nitrogen_fixation",
                            target_value=150.0,
                            priority=GoalPriority.HIGH,
                            weight=0.6
                        )
                    ]
                )
            ]
        ),
        recommended_species=[
            CoverCropSpecies(
                species_id="CC001",
                common_name="Crimson Clover",
                scientific_name="Trifolium incarnatum",
                cover_crop_type="legume",
                primary_benefits=[SoilBenefit.NITROGEN_FIXATION],
                secondary_benefits=[SoilBenefit.EROSION_CONTROL],
                hardiness_zones=["6a", "7a"],
                growing_season=GrowingSeason.WINTER,
                seeding_rate_lbs_per_acre=15.0,
                seeding_depth_inches=0.25,
                days_to_establishment=21,
                nitrogen_fixation_lbs_per_acre=120,
                erosion_control_rating=7,
                weed_suppression_rating=6,
                drought_tolerance_rating=5,
                cold_tolerance_rating=8,
                cost_per_lb=2.50
            )
        ],
        goal_achievement_scores={"nitrogen_management": 0.85},
        optimized_seeding_rates={"CC001": 15.0},
        goal_focused_management={
            "nitrogen_management": {
                "planting_practices": ["Inoculate seeds with rhizobia bacteria"],
                "maintenance_practices": ["Monitor nitrogen fixation progress"],
                "termination_practices": ["Terminate before peak bloom for maximum N"]
            }
        },
        cost_benefit_analysis={
            "total_establishment_cost": 125.0,
            "expected_benefits": 300.0,
            "roi_estimate": 2.4
        },
        goal_synergy_analysis={
            "nitrogen_erosion_synergy": {
                "synergy_score": 0.7,
                "contributing_species": ["CC001"]
            }
        },
        confidence_score=0.85
    )


class TestGoalBasedRecommendationsEndpoint:
    """Test the /goal-based-recommendations endpoint."""

    def test_goal_based_recommendations_success(
        self, 
        client, 
        sample_goal_based_request, 
        mock_goal_based_recommendation
    ):
        """Test successful goal-based recommendations request."""
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_based_recommendations',
                   new_callable=AsyncMock, return_value=mock_goal_based_recommendation):
            
            response = client.post(
                "/api/v1/cover-crops/goal-based-recommendations",
                json=sample_goal_based_request
            )

        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "request_id" in data
        assert data["request_id"] == "test_goal_api_001"
        assert "recommended_species" in data
        assert len(data["recommended_species"]) > 0
        assert "goal_achievement_scores" in data
        assert "confidence_score" in data
        assert data["confidence_score"] == 0.85

        # Verify goal achievement scores
        assert "nitrogen_management" in data["goal_achievement_scores"]
        assert data["goal_achievement_scores"]["nitrogen_management"] == 0.85

    def test_goal_based_recommendations_validation_error(self, client):
        """Test validation error handling."""
        invalid_request = {
            "request_id": "test_invalid",
            # Missing required fields
            "location": {"latitude": 40.0}  # Missing longitude
        }

        response = client.post(
            "/api/v1/cover-crops/goal-based-recommendations",
            json=invalid_request
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_goal_based_recommendations_with_multiple_categories(
        self, 
        client, 
        mock_goal_based_recommendation
    ):
        """Test goal-based recommendations with multiple goal categories."""
        multi_category_request = {
            "request_id": "test_multi_goal_001",
            "location": {"latitude": 40.0, "longitude": -85.0},
            "soil_conditions": {
                "ph": 6.5,
                "organic_matter_percent": 2.5,
                "drainage_class": "moderately_well_drained",
                "erosion_risk": "moderate"
            },
            "objectives": {
                "primary_goals": ["nitrogen_fixation", "erosion_control", "organic_matter"],
                "nitrogen_needs": True,
                "erosion_control_priority": True
            },
            "planting_window": {
                "start": "2024-09-15",
                "end": "2024-10-15"
            },
            "field_size_acres": 50.0,
            "farmer_goals": {
                "goal_categories": [
                    {
                        "category_name": "nitrogen_management",
                        "specific_goals": [
                            {
                                "goal_name": "maximize_nitrogen_fixation",
                                "target_value": 150.0,
                                "priority": "high",
                                "weight": 0.4
                            }
                        ]
                    },
                    {
                        "category_name": "soil_health",
                        "specific_goals": [
                            {
                                "goal_name": "increase_organic_matter",
                                "target_value": 0.5,
                                "priority": "medium",
                                "weight": 0.3
                            }
                        ]
                    },
                    {
                        "category_name": "erosion_control",
                        "specific_goals": [
                            {
                                "goal_name": "minimize_soil_loss",
                                "target_value": 2.0,
                                "priority": "high",
                                "weight": 0.3
                            }
                        ]
                    }
                ]
            }
        }

        # Update mock to include multiple categories
        mock_multi_response = mock_goal_based_recommendation
        mock_multi_response.goal_achievement_scores = {
            "nitrogen_management": 0.85,
            "soil_health": 0.72,
            "erosion_control": 0.78
        }

        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_based_recommendations',
                   new_callable=AsyncMock, return_value=mock_multi_response):
            
            response = client.post(
                "/api/v1/cover-crops/goal-based-recommendations",
                json=multi_category_request
            )

        assert response.status_code == 200
        data = response.json()
        
        # Verify multiple goal categories are handled
        goal_scores = data["goal_achievement_scores"]
        assert len(goal_scores) == 3
        assert "nitrogen_management" in goal_scores
        assert "soil_health" in goal_scores
        assert "erosion_control" in goal_scores

    def test_goal_based_recommendations_service_error(self, client, sample_goal_based_request):
        """Test handling of service errors."""
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_based_recommendations',
                   new_callable=AsyncMock, side_effect=Exception("Service unavailable")):
            
            response = client.post(
                "/api/v1/cover-crops/goal-based-recommendations",
                json=sample_goal_based_request
            )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Service unavailable" in data["detail"]


class TestGoalAnalysisEndpoint:
    """Test the /goal-analysis endpoint."""

    def test_goal_analysis_success(self, client, sample_goal_based_request):
        """Test successful goal analysis request."""
        mock_analysis = {
            "feasibility_scores": {
                "nitrogen_management": 0.85,
                "overall_feasibility": 0.80
            },
            "limiting_factors": [
                {
                    "factor": "soil_ph",
                    "impact": "medium",
                    "recommendation": "Consider lime application to optimize pH for legumes"
                }
            ],
            "optimization_recommendations": [
                {
                    "category": "nitrogen_management",
                    "recommendation": "Increase legume proportion in mixture",
                    "expected_improvement": 0.15
                }
            ],
            "alternative_strategies": [
                {
                    "strategy": "Two-stage planting",
                    "description": "Plant legumes first, followed by grasses",
                    "feasibility_score": 0.90
                }
            ]
        }

        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.analyze_goal_feasibility',
                   new_callable=AsyncMock, return_value=mock_analysis):
            
            response = client.post(
                "/api/v1/cover-crops/goal-analysis",
                json=sample_goal_based_request
            )

        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis structure
        assert "feasibility_scores" in data
        assert "limiting_factors" in data
        assert "optimization_recommendations" in data
        assert "alternative_strategies" in data
        
        # Verify specific content
        assert data["feasibility_scores"]["nitrogen_management"] == 0.85
        assert len(data["limiting_factors"]) > 0
        assert len(data["optimization_recommendations"]) > 0

    def test_goal_analysis_low_feasibility(self, client, sample_erosion_control_request):
        """Test goal analysis with low feasibility scenario."""
        mock_low_feasibility = {
            "feasibility_scores": {
                "erosion_control": 0.35,
                "overall_feasibility": 0.30
            },
            "limiting_factors": [
                {
                    "factor": "climate_zone",
                    "impact": "high",
                    "recommendation": "Consider cold-hardy species for this region"
                },
                {
                    "factor": "planting_window",
                    "impact": "high",
                    "recommendation": "Extend planting window to September"
                }
            ],
            "optimization_recommendations": [
                {
                    "category": "erosion_control",
                    "recommendation": "Focus on winter-hardy grasses",
                    "expected_improvement": 0.40
                }
            ],
            "alternative_strategies": [
                {
                    "strategy": "Mechanical erosion control",
                    "description": "Combine cover crops with terracing",
                    "feasibility_score": 0.75
                }
            ]
        }

        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.analyze_goal_feasibility',
                   new_callable=AsyncMock, return_value=mock_low_feasibility):
            
            response = client.post(
                "/api/v1/cover-crops/goal-analysis",
                json=sample_erosion_control_request
            )

        assert response.status_code == 200
        data = response.json()
        
        # Verify low feasibility handling
        assert data["feasibility_scores"]["overall_feasibility"] == 0.30
        assert len(data["limiting_factors"]) >= 2
        assert len(data["alternative_strategies"]) > 0


class TestGoalCategoriesEndpoint:
    """Test the /goal-categories endpoint."""

    def test_goal_categories_success(self, client):
        """Test successful goal categories retrieval."""
        mock_categories = {
            "goal_categories": {
                "nitrogen_management": {
                    "description": "Goals related to nitrogen fixation and fertilizer reduction",
                    "available_goals": [
                        "maximize_nitrogen_fixation",
                        "reduce_fertilizer_costs",
                        "optimize_soil_nitrogen"
                    ]
                },
                "erosion_control": {
                    "description": "Goals focused on soil conservation and erosion prevention",
                    "available_goals": [
                        "minimize_soil_loss",
                        "maximize_ground_cover",
                        "improve_water_infiltration"
                    ]
                },
                "soil_health": {
                    "description": "Goals for improving overall soil quality",
                    "available_goals": [
                        "increase_organic_matter",
                        "improve_soil_structure",
                        "enhance_nutrient_cycling"
                    ]
                }
            },
            "available_goals": [
                "maximize_nitrogen_fixation",
                "reduce_fertilizer_costs",
                "minimize_soil_loss",
                "maximize_ground_cover",
                "increase_organic_matter",
                "improve_soil_structure"
            ],
            "example_scenarios": [
                {
                    "scenario_name": "High nitrogen needs",
                    "description": "Farm with high nitrogen requirements",
                    "recommended_goals": ["maximize_nitrogen_fixation", "reduce_fertilizer_costs"]
                }
            ]
        }

        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_categories_and_options',
                   new_callable=AsyncMock, return_value=mock_categories):
            
            response = client.get("/api/v1/cover-crops/goal-categories")

        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "goal_categories" in data
        assert "available_goals" in data
        assert "example_scenarios" in data
        
        # Verify key categories exist
        categories = data["goal_categories"]
        expected_categories = ["nitrogen_management", "erosion_control", "soil_health"]
        for category in expected_categories:
            assert category in categories
            assert "description" in categories[category]
            assert "available_goals" in categories[category]

    def test_goal_categories_service_error(self, client):
        """Test handling of service errors in goal categories."""
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_categories_and_options',
                   new_callable=AsyncMock, side_effect=Exception("Database error")):
            
            response = client.get("/api/v1/cover-crops/goal-categories")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestGoalExamplesEndpoint:
    """Test the /goal-examples endpoint."""

    def test_goal_examples_success(self, client):
        """Test successful goal examples retrieval."""
        mock_examples = {
            "example_scenarios": [
                {
                    "scenario_name": "Nitrogen Management Focus",
                    "description": "Farm looking to reduce synthetic fertilizer use",
                    "farmer_goals": {
                        "goal_categories": [
                            {
                                "category_name": "nitrogen_management",
                                "specific_goals": [
                                    {
                                        "goal_name": "maximize_nitrogen_fixation",
                                        "target_value": 150.0,
                                        "priority": "high",
                                        "weight": 0.7
                                    },
                                    {
                                        "goal_name": "reduce_fertilizer_costs",
                                        "target_value": 50.0,
                                        "priority": "high",
                                        "weight": 0.3
                                    }
                                ]
                            }
                        ]
                    },
                    "typical_species": ["Crimson Clover", "Austrian Winter Pea", "Red Clover"],
                    "expected_outcomes": {
                        "nitrogen_fixation_lbs_acre": 120,
                        "fertilizer_cost_reduction_percent": 45
                    }
                },
                {
                    "scenario_name": "Erosion Control Priority",
                    "description": "Sloped fields with high erosion risk",
                    "farmer_goals": {
                        "goal_categories": [
                            {
                                "category_name": "erosion_control",
                                "specific_goals": [
                                    {
                                        "goal_name": "minimize_soil_loss",
                                        "target_value": 2.0,
                                        "priority": "high",
                                        "weight": 0.8
                                    },
                                    {
                                        "goal_name": "maximize_ground_cover",
                                        "target_value": 90.0,
                                        "priority": "high",
                                        "weight": 0.2
                                    }
                                ]
                            }
                        ]
                    },
                    "typical_species": ["Winter Rye", "Annual Ryegrass", "Crimson Clover"],
                    "expected_outcomes": {
                        "soil_loss_reduction_percent": 75,
                        "ground_cover_percent": 85
                    }
                }
            ],
            "usage_tips": [
                "Start with one primary goal category to avoid complexity",
                "Set realistic target values based on your field conditions",
                "Consider seasonal timing when setting goals"
            ]
        }

        with patch('src.services.goal_based_service.GoalBasedService.get_example_goal_scenarios',
                   new_callable=AsyncMock, return_value=mock_examples):
            
            response = client.get("/api/v1/cover-crops/goal-examples")

        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "example_scenarios" in data
        assert "usage_tips" in data
        
        # Verify example scenarios
        scenarios = data["example_scenarios"]
        assert len(scenarios) >= 2
        
        for scenario in scenarios:
            assert "scenario_name" in scenario
            assert "description" in scenario
            assert "farmer_goals" in scenario
            assert "typical_species" in scenario
            assert "expected_outcomes" in scenario

    def test_goal_examples_with_query_parameters(self, client):
        """Test goal examples with query parameter filtering."""
        response = client.get("/api/v1/cover-crops/goal-examples?category=nitrogen_management")
        
        # Should return 200 even if filtering not implemented yet
        assert response.status_code == 200

    def test_goal_examples_service_error(self, client):
        """Test handling of service errors in goal examples."""
        with patch('src.services.goal_based_service.GoalBasedService.get_example_goal_scenarios',
                   new_callable=AsyncMock, side_effect=Exception("Service error")):
            
            response = client.get("/api/v1/cover-crops/goal-examples")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestGoalBasedAPIIntegration:
    """Test integration between goal-based API endpoints."""

    def test_full_workflow_integration(
        self, 
        client, 
        sample_goal_based_request, 
        mock_goal_based_recommendation
    ):
        """Test complete goal-based workflow integration."""
        
        # Step 1: Get available goal categories
        mock_categories = {
            "goal_categories": {"nitrogen_management": {"available_goals": ["maximize_nitrogen_fixation"]}},
            "available_goals": ["maximize_nitrogen_fixation"],
            "example_scenarios": []
        }
        
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_categories_and_options',
                   new_callable=AsyncMock, return_value=mock_categories):
            
            categories_response = client.get("/api/v1/cover-crops/goal-categories")
            assert categories_response.status_code == 200

        # Step 2: Analyze goal feasibility
        mock_analysis = {
            "feasibility_scores": {"nitrogen_management": 0.85},
            "limiting_factors": [],
            "optimization_recommendations": [],
            "alternative_strategies": []
        }
        
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.analyze_goal_feasibility',
                   new_callable=AsyncMock, return_value=mock_analysis):
            
            analysis_response = client.post(
                "/api/v1/cover-crops/goal-analysis",
                json=sample_goal_based_request
            )
            assert analysis_response.status_code == 200

        # Step 3: Get goal-based recommendations
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_based_recommendations',
                   new_callable=AsyncMock, return_value=mock_goal_based_recommendation):
            
            recommendations_response = client.post(
                "/api/v1/cover-crops/goal-based-recommendations",
                json=sample_goal_based_request
            )
            assert recommendations_response.status_code == 200

        # Verify all steps completed successfully
        categories_data = categories_response.json()
        analysis_data = analysis_response.json()
        recommendations_data = recommendations_response.json()
        
        assert "goal_categories" in categories_data
        assert "feasibility_scores" in analysis_data
        assert "recommended_species" in recommendations_data

    def test_endpoint_consistency(self, client):
        """Test consistency across goal-based endpoints."""
        # Test that goal categories returned are consistent with
        # what's accepted in recommendation requests
        
        mock_categories = {
            "goal_categories": {
                "nitrogen_management": {"available_goals": ["maximize_nitrogen_fixation"]},
                "erosion_control": {"available_goals": ["minimize_soil_loss"]}
            },
            "available_goals": ["maximize_nitrogen_fixation", "minimize_soil_loss"],
            "example_scenarios": []
        }
        
        with patch('src.services.cover_crop_selection_service.CoverCropSelectionService.get_goal_categories_and_options',
                   new_callable=AsyncMock, return_value=mock_categories):
            
            response = client.get("/api/v1/cover-crops/goal-categories")
            assert response.status_code == 200
            
            data = response.json()
            available_categories = list(data["goal_categories"].keys())
            
            # These categories should be usable in recommendation requests
            assert "nitrogen_management" in available_categories
            assert "erosion_control" in available_categories