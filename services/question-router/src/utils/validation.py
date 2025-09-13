"""
Agricultural Context Validation

Validation utilities for agricultural data and context.
"""

import re
from typing import Dict, Any, List, Optional
from pydantic import ValidationError


def validate_agricultural_context(context: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate agricultural context data for reasonableness.
    
    Args:
        context: Dictionary containing agricultural context data
        
    Returns:
        Dictionary with validation errors by field
    """
    errors = {}
    
    # Validate location data
    if "location" in context:
        location_errors = _validate_location(context["location"])
        if location_errors:
            errors["location"] = location_errors
    
    # Validate soil data
    if "soil_data" in context:
        soil_errors = _validate_soil_data(context["soil_data"])
        if soil_errors:
            errors["soil_data"] = soil_errors
    
    # Validate farm data
    if "farm_data" in context:
        farm_errors = _validate_farm_data(context["farm_data"])
        if farm_errors:
            errors["farm_data"] = farm_errors
    
    return errors


def _validate_location(location: Dict[str, Any]) -> List[str]:
    """Validate GPS coordinates and location data."""
    errors = []
    
    if "latitude" in location:
        lat = location["latitude"]
        if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
            errors.append("Latitude must be between -90 and 90 degrees")
    
    if "longitude" in location:
        lon = location["longitude"]
        if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
            errors.append("Longitude must be between -180 and 180 degrees")
    
    return errors


def _validate_soil_data(soil_data: Dict[str, Any]) -> List[str]:
    """Validate soil test data for agricultural reasonableness."""
    errors = []
    
    # pH validation
    if "ph" in soil_data:
        ph = soil_data["ph"]
        if not isinstance(ph, (int, float)):
            errors.append("Soil pH must be numeric")
        elif not 3.0 <= ph <= 10.0:
            errors.append("Soil pH outside reasonable range (3.0-10.0)")
        elif ph < 4.5:
            errors.append("Warning: Extremely acidic soil (pH < 4.5)")
        elif ph > 8.5:
            errors.append("Warning: Very alkaline soil (pH > 8.5)")
    
    # Organic matter validation
    if "organic_matter_percent" in soil_data:
        om = soil_data["organic_matter_percent"]
        if not isinstance(om, (int, float)):
            errors.append("Organic matter must be numeric")
        elif not 0.0 <= om <= 15.0:
            errors.append("Organic matter outside reasonable range (0-15%)")
    
    # Nutrient level validation
    nutrient_ranges = {
        "phosphorus_ppm": (0, 200),
        "potassium_ppm": (0, 800),
        "nitrogen_ppm": (0, 100)
    }
    
    for nutrient, (min_val, max_val) in nutrient_ranges.items():
        if nutrient in soil_data:
            value = soil_data[nutrient]
            if not isinstance(value, (int, float)):
                errors.append(f"{nutrient} must be numeric")
            elif not min_val <= value <= max_val:
                errors.append(f"{nutrient} outside typical range ({min_val}-{max_val} ppm)")
    
    return errors


def _validate_farm_data(farm_data: Dict[str, Any]) -> List[str]:
    """Validate farm profile data."""
    errors = []
    
    # Farm size validation
    if "farm_size_acres" in farm_data:
        size = farm_data["farm_size_acres"]
        if not isinstance(size, (int, float)):
            errors.append("Farm size must be numeric")
        elif size <= 0:
            errors.append("Farm size must be positive")
        elif size > 50000:
            errors.append("Warning: Very large farm size (>50,000 acres)")
    
    # Crop validation
    if "primary_crops" in farm_data:
        crops = farm_data["primary_crops"]
        if not isinstance(crops, list):
            errors.append("Primary crops must be a list")
        else:
            valid_crops = {
                "corn", "soybean", "wheat", "cotton", "rice", "barley", "oats",
                "sorghum", "sunflower", "canola", "alfalfa", "hay"
            }
            for crop in crops:
                if crop.lower() not in valid_crops:
                    errors.append(f"Unknown crop type: {crop}")
    
    return errors


def sanitize_question_text(question_text: str) -> str:
    """
    Sanitize question text for security and processing.
    
    Args:
        question_text: Raw question text from user
        
    Returns:
        Sanitized question text
    """
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', question_text)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000] + "..."
    
    return sanitized