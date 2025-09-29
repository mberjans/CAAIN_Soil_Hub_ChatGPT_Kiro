"""
User Experience Testing Configuration

Configuration settings for user experience testing and optimization system.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class TestEnvironment(str, Enum):
    """Testing environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class UserExperienceTestingConfig:
    """Configuration for user experience testing system."""
    
    # General Settings
    environment: TestEnvironment = TestEnvironment.DEVELOPMENT
    debug_mode: bool = True
    log_level: str = "INFO"
    
    # Test Settings
    default_sample_size: int = 50
    min_sample_size: int = 10
    max_sample_size: int = 1000
    test_duration_days: int = 14
    
    # Performance Targets
    max_response_time_seconds: float = 3.0
    min_success_rate: float = 0.95
    max_error_rate: float = 0.05
    
    # User Satisfaction Targets
    min_satisfaction_score: float = 4.0
    min_task_completion_rate: float = 0.8
    min_recommendation_adoption_rate: float = 0.6
    
    # Accessibility Targets
    min_accessibility_score: float = 0.9
    wcag_level: str = "AA"
    
    # A/B Testing Settings
    min_ab_test_sample_size: int = 100
    ab_test_confidence_level: float = 0.95
    min_statistical_significance: float = 0.05
    min_effect_size: float = 0.1
    
    # Database Settings
    database_url: str = "postgresql://user:password@localhost/ux_testing"
    redis_url: str = "redis://localhost:6379"
    
    # External Services
    analytics_service_url: str = "http://localhost:8000/api/v1/analytics"
    feedback_service_url: str = "http://localhost:8000/api/v1/feedback"
    
    # Notification Settings
    email_notifications: bool = True
    slack_notifications: bool = False
    notification_email: str = "ux-testing@afas.com"
    
    # Security Settings
    api_key_required: bool = True
    rate_limit_per_minute: int = 100
    max_request_size_mb: int = 10


# Predefined Test Scenarios
USABILITY_TEST_SCENARIOS = {
    "basic_variety_selection": {
        "name": "Basic Variety Selection",
        "description": "Find suitable crop varieties for farm conditions",
        "tasks": [
            {
                "task_id": "navigate_to_selection",
                "name": "Navigate to Variety Selection",
                "instructions": "Go to the variety selection page",
                "expected_outcome": "User successfully navigates to variety selection",
                "time_limit_minutes": 2,
                "difficulty": "easy"
            },
            {
                "task_id": "input_farm_data",
                "name": "Input Farm Data",
                "instructions": "Enter farm location, soil type, and preferences",
                "expected_outcome": "User successfully inputs farm information",
                "time_limit_minutes": 5,
                "difficulty": "easy"
            },
            {
                "task_id": "review_recommendations",
                "name": "Review Recommendations",
                "instructions": "Review and understand the variety recommendations",
                "expected_outcome": "User reviews and understands recommendations",
                "time_limit_minutes": 8,
                "difficulty": "medium"
            }
        ],
        "success_criteria": {
            "task_completion_rate": 0.85,
            "satisfaction_score": 4.0,
            "time_to_completion_minutes": 15
        }
    },
    
    "variety_comparison": {
        "name": "Variety Comparison",
        "description": "Compare multiple varieties side-by-side",
        "tasks": [
            {
                "task_id": "select_varieties",
                "name": "Select Varieties for Comparison",
                "instructions": "Select 2-3 varieties to compare",
                "expected_outcome": "User selects multiple varieties",
                "time_limit_minutes": 3,
                "difficulty": "easy"
            },
            {
                "task_id": "use_comparison_tool",
                "name": "Use Comparison Tool",
                "instructions": "Use the comparison tool to analyze differences",
                "expected_outcome": "User successfully uses comparison tool",
                "time_limit_minutes": 10,
                "difficulty": "medium"
            },
            {
                "task_id": "analyze_differences",
                "name": "Analyze Differences",
                "instructions": "Identify key differences between varieties",
                "expected_outcome": "User identifies important differences",
                "time_limit_minutes": 5,
                "difficulty": "medium"
            }
        ],
        "success_criteria": {
            "task_completion_rate": 0.75,
            "satisfaction_score": 4.2,
            "time_to_completion_minutes": 18
        }
    },
    
    "mobile_field_use": {
        "name": "Mobile Field Use",
        "description": "Use variety selection on mobile device in field conditions",
        "tasks": [
            {
                "task_id": "mobile_navigation",
                "name": "Mobile Navigation",
                "instructions": "Navigate the interface on mobile device",
                "expected_outcome": "User successfully navigates on mobile",
                "time_limit_minutes": 3,
                "difficulty": "easy"
            },
            {
                "task_id": "field_data_input",
                "name": "Field Data Input",
                "instructions": "Input field data using mobile interface",
                "expected_outcome": "User inputs field data on mobile",
                "time_limit_minutes": 8,
                "difficulty": "medium"
            },
            {
                "task_id": "mobile_recommendations",
                "name": "Mobile Recommendations",
                "instructions": "View and interact with recommendations on mobile",
                "expected_outcome": "User successfully views recommendations",
                "time_limit_minutes": 10,
                "difficulty": "medium"
            }
        ],
        "success_criteria": {
            "task_completion_rate": 0.70,
            "satisfaction_score": 3.8,
            "time_to_completion_minutes": 21
        }
    }
}

# A/B Test Variants
AB_TEST_VARIANTS = {
    "interface_optimization": {
        "test_name": "Interface Optimization A/B Test",
        "description": "Test different interface designs for variety selection",
        "variants": [
            {
                "variant_id": "control",
                "name": "Current Interface",
                "description": "Current variety selection interface",
                "configuration": {
                    "layout": "standard",
                    "recommendations_per_page": 10,
                    "show_comparison_tool": True,
                    "mobile_optimized": False
                },
                "traffic_percentage": 50.0,
                "is_control": True
            },
            {
                "variant_id": "enhanced",
                "name": "Enhanced Interface",
                "description": "Interface with enhanced recommendation display",
                "configuration": {
                    "layout": "enhanced",
                    "recommendations_per_page": 15,
                    "show_comparison_tool": True,
                    "mobile_optimized": True,
                    "enhanced_visualization": True
                },
                "traffic_percentage": 50.0,
                "is_control": False
            }
        ],
        "primary_metric": "conversion_rate",
        "success_criteria": {
            "statistical_significance": 0.95,
            "min_effect_size": 0.1,
            "conversion_rate_improvement": 0.15
        }
    },
    
    "recommendation_algorithm": {
        "test_name": "Recommendation Algorithm A/B Test",
        "description": "Test different recommendation algorithms",
        "variants": [
            {
                "variant_id": "current_algorithm",
                "name": "Current Algorithm",
                "description": "Current variety recommendation algorithm",
                "configuration": {
                    "algorithm_type": "rule_based",
                    "weighting": "standard",
                    "personalization": False
                },
                "traffic_percentage": 50.0,
                "is_control": True
            },
            {
                "variant_id": "ml_algorithm",
                "name": "Machine Learning Algorithm",
                "description": "ML-enhanced recommendation algorithm",
                "configuration": {
                    "algorithm_type": "machine_learning",
                    "weighting": "adaptive",
                    "personalization": True,
                    "ml_model_version": "v2.1"
                },
                "traffic_percentage": 50.0,
                "is_control": False
            }
        ],
        "primary_metric": "recommendation_adoption_rate",
        "success_criteria": {
            "statistical_significance": 0.95,
            "min_effect_size": 0.1,
            "adoption_rate_improvement": 0.2
        }
    }
}

# Performance Test Scenarios
PERFORMANCE_TEST_SCENARIOS = {
    "basic_variety_search": {
        "name": "Basic Variety Search",
        "endpoint": "/api/v1/varieties/search",
        "method": "POST",
        "payload": {
            "crop_type": "corn",
            "location": "Iowa",
            "soil_type": "clay_loam"
        },
        "expected_response_time_ms": 2000,
        "concurrent_users": 100
    },
    
    "complex_recommendation": {
        "name": "Complex Variety Recommendation",
        "endpoint": "/api/v1/recommendations/varieties",
        "method": "POST",
        "payload": {
            "farm_data": {
                "location": {"lat": 41.8781, "lng": -87.6298},
                "soil_ph": 6.5,
                "organic_matter": 3.2,
                "drainage": "good",
                "slope": "moderate"
            },
            "preferences": {
                "yield_priority": "high",
                "disease_resistance": "important",
                "maturity_group": "3.5-4.0"
            }
        },
        "expected_response_time_ms": 3000,
        "concurrent_users": 50
    },
    
    "variety_comparison": {
        "name": "Variety Comparison",
        "endpoint": "/api/v1/varieties/compare",
        "method": "POST",
        "payload": {
            "variety_ids": ["var_001", "var_002", "var_003"],
            "comparison_metrics": ["yield", "disease_resistance", "maturity"]
        },
        "expected_response_time_ms": 1500,
        "concurrent_users": 75
    }
}

# Accessibility Test Configuration
ACCESSIBILITY_TEST_CONFIG = {
    "standards": ["WCAG 2.1 AA", "Section 508"],
    "test_urls": [
        "https://afas.com/variety-selection",
        "https://afas.com/mobile/variety-selection",
        "https://afas.com/variety-comparison"
    ],
    "automated_tools": [
        "axe-core",
        "WAVE",
        "Lighthouse"
    ],
    "manual_testing": {
        "keyboard_navigation": True,
        "screen_reader_testing": True,
        "color_contrast_validation": True,
        "focus_management": True
    },
    "success_criteria": {
        "overall_score": 0.9,
        "critical_issues": 0,
        "major_issues": 5,
        "minor_issues": 10
    }
}

# User Group Configurations
USER_GROUP_CONFIGS = {
    "farmers": {
        "sample_size": 50,
        "recruitment_criteria": [
            "Active farmers with 5+ years experience",
            "Variety of farm sizes (small, medium, large)",
            "Different crop types (corn, soybeans, wheat)",
            "Geographic diversity across regions"
        ],
        "incentives": {
            "type": "gift_card",
            "amount": 50,
            "currency": "USD"
        },
        "testing_preferences": {
            "session_length_minutes": 30,
            "max_sessions_per_user": 2,
            "preferred_time_slots": ["morning", "afternoon"]
        }
    },
    
    "agricultural_consultants": {
        "sample_size": 20,
        "recruitment_criteria": [
            "Certified agricultural consultants",
            "Experience with variety selection",
            "Client base of 10+ farms",
            "Professional credentials (CCA, etc.)"
        ],
        "incentives": {
            "type": "professional_development",
            "amount": 100,
            "currency": "USD"
        },
        "testing_preferences": {
            "session_length_minutes": 45,
            "max_sessions_per_user": 3,
            "preferred_time_slots": ["business_hours"]
        }
    },
    
    "extension_agents": {
        "sample_size": 15,
        "recruitment_criteria": [
            "University extension specialists",
            "Experience with variety trials",
            "Regional expertise",
            "Educational background in agronomy"
        ],
        "incentives": {
            "type": "research_participation",
            "amount": 75,
            "currency": "USD"
        },
        "testing_preferences": {
            "session_length_minutes": 60,
            "max_sessions_per_user": 2,
            "preferred_time_slots": ["business_hours"]
        }
    }
}

# Notification Templates
NOTIFICATION_TEMPLATES = {
    "test_completion": {
        "subject": "User Experience Test Completed - {test_name}",
        "body": """
        The user experience test '{test_name}' has been completed.
        
        Key Results:
        - Task Completion Rate: {completion_rate:.1%}
        - User Satisfaction: {satisfaction_score:.1f}/5.0
        - Recommendation Adoption: {adoption_rate:.1%}
        
        View detailed results: {results_url}
        """
    },
    
    "ab_test_results": {
        "subject": "A/B Test Results - {test_name}",
        "body": """
        A/B test '{test_name}' has reached statistical significance.
        
        Results:
        - Winning Variant: {winning_variant}
        - Statistical Significance: {significance:.1%}
        - Effect Size: {effect_size:.1%}
        - Conversion Rate Improvement: {improvement:.1%}
        
        View detailed analysis: {analysis_url}
        """
    },
    
    "accessibility_issues": {
        "subject": "Accessibility Issues Found - {interface_name}",
        "body": """
        Accessibility testing has identified issues in {interface_name}.
        
        Issues Found:
        - Critical: {critical_count}
        - Major: {major_count}
        - Minor: {minor_count}
        
        Overall Score: {overall_score:.1%}
        
        View detailed report: {report_url}
        """
    }
}

# Default Configuration Instance
DEFAULT_CONFIG = UserExperienceTestingConfig()