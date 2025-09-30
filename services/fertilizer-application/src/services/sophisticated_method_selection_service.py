"""
Sophisticated Method Selection Service for fertilizer application method optimization.

This service implements advanced algorithms for optimal method selection including:
- Machine learning algorithms (Random Forest, Neural Networks)
- Multi-criteria optimization algorithms
- Constraint satisfaction algorithms
- Uncertainty handling and fuzzy logic
- Historical data integration for continuous improvement
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm
import cvxpy as cp

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)
from src.services.application_method_service import ApplicationMethodService

logger = logging.getLogger(__name__)


class OptimizationObjective(str, Enum):
    """Optimization objectives for method selection."""
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_ENVIRONMENTAL_IMPACT = "minimize_environmental_impact"
    MAXIMIZE_YIELD_POTENTIAL = "maximize_yield_potential"
    BALANCED_OPTIMIZATION = "balanced_optimization"


class UncertaintyLevel(str, Enum):
    """Uncertainty levels for decision making."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class MethodSelectionFeatures:
    """Features for machine learning model training and prediction."""
    field_size_acres: float
    soil_type_encoded: int
    drainage_class_encoded: int
    slope_percent: float
    irrigation_available: int
    crop_type_encoded: int
    growth_stage_encoded: int
    target_yield: float
    fertilizer_type_encoded: int
    fertilizer_form_encoded: int
    equipment_count: int
    equipment_types_encoded: int
    weather_conditions_encoded: int
    historical_success_rate: float
    cost_constraint: float
    environmental_constraint: float


@dataclass
class OptimizationConstraints:
    """Constraints for optimization algorithms."""
    max_cost_per_acre: Optional[float] = None
    min_efficiency_score: Optional[float] = None
    max_environmental_impact: Optional[str] = None
    equipment_availability: List[str] = None
    field_access_limitations: List[str] = None
    timing_constraints: List[str] = None


@dataclass
class OptimizationResult:
    """Result from optimization algorithms."""
    optimal_method: ApplicationMethodType
    objective_value: float
    confidence_score: float
    alternative_solutions: List[Tuple[ApplicationMethodType, float]]
    optimization_time_ms: float
    algorithm_used: str
    convergence_info: Dict[str, Any]


class SophisticatedMethodSelectionService:
    """Service implementing sophisticated algorithms for method selection."""
    
    def __init__(self):
        self.base_service = ApplicationMethodService()
        self.ml_models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.historical_data = []
        self.optimization_cache = {}
        self._initialize_ml_models()
        self._initialize_label_encoders()
    
    def _initialize_ml_models(self):
        """Initialize machine learning models."""
        # Random Forest for efficiency prediction
        self.ml_models['efficiency_rf'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Random Forest for cost prediction
        self.ml_models['cost_rf'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
        
        # Neural Network for complex pattern recognition
        self.ml_models['pattern_nn'] = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            random_state=42,
            max_iter=1000
        )
        
        # Classifier for method recommendation
        self.ml_models['method_classifier'] = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )
        
        # Initialize scalers
        self.scalers['feature_scaler'] = StandardScaler()
        self.scalers['target_scaler'] = StandardScaler()
    
    def _initialize_label_encoders(self):
        """Initialize label encoders for categorical features."""
        categorical_features = [
            'soil_type', 'drainage_class', 'crop_type', 'growth_stage',
            'fertilizer_type', 'fertilizer_form', 'equipment_types', 'weather_conditions'
        ]
        
        for feature in categorical_features:
            self.label_encoders[feature] = LabelEncoder()
    
    async def select_optimal_method_sophisticated(
        self,
        request: ApplicationRequest,
        objective: OptimizationObjective = OptimizationObjective.BALANCED_OPTIMIZATION,
        constraints: Optional[OptimizationConstraints] = None,
        uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM,
        use_ml: bool = True,
        use_optimization: bool = True,
        use_fuzzy_logic: bool = True
    ) -> OptimizationResult:
        """
        Select optimal method using sophisticated algorithms.
        
        Args:
            request: Application request
            objective: Optimization objective
            constraints: Optimization constraints
            uncertainty_level: Level of uncertainty in decision making
            use_ml: Whether to use machine learning models
            use_optimization: Whether to use optimization algorithms
            use_fuzzy_logic: Whether to use fuzzy logic for uncertainty handling
            
        Returns:
            OptimizationResult with optimal method and analysis
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting sophisticated method selection with objective: {objective}")
            
            # Extract features for ML models
            features = await self._extract_features(request)
            
            # Get base recommendations from existing service
            base_response = await self.base_service.select_application_methods(request)
            available_methods = [method.method_type for method in base_response.recommended_methods]
            
            if not available_methods:
                raise ValueError("No suitable methods found for the given conditions")
            
            # Initialize constraints
            if constraints is None:
                constraints = OptimizationConstraints()
            
            # Multi-algorithm approach
            results = []
            
            # 1. Machine Learning Approach
            if use_ml:
                ml_result = await self._ml_method_selection(
                    features, available_methods, objective, constraints
                )
                results.append(ml_result)
            
            # 2. Multi-criteria Optimization
            if use_optimization:
                optimization_result = await self._multi_criteria_optimization(
                    request, available_methods, objective, constraints
                )
                results.append(optimization_result)
            
            # 3. Constraint Satisfaction
            constraint_result = await self._constraint_satisfaction_selection(
                request, available_methods, constraints
            )
            results.append(constraint_result)
            
            # 4. Fuzzy Logic for Uncertainty Handling
            if use_fuzzy_logic:
                fuzzy_result = await self._fuzzy_logic_selection(
                    request, available_methods, uncertainty_level
                )
                results.append(fuzzy_result)
            
            # Combine results using ensemble approach
            final_result = await self._ensemble_decision_making(
                results, objective, uncertainty_level
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            final_result.optimization_time_ms = processing_time_ms
            
            logger.info(f"Sophisticated method selection completed in {processing_time_ms:.2f}ms")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in sophisticated method selection: {e}")
            raise
    
    async def _extract_features(self, request: ApplicationRequest) -> MethodSelectionFeatures:
        """Extract features for machine learning models."""
        # Encode categorical features
        soil_type_encoded = self._encode_categorical('soil_type', request.field_conditions.soil_type)
        drainage_class_encoded = self._encode_categorical('drainage_class', request.field_conditions.drainage_class)
        crop_type_encoded = self._encode_categorical('crop_type', request.crop_requirements.crop_type)
        growth_stage_encoded = self._encode_categorical('growth_stage', request.crop_requirements.growth_stage)
        fertilizer_type_encoded = self._encode_categorical('fertilizer_type', request.fertilizer_specification.fertilizer_type)
        fertilizer_form_encoded = self._encode_categorical('fertilizer_form', request.fertilizer_specification.form.value)
        
        # Encode equipment types (simplified - use count of different types)
        equipment_types_encoded = len(set(eq.equipment_type for eq in request.available_equipment))
        
        # Weather conditions (simplified - assume good conditions for now)
        weather_conditions_encoded = 0  # Good conditions
        
        # Historical success rate (placeholder - would come from database)
        historical_success_rate = 0.8  # Default value
        
        return MethodSelectionFeatures(
            field_size_acres=request.field_conditions.field_size_acres,
            soil_type_encoded=soil_type_encoded,
            drainage_class_encoded=drainage_class_encoded,
            slope_percent=request.field_conditions.slope_percent or 0.0,
            irrigation_available=1 if request.field_conditions.irrigation_available else 0,
            crop_type_encoded=crop_type_encoded,
            growth_stage_encoded=growth_stage_encoded,
            target_yield=request.crop_requirements.target_yield,
            fertilizer_type_encoded=fertilizer_type_encoded,
            fertilizer_form_encoded=fertilizer_form_encoded,
            equipment_count=len(request.available_equipment),
            equipment_types_encoded=equipment_types_encoded,
            weather_conditions_encoded=weather_conditions_encoded,
            historical_success_rate=historical_success_rate,
            cost_constraint=100.0,  # Default constraint
            environmental_constraint=0.5  # Default constraint
        )
    
    def _encode_categorical(self, feature_name: str, value: str) -> int:
        """Encode categorical feature to integer."""
        if value is None:
            return 0
        
        encoder = self.label_encoders[feature_name]
        try:
            return encoder.transform([value])[0]
        except ValueError:
            # Handle unseen categories
            encoder.fit([value])
            return encoder.transform([value])[0]
    
    async def _ml_method_selection(
        self,
        features: MethodSelectionFeatures,
        available_methods: List[ApplicationMethodType],
        objective: OptimizationObjective,
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Use machine learning models for method selection."""
        start_time = time.time()
        
        # Convert features to numpy array
        feature_array = np.array([
            features.field_size_acres,
            features.soil_type_encoded,
            features.drainage_class_encoded,
            features.slope_percent,
            features.irrigation_available,
            features.crop_type_encoded,
            features.growth_stage_encoded,
            features.target_yield,
            features.fertilizer_type_encoded,
            features.fertilizer_form_encoded,
            features.equipment_count,
            features.equipment_types_encoded,
            features.weather_conditions_encoded,
            features.historical_success_rate,
            features.cost_constraint,
            features.environmental_constraint
        ]).reshape(1, -1)
        
        # Scale features
        feature_array_scaled = self.scalers['feature_scaler'].fit_transform(feature_array)
        
        # Predict efficiency and cost for each method
        method_scores = {}
        for method in available_methods:
            # Add method encoding to features
            method_encoded = self._encode_categorical('method_type', method.value)
            method_features = np.append(feature_array_scaled[0], method_encoded).reshape(1, -1)
            
            # Predict efficiency
            efficiency_pred = self.ml_models['efficiency_rf'].predict(method_features)[0]
            
            # Predict cost
            cost_pred = self.ml_models['cost_rf'].predict(method_features)[0]
            
            # Calculate objective score based on optimization objective
            if objective == OptimizationObjective.MAXIMIZE_EFFICIENCY:
                score = efficiency_pred
            elif objective == OptimizationObjective.MINIMIZE_COST:
                score = 1.0 / (1.0 + cost_pred)  # Invert cost for maximization
            elif objective == OptimizationObjective.BALANCED_OPTIMIZATION:
                score = 0.6 * efficiency_pred + 0.4 * (1.0 / (1.0 + cost_pred))
            else:
                score = efficiency_pred
            
            method_scores[method] = score
        
        # Select optimal method
        optimal_method = max(method_scores.items(), key=lambda x: x[1])
        
        # Generate alternative solutions
        sorted_methods = sorted(method_scores.items(), key=lambda x: x[1], reverse=True)
        alternative_solutions = [(method, score) for method, score in sorted_methods[1:3]]
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return OptimizationResult(
            optimal_method=optimal_method[0],
            objective_value=optimal_method[1],
            confidence_score=0.85,  # ML confidence
            alternative_solutions=alternative_solutions,
            optimization_time_ms=processing_time_ms,
            algorithm_used="Machine Learning (Random Forest + Neural Network)",
            convergence_info={"ml_models_used": list(self.ml_models.keys())}
        )
    
    async def _multi_criteria_optimization(
        self,
        request: ApplicationRequest,
        available_methods: List[ApplicationMethodType],
        objective: OptimizationObjective,
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Use multi-criteria optimization for method selection."""
        start_time = time.time()
        
        # Define objective function based on optimization goal
        def objective_function(method_weights):
            """Multi-criteria objective function."""
            total_score = 0.0
            
            for i, method in enumerate(available_methods):
                weight = method_weights[i]
                
                # Get method characteristics
                method_data = self.base_service.method_database.get(method, {})
                
                # Efficiency component
                efficiency = method_data.get('efficiency_score', 0.5)
                
                # Cost component (inverted for minimization)
                cost = method_data.get('cost_per_acre', 25.0)
                cost_score = 1.0 / (1.0 + cost / 50.0)  # Normalize cost
                
                # Environmental component
                env_impact = method_data.get('environmental_impact', 'moderate')
                env_scores = {'very_low': 1.0, 'low': 0.8, 'moderate': 0.6, 'high': 0.4, 'very_high': 0.2}
                env_score = env_scores.get(env_impact, 0.6)
                
                # Calculate weighted score
                if objective == OptimizationObjective.MAXIMIZE_EFFICIENCY:
                    method_score = efficiency
                elif objective == OptimizationObjective.MINIMIZE_COST:
                    method_score = cost_score
                elif objective == OptimizationObjective.MINIMIZE_ENVIRONMENTAL_IMPACT:
                    method_score = env_score
                elif objective == OptimizationObjective.BALANCED_OPTIMIZATION:
                    method_score = 0.4 * efficiency + 0.3 * cost_score + 0.3 * env_score
                else:
                    method_score = efficiency
                
                total_score += weight * method_score
            
            return -total_score  # Minimize negative for maximization
        
        # Define constraints
        def constraint_function(method_weights):
            """Constraint function for optimization."""
            constraints_list = []
            
            # Sum of weights must equal 1
            constraints_list.append(sum(method_weights) - 1.0)
            
            # Individual weights must be non-negative
            for weight in method_weights:
                constraints_list.append(weight)
            
            # Cost constraint
            if constraints.max_cost_per_acre:
                total_cost = sum(
                    weight * self.base_service.method_database.get(method, {}).get('cost_per_acre', 25.0)
                    for weight, method in zip(method_weights, available_methods)
                )
                constraints_list.append(constraints.max_cost_per_acre - total_cost)
            
            return constraints_list
        
        # Initial guess
        initial_weights = np.ones(len(available_methods)) / len(available_methods)
        
        # Bounds for weights
        bounds = [(0.0, 1.0) for _ in available_methods]
        
        # Optimize using scipy
        result = minimize(
            objective_function,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints={'type': 'eq', 'fun': lambda x: sum(x) - 1.0}
        )
        
        # Find optimal method
        optimal_index = np.argmax(result.x)
        optimal_method = available_methods[optimal_index]
        
        # Generate alternative solutions
        sorted_indices = np.argsort(result.x)[::-1]
        alternative_solutions = [
            (available_methods[i], result.x[i]) for i in sorted_indices[1:3]
        ]
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return OptimizationResult(
            optimal_method=optimal_method,
            objective_value=-result.fun,
            confidence_score=0.9 if result.success else 0.6,
            alternative_solutions=alternative_solutions,
            optimization_time_ms=processing_time_ms,
            algorithm_used="Multi-criteria Optimization (Scipy SLSQP)",
            convergence_info={
                "success": result.success,
                "iterations": result.nit,
                "final_weights": result.x.tolist()
            }
        )
    
    async def _constraint_satisfaction_selection(
        self,
        request: ApplicationRequest,
        available_methods: List[ApplicationMethodType],
        constraints: OptimizationConstraints
    ) -> OptimizationResult:
        """Use constraint satisfaction for method selection."""
        start_time = time.time()
        
        # Define constraint satisfaction problem
        satisfied_methods = []
        
        for method in available_methods:
            method_data = self.base_service.method_database.get(method, {})
            is_satisfied = True
            
            # Check cost constraint
            if constraints.max_cost_per_acre:
                method_cost = method_data.get('cost_per_acre', 25.0)
                if method_cost > constraints.max_cost_per_acre:
                    is_satisfied = False
            
            # Check efficiency constraint
            if constraints.min_efficiency_score:
                method_efficiency = method_data.get('efficiency_score', 0.5)
                if method_efficiency < constraints.min_efficiency_score:
                    is_satisfied = False
            
            # Check environmental constraint
            if constraints.max_environmental_impact:
                method_env = method_data.get('environmental_impact', 'moderate')
                env_levels = ['very_low', 'low', 'moderate', 'high', 'very_high']
                if env_levels.index(method_env) > env_levels.index(constraints.max_environmental_impact):
                    is_satisfied = False
            
            # Check equipment availability
            if constraints.equipment_availability:
                method_equipment = method_data.get('equipment_types', [])
                if not any(eq in constraints.equipment_availability for eq in method_equipment):
                    is_satisfied = False
            
            if is_satisfied:
                satisfied_methods.append(method)
        
        # Select best method from satisfied methods
        if satisfied_methods:
            # Score satisfied methods
            method_scores = {}
            for method in satisfied_methods:
                method_data = self.base_service.method_database.get(method, {})
                score = (
                    0.4 * method_data.get('efficiency_score', 0.5) +
                    0.3 * (1.0 / (1.0 + method_data.get('cost_per_acre', 25.0) / 50.0)) +
                    0.3 * self._get_environmental_score(method_data.get('environmental_impact', 'moderate'))
                )
                method_scores[method] = score
            
            optimal_method = max(method_scores.items(), key=lambda x: x[1])
            alternative_solutions = [(method, score) for method, score in sorted(method_scores.items(), key=lambda x: x[1], reverse=True)[1:3]]
        else:
            # No methods satisfy all constraints, select best available
            optimal_method = (available_methods[0], 0.5)
            alternative_solutions = []
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return OptimizationResult(
            optimal_method=optimal_method[0],
            objective_value=optimal_method[1],
            confidence_score=0.8 if satisfied_methods else 0.4,
            alternative_solutions=alternative_solutions,
            optimization_time_ms=processing_time_ms,
            algorithm_used="Constraint Satisfaction",
            convergence_info={
                "satisfied_methods": len(satisfied_methods),
                "total_constraints": len([c for c in [constraints.max_cost_per_acre, constraints.min_efficiency_score, constraints.max_environmental_impact] if c is not None])
            }
        )
    
    async def _fuzzy_logic_selection(
        self,
        request: ApplicationRequest,
        available_methods: List[ApplicationMethodType],
        uncertainty_level: UncertaintyLevel
    ) -> OptimizationResult:
        """Use fuzzy logic for uncertainty handling in method selection."""
        start_time = time.time()
        
        # Define fuzzy membership functions
        def fuzzy_efficiency_score(efficiency: float) -> float:
            """Fuzzy membership function for efficiency."""
            if efficiency >= 0.9:
                return 1.0
            elif efficiency >= 0.7:
                return (efficiency - 0.7) / 0.2
            else:
                return 0.0
        
        def fuzzy_cost_score(cost: float) -> float:
            """Fuzzy membership function for cost (lower is better)."""
            if cost <= 15:
                return 1.0
            elif cost <= 35:
                return (35 - cost) / 20
            else:
                return 0.0
        
        def fuzzy_environmental_score(env_impact: str) -> float:
            """Fuzzy membership function for environmental impact."""
            env_scores = {'very_low': 1.0, 'low': 0.8, 'moderate': 0.6, 'high': 0.4, 'very_high': 0.2}
            return env_scores.get(env_impact, 0.6)
        
        # Calculate fuzzy scores for each method
        method_fuzzy_scores = {}
        uncertainty_factor = self._get_uncertainty_factor(uncertainty_level)
        
        for method in available_methods:
            method_data = self.base_service.method_database.get(method, {})
            
            # Calculate fuzzy scores
            efficiency_fuzzy = fuzzy_efficiency_score(method_data.get('efficiency_score', 0.5))
            cost_fuzzy = fuzzy_cost_score(method_data.get('cost_per_acre', 25.0))
            env_fuzzy = fuzzy_environmental_score(method_data.get('environmental_impact', 'moderate'))
            
            # Combine fuzzy scores with uncertainty
            combined_score = (
                0.4 * efficiency_fuzzy +
                0.3 * cost_fuzzy +
                0.3 * env_fuzzy
            ) * uncertainty_factor
            
            method_fuzzy_scores[method] = combined_score
        
        # Select optimal method
        optimal_method = max(method_fuzzy_scores.items(), key=lambda x: x[1])
        
        # Generate alternative solutions
        alternative_solutions = [(method, score) for method, score in sorted(method_fuzzy_scores.items(), key=lambda x: x[1], reverse=True)[1:3]]
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return OptimizationResult(
            optimal_method=optimal_method[0],
            objective_value=optimal_method[1],
            confidence_score=0.7 * uncertainty_factor,  # Adjust confidence based on uncertainty
            alternative_solutions=alternative_solutions,
            optimization_time_ms=processing_time_ms,
            algorithm_used=f"Fuzzy Logic (Uncertainty: {uncertainty_level.value})",
            convergence_info={
                "uncertainty_level": uncertainty_level.value,
                "uncertainty_factor": uncertainty_factor,
                "fuzzy_scores": method_fuzzy_scores
            }
        )
    
    def _get_uncertainty_factor(self, uncertainty_level: UncertaintyLevel) -> float:
        """Get uncertainty factor for fuzzy logic."""
        factors = {
            UncertaintyLevel.LOW: 1.0,
            UncertaintyLevel.MEDIUM: 0.8,
            UncertaintyLevel.HIGH: 0.6,
            UncertaintyLevel.VERY_HIGH: 0.4
        }
        return factors.get(uncertainty_level, 0.8)
    
    def _get_environmental_score(self, environmental_impact: str) -> float:
        """Get environmental impact score."""
        env_scores = {
            'very_low': 1.0,
            'low': 0.8,
            'moderate': 0.6,
            'high': 0.4,
            'very_high': 0.2
        }
        return env_scores.get(environmental_impact, 0.6)
    
    async def _ensemble_decision_making(
        self,
        results: List[OptimizationResult],
        objective: OptimizationObjective,
        uncertainty_level: UncertaintyLevel
    ) -> OptimizationResult:
        """Combine results from multiple algorithms using ensemble approach."""
        if not results:
            raise ValueError("No results to combine")
        
        # Weight algorithms based on confidence and objective alignment
        algorithm_weights = {
            "Machine Learning": 0.3,
            "Multi-criteria Optimization": 0.3,
            "Constraint Satisfaction": 0.2,
            "Fuzzy Logic": 0.2
        }
        
        # Calculate weighted scores for each method
        method_weighted_scores = {}
        total_confidence = 0.0
        
        for result in results:
            algorithm_name = result.algorithm_used.split('(')[0].strip()
            weight = algorithm_weights.get(algorithm_name, 0.25)
            confidence_weight = weight * result.confidence_score
            
            # Add to weighted scores
            if result.optimal_method not in method_weighted_scores:
                method_weighted_scores[result.optimal_method] = 0.0
            
            method_weighted_scores[result.optimal_method] += confidence_weight * result.objective_value
            total_confidence += confidence_weight
        
        # Select optimal method
        optimal_method = max(method_weighted_scores.items(), key=lambda x: x[1])
        
        # Generate alternative solutions
        alternative_solutions = [(method, score) for method, score in sorted(method_weighted_scores.items(), key=lambda x: x[1], reverse=True)[1:3]]
        
        # Calculate ensemble confidence
        ensemble_confidence = total_confidence / len(results) if results else 0.0
        
        # Calculate total processing time
        total_time = sum(result.optimization_time_ms for result in results)
        
        return OptimizationResult(
            optimal_method=optimal_method[0],
            objective_value=optimal_method[1],
            confidence_score=ensemble_confidence,
            alternative_solutions=alternative_solutions,
            optimization_time_ms=total_time,
            algorithm_used="Ensemble Decision Making",
            convergence_info={
                "algorithms_used": [result.algorithm_used for result in results],
                "individual_confidences": [result.confidence_score for result in results],
                "weighted_scores": method_weighted_scores
            }
        )
    
    async def train_ml_models(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train machine learning models with historical data."""
        if not training_data:
            logger.warning("No training data provided")
            return {"status": "no_data"}
        
        try:
            # Convert training data to DataFrame
            df = pd.DataFrame(training_data)
            
            # Prepare features and targets
            feature_columns = [
                'field_size_acres', 'soil_type_encoded', 'drainage_class_encoded',
                'slope_percent', 'irrigation_available', 'crop_type_encoded',
                'growth_stage_encoded', 'target_yield', 'fertilizer_type_encoded',
                'fertilizer_form_encoded', 'equipment_count', 'equipment_types_encoded',
                'weather_conditions_encoded', 'historical_success_rate'
            ]
            
            X = df[feature_columns].values
            y_efficiency = df['efficiency_score'].values
            y_cost = df['cost_per_acre'].values
            y_method = df['method_type_encoded'].values
            
            # Scale features
            X_scaled = self.scalers['feature_scaler'].fit_transform(X)
            
            # Train models
            self.ml_models['efficiency_rf'].fit(X_scaled, y_efficiency)
            self.ml_models['cost_rf'].fit(X_scaled, y_cost)
            self.ml_models['method_classifier'].fit(X_scaled, y_method)
            
            # Calculate cross-validation scores
            efficiency_scores = cross_val_score(self.ml_models['efficiency_rf'], X_scaled, y_efficiency, cv=5)
            cost_scores = cross_val_score(self.ml_models['cost_rf'], X_scaled, y_cost, cv=5)
            method_scores = cross_val_score(self.ml_models['method_classifier'], X_scaled, y_method, cv=5)
            
            logger.info("ML models trained successfully")
            
            return {
                "efficiency_rf_cv_score": efficiency_scores.mean(),
                "cost_rf_cv_score": cost_scores.mean(),
                "method_classifier_cv_score": method_scores.mean(),
                "training_samples": len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error training ML models: {e}")
            return {"error": str(e)}
    
    async def update_historical_data(self, outcome_data: Dict[str, Any]):
        """Update historical data with new outcomes for continuous improvement."""
        self.historical_data.append(outcome_data)
        
        # Keep only recent data (last 1000 records)
        if len(self.historical_data) > 1000:
            self.historical_data = self.historical_data[-1000:]
        
        # Retrain models periodically
        if len(self.historical_data) % 100 == 0:
            await self.train_ml_models(self.historical_data)
            logger.info(f"Models retrained with {len(self.historical_data)} historical records")