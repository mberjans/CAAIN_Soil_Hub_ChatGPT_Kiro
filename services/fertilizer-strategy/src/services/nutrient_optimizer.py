"""
Comprehensive Multi-Nutrient Optimization Service.

This service provides advanced multi-nutrient optimization including:
- N-P-K optimization with interaction effects
- Micronutrient integration and synergistic benefits
- Simultaneous nutrient optimization with constraints
- Response surface methodology and machine learning models
- Integration with soil test levels, crop requirements, and environmental limits
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
from uuid import uuid4, UUID
from enum import Enum
from scipy.optimize import minimize, differential_evolution, linprog
from scipy.stats import norm
import pandas as pd
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class NutrientType(str, Enum):
    """Types of nutrients for optimization."""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    SULFUR = "sulfur"
    ZINC = "zinc"
    IRON = "iron"
    MANGANESE = "manganese"
    COPPER = "copper"
    BORON = "boron"
    MOLYBDENUM = "molybdenum"


class OptimizationConstraint(str, Enum):
    """Types of optimization constraints."""
    SOIL_TEST_LEVELS = "soil_test_levels"
    CROP_REQUIREMENTS = "crop_requirements"
    ENVIRONMENTAL_LIMITS = "environmental_limits"
    BUDGET_CONSTRAINTS = "budget_constraints"
    APPLICATION_LIMITS = "application_limits"


class InteractionType(str, Enum):
    """Types of nutrient interactions."""
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"
    INDEPENDENT = "independent"
    COMPETITIVE = "competitive"


class NutrientInteraction(BaseModel):
    """Model for nutrient interactions."""
    nutrient1: NutrientType = Field(..., description="First nutrient in interaction")
    nutrient2: NutrientType = Field(..., description="Second nutrient in interaction")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    interaction_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of interaction (0-1)")
    interaction_coefficient: float = Field(..., description="Mathematical coefficient for interaction")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions affecting interaction")


class SoilTestData(BaseModel):
    """Soil test data for optimization."""
    nutrient: NutrientType = Field(..., description="Nutrient type")
    test_value: float = Field(..., ge=0.0, description="Soil test value")
    test_unit: str = Field(..., description="Unit of measurement")
    test_method: str = Field(..., description="Testing method used")
    test_date: date = Field(..., description="Date of soil test")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in test result")


class CropRequirement(BaseModel):
    """Crop nutrient requirements."""
    nutrient: NutrientType = Field(..., description="Nutrient type")
    minimum_requirement: float = Field(..., ge=0.0, description="Minimum nutrient requirement")
    optimal_range_min: float = Field(..., ge=0.0, description="Minimum of optimal range")
    optimal_range_max: float = Field(..., ge=0.0, description="Maximum of optimal range")
    maximum_tolerance: float = Field(..., ge=0.0, description="Maximum nutrient tolerance")
    uptake_efficiency: float = Field(default=0.7, ge=0.0, le=1.0, description="Nutrient uptake efficiency")
    critical_stage: Optional[str] = Field(None, description="Critical growth stage for nutrient")


class EnvironmentalLimit(BaseModel):
    """Environmental limits for nutrient application."""
    nutrient: NutrientType = Field(..., description="Nutrient type")
    max_application_rate: float = Field(..., ge=0.0, description="Maximum application rate")
    application_unit: str = Field(..., description="Unit for application rate")
    environmental_risk: str = Field(..., description="Environmental risk level")
    regulatory_limit: Optional[float] = Field(None, description="Regulatory application limit")
    seasonal_limit: Optional[float] = Field(None, description="Seasonal application limit")


class NutrientOptimizationRequest(BaseModel):
    """Request model for multi-nutrient optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    target_yield: float = Field(..., ge=0.0, description="Target yield per acre")
    yield_unit: str = Field(default="bushels", description="Unit for yield")
    
    # Soil test data
    soil_tests: List[SoilTestData] = Field(..., description="Soil test results")
    
    # Crop requirements
    crop_requirements: List[CropRequirement] = Field(..., description="Crop nutrient requirements")
    
    # Environmental limits
    environmental_limits: List[EnvironmentalLimit] = Field(default_factory=list, description="Environmental limits")
    
    # Optimization parameters
    optimization_objective: str = Field(default="balanced", description="Optimization objective")
    budget_constraint: Optional[float] = Field(None, ge=0.0, description="Budget constraint in dollars per acre")
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk tolerance level")
    
    # Additional parameters
    field_size_acres: float = Field(..., ge=0.0, description="Field size in acres")
    soil_type: str = Field(..., description="Soil type classification")
    ph_level: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
    organic_matter_percent: float = Field(default=2.0, ge=0.0, le=20.0, description="Organic matter percentage")
    
    # Interaction modeling
    include_interactions: bool = Field(default=True, description="Include nutrient interactions")
    interaction_model: str = Field(default="response_surface", description="Interaction model type")


class NutrientOptimizationResult(BaseModel):
    """Result model for multi-nutrient optimization."""
    optimization_id: str = Field(..., description="Unique optimization identifier")
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Crop type")
    
    # Optimization results
    optimal_nutrient_rates: Dict[str, float] = Field(..., description="Optimal nutrient application rates")
    expected_yield: float = Field(..., description="Expected yield with optimal rates")
    yield_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in yield prediction")
    
    # Economic analysis
    total_cost: float = Field(..., description="Total fertilizer cost per acre")
    expected_revenue: float = Field(..., description="Expected revenue per acre")
    net_profit: float = Field(..., description="Net profit per acre")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    
    # Optimization details
    optimization_method: str = Field(..., description="Optimization method used")
    convergence_status: str = Field(..., description="Optimization convergence status")
    iterations_required: int = Field(..., description="Number of iterations required")
    optimization_time_seconds: float = Field(..., description="Time taken for optimization")
    
    # Interaction analysis
    nutrient_interactions: List[NutrientInteraction] = Field(default_factory=list, description="Detected interactions")
    interaction_effects: Dict[str, float] = Field(default_factory=dict, description="Quantified interaction effects")
    
    # Risk assessment
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    alternative_strategies: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative strategies")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")
    model_version: str = Field(default="1.0", description="Model version used")


class MultiNutrientOptimizer:
    """Comprehensive multi-nutrient optimization service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nutrient_interactions = self._initialize_nutrient_interactions()
        self.response_models = {}
        self.scaler = StandardScaler()
        
    def _initialize_nutrient_interactions(self) -> List[NutrientInteraction]:
        """Initialize known nutrient interactions."""
        interactions = [
            # N-P interactions
            NutrientInteraction(
                nutrient1=NutrientType.NITROGEN,
                nutrient2=NutrientType.PHOSPHORUS,
                interaction_type=InteractionType.SYNERGISTIC,
                interaction_strength=0.7,
                interaction_coefficient=1.15,
                conditions={"ph_range": (6.0, 7.5)}
            ),
            # N-K interactions
            NutrientInteraction(
                nutrient1=NutrientType.NITROGEN,
                nutrient2=NutrientType.POTASSIUM,
                interaction_type=InteractionType.SYNERGISTIC,
                interaction_strength=0.6,
                interaction_coefficient=1.10,
                conditions={"soil_type": "loam"}
            ),
            # P-K interactions
            NutrientInteraction(
                nutrient1=NutrientType.PHOSPHORUS,
                nutrient2=NutrientType.POTASSIUM,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.3,
                interaction_coefficient=0.95,
                conditions={"ph_range": (5.5, 6.5)}
            ),
            # Macronutrient-micronutrient interactions
            NutrientInteraction(
                nutrient1=NutrientType.ZINC,
                nutrient2=NutrientType.PHOSPHORUS,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.8,
                interaction_coefficient=0.85,
                conditions={"ph_range": (7.0, 8.0)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.IRON,
                nutrient2=NutrientType.PHOSPHORUS,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.6,
                interaction_coefficient=0.90,
                conditions={"ph_range": (7.5, 8.5)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.MANGANESE,
                nutrient2=NutrientType.PHOSPHORUS,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.5,
                interaction_coefficient=0.92,
                conditions={"ph_range": (7.0, 8.0)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.COPPER,
                nutrient2=NutrientType.PHOSPHORUS,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.4,
                interaction_coefficient=0.95,
                conditions={"ph_range": (7.5, 8.5)}
            ),
            # Nitrogen-micronutrient interactions
            NutrientInteraction(
                nutrient1=NutrientType.NITROGEN,
                nutrient2=NutrientType.ZINC,
                interaction_type=InteractionType.SYNERGISTIC,
                interaction_strength=0.4,
                interaction_coefficient=1.08,
                conditions={"ph_range": (6.0, 7.0)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.NITROGEN,
                nutrient2=NutrientType.BORON,
                interaction_type=InteractionType.SYNERGISTIC,
                interaction_strength=0.3,
                interaction_coefficient=1.05,
                conditions={"ph_range": (6.5, 7.5)}
            ),
            # Potassium-micronutrient interactions
            NutrientInteraction(
                nutrient1=NutrientType.POTASSIUM,
                nutrient2=NutrientType.MAGNESIUM,
                interaction_type=InteractionType.COMPETITIVE,
                interaction_strength=0.6,
                interaction_coefficient=0.90,
                conditions={"soil_type": "sandy"}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.POTASSIUM,
                nutrient2=NutrientType.CALCIUM,
                interaction_type=InteractionType.COMPETITIVE,
                interaction_strength=0.5,
                interaction_coefficient=0.92,
                conditions={"soil_type": "clay"}
            ),
            # Micronutrient-micronutrient interactions
            NutrientInteraction(
                nutrient1=NutrientType.ZINC,
                nutrient2=NutrientType.COPPER,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.7,
                interaction_coefficient=0.88,
                conditions={"ph_range": (6.5, 7.5)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.IRON,
                nutrient2=NutrientType.MANGANESE,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.6,
                interaction_coefficient=0.90,
                conditions={"ph_range": (6.0, 7.0)}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.MOLYBDENUM,
                nutrient2=NutrientType.COPPER,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.5,
                interaction_coefficient=0.93,
                conditions={"ph_range": (6.5, 7.5)}
            ),
            # Sulfur interactions
            NutrientInteraction(
                nutrient1=NutrientType.SULFUR,
                nutrient2=NutrientType.NITROGEN,
                interaction_type=InteractionType.SYNERGISTIC,
                interaction_strength=0.5,
                interaction_coefficient=1.12,
                conditions={"soil_type": "loam"}
            ),
            NutrientInteraction(
                nutrient1=NutrientType.SULFUR,
                nutrient2=NutrientType.MOLYBDENUM,
                interaction_type=InteractionType.ANTAGONISTIC,
                interaction_strength=0.8,
                interaction_coefficient=0.85,
                conditions={"ph_range": (6.0, 7.0)}
            )
        ]
        return interactions
    
    async def optimize_nutrients(self, request: NutrientOptimizationRequest) -> NutrientOptimizationResult:
        """
        Perform comprehensive multi-nutrient optimization.
        
        Args:
            request: Optimization request with field data and constraints
            
        Returns:
            NutrientOptimizationResult with optimal rates and analysis
        """
        start_time = datetime.utcnow()
        optimization_id = str(uuid4())
        
        try:
            self.logger.info(f"Starting multi-nutrient optimization for field {request.field_id}")
            
            # Validate input data
            self._validate_optimization_request(request)
            
            # Prepare optimization data
            optimization_data = self._prepare_optimization_data(request)
            
            # Perform optimization based on method
            if request.interaction_model == "response_surface":
                optimal_rates, optimization_info = await self._response_surface_optimization(
                    optimization_data, request
                )
            elif request.interaction_model == "machine_learning":
                optimal_rates, optimization_info = await self._ml_optimization(
                    optimization_data, request
                )
            else:
                optimal_rates, optimization_info = await self._linear_optimization(
                    optimization_data, request
                )
            
            # Calculate economic analysis
            economic_analysis = self._calculate_economic_analysis(
                optimal_rates, request, optimization_data
            )
            
            # Analyze nutrient interactions
            interaction_analysis = self._analyze_nutrient_interactions(
                optimal_rates, request, optimization_data
            )
            
            # Assess risks
            risk_assessment = self._assess_optimization_risks(
                optimal_rates, request, optimization_data
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                optimal_rates, request, optimization_data, risk_assessment
            )
            
            # Create alternative strategies
            alternative_strategies = self._generate_alternative_strategies(
                optimization_data, request
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = NutrientOptimizationResult(
                optimization_id=optimization_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                optimal_nutrient_rates=optimal_rates,
                expected_yield=economic_analysis["expected_yield"],
                yield_confidence=optimization_info["confidence"],
                total_cost=economic_analysis["total_cost"],
                expected_revenue=economic_analysis["expected_revenue"],
                net_profit=economic_analysis["net_profit"],
                roi_percentage=economic_analysis["roi_percentage"],
                optimization_method=optimization_info["method"],
                convergence_status=optimization_info["status"],
                iterations_required=optimization_info["iterations"],
                optimization_time_seconds=processing_time,
                nutrient_interactions=interaction_analysis["interactions"],
                interaction_effects=interaction_analysis["effects"],
                risk_factors=risk_assessment["factors"],
                risk_score=risk_assessment["score"],
                recommendations=recommendations,
                alternative_strategies=alternative_strategies
            )
            
            self.logger.info(f"Multi-nutrient optimization completed for field {request.field_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in multi-nutrient optimization: {str(e)}")
            raise
    
    def _validate_optimization_request(self, request: NutrientOptimizationRequest):
        """Validate optimization request data."""
        if not request.soil_tests:
            raise ValueError("Soil test data is required for optimization")
        
        if not request.crop_requirements:
            raise ValueError("Crop requirements are required for optimization")
        
        if request.field_size_acres <= 0:
            raise ValueError("Field size must be greater than zero")
        
        # Validate soil test data
        for soil_test in request.soil_tests:
            if soil_test.test_value < 0:
                raise ValueError(f"Invalid soil test value for {soil_test.nutrient}")
        
        # Validate crop requirements
        for requirement in request.crop_requirements:
            if requirement.minimum_requirement < 0:
                raise ValueError(f"Invalid minimum requirement for {requirement.nutrient}")
    
    def _prepare_optimization_data(self, request: NutrientOptimizationRequest) -> Dict[str, Any]:
        """Prepare data for optimization."""
        # Create nutrient mapping
        nutrient_mapping = {}
        for i, nutrient in enumerate([NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]):
            nutrient_mapping[nutrient.value] = i
        
        # Prepare soil test data
        soil_data = {}
        for soil_test in request.soil_tests:
            soil_data[soil_test.nutrient.value] = soil_test.test_value
        
        # Prepare crop requirements
        crop_data = {}
        for requirement in request.crop_requirements:
            crop_data[requirement.nutrient.value] = {
                "minimum": requirement.minimum_requirement,
                "optimal_min": requirement.optimal_range_min,
                "optimal_max": requirement.optimal_range_max,
                "maximum": requirement.maximum_tolerance,
                "efficiency": requirement.uptake_efficiency
            }
        
        # Prepare environmental limits
        env_limits = {}
        for limit in request.environmental_limits:
            env_limits[limit.nutrient.value] = limit.max_application_rate
        
        return {
            "nutrient_mapping": nutrient_mapping,
            "soil_data": soil_data,
            "crop_data": crop_data,
            "env_limits": env_limits,
            "field_size": request.field_size_acres,
            "target_yield": request.target_yield,
            "ph_level": request.ph_level,
            "organic_matter": request.organic_matter_percent,
            "soil_type": request.soil_type
        }
    
    async def _response_surface_optimization(
        self, 
        optimization_data: Dict[str, Any], 
        request: NutrientOptimizationRequest
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Perform response surface optimization."""
        self.logger.info("Performing response surface optimization")
        
        # Determine which nutrients to optimize based on crop requirements
        nutrients_to_optimize = []
        nutrient_mapping = {}
        
        for i, nutrient in enumerate([NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]):
            if nutrient.value in optimization_data["crop_data"]:
                nutrients_to_optimize.append(nutrient.value)
                nutrient_mapping[nutrient.value] = i
        
        # Add secondary macronutrients if present
        secondary_nutrients = [NutrientType.CALCIUM, NutrientType.MAGNESIUM, NutrientType.SULFUR]
        for nutrient in secondary_nutrients:
            if nutrient.value in optimization_data["crop_data"]:
                nutrients_to_optimize.append(nutrient.value)
                nutrient_mapping[nutrient.value] = len(nutrient_mapping)
        
        # Add micronutrients if present
        micronutrients = [NutrientType.ZINC, NutrientType.IRON, NutrientType.MANGANESE, 
                         NutrientType.COPPER, NutrientType.BORON, NutrientType.MOLYBDENUM]
        for nutrient in micronutrients:
            if nutrient.value in optimization_data["crop_data"]:
                nutrients_to_optimize.append(nutrient.value)
                nutrient_mapping[nutrient.value] = len(nutrient_mapping)
        
        # Define objective function
        def objective_function(nutrient_rates):
            """Objective function for response surface optimization."""
            # Convert array to nutrient rates
            rates = {}
            for i, nutrient in enumerate(nutrients_to_optimize):
                rates[nutrient] = nutrient_rates[i]
            
            # Calculate yield response
            yield_response = self._calculate_yield_response(rates, optimization_data, request)
            
            # Calculate cost
            cost = self._calculate_fertilizer_cost(rates, request)
            
            # Apply objective
            if request.optimization_objective == "maximize_profit":
                return -(yield_response * request.target_yield * 0.1 - cost)  # Negative for minimization
            elif request.optimization_objective == "minimize_cost":
                return cost
            elif request.optimization_objective == "maximize_yield":
                return -yield_response  # Negative for minimization
            else:  # balanced
                return -(yield_response * 0.7 + (yield_response * request.target_yield * 0.1 - cost) * 0.3)
        
        # Define constraints
        constraints = self._define_optimization_constraints(optimization_data, request, nutrients_to_optimize)
        
        # Initial guess based on nutrients to optimize
        initial_guess = []
        bounds = []
        
        for nutrient in nutrients_to_optimize:
            if nutrient == NutrientType.NITROGEN.value:
                initial_guess.append(50)
                bounds.append((0, optimization_data["env_limits"].get(nutrient, 200)))
            elif nutrient == NutrientType.PHOSPHORUS.value:
                initial_guess.append(30)
                bounds.append((0, optimization_data["env_limits"].get(nutrient, 150)))
            elif nutrient == NutrientType.POTASSIUM.value:
                initial_guess.append(40)
                bounds.append((0, optimization_data["env_limits"].get(nutrient, 200)))
            elif nutrient in [NutrientType.CALCIUM.value, NutrientType.MAGNESIUM.value, NutrientType.SULFUR.value]:
                initial_guess.append(20)  # Secondary macronutrients
                bounds.append((0, optimization_data["env_limits"].get(nutrient, 100)))
            else:  # Micronutrients
                initial_guess.append(1)  # Micronutrients in lbs/acre
                bounds.append((0, optimization_data["env_limits"].get(nutrient, 10)))
        
        # Perform optimization
        try:
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-6}
            )
            
            if result.success:
                optimal_rates = {}
                for i, nutrient in enumerate(nutrients_to_optimize):
                    optimal_rates[nutrient] = max(0, result.x[i])
                
                # Check if budget constraint is satisfied
                total_cost = self._calculate_fertilizer_cost(optimal_rates, request)
                if request.budget_constraint and total_cost > request.budget_constraint * 1.05:  # 5% tolerance
                    # If budget exceeded, scale down rates proportionally
                    scale_factor = request.budget_constraint / total_cost
                    for nutrient in optimal_rates:
                        optimal_rates[nutrient] *= scale_factor
                
                optimization_info = {
                    "method": "response_surface",
                    "status": "converged",
                    "iterations": result.nit,
                    "confidence": 0.85
                }
            else:
                # Fallback to differential evolution with budget-aware bounds
                if request.budget_constraint:
                    # Adjust bounds to respect budget constraint
                    adjusted_bounds = []
                    for i, nutrient in enumerate(nutrients_to_optimize):
                        original_bound = bounds[i][1]
                        # Estimate max rate based on budget
                        cost_per_lb = {
                            NutrientType.NITROGEN.value: 0.50,
                            NutrientType.PHOSPHORUS.value: 0.60,
                            NutrientType.POTASSIUM.value: 0.40,
                            NutrientType.CALCIUM.value: 0.15,
                            NutrientType.MAGNESIUM.value: 0.25,
                            NutrientType.SULFUR.value: 0.20,
                            NutrientType.ZINC.value: 8.00,
                            NutrientType.IRON.value: 6.00,
                            NutrientType.MANGANESE.value: 7.00,
                            NutrientType.COPPER.value: 12.00,
                            NutrientType.BORON.value: 15.00,
                            NutrientType.MOLYBDENUM.value: 25.00
                        }
                        max_rate_by_budget = request.budget_constraint / cost_per_lb.get(nutrient, 1.0)
                        adjusted_bound = min(original_bound, max_rate_by_budget)
                        adjusted_bounds.append((bounds[i][0], adjusted_bound))
                    bounds = adjusted_bounds
                
                result_de = differential_evolution(
                    objective_function,
                    bounds,
                    maxiter=1000,
                    popsize=15,
                    seed=42
                )
                
                optimal_rates = {}
                for i, nutrient in enumerate(nutrients_to_optimize):
                    optimal_rates[nutrient] = max(0, result_de.x[i])
                
                # Final budget check and adjustment
                total_cost = self._calculate_fertilizer_cost(optimal_rates, request)
                if request.budget_constraint and total_cost > request.budget_constraint * 1.05:
                    scale_factor = request.budget_constraint / total_cost
                    for nutrient in optimal_rates:
                        optimal_rates[nutrient] *= scale_factor
                
                optimization_info = {
                    "method": "differential_evolution",
                    "status": "converged" if result_de.success else "partial",
                    "iterations": result_de.nit,
                    "confidence": 0.75
                }
                
        except Exception as e:
            self.logger.warning(f"Optimization failed, using fallback: {str(e)}")
            optimal_rates = self._calculate_fallback_rates(optimization_data, request)
            optimization_info = {
                "method": "fallback",
                "status": "fallback",
                "iterations": 0,
                "confidence": 0.6
            }
        
        return optimal_rates, optimization_info
    
    async def _ml_optimization(
        self, 
        optimization_data: Dict[str, Any], 
        request: NutrientOptimizationRequest
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Perform machine learning-based optimization."""
        self.logger.info("Performing machine learning optimization")
        
        # Generate training data (simplified - in production, use real historical data)
        training_data = self._generate_training_data(optimization_data, request)
        
        # Train model
        X = training_data[['N_rate', 'P_rate', 'K_rate', 'soil_N', 'soil_P', 'soil_K', 'ph', 'om']]
        y = training_data['yield_response']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Store model for future use
        self.response_models[f"{request.crop_type}_{request.field_id}"] = {
            "model": model,
            "scaler": self.scaler
        }
        
        # Optimize using the trained model
        def ml_objective(nutrient_rates):
            """ML-based objective function."""
            features = np.array([[
                nutrient_rates[0],  # N rate
                nutrient_rates[1],  # P rate
                nutrient_rates[2],  # K rate
                optimization_data["soil_data"].get(NutrientType.NITROGEN.value, 0),
                optimization_data["soil_data"].get(NutrientType.PHOSPHORUS.value, 0),
                optimization_data["soil_data"].get(NutrientType.POTASSIUM.value, 0),
                optimization_data["ph_level"],
                optimization_data["organic_matter"]
            ]])
            
            features_scaled = self.scaler.transform(features)
            yield_response = model.predict(features_scaled)[0]
            
            cost = self._calculate_fertilizer_cost({
                NutrientType.NITROGEN.value: nutrient_rates[0],
                NutrientType.PHOSPHORUS.value: nutrient_rates[1],
                NutrientType.POTASSIUM.value: nutrient_rates[2]
            }, request)
            
            return -(yield_response * 0.7 + (yield_response * request.target_yield * 0.1 - cost) * 0.3)
        
        # Perform optimization
        bounds = [
            (0, optimization_data["env_limits"].get(NutrientType.NITROGEN.value, 200)),
            (0, optimization_data["env_limits"].get(NutrientType.PHOSPHORUS.value, 150)),
            (0, optimization_data["env_limits"].get(NutrientType.POTASSIUM.value, 200))
        ]
        
        result = differential_evolution(
            ml_objective,
            bounds,
            maxiter=1000,
            popsize=15,
            seed=42
        )
        
        optimal_rates = {
            NutrientType.NITROGEN.value: max(0, result.x[0]),
            NutrientType.PHOSPHORUS.value: max(0, result.x[1]),
            NutrientType.POTASSIUM.value: max(0, result.x[2])
        }
        
        optimization_info = {
            "method": "machine_learning",
            "status": "converged" if result.success else "partial",
            "iterations": result.nit,
            "confidence": 0.8
        }
        
        return optimal_rates, optimization_info
    
    async def _linear_optimization(
        self, 
        optimization_data: Dict[str, Any], 
        request: NutrientOptimizationRequest
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """Perform linear optimization."""
        self.logger.info("Performing linear optimization")
        
        # Simplified linear optimization
        optimal_rates = {}
        
        for nutrient in [NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]:
            crop_req = optimization_data["crop_data"].get(nutrient.value, {})
            soil_level = optimization_data["soil_data"].get(nutrient.value, 0)
            
            # Calculate required application
            required = max(0, crop_req.get("optimal_min", 0) - soil_level)
            
            # Apply efficiency factor
            efficiency = crop_req.get("efficiency", 0.7)
            application_rate = required / efficiency if efficiency > 0 else 0
            
            # Apply environmental limits
            env_limit = optimization_data["env_limits"].get(nutrient.value, float('inf'))
            optimal_rates[nutrient.value] = min(application_rate, env_limit)
        
        optimization_info = {
            "method": "linear",
            "status": "converged",
            "iterations": 1,
            "confidence": 0.7
        }
        
        return optimal_rates, optimization_info
    
    def _calculate_yield_response(
        self, 
        nutrient_rates: Dict[str, float], 
        optimization_data: Dict[str, Any], 
        request: NutrientOptimizationRequest
    ) -> float:
        """Calculate yield response based on nutrient rates including micronutrients."""
        # Simplified yield response calculation with micronutrient effects
        # In production, use sophisticated response models
        
        base_yield = request.target_yield * 0.8  # Assume 80% base yield
        
        # Macronutrient responses
        n_rate = nutrient_rates.get(NutrientType.NITROGEN.value, 0)
        n_response = min(0.3, n_rate * 0.002 - (n_rate ** 2) * 0.00001)
        
        p_rate = nutrient_rates.get(NutrientType.PHOSPHORUS.value, 0)
        p_response = min(0.2, p_rate * 0.001)
        
        k_rate = nutrient_rates.get(NutrientType.POTASSIUM.value, 0)
        k_response = min(0.15, k_rate * 0.0008)
        
        # Secondary macronutrient responses
        ca_rate = nutrient_rates.get(NutrientType.CALCIUM.value, 0)
        ca_response = min(0.05, ca_rate * 0.0001)  # Calcium response
        
        mg_rate = nutrient_rates.get(NutrientType.MAGNESIUM.value, 0)
        mg_response = min(0.08, mg_rate * 0.0002)  # Magnesium response
        
        s_rate = nutrient_rates.get(NutrientType.SULFUR.value, 0)
        s_response = min(0.06, s_rate * 0.0003)  # Sulfur response
        
        # Micronutrient responses (smaller individual effects but important)
        zn_rate = nutrient_rates.get(NutrientType.ZINC.value, 0)
        zn_response = min(0.03, zn_rate * 0.001)  # Zinc response
        
        fe_rate = nutrient_rates.get(NutrientType.IRON.value, 0)
        fe_response = min(0.02, fe_rate * 0.0008)  # Iron response
        
        mn_rate = nutrient_rates.get(NutrientType.MANGANESE.value, 0)
        mn_response = min(0.02, mn_rate * 0.0008)  # Manganese response
        
        cu_rate = nutrient_rates.get(NutrientType.COPPER.value, 0)
        cu_response = min(0.015, cu_rate * 0.001)  # Copper response
        
        b_rate = nutrient_rates.get(NutrientType.BORON.value, 0)
        b_response = min(0.025, b_rate * 0.002)  # Boron response
        
        mo_rate = nutrient_rates.get(NutrientType.MOLYBDENUM.value, 0)
        mo_response = min(0.01, mo_rate * 0.005)  # Molybdenum response
        
        # Interaction effects
        interaction_bonus = 0
        interaction_penalty = 0
        
        if request.include_interactions:
            # Macronutrient interactions
            if n_rate > 0 and p_rate > 0:
                interaction_bonus += min(0.05, n_rate * p_rate * 0.00001)
            
            if n_rate > 0 and k_rate > 0:
                interaction_bonus += min(0.03, n_rate * k_rate * 0.000005)
            
            # Macronutrient-micronutrient interactions
            if p_rate > 0 and zn_rate > 0:
                # P-Zn antagonism
                ph_level = optimization_data["ph_level"]
                if ph_level > 7.0:
                    interaction_penalty += min(0.02, p_rate * zn_rate * 0.000001)
            
            if p_rate > 0 and fe_rate > 0:
                # P-Fe antagonism
                ph_level = optimization_data["ph_level"]
                if ph_level > 7.5:
                    interaction_penalty += min(0.015, p_rate * fe_rate * 0.000001)
            
            # Micronutrient-micronutrient interactions
            if zn_rate > 0 and cu_rate > 0:
                # Zn-Cu antagonism
                interaction_penalty += min(0.01, zn_rate * cu_rate * 0.000002)
            
            if fe_rate > 0 and mn_rate > 0:
                # Fe-Mn antagonism
                interaction_penalty += min(0.008, fe_rate * mn_rate * 0.000001)
            
            # Sulfur interactions
            if s_rate > 0 and n_rate > 0:
                # S-N synergy
                interaction_bonus += min(0.02, s_rate * n_rate * 0.000005)
            
            if s_rate > 0 and mo_rate > 0:
                # S-Mo antagonism
                interaction_penalty += min(0.01, s_rate * mo_rate * 0.00001)
        
        # Calculate total response
        macronutrient_response = n_response + p_response + k_response
        secondary_macronutrient_response = ca_response + mg_response + s_response
        micronutrient_response = zn_response + fe_response + mn_response + cu_response + b_response + mo_response
        
        total_response = base_yield * (
            1 + macronutrient_response + secondary_macronutrient_response + 
            micronutrient_response + interaction_bonus - interaction_penalty
        )
        
        return min(total_response, request.target_yield * 1.2)  # Cap at 120% of target
    
    def _calculate_fertilizer_cost(self, nutrient_rates: Dict[str, float], request: NutrientOptimizationRequest) -> float:
        """Calculate fertilizer cost based on nutrient rates including micronutrients."""
        # Simplified cost calculation with micronutrient pricing
        # In production, use real-time fertilizer prices
        
        cost_per_lb = {
            # Macronutrients
            NutrientType.NITROGEN.value: 0.50,
            NutrientType.PHOSPHORUS.value: 0.60,
            NutrientType.POTASSIUM.value: 0.40,
            
            # Secondary macronutrients
            NutrientType.CALCIUM.value: 0.15,
            NutrientType.MAGNESIUM.value: 0.25,
            NutrientType.SULFUR.value: 0.20,
            
            # Micronutrients (higher cost per unit)
            NutrientType.ZINC.value: 8.00,
            NutrientType.IRON.value: 6.00,
            NutrientType.MANGANESE.value: 7.00,
            NutrientType.COPPER.value: 12.00,
            NutrientType.BORON.value: 15.00,
            NutrientType.MOLYBDENUM.value: 25.00
        }
        
        total_cost = 0
        for nutrient, rate in nutrient_rates.items():
            if nutrient in cost_per_lb:
                total_cost += rate * cost_per_lb[nutrient]
        
        return total_cost
    
    def _define_optimization_constraints(self, optimization_data: Dict[str, Any], request: NutrientOptimizationRequest, nutrients_to_optimize: List[str]):
        """Define optimization constraints."""
        constraints = []
        
        # Budget constraint
        if request.budget_constraint:
            def budget_constraint(nutrient_rates):
                # Convert array to nutrient rates dictionary
                rates = {}
                for i, nutrient in enumerate(nutrients_to_optimize):
                    rates[nutrient] = nutrient_rates[i]
                
                cost = self._calculate_fertilizer_cost(rates, request)
                # Return positive value if constraint is satisfied
                return request.budget_constraint - cost
            
            constraints.append({'type': 'ineq', 'fun': budget_constraint})
        
        # Minimum requirement constraints
        def min_requirement_constraint(nutrient_rates):
            violations = []
            for i, nutrient in enumerate(nutrients_to_optimize):
                crop_req = optimization_data["crop_data"].get(nutrient, {})
                min_req = crop_req.get("minimum", 0)
                soil_level = optimization_data["soil_data"].get(nutrient, 0)
                required = max(0, min_req - soil_level)
                efficiency = crop_req.get("efficiency", 0.7)
                min_application = required / efficiency if efficiency > 0 else 0
                violations.append(nutrient_rates[i] - min_application)
            return violations
        
        constraints.append({'type': 'ineq', 'fun': min_requirement_constraint})
        
        return constraints
    
    def _calculate_fallback_rates(self, optimization_data: Dict[str, Any], request: NutrientOptimizationRequest) -> Dict[str, float]:
        """Calculate fallback nutrient rates when optimization fails."""
        fallback_rates = {}
        
        for nutrient in [NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]:
            crop_req = optimization_data["crop_data"].get(nutrient.value, {})
            soil_level = optimization_data["soil_data"].get(nutrient.value, 0)
            
            # Use optimal range midpoint
            optimal_min = crop_req.get("optimal_min", 0)
            optimal_max = crop_req.get("optimal_max", optimal_min + 50)
            target_level = (optimal_min + optimal_max) / 2
            
            required = max(0, target_level - soil_level)
            efficiency = crop_req.get("efficiency", 0.7)
            application_rate = required / efficiency if efficiency > 0 else 0
            
            env_limit = optimization_data["env_limits"].get(nutrient.value, float('inf'))
            fallback_rates[nutrient.value] = min(application_rate, env_limit)
        
        return fallback_rates
    
    def _generate_training_data(self, optimization_data: Dict[str, Any], request: NutrientOptimizationRequest) -> pd.DataFrame:
        """Generate training data for ML model."""
        # Simplified training data generation
        # In production, use real historical data
        
        data = []
        for _ in range(1000):
            n_rate = np.random.uniform(0, 200)
            p_rate = np.random.uniform(0, 150)
            k_rate = np.random.uniform(0, 200)
            
            # Simulate yield response
            yield_response = (
                request.target_yield * 0.8 +
                n_rate * 0.002 - (n_rate ** 2) * 0.00001 +
                p_rate * 0.001 +
                k_rate * 0.0008 +
                np.random.normal(0, 5)  # Noise
            )
            
            data.append({
                'N_rate': n_rate,
                'P_rate': p_rate,
                'K_rate': k_rate,
                'soil_N': optimization_data["soil_data"].get(NutrientType.NITROGEN.value, 0),
                'soil_P': optimization_data["soil_data"].get(NutrientType.PHOSPHORUS.value, 0),
                'soil_K': optimization_data["soil_data"].get(NutrientType.POTASSIUM.value, 0),
                'ph': optimization_data["ph_level"],
                'om': optimization_data["organic_matter"],
                'yield_response': max(0, yield_response)
            })
        
        return pd.DataFrame(data)
    
    def _calculate_economic_analysis(
        self, 
        optimal_rates: Dict[str, float], 
        request: NutrientOptimizationRequest, 
        optimization_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate economic analysis for optimization results."""
        # Calculate costs
        total_cost = self._calculate_fertilizer_cost(optimal_rates, request)
        
        # Calculate expected yield
        expected_yield = self._calculate_yield_response(optimal_rates, optimization_data, request)
        
        # Calculate revenue (simplified - use crop price)
        crop_price_per_unit = 5.0  # $5 per bushel (simplified)
        expected_revenue = expected_yield * crop_price_per_unit
        
        # Calculate profit and ROI
        net_profit = expected_revenue - total_cost
        roi_percentage = (net_profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "total_cost": total_cost,
            "expected_yield": expected_yield,
            "expected_revenue": expected_revenue,
            "net_profit": net_profit,
            "roi_percentage": roi_percentage
        }
    
    def _analyze_nutrient_interactions(
        self, 
        optimal_rates: Dict[str, float], 
        request: NutrientOptimizationRequest, 
        optimization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze nutrient interactions in optimization results."""
        interactions = []
        effects = {}
        
        if request.include_interactions:
            for interaction in self.nutrient_interactions:
                nutrient1_rate = optimal_rates.get(interaction.nutrient1.value, 0)
                nutrient2_rate = optimal_rates.get(interaction.nutrient2.value, 0)
                
                if nutrient1_rate > 0 and nutrient2_rate > 0:
                    # Check if conditions are met
                    conditions_met = True
                    for condition, value in interaction.conditions.items():
                        if condition == "ph_range":
                            ph_min, ph_max = value
                            if not (ph_min <= optimization_data["ph_level"] <= ph_max):
                                conditions_met = False
                                break
                        elif condition == "soil_type":
                            if optimization_data["soil_type"] != value:
                                conditions_met = False
                                break
                    
                    if conditions_met:
                        interactions.append(interaction)
                        effect_key = f"{interaction.nutrient1.value}_{interaction.nutrient2.value}"
                        effects[effect_key] = interaction.interaction_coefficient
        
        return {
            "interactions": interactions,
            "effects": effects
        }
    
    def _assess_optimization_risks(
        self, 
        optimal_rates: Dict[str, float], 
        request: NutrientOptimizationRequest, 
        optimization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risks associated with optimization results."""
        risk_factors = []
        risk_score = 0.0
        
        # High application rates risk
        for nutrient, rate in optimal_rates.items():
            env_limit = optimization_data["env_limits"].get(nutrient, float('inf'))
            if rate > env_limit * 0.8:
                risk_factors.append(f"High {nutrient} application rate")
                risk_score += 0.2
        
        # Budget risk
        if request.budget_constraint:
            total_cost = self._calculate_fertilizer_cost(optimal_rates, request)
            if total_cost > request.budget_constraint * 0.9:
                risk_factors.append("High fertilizer cost")
                risk_score += 0.3
        
        # Soil pH risk
        if optimization_data["ph_level"] < 5.5 or optimization_data["ph_level"] > 8.0:
            risk_factors.append("Suboptimal soil pH")
            risk_score += 0.2
        
        # Low organic matter risk
        if optimization_data["organic_matter"] < 1.0:
            risk_factors.append("Low organic matter content")
            risk_score += 0.1
        
        risk_score = min(1.0, risk_score)
        
        return {
            "factors": risk_factors,
            "score": risk_score
        }
    
    def _generate_recommendations(
        self, 
        optimal_rates: Dict[str, float], 
        request: NutrientOptimizationRequest, 
        optimization_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on optimization results."""
        recommendations = []
        
        # Application timing recommendations
        recommendations.append("Apply nitrogen in split applications: 60% at planting, 40% at V6 stage")
        recommendations.append("Apply phosphorus and potassium at planting for optimal root development")
        
        # Risk-based recommendations
        if risk_assessment["score"] > 0.5:
            recommendations.append("Consider reducing application rates to minimize risk")
            recommendations.append("Monitor soil conditions closely during growing season")
        
        # Soil pH recommendations
        if optimization_data["ph_level"] < 6.0:
            recommendations.append("Consider lime application to raise soil pH")
        elif optimization_data["ph_level"] > 7.5:
            recommendations.append("Monitor micronutrient availability due to high pH")
        
        # Organic matter recommendations
        if optimization_data["organic_matter"] < 2.0:
            recommendations.append("Consider cover crops or organic amendments to increase organic matter")
        
        return recommendations
    
    def _generate_alternative_strategies(
        self, 
        optimization_data: Dict[str, Any], 
        request: NutrientOptimizationRequest
    ) -> List[Dict[str, Any]]:
        """Generate alternative optimization strategies."""
        alternatives = []
        
        # Conservative strategy
        conservative_rates = {}
        for nutrient in [NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]:
            crop_req = optimization_data["crop_data"].get(nutrient.value, {})
            soil_level = optimization_data["soil_data"].get(nutrient.value, 0)
            min_req = crop_req.get("minimum", 0)
            required = max(0, min_req - soil_level)
            efficiency = crop_req.get("efficiency", 0.7)
            conservative_rates[nutrient.value] = required / efficiency if efficiency > 0 else 0
        
        alternatives.append({
            "strategy": "conservative",
            "description": "Minimum nutrient requirements only",
            "rates": conservative_rates,
            "expected_yield": request.target_yield * 0.85,
            "cost": self._calculate_fertilizer_cost(conservative_rates, request)
        })
        
        # Aggressive strategy
        aggressive_rates = {}
        for nutrient in [NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]:
            crop_req = optimization_data["crop_data"].get(nutrient.value, {})
            optimal_max = crop_req.get("optimal_max", 0)
            soil_level = optimization_data["soil_data"].get(nutrient.value, 0)
            required = max(0, optimal_max - soil_level)
            efficiency = crop_req.get("efficiency", 0.7)
            aggressive_rates[nutrient.value] = required / efficiency if efficiency > 0 else 0
        
        alternatives.append({
            "strategy": "aggressive",
            "description": "Maximum optimal nutrient rates",
            "rates": aggressive_rates,
            "expected_yield": request.target_yield * 1.1,
            "cost": self._calculate_fertilizer_cost(aggressive_rates, request)
        })
        
        return alternatives