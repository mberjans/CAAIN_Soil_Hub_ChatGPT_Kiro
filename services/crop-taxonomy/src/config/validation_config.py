"""
Agricultural Validation Configuration

This module contains configuration settings for the agricultural validation
and expert review system.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(str, Enum):
    """Validation status levels."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPERT_REVIEW_REQUIRED = "expert_review_required"


class ExpertReviewStatus(str, Enum):
    """Expert review status levels."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    EXPERT_CONSULTATION = "expert_consultation"


class ReviewPriority(str, Enum):
    """Review priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ValidationThresholds:
    """Validation performance thresholds."""
    agricultural_soundness: float = 0.8
    regional_applicability: float = 0.7
    economic_feasibility: float = 0.6
    farmer_practicality: float = 0.7
    overall_minimum: float = 0.75


@dataclass
class ExpertReviewThresholds:
    """Expert review trigger thresholds."""
    low_confidence: float = 0.6
    regional_edge_case: float = 0.7
    new_variety: float = 0.8
    complex_scenario: float = 0.75


@dataclass
class ReviewTimeouts:
    """Review timeout configurations."""
    low: int = 14  # days
    normal: int = 7  # days
    high: int = 3  # days
    urgent: int = 1  # day


@dataclass
class QualityThresholds:
    """Quality assessment thresholds."""
    minimum_expert_score: float = 0.7
    minimum_agricultural_soundness: float = 0.8
    minimum_regional_applicability: float = 0.7
    minimum_economic_feasibility: float = 0.6
    minimum_farmer_practicality: float = 0.7


@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds."""
    validation_success_rate: float = 0.95
    expert_review_completion_rate: float = 0.90
    average_farmer_satisfaction: float = 0.85
    average_validation_score: float = 0.80
    average_expert_score: float = 0.85


class ValidationConfig:
    """Main configuration class for agricultural validation system."""

    def __init__(self):
        # Database configuration
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/validation_db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Validation thresholds
        self.validation_thresholds = ValidationThresholds()
        self.expert_review_thresholds = ExpertReviewThresholds()
        self.review_timeouts = ReviewTimeouts()
        self.quality_thresholds = QualityThresholds()
        self.performance_thresholds = PerformanceThresholds()
        
        # System configuration
        self.max_concurrent_validations = int(os.getenv("MAX_CONCURRENT_VALIDATIONS", "100"))
        self.validation_timeout_seconds = int(os.getenv("VALIDATION_TIMEOUT_SECONDS", "30"))
        self.cache_ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        
        # Expert review configuration
        self.max_reviewer_assignments = {
            ReviewPriority.LOW: 5,
            ReviewPriority.NORMAL: 3,
            ReviewPriority.HIGH: 2,
            ReviewPriority.URGENT: 1
        }
        
        self.minimum_review_interval_hours = int(os.getenv("MINIMUM_REVIEW_INTERVAL_HOURS", "24"))
        
        # Regional configuration
        self.supported_regions = [
            "Midwest", "Northeast", "Southeast", "Southwest", "Northwest",
            "Great Plains", "Corn Belt", "Cotton Belt", "Wheat Belt"
        ]
        
        self.supported_crop_types = [
            "corn", "soybeans", "wheat", "cotton", "rice", "barley", "oats",
            "sorghum", "sunflower", "canola", "sugar_beets", "potatoes",
            "tomatoes", "lettuce", "onions", "carrots", "broccoli"
        ]
        
        # Validation criteria weights
        self.validation_criteria_weights = {
            "agricultural_soundness": 0.30,
            "regional_applicability": 0.25,
            "economic_feasibility": 0.20,
            "farmer_practicality": 0.25
        }
        
        # Expert review criteria weights
        self.expert_review_criteria_weights = {
            "agricultural_soundness": 0.30,
            "regional_applicability": 0.25,
            "economic_feasibility": 0.20,
            "farmer_practicality": 0.25
        }
        
        # Notification configuration
        self.notification_enabled = os.getenv("NOTIFICATION_ENABLED", "true").lower() == "true"
        self.email_notifications = os.getenv("EMAIL_NOTIFICATIONS", "true").lower() == "true"
        self.slack_notifications = os.getenv("SLACK_NOTIFICATIONS", "false").lower() == "true"
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.log_file = os.getenv("LOG_FILE", "validation_system.log")
        
        # Metrics configuration
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.metrics_retention_days = int(os.getenv("METRICS_RETENTION_DAYS", "365"))
        self.real_time_metrics_interval = int(os.getenv("REAL_TIME_METRICS_INTERVAL", "60"))  # seconds
        
        # Security configuration
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "default_encryption_key")
        self.jwt_secret = os.getenv("JWT_SECRET", "default_jwt_secret")
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
        
        # API configuration
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "1000"))  # requests per hour
        self.api_timeout_seconds = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # External service configuration
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "")
        self.soil_api_key = os.getenv("SOIL_API_KEY", "")
        self.market_data_api_key = os.getenv("MARKET_DATA_API_KEY", "")
        
        # Validation algorithm configuration
        self.validation_algorithm_version = os.getenv("VALIDATION_ALGORITHM_VERSION", "1.0")
        self.enable_ml_validation = os.getenv("ENABLE_ML_VALIDATION", "false").lower() == "true"
        self.ml_model_path = os.getenv("ML_MODEL_PATH", "models/validation_model.pkl")
        
        # Expert review workflow configuration
        self.auto_assignment_enabled = os.getenv("AUTO_ASSIGNMENT_ENABLED", "true").lower() == "true"
        self.escalation_enabled = os.getenv("ESCALATION_ENABLED", "true").lower() == "true"
        self.peer_review_threshold = float(os.getenv("PEER_REVIEW_THRESHOLD", "0.8"))
        
        # Farmer feedback configuration
        self.farmer_feedback_enabled = os.getenv("FARMER_FEEDBACK_ENABLED", "true").lower() == "true"
        self.feedback_retention_days = int(os.getenv("FEEDBACK_RETENTION_DAYS", "730"))
        self.automatic_feedback_requests = os.getenv("AUTOMATIC_FEEDBACK_REQUESTS", "true").lower() == "true"
        
        # Performance monitoring configuration
        self.performance_monitoring_enabled = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
        self.slow_query_threshold_ms = int(os.getenv("SLOW_QUERY_THRESHOLD_MS", "1000"))
        self.memory_usage_threshold_percent = int(os.getenv("MEMORY_USAGE_THRESHOLD_PERCENT", "80"))
        self.cpu_usage_threshold_percent = int(os.getenv("CPU_USAGE_THRESHOLD_PERCENT", "80"))
        
        # Backup and recovery configuration
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_interval_hours = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
        self.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        
        # Development and testing configuration
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.mock_external_services = os.getenv("MOCK_EXTERNAL_SERVICES", "false").lower() == "true"

    def get_validation_threshold(self, criterion: str) -> float:
        """Get validation threshold for specific criterion."""
        return getattr(self.validation_thresholds, criterion, 0.0)

    def get_expert_review_threshold(self, threshold_type: str) -> float:
        """Get expert review threshold for specific type."""
        return getattr(self.expert_review_thresholds, threshold_type, 0.0)

    def get_review_timeout(self, priority: ReviewPriority) -> int:
        """Get review timeout for specific priority."""
        return getattr(self.review_timeouts, priority.value, 7)

    def get_quality_threshold(self, criterion: str) -> float:
        """Get quality threshold for specific criterion."""
        return getattr(self.quality_thresholds, criterion, 0.0)

    def get_performance_threshold(self, metric: str) -> float:
        """Get performance threshold for specific metric."""
        return getattr(self.performance_thresholds, metric, 0.0)

    def is_region_supported(self, region: str) -> bool:
        """Check if region is supported."""
        return region in self.supported_regions

    def is_crop_type_supported(self, crop_type: str) -> bool:
        """Check if crop type is supported."""
        return crop_type in self.supported_crop_types

    def get_validation_criteria_weight(self, criterion: str) -> float:
        """Get validation criteria weight."""
        return self.validation_criteria_weights.get(criterion, 0.0)

    def get_expert_review_criteria_weight(self, criterion: str) -> float:
        """Get expert review criteria weight."""
        return self.expert_review_criteria_weights.get(criterion, 0.0)

    def get_max_reviewer_assignments(self, priority: ReviewPriority) -> int:
        """Get maximum reviewer assignments for priority."""
        return self.max_reviewer_assignments.get(priority, 1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "validation_thresholds": {
                "agricultural_soundness": self.validation_thresholds.agricultural_soundness,
                "regional_applicability": self.validation_thresholds.regional_applicability,
                "economic_feasibility": self.validation_thresholds.economic_feasibility,
                "farmer_practicality": self.validation_thresholds.farmer_practicality,
                "overall_minimum": self.validation_thresholds.overall_minimum
            },
            "expert_review_thresholds": {
                "low_confidence": self.expert_review_thresholds.low_confidence,
                "regional_edge_case": self.expert_review_thresholds.regional_edge_case,
                "new_variety": self.expert_review_thresholds.new_variety,
                "complex_scenario": self.expert_review_thresholds.complex_scenario
            },
            "review_timeouts": {
                "low": self.review_timeouts.low,
                "normal": self.review_timeouts.normal,
                "high": self.review_timeouts.high,
                "urgent": self.review_timeouts.urgent
            },
            "quality_thresholds": {
                "minimum_expert_score": self.quality_thresholds.minimum_expert_score,
                "minimum_agricultural_soundness": self.quality_thresholds.minimum_agricultural_soundness,
                "minimum_regional_applicability": self.quality_thresholds.minimum_regional_applicability,
                "minimum_economic_feasibility": self.quality_thresholds.minimum_economic_feasibility,
                "minimum_farmer_practicality": self.quality_thresholds.minimum_farmer_practicality
            },
            "performance_thresholds": {
                "validation_success_rate": self.performance_thresholds.validation_success_rate,
                "expert_review_completion_rate": self.performance_thresholds.expert_review_completion_rate,
                "average_farmer_satisfaction": self.performance_thresholds.average_farmer_satisfaction,
                "average_validation_score": self.performance_thresholds.average_validation_score,
                "average_expert_score": self.performance_thresholds.average_expert_score
            },
            "supported_regions": self.supported_regions,
            "supported_crop_types": self.supported_crop_types,
            "validation_criteria_weights": self.validation_criteria_weights,
            "expert_review_criteria_weights": self.expert_review_criteria_weights,
            "max_concurrent_validations": self.max_concurrent_validations,
            "validation_timeout_seconds": self.validation_timeout_seconds,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "minimum_review_interval_hours": self.minimum_review_interval_hours,
            "notification_enabled": self.notification_enabled,
            "email_notifications": self.email_notifications,
            "slack_notifications": self.slack_notifications,
            "log_level": self.log_level,
            "metrics_enabled": self.metrics_enabled,
            "metrics_retention_days": self.metrics_retention_days,
            "real_time_metrics_interval": self.real_time_metrics_interval,
            "api_rate_limit": self.api_rate_limit,
            "api_timeout_seconds": self.api_timeout_seconds,
            "cors_origins": self.cors_origins,
            "validation_algorithm_version": self.validation_algorithm_version,
            "enable_ml_validation": self.enable_ml_validation,
            "ml_model_path": self.ml_model_path,
            "auto_assignment_enabled": self.auto_assignment_enabled,
            "escalation_enabled": self.escalation_enabled,
            "peer_review_threshold": self.peer_review_threshold,
            "farmer_feedback_enabled": self.farmer_feedback_enabled,
            "feedback_retention_days": self.feedback_retention_days,
            "automatic_feedback_requests": self.automatic_feedback_requests,
            "performance_monitoring_enabled": self.performance_monitoring_enabled,
            "slow_query_threshold_ms": self.slow_query_threshold_ms,
            "memory_usage_threshold_percent": self.memory_usage_threshold_percent,
            "cpu_usage_threshold_percent": self.cpu_usage_threshold_percent,
            "backup_enabled": self.backup_enabled,
            "backup_interval_hours": self.backup_interval_hours,
            "backup_retention_days": self.backup_retention_days,
            "debug_mode": self.debug_mode,
            "test_mode": self.test_mode,
            "mock_external_services": self.mock_external_services
        }


# Global configuration instance
config = ValidationConfig()


def get_config() -> ValidationConfig:
    """Get global configuration instance."""
    return config


def reload_config():
    """Reload configuration from environment variables."""
    global config
    config = ValidationConfig()


# Configuration validation
def validate_config() -> List[str]:
    """Validate configuration settings."""
    errors = []
    
    # Validate thresholds
    if config.validation_thresholds.overall_minimum < 0.0 or config.validation_thresholds.overall_minimum > 1.0:
        errors.append("Overall minimum validation threshold must be between 0.0 and 1.0")
    
    if config.expert_review_thresholds.low_confidence < 0.0 or config.expert_review_thresholds.low_confidence > 1.0:
        errors.append("Low confidence expert review threshold must be between 0.0 and 1.0")
    
    # Validate timeouts
    if config.review_timeouts.urgent < 1:
        errors.append("Urgent review timeout must be at least 1 day")
    
    if config.review_timeouts.low < config.review_timeouts.normal:
        errors.append("Low priority timeout should be greater than normal priority timeout")
    
    # Validate weights
    total_validation_weight = sum(config.validation_criteria_weights.values())
    if abs(total_validation_weight - 1.0) > 0.01:
        errors.append(f"Validation criteria weights must sum to 1.0, got {total_validation_weight}")
    
    total_expert_weight = sum(config.expert_review_criteria_weights.values())
    if abs(total_expert_weight - 1.0) > 0.01:
        errors.append(f"Expert review criteria weights must sum to 1.0, got {total_expert_weight}")
    
    # Validate limits
    if config.max_concurrent_validations < 1:
        errors.append("Maximum concurrent validations must be at least 1")
    
    if config.validation_timeout_seconds < 1:
        errors.append("Validation timeout must be at least 1 second")
    
    if config.cache_ttl_seconds < 0:
        errors.append("Cache TTL must be non-negative")
    
    return errors