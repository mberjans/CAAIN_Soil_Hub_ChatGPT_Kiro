"""
UX Test Suite for CAAIN Soil Hub

This package contains comprehensive user experience tests for the agricultural
advisory system, focusing on usability, accessibility, and user workflows.
"""

__version__ = "1.0.0"
__author__ = "CAAIN Soil Hub Development Team"

# Test categories available in this package
TEST_CATEGORIES = [
    "web_ux",
    "mobile_ux", 
    "accessibility",
    "performance",
    "integration_workflows"
]

# UX testing utilities and configurations
UX_TEST_CONFIG = {
    "default_timeout": 30,  # seconds
    "performance_thresholds": {
        "page_load": 2.0,  # seconds
        "first_input_delay": 100,  # milliseconds
        "cumulative_layout_shift": 0.1
    },
    "accessibility_standards": "WCAG_2_1_AA",
    "supported_viewports": [
        {"name": "mobile", "width": 375, "height": 667},
        {"name": "tablet", "width": 768, "height": 1024}, 
        {"name": "desktop", "width": 1920, "height": 1080}
    ]
}