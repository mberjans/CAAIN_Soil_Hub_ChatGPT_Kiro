"""
Enhanced Data Validation and Cleaning Pipeline

Provides comprehensive data validation, cleaning, and quality assurance
for agricultural data with domain-specific rules and automated corrections.
"""

import asyncio
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from pydantic import BaseModel, ValidationError, validator
import structlog

logger = structlog.get_logger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"  # Data cannot be used
    ERROR = "error"       # Data has significant issues
    WARNING = "warning"   # Data has minor issues
    INFO = "info"        # Informational notices


class CleaningAction(Enum):
    """Types of data cleaning actions."""
    REMOVE = "remove"           # Remove invalid data
    CORRECT = "correct"         # Automatically correct data
    NORMALIZE = "normalize"     # Normalize format/units
    INTERPOLATE = "interpolate" # Fill missing values
    FLAG = "flag"              # Flag for manual review


@dataclass
class ValidationIssue:
    """Represents a data validation issue."""
    field_name: str
    severity: ValidationSeverity
    message: str
    original_value: Any
    suggested_value: Optional[Any] = None
    cleaning_action: Optional[CleaningAction] = None
    confidence: float = 1.0
    agricultural_context: Optional[str] = None


@dataclass
class CleaningResult:
    """Result of data cleaning operation."""
    original_data: Dict[str, Any]
    cleaned_data: Dict[str, Any]
    issues_found: List[ValidationIssue]
    actions_taken: List[str]
    quality_score: float
    cleaning_confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgriculturalDataCleaner(ABC):
    """Abstract base class for agricultural data cleaners."""
    
    @abstractmethod
    async def clean_data(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> CleaningResult:
        """Clean and validate agricultural data."""
        pass


class WeatherDataCleaner(AgriculturalDataCleaner):
    """Cleaner for weather data with agricultural context."""
    
    # Agricultural weather data ranges
    TEMPERATURE_RANGES = {
        "extreme_min": -60.0,  # °F
        "extreme_max": 140.0,  # °F
        "typical_min": -30.0,  # °F
        "typical_max": 120.0,  # °F
        "growing_season_min": 32.0,  # °F
        "growing_season_max": 100.0   # °F
    }
    
    HUMIDITY_RANGES = {
        "min": 0.0,    # %
        "max": 100.0,  # %
        "typical_min": 20.0,  # %
        "typical_max": 95.0   # %
    }
    
    PRECIPITATION_RANGES = {
        "min": 0.0,      # inches
        "max": 20.0,     # inches (daily)
        "extreme_max": 50.0,  # inches (extreme events)
        "typical_max": 5.0    # inches (typical daily)
    }
    
    WIND_SPEED_RANGES = {
        "min": 0.0,      # mph
        "max": 200.0,    # mph (extreme)
        "typical_max": 50.0,  # mph (typical)
        "damaging_threshold": 25.0  # mph (crop damage)
    }
    
    async def clean_data(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> CleaningResult:
        """Clean weather data with agricultural validation."""
        issues = []
        cleaned_data = data.copy()
        actions_taken = []
        
        # Clean temperature data
        temp_result = await self._clean_temperature(cleaned_data, context)
        issues.extend(temp_result["issues"])
        actions_taken.extend(temp_result["actions"])
        
        # Clean humidity data
        humidity_result = await self._clean_humidity(cleaned_data, context)
        issues.extend(humidity_result["issues"])
        actions_taken.extend(humidity_result["actions"])
        
        # Clean precipitation data
        precip_result = await self._clean_precipitation(cleaned_data, context)
        issues.extend(precip_result["issues"])
        actions_taken.extend(precip_result["actions"])
        
        # Clean wind data
        wind_result = await self._clean_wind_speed(cleaned_data, context)
        issues.extend(wind_result["issues"])
        actions_taken.extend(wind_result["actions"])
        
        # Validate timestamp
        timestamp_result = await self._clean_timestamp(cleaned_data, context)
        issues.extend(timestamp_result["issues"])
        actions_taken.extend(timestamp_result["actions"])
        
        # Calculate quality score
        quality_score = self._calculate_weather_quality_score(cleaned_data, issues)
        
        # Calculate cleaning confidence
        cleaning_confidence = self._calculate_cleaning_confidence(issues, actions_taken)
        
        return CleaningResult(
            original_data=data,
            cleaned_data=cleaned_data,
            issues_found=issues,
            actions_taken=actions_taken,
            quality_score=quality_score,
            cleaning_confidence=cleaning_confidence,
            metadata={
                "cleaner_type": "weather",
                "agricultural_context": context.get("agricultural_context", "general") if context else "general",
                "season": self._determine_season(context) if context else "unknown"
            }
        )
    
    async def _clean_temperature(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean temperature data."""
        issues = []
        actions = []
        
        for temp_field in ["temperature_f", "temperature_celsius", "temp_f", "temp_c"]:
            if temp_field in data:
                temp_value = data[temp_field]
                
                # Type validation and conversion
                if isinstance(temp_value, str):
                    try:
                        temp_value = float(temp_value)
                        data[temp_field] = temp_value
                        actions.append(f"Converted {temp_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=temp_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert temperature '{temp_value}' to numeric",
                            original_value=temp_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[temp_field]
                        actions.append(f"Removed invalid temperature field {temp_field}")
                        continue
                
                # Range validation
                if temp_value < self.TEMPERATURE_RANGES["extreme_min"] or temp_value > self.TEMPERATURE_RANGES["extreme_max"]:
                    issues.append(ValidationIssue(
                        field_name=temp_field,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Temperature {temp_value}°F is outside physically possible range",
                        original_value=temp_value,
                        cleaning_action=CleaningAction.REMOVE,
                        agricultural_context="Temperature outside survivable range for any crops"
                    ))
                    del data[temp_field]
                    actions.append(f"Removed extreme temperature value {temp_value}")
                
                elif temp_value < self.TEMPERATURE_RANGES["typical_min"] or temp_value > self.TEMPERATURE_RANGES["typical_max"]:
                    issues.append(ValidationIssue(
                        field_name=temp_field,
                        severity=ValidationSeverity.WARNING,
                        message=f"Temperature {temp_value}°F is outside typical agricultural range",
                        original_value=temp_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Extreme temperature may affect crop growth and recommendations"
                    ))
                
                # Unit consistency check
                if temp_field.endswith("_celsius") or temp_field.endswith("_c"):
                    if temp_value > 60:  # Likely Fahrenheit in Celsius field
                        fahrenheit_value = temp_value
                        celsius_value = (temp_value - 32) * 5/9
                        data[temp_field] = celsius_value
                        issues.append(ValidationIssue(
                            field_name=temp_field,
                            severity=ValidationSeverity.WARNING,
                            message=f"Temperature {temp_value} appears to be Fahrenheit in Celsius field",
                            original_value=temp_value,
                            suggested_value=celsius_value,
                            cleaning_action=CleaningAction.CORRECT
                        ))
                        actions.append(f"Converted {temp_field} from Fahrenheit to Celsius")
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_humidity(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean humidity data."""
        issues = []
        actions = []
        
        for humidity_field in ["humidity_percent", "humidity", "relative_humidity"]:
            if humidity_field in data:
                humidity_value = data[humidity_field]
                
                # Type validation
                if isinstance(humidity_value, str):
                    # Remove percentage sign if present
                    humidity_str = humidity_value.replace("%", "").strip()
                    try:
                        humidity_value = float(humidity_str)
                        data[humidity_field] = humidity_value
                        actions.append(f"Converted {humidity_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=humidity_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert humidity '{humidity_value}' to numeric",
                            original_value=humidity_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[humidity_field]
                        continue
                
                # Range validation and correction
                if humidity_value < 0:
                    issues.append(ValidationIssue(
                        field_name=humidity_field,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative humidity {humidity_value}% is invalid",
                        original_value=humidity_value,
                        suggested_value=0.0,
                        cleaning_action=CleaningAction.CORRECT
                    ))
                    data[humidity_field] = 0.0
                    actions.append(f"Corrected negative humidity to 0%")
                
                elif humidity_value > 100:
                    if humidity_value <= 110:  # Likely measurement error
                        corrected_value = 100.0
                        issues.append(ValidationIssue(
                            field_name=humidity_field,
                            severity=ValidationSeverity.WARNING,
                            message=f"Humidity {humidity_value}% exceeds 100%, correcting to 100%",
                            original_value=humidity_value,
                            suggested_value=corrected_value,
                            cleaning_action=CleaningAction.CORRECT
                        ))
                        data[humidity_field] = corrected_value
                        actions.append(f"Corrected humidity from {humidity_value}% to 100%")
                    else:
                        issues.append(ValidationIssue(
                            field_name=humidity_field,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Humidity {humidity_value}% is impossibly high",
                            original_value=humidity_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[humidity_field]
                        actions.append(f"Removed invalid humidity value {humidity_value}%")
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_precipitation(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean precipitation data."""
        issues = []
        actions = []
        
        for precip_field in ["precipitation_inches", "precipitation", "rainfall", "precip"]:
            if precip_field in data:
                precip_value = data[precip_field]
                
                # Type validation
                if isinstance(precip_value, str):
                    try:
                        precip_value = float(precip_value)
                        data[precip_field] = precip_value
                        actions.append(f"Converted {precip_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=precip_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert precipitation '{precip_value}' to numeric",
                            original_value=precip_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[precip_field]
                        continue
                
                # Range validation
                if precip_value < 0:
                    issues.append(ValidationIssue(
                        field_name=precip_field,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative precipitation {precip_value} is invalid",
                        original_value=precip_value,
                        suggested_value=0.0,
                        cleaning_action=CleaningAction.CORRECT
                    ))
                    data[precip_field] = 0.0
                    actions.append(f"Corrected negative precipitation to 0")
                
                elif precip_value > self.PRECIPITATION_RANGES["extreme_max"]:
                    issues.append(ValidationIssue(
                        field_name=precip_field,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Precipitation {precip_value} inches is extremely high",
                        original_value=precip_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Extreme precipitation may indicate flooding conditions"
                    ))
                
                elif precip_value > self.PRECIPITATION_RANGES["typical_max"]:
                    issues.append(ValidationIssue(
                        field_name=precip_field,
                        severity=ValidationSeverity.WARNING,
                        message=f"High precipitation {precip_value} inches reported",
                        original_value=precip_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Heavy rainfall may affect field operations and crop health"
                    ))
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_wind_speed(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean wind speed data."""
        issues = []
        actions = []
        
        for wind_field in ["wind_speed_mph", "wind_speed", "wind_mph"]:
            if wind_field in data:
                wind_value = data[wind_field]
                
                # Type validation
                if isinstance(wind_value, str):
                    try:
                        wind_value = float(wind_value)
                        data[wind_field] = wind_value
                        actions.append(f"Converted {wind_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=wind_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert wind speed '{wind_value}' to numeric",
                            original_value=wind_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[wind_field]
                        continue
                
                # Range validation
                if wind_value < 0:
                    issues.append(ValidationIssue(
                        field_name=wind_field,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative wind speed {wind_value} is invalid",
                        original_value=wind_value,
                        suggested_value=0.0,
                        cleaning_action=CleaningAction.CORRECT
                    ))
                    data[wind_field] = 0.0
                    actions.append(f"Corrected negative wind speed to 0")
                
                elif wind_value > self.WIND_SPEED_RANGES["max"]:
                    issues.append(ValidationIssue(
                        field_name=wind_field,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Wind speed {wind_value} mph is extremely high",
                        original_value=wind_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Extreme wind speeds may indicate severe weather"
                    ))
                
                elif wind_value > self.WIND_SPEED_RANGES["damaging_threshold"]:
                    issues.append(ValidationIssue(
                        field_name=wind_field,
                        severity=ValidationSeverity.WARNING,
                        message=f"High wind speed {wind_value} mph may damage crops",
                        original_value=wind_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Wind speeds above 25 mph can cause crop lodging and damage"
                    ))
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_timestamp(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate timestamp data."""
        issues = []
        actions = []
        
        for timestamp_field in ["timestamp", "datetime", "observation_time", "recorded_at"]:
            if timestamp_field in data:
                timestamp_value = data[timestamp_field]
                
                if isinstance(timestamp_value, str):
                    try:
                        # Try to parse various timestamp formats
                        parsed_time = self._parse_timestamp(timestamp_value)
                        data[timestamp_field] = parsed_time.isoformat()
                        actions.append(f"Normalized {timestamp_field} format")
                        
                        # Check if timestamp is reasonable
                        now = datetime.utcnow()
                        age_hours = (now - parsed_time).total_seconds() / 3600
                        
                        if age_hours > 48:  # Data older than 48 hours
                            issues.append(ValidationIssue(
                                field_name=timestamp_field,
                                severity=ValidationSeverity.WARNING,
                                message=f"Weather data is {age_hours:.1f} hours old",
                                original_value=timestamp_value,
                                cleaning_action=CleaningAction.FLAG,
                                agricultural_context="Older weather data may be less relevant for current conditions"
                            ))
                        
                        if parsed_time > now + timedelta(hours=1):  # Future timestamp
                            issues.append(ValidationIssue(
                                field_name=timestamp_field,
                                severity=ValidationSeverity.WARNING,
                                message="Timestamp is in the future",
                                original_value=timestamp_value,
                                cleaning_action=CleaningAction.FLAG
                            ))
                    
                    except ValueError as e:
                        issues.append(ValidationIssue(
                            field_name=timestamp_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot parse timestamp '{timestamp_value}': {str(e)}",
                            original_value=timestamp_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[timestamp_field]
                        actions.append(f"Removed invalid timestamp {timestamp_field}")
        
        return {"issues": issues, "actions": actions}
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp from various formats."""
        # Common timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # Try ISO format parsing
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass
        
        raise ValueError(f"Unable to parse timestamp format: {timestamp_str}")
    
    def _calculate_weather_quality_score(self, data: Dict[str, Any], issues: List[ValidationIssue]) -> float:
        """Calculate quality score for weather data."""
        base_score = 1.0
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.3
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.2
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
        
        # Calculate completeness score
        required_fields = ["temperature_f", "humidity_percent", "precipitation_inches"]
        present_fields = sum(1 for field in required_fields if field in data)
        completeness_score = present_fields / len(required_fields)
        
        # Combine base score with completeness (weighted average)
        final_score = (base_score * 0.7) + (completeness_score * 0.3)
        
        return max(0.0, min(1.0, final_score))
    
    def _calculate_cleaning_confidence(self, issues: List[ValidationIssue], actions: List[str]) -> float:
        """Calculate confidence in cleaning actions."""
        if not issues:
            return 1.0
        
        # High confidence for automatic corrections
        auto_corrections = sum(1 for issue in issues if issue.cleaning_action in [CleaningAction.CORRECT, CleaningAction.NORMALIZE])
        manual_reviews = sum(1 for issue in issues if issue.cleaning_action == CleaningAction.FLAG)
        removals = sum(1 for issue in issues if issue.cleaning_action == CleaningAction.REMOVE)
        
        total_issues = len(issues)
        confidence = (auto_corrections * 0.9 + manual_reviews * 0.7 + removals * 0.5) / total_issues
        
        return max(0.0, min(1.0, confidence))
    
    def _determine_season(self, context: Dict[str, Any]) -> str:
        """Determine agricultural season from context."""
        if not context:
            return "unknown"
        
        # Try to get season from context
        if "season" in context:
            return context["season"]
        
        # Determine from date if available
        if "date" in context:
            try:
                date_obj = datetime.fromisoformat(context["date"])
                month = date_obj.month
                
                if month in [3, 4, 5]:
                    return "spring"
                elif month in [6, 7, 8]:
                    return "summer"
                elif month in [9, 10, 11]:
                    return "fall"
                else:
                    return "winter"
            except (ValueError, TypeError):
                pass
        
        return "unknown"


class SoilDataCleaner(AgriculturalDataCleaner):
    """Cleaner for soil data with agricultural validation."""
    
    # Agricultural soil data ranges
    PH_RANGES = {
        "min": 3.0,
        "max": 10.0,
        "agricultural_min": 4.0,
        "agricultural_max": 9.0,
        "optimal_min": 6.0,
        "optimal_max": 7.5
    }
    
    ORGANIC_MATTER_RANGES = {
        "min": 0.0,
        "max": 20.0,
        "low_threshold": 2.0,
        "good_threshold": 3.0,
        "high_threshold": 8.0
    }
    
    NUTRIENT_RANGES = {
        "phosphorus_ppm": {"min": 0, "max": 200, "optimal_min": 20, "optimal_max": 40},
        "potassium_ppm": {"min": 0, "max": 800, "optimal_min": 150, "optimal_max": 300},
        "nitrogen_ppm": {"min": 0, "max": 100, "optimal_min": 10, "optimal_max": 30}
    }
    
    async def clean_data(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> CleaningResult:
        """Clean soil data with agricultural validation."""
        issues = []
        cleaned_data = data.copy()
        actions_taken = []
        
        # Clean pH data
        ph_result = await self._clean_ph_data(cleaned_data, context)
        issues.extend(ph_result["issues"])
        actions_taken.extend(ph_result["actions"])
        
        # Clean organic matter data
        om_result = await self._clean_organic_matter(cleaned_data, context)
        issues.extend(om_result["issues"])
        actions_taken.extend(om_result["actions"])
        
        # Clean nutrient data
        nutrient_result = await self._clean_nutrient_data(cleaned_data, context)
        issues.extend(nutrient_result["issues"])
        actions_taken.extend(nutrient_result["actions"])
        
        # Clean texture and classification data
        texture_result = await self._clean_texture_data(cleaned_data, context)
        issues.extend(texture_result["issues"])
        actions_taken.extend(texture_result["actions"])
        
        # Validate soil test metadata
        metadata_result = await self._clean_test_metadata(cleaned_data, context)
        issues.extend(metadata_result["issues"])
        actions_taken.extend(metadata_result["actions"])
        
        # Calculate quality score
        quality_score = self._calculate_soil_quality_score(cleaned_data, issues)
        
        # Calculate cleaning confidence
        cleaning_confidence = self._calculate_cleaning_confidence(issues, actions_taken)
        
        return CleaningResult(
            original_data=data,
            cleaned_data=cleaned_data,
            issues_found=issues,
            actions_taken=actions_taken,
            quality_score=quality_score,
            cleaning_confidence=cleaning_confidence,
            metadata={
                "cleaner_type": "soil",
                "agricultural_context": context.get("agricultural_context", "general") if context else "general",
                "soil_type": self._determine_soil_type(cleaned_data)
            }
        )
    
    async def _clean_ph_data(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean soil pH data."""
        issues = []
        actions = []
        
        # Handle various pH field names
        ph_fields = ["ph", "soil_ph", "pH", "ph_level"]
        ph_range_fields = ["ph_range", "typical_ph_range", "ph_min_max"]
        
        for ph_field in ph_fields:
            if ph_field in data:
                ph_value = data[ph_field]
                
                # Type validation and conversion
                if isinstance(ph_value, str):
                    try:
                        ph_value = float(ph_value)
                        data[ph_field] = ph_value
                        actions.append(f"Converted {ph_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=ph_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert pH '{ph_value}' to numeric",
                            original_value=ph_value,
                            cleaning_action=CleaningAction.REMOVE,
                            agricultural_context="pH must be numeric for agricultural calculations"
                        ))
                        del data[ph_field]
                        continue
                
                # Range validation
                if ph_value < self.PH_RANGES["min"] or ph_value > self.PH_RANGES["max"]:
                    issues.append(ValidationIssue(
                        field_name=ph_field,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"pH {ph_value} is outside possible range (3.0-10.0)",
                        original_value=ph_value,
                        cleaning_action=CleaningAction.REMOVE,
                        agricultural_context="pH outside possible range indicates measurement error"
                    ))
                    del data[ph_field]
                    actions.append(f"Removed invalid pH value {ph_value}")
                
                elif ph_value < self.PH_RANGES["agricultural_min"] or ph_value > self.PH_RANGES["agricultural_max"]:
                    severity = ValidationSeverity.WARNING if self.PH_RANGES["agricultural_min"] <= ph_value <= self.PH_RANGES["agricultural_max"] else ValidationSeverity.ERROR
                    
                    agricultural_advice = ""
                    if ph_value < self.PH_RANGES["agricultural_min"]:
                        agricultural_advice = "Very acidic soil - lime application recommended"
                    else:
                        agricultural_advice = "Very alkaline soil - may limit nutrient availability"
                    
                    issues.append(ValidationIssue(
                        field_name=ph_field,
                        severity=severity,
                        message=f"pH {ph_value} is outside typical agricultural range",
                        original_value=ph_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context=agricultural_advice
                    ))
        
        # Handle pH ranges
        for range_field in ph_range_fields:
            if range_field in data:
                ph_range = data[range_field]
                if isinstance(ph_range, dict) and "min" in ph_range and "max" in ph_range:
                    ph_min = ph_range["min"]
                    ph_max = ph_range["max"]
                    
                    if ph_min >= ph_max:
                        issues.append(ValidationIssue(
                            field_name=range_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"pH range minimum ({ph_min}) must be less than maximum ({ph_max})",
                            original_value=ph_range,
                            cleaning_action=CleaningAction.CORRECT,
                            suggested_value={"min": min(ph_min, ph_max), "max": max(ph_min, ph_max)}
                        ))
                        data[range_field] = {"min": min(ph_min, ph_max), "max": max(ph_min, ph_max)}
                        actions.append(f"Corrected pH range order in {range_field}")
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_organic_matter(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean organic matter data."""
        issues = []
        actions = []
        
        om_fields = ["organic_matter_percent", "organic_matter", "om_percent", "om"]
        
        for om_field in om_fields:
            if om_field in data:
                om_value = data[om_field]
                
                # Type validation
                if isinstance(om_value, str):
                    # Remove percentage sign if present
                    om_str = om_value.replace("%", "").strip()
                    try:
                        om_value = float(om_str)
                        data[om_field] = om_value
                        actions.append(f"Converted {om_field} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=om_field,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert organic matter '{om_value}' to numeric",
                            original_value=om_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[om_field]
                        continue
                
                # Range validation
                if om_value < self.ORGANIC_MATTER_RANGES["min"]:
                    issues.append(ValidationIssue(
                        field_name=om_field,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative organic matter {om_value}% is invalid",
                        original_value=om_value,
                        suggested_value=0.0,
                        cleaning_action=CleaningAction.CORRECT
                    ))
                    data[om_field] = 0.0
                    actions.append(f"Corrected negative organic matter to 0%")
                
                elif om_value > self.ORGANIC_MATTER_RANGES["max"]:
                    issues.append(ValidationIssue(
                        field_name=om_field,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Organic matter {om_value}% is extremely high",
                        original_value=om_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Extremely high organic matter may indicate peat soil or measurement error"
                    ))
                
                # Agricultural interpretation
                elif om_value < self.ORGANIC_MATTER_RANGES["low_threshold"]:
                    issues.append(ValidationIssue(
                        field_name=om_field,
                        severity=ValidationSeverity.WARNING,
                        message=f"Low organic matter {om_value}%",
                        original_value=om_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Low organic matter - consider cover crops or organic amendments"
                    ))
                
                elif om_value > self.ORGANIC_MATTER_RANGES["high_threshold"]:
                    issues.append(ValidationIssue(
                        field_name=om_field,
                        severity=ValidationSeverity.INFO,
                        message=f"High organic matter {om_value}%",
                        original_value=om_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="High organic matter - excellent soil health indicator"
                    ))
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_nutrient_data(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean soil nutrient data."""
        issues = []
        actions = []
        
        for nutrient, ranges in self.NUTRIENT_RANGES.items():
            if nutrient in data:
                nutrient_value = data[nutrient]
                
                # Type validation
                if isinstance(nutrient_value, str):
                    try:
                        nutrient_value = float(nutrient_value)
                        data[nutrient] = nutrient_value
                        actions.append(f"Converted {nutrient} from string to float")
                    except ValueError:
                        issues.append(ValidationIssue(
                            field_name=nutrient,
                            severity=ValidationSeverity.ERROR,
                            message=f"Cannot convert {nutrient} '{nutrient_value}' to numeric",
                            original_value=nutrient_value,
                            cleaning_action=CleaningAction.REMOVE
                        ))
                        del data[nutrient]
                        continue
                
                # Range validation
                if nutrient_value < ranges["min"]:
                    issues.append(ValidationIssue(
                        field_name=nutrient,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative {nutrient} {nutrient_value} is invalid",
                        original_value=nutrient_value,
                        suggested_value=0.0,
                        cleaning_action=CleaningAction.CORRECT
                    ))
                    data[nutrient] = 0.0
                    actions.append(f"Corrected negative {nutrient} to 0")
                
                elif nutrient_value > ranges["max"]:
                    issues.append(ValidationIssue(
                        field_name=nutrient,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"{nutrient} {nutrient_value} ppm is extremely high",
                        original_value=nutrient_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context=f"Extremely high {nutrient} may indicate contamination or measurement error"
                    ))
                
                # Agricultural interpretation
                elif nutrient_value < ranges["optimal_min"]:
                    issues.append(ValidationIssue(
                        field_name=nutrient,
                        severity=ValidationSeverity.WARNING,
                        message=f"Low {nutrient} {nutrient_value} ppm",
                        original_value=nutrient_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context=f"Low {nutrient} - fertilizer application may be needed"
                    ))
                
                elif nutrient_value > ranges["optimal_max"]:
                    issues.append(ValidationIssue(
                        field_name=nutrient,
                        severity=ValidationSeverity.INFO,
                        message=f"High {nutrient} {nutrient_value} ppm",
                        original_value=nutrient_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context=f"High {nutrient} - reduce fertilizer application"
                    ))
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_texture_data(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean soil texture and classification data."""
        issues = []
        actions = []
        
        # Standardize soil texture classifications
        texture_field = "soil_texture"
        if texture_field in data:
            texture_value = data[texture_field]
            
            if isinstance(texture_value, str):
                # Normalize texture classification
                normalized_texture = self._normalize_soil_texture(texture_value)
                if normalized_texture != texture_value:
                    data[texture_field] = normalized_texture
                    actions.append(f"Normalized soil texture from '{texture_value}' to '{normalized_texture}'")
                
                # Validate texture classification
                valid_textures = [
                    "sand", "loamy_sand", "sandy_loam", "loam", "silt_loam", 
                    "silt", "sandy_clay_loam", "clay_loam", "silty_clay_loam",
                    "sandy_clay", "silty_clay", "clay"
                ]
                
                if normalized_texture not in valid_textures:
                    issues.append(ValidationIssue(
                        field_name=texture_field,
                        severity=ValidationSeverity.WARNING,
                        message=f"Unrecognized soil texture '{normalized_texture}'",
                        original_value=texture_value,
                        cleaning_action=CleaningAction.FLAG,
                        agricultural_context="Soil texture affects water retention and nutrient management"
                    ))
        
        # Clean drainage class
        drainage_field = "drainage_class"
        if drainage_field in data:
            drainage_value = data[drainage_field]
            
            if isinstance(drainage_value, str):
                normalized_drainage = self._normalize_drainage_class(drainage_value)
                if normalized_drainage != drainage_value:
                    data[drainage_field] = normalized_drainage
                    actions.append(f"Normalized drainage class from '{drainage_value}' to '{normalized_drainage}'")
        
        return {"issues": issues, "actions": actions}
    
    async def _clean_test_metadata(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean soil test metadata."""
        issues = []
        actions = []
        
        # Validate test date
        if "test_date" in data:
            test_date = data["test_date"]
            
            if isinstance(test_date, str):
                try:
                    parsed_date = datetime.fromisoformat(test_date.replace("Z", "+00:00")).replace(tzinfo=None)
                    data["test_date"] = parsed_date.isoformat()
                    
                    # Check test age
                    age_days = (datetime.utcnow() - parsed_date).days
                    
                    if age_days > 1095:  # 3 years
                        issues.append(ValidationIssue(
                            field_name="test_date",
                            severity=ValidationSeverity.WARNING,
                            message=f"Soil test is {age_days} days old",
                            original_value=test_date,
                            cleaning_action=CleaningAction.FLAG,
                            agricultural_context="Soil tests older than 3 years may not reflect current conditions"
                        ))
                    
                    elif age_days > 1825:  # 5 years
                        issues.append(ValidationIssue(
                            field_name="test_date",
                            severity=ValidationSeverity.ERROR,
                            message=f"Soil test is very old ({age_days} days)",
                            original_value=test_date,
                            cleaning_action=CleaningAction.FLAG,
                            agricultural_context="Very old soil tests should not be used for current recommendations"
                        ))
                
                except ValueError:
                    issues.append(ValidationIssue(
                        field_name="test_date",
                        severity=ValidationSeverity.ERROR,
                        message=f"Cannot parse test date '{test_date}'",
                        original_value=test_date,
                        cleaning_action=CleaningAction.REMOVE
                    ))
                    del data["test_date"]
        
        # Validate lab information
        if "lab_name" in data:
            lab_name = data["lab_name"]
            if isinstance(lab_name, str):
                # Clean lab name
                cleaned_lab_name = re.sub(r'[<>"\';\\]', '', lab_name).strip()
                if len(cleaned_lab_name) > 100:
                    cleaned_lab_name = cleaned_lab_name[:100]
                
                if cleaned_lab_name != lab_name:
                    data["lab_name"] = cleaned_lab_name
                    actions.append("Cleaned lab name for security")
        
        return {"issues": issues, "actions": actions}
    
    def _normalize_soil_texture(self, texture: str) -> str:
        """Normalize soil texture classification."""
        texture_lower = texture.lower().strip()
        
        # Mapping of common variations to standard classifications
        texture_mapping = {
            "sandy": "sand",
            "loamy sand": "loamy_sand",
            "sandy loam": "sandy_loam",
            "silt loam": "silt_loam",
            "sandy clay loam": "sandy_clay_loam",
            "clay loam": "clay_loam",
            "silty clay loam": "silty_clay_loam",
            "sandy clay": "sandy_clay",
            "silty clay": "silty_clay"
        }
        
        return texture_mapping.get(texture_lower, texture_lower.replace(" ", "_"))
    
    def _normalize_drainage_class(self, drainage: str) -> str:
        """Normalize drainage class."""
        drainage_lower = drainage.lower().strip()
        
        drainage_mapping = {
            "well drained": "well_drained",
            "moderately well drained": "moderately_well_drained",
            "somewhat poorly drained": "somewhat_poorly_drained",
            "poorly drained": "poorly_drained",
            "very poorly drained": "very_poorly_drained",
            "excessively drained": "excessively_drained"
        }
        
        return drainage_mapping.get(drainage_lower, drainage_lower.replace(" ", "_"))
    
    def _calculate_soil_quality_score(self, data: Dict[str, Any], issues: List[ValidationIssue]) -> float:
        """Calculate quality score for soil data."""
        base_score = 1.0
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 0.4
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 0.25
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 0.1
        
        # Bonus for completeness
        required_fields = ["ph", "organic_matter_percent", "phosphorus_ppm", "potassium_ppm"]
        present_fields = sum(1 for field in required_fields if field in data)
        completeness_bonus = (present_fields / len(required_fields)) * 0.15
        
        return max(0.0, min(1.0, base_score + completeness_bonus))
    
    def _calculate_cleaning_confidence(self, issues: List[ValidationIssue], actions: List[str]) -> float:
        """Calculate confidence in cleaning actions."""
        if not issues:
            return 1.0
        
        # High confidence for automatic corrections
        auto_corrections = sum(1 for issue in issues if issue.cleaning_action in [CleaningAction.CORRECT, CleaningAction.NORMALIZE])
        manual_reviews = sum(1 for issue in issues if issue.cleaning_action == CleaningAction.FLAG)
        removals = sum(1 for issue in issues if issue.cleaning_action == CleaningAction.REMOVE)
        
        total_issues = len(issues)
        confidence = (auto_corrections * 0.9 + manual_reviews * 0.7 + removals * 0.5) / total_issues
        
        return max(0.0, min(1.0, confidence))
    
    def _determine_soil_type(self, data: Dict[str, Any]) -> str:
        """Determine soil type from cleaned data."""
        if "soil_texture" in data:
            return data["soil_texture"]
        elif "texture" in data:
            return data["texture"]
        else:
            return "unknown"


class DataValidationPipeline:
    """Main data validation and cleaning pipeline."""
    
    def __init__(self):
        self.cleaners = {
            "weather": WeatherDataCleaner(),
            "soil": SoilDataCleaner()
        }
        self.validation_history = []
    
    async def validate_and_clean(self, data: Dict[str, Any], data_type: str, 
                                context: Dict[str, Any] = None) -> CleaningResult:
        """Validate and clean data using appropriate cleaner."""
        
        if data_type not in self.cleaners:
            raise ValueError(f"No cleaner available for data type: {data_type}")
        
        cleaner = self.cleaners[data_type]
        result = await cleaner.clean_data(data, context)
        
        # Store validation history
        self.validation_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "data_type": data_type,
            "quality_score": result.quality_score,
            "issues_count": len(result.issues_found),
            "actions_count": len(result.actions_taken)
        })
        
        # Keep only last 1000 validation records
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]
        
        return result
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation pipeline metrics."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "average_quality_score": 0.0,
                "data_types": {}
            }
        
        total_validations = len(self.validation_history)
        avg_quality = sum(record["quality_score"] for record in self.validation_history) / total_validations
        
        # Group by data type
        data_types = {}
        for record in self.validation_history:
            data_type = record["data_type"]
            if data_type not in data_types:
                data_types[data_type] = {
                    "count": 0,
                    "avg_quality": 0.0,
                    "total_issues": 0,
                    "total_actions": 0
                }
            
            data_types[data_type]["count"] += 1
            data_types[data_type]["total_issues"] += record["issues_count"]
            data_types[data_type]["total_actions"] += record["actions_count"]
        
        # Calculate averages
        for data_type, stats in data_types.items():
            type_records = [r for r in self.validation_history if r["data_type"] == data_type]
            stats["avg_quality"] = sum(r["quality_score"] for r in type_records) / len(type_records)
            stats["avg_issues_per_validation"] = stats["total_issues"] / stats["count"]
            stats["avg_actions_per_validation"] = stats["total_actions"] / stats["count"]
        
        return {
            "total_validations": total_validations,
            "average_quality_score": round(avg_quality, 3),
            "data_types": data_types,
            "recent_validations": self.validation_history[-10:]  # Last 10 validations
        }
    
    def register_cleaner(self, data_type: str, cleaner: AgriculturalDataCleaner):
        """Register a new data cleaner."""
        self.cleaners[data_type] = cleaner
        logger.info("Registered data cleaner", data_type=data_type)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on validation pipeline."""
        health_status = {
            "status": "healthy",
            "registered_cleaners": list(self.cleaners.keys()),
            "validation_history_size": len(self.validation_history)
        }
        
        # Check if cleaners are working
        try:
            # Test weather cleaner
            test_weather_data = {"temperature_f": 75.0, "humidity_percent": 65.0}
            weather_result = await self.cleaners["weather"].clean_data(test_weather_data)
            
            # Test soil cleaner
            test_soil_data = {"ph": 6.5, "organic_matter_percent": 3.0}
            soil_result = await self.cleaners["soil"].clean_data(test_soil_data)
            
            health_status["test_results"] = {
                "weather_cleaner": "healthy",
                "soil_cleaner": "healthy"
            }
            
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["error"] = str(e)
        
        return health_status