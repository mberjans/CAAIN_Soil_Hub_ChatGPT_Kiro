"""
Adaptive Recommendation Learning System for fertilizer application method optimization.

This module implements a comprehensive learning system that tracks recommendation outcomes,
integrates farmer feedback, and continuously improves recommendations through machine learning
and pattern recognition. The system adapts to regional conditions, farm-specific characteristics,
and seasonal variations.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json
import os

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType
)
from src.models.application_models import EquipmentSpecification
from src.servicesgoal_based_recommendation_engine import GoalBasedRecommendationEngine, OptimizationGoal
from srcdatabase.fertilizer_db import get_application_methods_by_type

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    YIELD_OUTCOME = "yield_outcome"
    COST_EFFECTIVENESS = "cost_effectiveness"
    LABOR_EFFICIENCY = "labor_efficiency"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    EQUIPMENT_PERFORMANCE = "equipment_performance"
    OVERALL_SATISFACTION = "overall_satisfaction"


class LearningModelType(Enum):
    """Types of machine learning models."""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR_REGRESSION = "linear_regression"
    ENSEMBLE = "ensemble"


@dataclass
class RecommendationOutcome:
    """Represents the outcome of a fertilizer application recommendation."""
    recommendation_id: str
    farmer_id: str
    field_id: str
    method_type: ApplicationMethodType
    field_conditions: Dict[str, Any]
    crop_requirements: Dict[str, Any]
    fertilizer_specification: Dict[str, Any]
    recommendation_date: datetime
    application_date: Optional[datetime] = None
    harvest_date: Optional[datetime] = None
    
    # Outcome metrics
    actual_yield: Optional[float] = None
    predicted_yield: Optional[float] = None
    yield_accuracy: Optional[float] = None
    
    actual_cost_per_acre: Optional[float] = None
    predicted_cost_per_acre: Optional[float] = None
    cost_accuracy: Optional[float] = None
    
    labor_hours: Optional[float] = None
    equipment_issues: Optional[List[str]] = None
    
    # Environmental metrics
    runoff_incident: Optional[bool] = None
    nutrient_loss_percent: Optional[float] = None
    
    # Farmer feedback
    farmer_rating: Optional[int] = None  # 1-5 scale
    farmer_comments: Optional[str] = None
    would_recommend: Optional[bool] = None
    
    # Learning features
    regional_adaptation_score: Optional[float] = None
    seasonal_adjustment_factor: Optional[float] = None
    farm_specific_factor: Optional[float] = None


@dataclass
class LearningMetrics:
    """Metrics for evaluating learning system performance."""
    model_accuracy: float
    prediction_error: float
    feedback_integration_rate: float
    adaptation_effectiveness: float
    seasonal_adjustment_accuracy: float
    regional_adaptation_score: float
    last_updated: datetime


@dataclass
class AdaptationProfile:
    """Profile for regional and farm-specific adaptation."""
    region_id: str
    farm_id: str
    soil_type_preferences: Dict[str, float]
    crop_success_patterns: Dict[str, float]
    seasonal_factors: Dict[str, float]
    equipment_efficiency: Dict[str, float]
    cost_sensitivity: float
    labor_preferences: Dict[str, float]
    environmental_priorities: Dict[str, float]
    last_updated: datetime


class AdaptiveLearningService:
    """
    Adaptive recommendation learning system for fertilizer application methods.
    
    This service implements machine learning-based recommendation improvement through:
    - Outcome tracking and analysis
    - Farmer feedback integration
    - Regional and farm-specific adaptation
    - Seasonal adjustment mechanisms
    - Continuous model refinement
    """
    
    def __init__(self):
        """Initialize the adaptive learning service."""
        self.goal_engine = GoalBasedRecommendationEngine()
        self.outcomes_db = {}  # In production, this would be a proper database
        self.feedback_db = {}  # In production, this would be a proper database
        self.adaptation_profiles = {}  # In production, this would be a proper database
        self.learning_models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.learning_metrics = LearningMetrics(
            model_accuracy=0.0,
            prediction_error=0.0,
            feedback_integration_rate=0.0,
            adaptation_effectiveness=0.0,
            seasonal_adjustment_accuracy=0.0,
            regional_adaptation_score=0.0,
            last_updated=datetime.utcnow()
        )
        
        # Initialize learning models
        self._initialize_learning_models()
        
        # Load existing models if available
        self._load_existing_models()
    
    def _initialize_learning_models(self):
        """Initialize machine learning models for different prediction tasks."""
        self.learning_models = {
            "yield_prediction": {
                "model": RandomForestRegressor(n_estimators=100, random_state=42),
                "features": ["field_size", "soil_ph", "organic_matter", "method_efficiency", "fertilizer_rate"],
                "target": "actual_yield"
            },
            "cost_prediction": {
                "model": LinearRegression(),
                "features": ["method_cost", "fertilizer_cost", "labor_cost", "equipment_cost"],
                "target": "actual_cost_per_acre"
            },
            "satisfaction_prediction": {
                "model": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "features": ["yield_accuracy", "cost_accuracy", "labor_efficiency", "environmental_impact"],
                "target": "farmer_rating"
            },
            "method_selection": {
                "model": RandomForestRegressor(n_estimators=100, random_state=42),
                "features": ["field_conditions", "crop_requirements", "farmer_preferences", "seasonal_factors"],
                "target": "method_type"
            }
        }
        
        # Initialize scalers and encoders
        for model_name in self.learning_models:
            self.scalers[model_name] = StandardScaler()
            self.label_encoders[model_name] = LabelEncoder()
    
    def _load_existing_models(self):
        """Load pre-trained models if they exist."""
        model_dir = "models/adaptive_learning"
        if os.path.exists(model_dir):
            try:
                for model_name, model_info in self.learning_models.items():
                    model_path = os.path.join(model_dir, f"{model_name}_model.joblib")
                    scaler_path = os.path.join(model_dir, f"{model_name}_scaler.joblib")
                    
                    if os.path.exists(model_path):
                        self.learning_models[model_name]["model"] = joblib.load(model_path)
                        logger.info(f"Loaded pre-trained model: {model_name}")
                    
                    if os.path.exists(scaler_path):
                        self.scalers[model_name] = joblib.load(scaler_path)
                        logger.info(f"Loaded scaler for model: {model_name}")
            except Exception as e:
                logger.warning(f"Error loading existing models: {e}")
    
    async def track_recommendation_outcome(
        self,
        recommendation_id: str,
        farmer_id: str,
        field_id: str,
        method_type: ApplicationMethodType,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        outcome_data: Dict[str, Any]
    ) -> RecommendationOutcome:
        """
        Track the outcome of a fertilizer application recommendation.
        
        Args:
            recommendation_id: Unique identifier for the recommendation
            farmer_id: Identifier for the farmer
            field_id: Identifier for the field
            method_type: Application method that was recommended
            field_conditions: Field conditions at time of recommendation
            crop_requirements: Crop requirements for the application
            fertilizer_specification: Fertilizer specification used
            outcome_data: Dictionary containing outcome metrics
            
        Returns:
            RecommendationOutcome object with tracked data
        """
        try:
            logger.info(f"Tracking outcome for recommendation {recommendation_id}")
            
            # Create outcome record
            outcome = RecommendationOutcome(
                recommendation_id=recommendation_id,
                farmer_id=farmer_id,
                field_id=field_id,
                method_type=method_type,
                field_conditions=field_conditions.dict(),
                crop_requirements=crop_requirements.dict(),
                fertilizer_specification=fertilizer_specification.dict(),
                recommendation_date=datetime.utcnow(),
                application_date=outcome_data.get("application_date"),
                harvest_date=outcome_data.get("harvest_date"),
                actual_yield=outcome_data.get("actual_yield"),
                predicted_yield=outcome_data.get("predicted_yield"),
                actual_cost_per_acre=outcome_data.get("actual_cost_per_acre"),
                predicted_cost_per_acre=outcome_data.get("predicted_cost_per_acre"),
                labor_hours=outcome_data.get("labor_hours"),
                equipment_issues=outcome_data.get("equipment_issues", []),
                runoff_incident=outcome_data.get("runoff_incident"),
                nutrient_loss_percent=outcome_data.get("nutrient_loss_percent"),
                farmer_rating=outcome_data.get("farmer_rating"),
                farmer_comments=outcome_data.get("farmer_comments"),
                would_recommend=outcome_data.get("would_recommend")
            )
            
            # Calculate accuracy metrics
            if outcome.actual_yield and outcome.predicted_yield:
                outcome.yield_accuracy = 1.0 - abs(outcome.actual_yield - outcome.predicted_yield) / outcome.predicted_yield
            
            if outcome.actual_cost_per_acre and outcome.predicted_cost_per_acre:
                outcome.cost_accuracy = 1.0 - abs(outcome.actual_cost_per_acre - outcome.predicted_cost_per_acre) / outcome.predicted_cost_per_acre
            
            # Store outcome
            self.outcomes_db[recommendation_id] = outcome
            
            # Update adaptation profiles
            await self._update_adaptation_profile(farmer_id, field_id, outcome)
            
            # Trigger learning if enough data is available
            await self._trigger_learning_if_ready()
            
            logger.info(f"Successfully tracked outcome for recommendation {recommendation_id}")
            return outcome
            
        except Exception as e:
            logger.error(f"Error tracking recommendation outcome: {e}")
            raise
    
    async def integrate_farmer_feedback(
        self,
        recommendation_id: str,
        feedback_type: FeedbackType,
        feedback_value: Any,
        comments: Optional[str] = None
    ) -> bool:
        """
        Integrate farmer feedback into the learning system.
        
        Args:
            recommendation_id: Identifier for the recommendation
            feedback_type: Type of feedback being provided
            feedback_value: The feedback value (rating, boolean, etc.)
            comments: Optional comments from the farmer
            
        Returns:
            True if feedback was successfully integrated
        """
        try:
            logger.info(f"Integrating farmer feedback for recommendation {recommendation_id}")
            
            # Get the outcome record
            outcome = self.outcomes_db.get(recommendation_id)
            if not outcome:
                logger.warning(f"No outcome found for recommendation {recommendation_id}")
                return False
            
            # Update outcome with feedback
            if feedback_type == FeedbackType.YIELD_OUTCOME:
                outcome.actual_yield = feedback_value
            elif feedback_type == FeedbackType.COST_EFFECTIVENESS:
                outcome.actual_cost_per_acre = feedback_value
            elif feedback_type == FeedbackType.LABOR_EFFICIENCY:
                outcome.labor_hours = feedback_value
            elif feedback_type == FeedbackType.ENVIRONMENTAL_IMPACT:
                outcome.runoff_incident = feedback_value
            elif feedback_type == FeedbackType.OVERALL_SATISFACTION:
                outcome.farmer_rating = feedback_value
            
            if comments:
                outcome.farmer_comments = comments
            
            # Store feedback
            self.feedback_db[recommendation_id] = {
                "feedback_type": feedback_type,
                "feedback_value": feedback_value,
                "comments": comments,
                "timestamp": datetime.utcnow()
            }
            
            # Update learning metrics
            await self._update_learning_metrics()
            
            logger.info(f"Successfully integrated farmer feedback for recommendation {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error integrating farmer feedback: {e}")
            return False
    
    async def improve_recommendations(
        self,
        request: ApplicationRequest,
        farmer_id: str,
        field_id: str
    ) -> ApplicationResponse:
        """
        Generate improved recommendations using machine learning insights.
        
        Args:
            request: Application request with field conditions and requirements
            farmer_id: Identifier for the farmer
            field_id: Identifier for the field
            
        Returns:
            Improved ApplicationResponse with ML-enhanced recommendations
        """
        try:
            logger.info(f"Generating ML-improved recommendations for farmer {farmer_id}")
            
            # Get base recommendations from goal-based engine
            base_response = await self.goal_engine.optimize_application_methods(request)
            
            # Apply regional adaptation
            regional_adjustments = await self._apply_regional_adaptation(
                farmer_id, field_id, request
            )
            
            # Apply farm-specific adaptation
            farm_adjustments = await self._apply_farm_specific_adaptation(
                farmer_id, field_id, request
            )
            
            # Apply seasonal adjustments
            seasonal_adjustments = await self._apply_seasonal_adjustments(
                request, datetime.utcnow()
            )
            
            # Predict outcomes for each method
            method_predictions = await self._predict_method_outcomes(
                request, base_response.method_scores
            )
            
            # Adjust scores based on predictions and adaptations
            improved_scores = await self._adjust_scores_with_ml_insights(
                base_response.method_scores,
                method_predictions,
                regional_adjustments,
                farm_adjustments,
                seasonal_adjustments
            )
            
            # Generate improved recommendations
            improved_response = await self._generate_improved_response(
                request, improved_scores, base_response
            )
            
            logger.info(f"Successfully generated ML-improved recommendations")
            return improved_response
            
        except Exception as e:
            logger.error(f"Error improving recommendations: {e}")
            # Fall back to base recommendations
            return await self.goal_engine.optimize_application_methods(request)
    
    async def _update_adaptation_profile(
        self,
        farmer_id: str,
        field_id: str,
        outcome: RecommendationOutcome
    ):
        """Update adaptation profile based on outcome data."""
        profile_key = f"{farmer_id}_{field_id}"
        
        if profile_key not in self.adaptation_profiles:
            self.adaptation_profiles[profile_key] = AdaptationProfile(
                region_id=self._get_region_id(field_id),
                farm_id=farmer_id,
                soil_type_preferences={},
                crop_success_patterns={},
                seasonal_factors={},
                equipment_efficiency={},
                cost_sensitivity=0.5,
                labor_preferences={},
                environmental_priorities={},
                last_updated=datetime.utcnow()
            )
        
        profile = self.adaptation_profiles[profile_key]
        
        # Update soil type preferences
        soil_type = outcome.field_conditions.get("soil_type", "unknown")
        if soil_type in profile.soil_type_preferences:
            profile.soil_type_preferences[soil_type] += 0.1
        else:
            profile.soil_type_preferences[soil_type] = 0.1
        
        # Update crop success patterns
        crop_type = outcome.crop_requirements.get("crop_type", "unknown")
        if outcome.farmer_rating and outcome.farmer_rating >= 4:
            if crop_type in profile.crop_success_patterns:
                profile.crop_success_patterns[crop_type] += 0.1
            else:
                profile.crop_success_patterns[crop_type] = 0.1
        
        # Update seasonal factors
        season = self._get_season(outcome.recommendation_date)
        if season in profile.seasonal_factors:
            profile.seasonal_factors[season] += 0.05
        else:
            profile.seasonal_factors[season] = 0.05
        
        profile.last_updated = datetime.utcnow()
    
    async def _apply_regional_adaptation(
        self,
        farmer_id: str,
        field_id: str,
        request: ApplicationRequest
    ) -> Dict[str, float]:
        """Apply regional adaptation factors to recommendations."""
        region_id = self._get_region_id(field_id)
        
        # Get regional patterns from adaptation profiles
        regional_patterns = {}
        for profile_key, profile in self.adaptation_profiles.items():
            if profile.region_id == region_id:
                # Aggregate patterns from this region
                for soil_type, preference in profile.soil_type_preferences.items():
                    if soil_type in regional_patterns:
                        regional_patterns[soil_type] += preference
                    else:
                        regional_patterns[soil_type] = preference
        
        # Normalize patterns
        total_preference = sum(regional_patterns.values())
        if total_preference > 0:
            regional_patterns = {k: v / total_preference for k, v in regional_patterns.items()}
        
        return regional_patterns
    
    async def _apply_farm_specific_adaptation(
        self,
        farmer_id: str,
        field_id: str,
        request: ApplicationRequest
    ) -> Dict[str, float]:
        """Apply farm-specific adaptation factors to recommendations."""
        profile_key = f"{farmer_id}_{field_id}"
        
        if profile_key not in self.adaptation_profiles:
            return {}
        
        profile = self.adaptation_profiles[profile_key]
        
        # Create farm-specific adjustments
        adjustments = {}
        
        # Soil type preferences
        soil_type = request.field_conditions.soil_type
        if soil_type in profile.soil_type_preferences:
            adjustments["soil_preference"] = profile.soil_type_preferences[soil_type]
        
        # Crop success patterns
        crop_type = request.crop_requirements.crop_type
        if crop_type in profile.crop_success_patterns:
            adjustments["crop_success"] = profile.crop_success_patterns[crop_type]
        
        # Cost sensitivity
        adjustments["cost_sensitivity"] = profile.cost_sensitivity
        
        return adjustments
    
    async def _apply_seasonal_adjustments(
        self,
        request: ApplicationRequest,
        current_date: datetime
    ) -> Dict[str, float]:
        """Apply seasonal adjustment factors to recommendations."""
        season = self._get_season(current_date)
        
        # Seasonal adjustment factors based on agricultural knowledge
        seasonal_factors = {
            "spring": {
                "broadcast": 1.1,  # Better for spring applications
                "band": 1.0,
                "injection": 0.9,
                "foliar": 0.8
            },
            "summer": {
                "broadcast": 0.8,  # Risk of volatilization
                "band": 1.0,
                "injection": 1.2,  # Better for summer
                "foliar": 1.1
            },
            "fall": {
                "broadcast": 1.0,
                "band": 1.1,  # Good for fall applications
                "injection": 1.0,
                "foliar": 0.7
            },
            "winter": {
                "broadcast": 0.6,  # Limited winter applications
                "band": 0.8,
                "injection": 0.9,
                "foliar": 0.5
            }
        }
        
        return seasonal_factors.get(season, {})
    
    async def _predict_method_outcomes(
        self,
        request: ApplicationRequest,
        method_scores: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Predict outcomes for each application method using ML models."""
        predictions = {}
        
        for method_type, score in method_scores.items():
            try:
                # Prepare features for prediction
                features = self._prepare_prediction_features(request, method_type)
                
                # Predict yield
                yield_pred = await self._predict_yield(features)
                
                # Predict cost
                cost_pred = await self._predict_cost(features)
                
                # Predict satisfaction
                satisfaction_pred = await self._predict_satisfaction(features)
                
                predictions[method_type] = {
                    "predicted_yield": yield_pred,
                    "predicted_cost": cost_pred,
                    "predicted_satisfaction": satisfaction_pred,
                    "confidence": score
                }
                
            except Exception as e:
                logger.warning(f"Error predicting outcomes for {method_type}: {e}")
                predictions[method_type] = {
                    "predicted_yield": 0.0,
                    "predicted_cost": 0.0,
                    "predicted_satisfaction": 0.0,
                    "confidence": score
                }
        
        return predictions
    
    async def _predict_yield(self, features: Dict[str, Any]) -> float:
        """Predict yield using ML model."""
        try:
            model_info = self.learning_models["yield_prediction"]
            model = model_info["model"]
            
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features, model_info["features"])
            
            # Make prediction
            prediction = model.predict([feature_vector])[0]
            return float(prediction)
            
        except Exception as e:
            logger.warning(f"Error predicting yield: {e}")
            return 0.0
    
    async def _predict_cost(self, features: Dict[str, Any]) -> float:
        """Predict cost using ML model."""
        try:
            model_info = self.learning_models["cost_prediction"]
            model = model_info["model"]
            
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features, model_info["features"])
            
            # Make prediction
            prediction = model.predict([feature_vector])[0]
            return float(prediction)
            
        except Exception as e:
            logger.warning(f"Error predicting cost: {e}")
            return 0.0
    
    async def _predict_satisfaction(self, features: Dict[str, Any]) -> float:
        """Predict farmer satisfaction using ML model."""
        try:
            model_info = self.learning_models["satisfaction_prediction"]
            model = model_info["model"]
            
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features, model_info["features"])
            
            # Make prediction
            prediction = model.predict([feature_vector])[0]
            return float(prediction)
            
        except Exception as e:
            logger.warning(f"Error predicting satisfaction: {e}")
            return 0.0
    
    def _prepare_prediction_features(
        self,
        request: ApplicationRequest,
        method_type: str
    ) -> Dict[str, Any]:
        """Prepare features for ML prediction."""
        features = {
            "field_size": request.field_conditions.field_size_acres,
            "soil_ph": request.field_conditions.soil_ph or 6.5,
            "organic_matter": request.field_conditions.organic_matter_percent or 2.0,
            "method_type": method_type,
            "fertilizer_rate": request.fertilizer_specification.application_rate or 100.0,
            "crop_type": request.crop_requirements.crop_type,
            "target_yield": request.crop_requirements.target_yield or 150.0,
            "fertilizer_cost": request.fertilizer_specification.cost_per_unit or 0.5,
            "equipment_available": len(request.available_equipment) if request.available_equipment else 0
        }
        
        return features
    
    def _prepare_feature_vector(self, features: Dict[str, Any], feature_names: List[str]) -> List[float]:
        """Prepare feature vector for ML model."""
        feature_vector = []
        
        for feature_name in feature_names:
            if feature_name in features:
                value = features[feature_name]
                if isinstance(value, str):
                    # Encode categorical features
                    if feature_name not in self.label_encoders:
                        self.label_encoders[feature_name] = LabelEncoder()
                    try:
                        encoded_value = self.label_encoders[feature_name].transform([value])[0]
                        feature_vector.append(float(encoded_value))
                    except ValueError:
                        # Handle unseen categories
                        feature_vector.append(0.0)
                else:
                    feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)
        
        return feature_vector
    
    async def _adjust_scores_with_ml_insights(
        self,
        base_scores: Dict[str, float],
        predictions: Dict[str, Dict[str, float]],
        regional_adjustments: Dict[str, float],
        farm_adjustments: Dict[str, float],
        seasonal_adjustments: Dict[str, float]
    ) -> Dict[str, float]:
        """Adjust recommendation scores based on ML insights and adaptations."""
        adjusted_scores = {}
        
        for method_type, base_score in base_scores.items():
            adjusted_score = base_score
            
            # Apply ML predictions
            if method_type in predictions:
                pred_data = predictions[method_type]
                
                # Weight by predicted satisfaction
                satisfaction_weight = pred_data.get("predicted_satisfaction", 0.5)
                adjusted_score *= (0.5 + satisfaction_weight)
                
                # Adjust for predicted yield vs cost ratio
                predicted_yield = pred_data.get("predicted_yield", 0.0)
                predicted_cost = pred_data.get("predicted_cost", 1.0)
                if predicted_cost > 0:
                    yield_cost_ratio = predicted_yield / predicted_cost
                    adjusted_score *= (1.0 + yield_cost_ratio * 0.1)
            
            # Apply regional adjustments
            if method_type in regional_adjustments:
                adjusted_score *= (1.0 + regional_adjustments[method_type] * 0.2)
            
            # Apply farm-specific adjustments
            if "soil_preference" in farm_adjustments:
                adjusted_score *= (1.0 + farm_adjustments["soil_preference"] * 0.15)
            
            if "crop_success" in farm_adjustments:
                adjusted_score *= (1.0 + farm_adjustments["crop_success"] * 0.15)
            
            # Apply seasonal adjustments
            if method_type in seasonal_adjustments:
                adjusted_score *= seasonal_adjustments[method_type]
            
            adjusted_scores[method_type] = max(0.0, adjusted_score)
        
        return adjusted_scores
    
    async def _generate_improved_response(
        self,
        request: ApplicationRequest,
        improved_scores: Dict[str, float],
        base_response: Any
    ) -> ApplicationResponse:
        """Generate improved ApplicationResponse with ML-enhanced recommendations."""
        # Sort methods by improved scores
        sorted_methods = sorted(improved_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get method details
        recommended_methods = []
        for method_type, score in sorted_methods[:3]:  # Top 3 recommendations
            method_details = await self._get_method_details(method_type, request)
            if method_details:
                recommended_methods.append(method_details)
        
        # Create improved response
        improved_response = ApplicationResponse(
            request_id=base_response.request_id if hasattr(base_response, 'request_id') else str(uuid4()),
            recommended_methods=recommended_methods,
            primary_recommendation=recommended_methods[0] if recommended_methods else None,
            alternative_methods=recommended_methods[1:] if len(recommended_methods) > 1 else [],
            analysis_summary={
                "ml_enhanced": True,
                "adaptation_applied": True,
                "confidence_scores": improved_scores,
                "learning_metrics": self.learning_metrics.__dict__
            },
            processing_time_ms=base_response.optimization_time_ms if hasattr(base_response, 'optimization_time_ms') else 0.0
        )
        
        return improved_response
    
    async def _get_method_details(
        self,
        method_type: str,
        request: ApplicationRequest
    ) -> Optional[ApplicationMethod]:
        """Get detailed method information."""
        try:
            # This would typically query the method database
            # For now, create a basic method object
            method = ApplicationMethod(
                method_id=str(uuid4()),
                method_type=ApplicationMethodType(method_type),
                name=f"{method_type.title()} Application",
                description=f"ML-enhanced {method_type} application method",
                efficiency_score=0.8,
                cost_per_acre=20.0,
                labor_requirements="medium",
                environmental_impact="moderate"
            )
            return method
        except Exception as e:
            logger.warning(f"Error getting method details for {method_type}: {e}")
            return None
    
    async def _trigger_learning_if_ready(self):
        """Trigger model retraining if enough new data is available."""
        # Check if we have enough new outcomes for retraining
        new_outcomes = [outcome for outcome in self.outcomes_db.values() 
                       if outcome.recommendation_date > self.learning_metrics.last_updated]
        
        if len(new_outcomes) >= 10:  # Threshold for retraining
            logger.info("Triggering model retraining with new data")
            await self._retrain_models()
    
    async def _retrain_models(self):
        """Retrain ML models with new data."""
        try:
            logger.info("Retraining ML models")
            
            # Prepare training data
            training_data = await self._prepare_training_data()
            
            if not training_data:
                logger.warning("No training data available for retraining")
                return
            
            # Retrain each model
            for model_name, model_info in self.learning_models.items():
                try:
                    # Prepare features and targets
                    X, y = self._prepare_model_data(training_data, model_name)
                    
                    if len(X) < 5:  # Need minimum data for training
                        continue
                    
                    # Split data
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42
                    )
                    
                    # Scale features
                    scaler = self.scalers[model_name]
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train model
                    model = model_info["model"]
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate model
                    y_pred = model.predict(X_test_scaled)
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    logger.info(f"Retrained {model_name}: MSE={mse:.4f}, R2={r2:.4f}")
                    
                    # Update learning metrics
                    self.learning_metrics.model_accuracy = r2
                    self.learning_metrics.prediction_error = mse
                    self.learning_metrics.last_updated = datetime.utcnow()
                    
                except Exception as e:
                    logger.error(f"Error retraining model {model_name}: {e}")
            
            # Save models
            await self._save_models()
            
        except Exception as e:
            logger.error(f"Error in model retraining: {e}")
    
    async def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from outcomes."""
        training_data = []
        
        for outcome in self.outcomes_db.values():
            if outcome.actual_yield and outcome.farmer_rating:
                data_point = {
                    "field_size": outcome.field_conditions.get("field_size_acres", 0),
                    "soil_ph": outcome.field_conditions.get("soil_ph", 6.5),
                    "organic_matter": outcome.field_conditions.get("organic_matter_percent", 2.0),
                    "method_type": outcome.method_type.value,
                    "fertilizer_rate": outcome.fertilizer_specification.get("application_rate", 100.0),
                    "crop_type": outcome.crop_requirements.get("crop_type", "unknown"),
                    "target_yield": outcome.crop_requirements.get("target_yield", 150.0),
                    "fertilizer_cost": outcome.fertilizer_specification.get("cost_per_unit", 0.5),
                    "actual_yield": outcome.actual_yield,
                    "actual_cost_per_acre": outcome.actual_cost_per_acre or 0,
                    "farmer_rating": outcome.farmer_rating
                }
                training_data.append(data_point)
        
        return training_data
    
    def _prepare_model_data(self, training_data: List[Dict[str, Any]], model_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare feature matrix and target vector for a specific model."""
        model_info = self.learning_models[model_name]
        features = model_info["features"]
        target = model_info["target"]
        
        X = []
        y = []
        
        for data_point in training_data:
            if target in data_point and data_point[target] is not None:
                feature_vector = []
                for feature in features:
                    if feature in data_point:
                        value = data_point[feature]
                        if isinstance(value, str):
                            # Encode categorical features
                            if feature not in self.label_encoders:
                                self.label_encoders[feature] = LabelEncoder()
                            try:
                                encoded_value = self.label_encoders[feature].transform([value])[0]
                                feature_vector.append(float(encoded_value))
                            except ValueError:
                                feature_vector.append(0.0)
                        else:
                            feature_vector.append(float(value))
                    else:
                        feature_vector.append(0.0)
                
                X.append(feature_vector)
                y.append(data_point[target])
        
        return np.array(X), np.array(y)
    
    async def _save_models(self):
        """Save trained models to disk."""
        model_dir = "models/adaptive_learning"
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            for model_name, model_info in self.learning_models.items():
                model_path = os.path.join(model_dir, f"{model_name}_model.joblib")
                scaler_path = os.path.join(model_dir, f"{model_name}_scaler.joblib")
                
                joblib.dump(model_info["model"], model_path)
                joblib.dump(self.scalers[model_name], scaler_path)
            
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def _update_learning_metrics(self):
        """Update learning system metrics."""
        try:
            # Calculate feedback integration rate
            total_recommendations = len(self.outcomes_db)
            total_feedback = len(self.feedback_db)
            
            if total_recommendations > 0:
                self.learning_metrics.feedback_integration_rate = total_feedback / total_recommendations
            
            # Calculate adaptation effectiveness
            adaptation_profiles_count = len(self.adaptation_profiles)
            self.learning_metrics.adaptation_effectiveness = min(adaptation_profiles_count / 100, 1.0)
            
            # Update regional adaptation score
            regions = set(profile.region_id for profile in self.adaptation_profiles.values())
            self.learning_metrics.regional_adaptation_score = min(len(regions) / 50, 1.0)
            
            self.learning_metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating learning metrics: {e}")
    
    def _get_region_id(self, field_id: str) -> str:
        """Get region ID for a field (simplified implementation)."""
        # In production, this would query a geospatial database
        # For now, return a simplified region ID
        return f"region_{hash(field_id) % 10}"
    
    def _get_season(self, date: datetime) -> str:
        """Get season for a given date."""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    async def get_learning_metrics(self) -> LearningMetrics:
        """Get current learning system metrics."""
        return self.learning_metrics
    
    async def get_adaptation_profile(self, farmer_id: str, field_id: str) -> Optional[AdaptationProfile]:
        """Get adaptation profile for a specific farmer and field."""
        profile_key = f"{farmer_id}_{field_id}"
        return self.adaptation_profiles.get(profile_key)
    
    async def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for analysis."""
        return {
            "outcomes": {k: v.__dict__ for k, v in self.outcomes_db.items()},
            "feedback": self.feedback_db,
            "adaptation_profiles": {k: v.__dict__ for k, v in self.adaptation_profiles.items()},
            "learning_metrics": self.learning_metrics.__dict__
        }
