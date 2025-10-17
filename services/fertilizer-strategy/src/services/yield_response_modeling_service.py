"""
Sophisticated Yield-Fertilizer Response Curves Service.

This service provides advanced curve fitting for yield-fertilizer response analysis including:
- Nutrient response curves with interaction effects
- Diminishing returns modeling
- Multiple mathematical models (Mitscherlich-Baule, quadratic plateau, linear plateau, exponential)
- Integration with university research data and field trial results
- Optimal rate calculations with confidence intervals
- Economic threshold analysis
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from uuid import uuid4
from scipy import optimize, stats
from scipy.optimize import curve_fit
import pandas as pd

from ..models.yield_response_models import (
    YieldResponseRequest, YieldResponseAnalysis, YieldResponseCurve,
    NutrientResponseData, ResponseModelType, CurveFitResult,
    OptimalRateAnalysis, EconomicThreshold, InteractionEffect,
    ConfidenceInterval, ModelValidation, ResponseCurveComparison
)

logger = logging.getLogger(__name__)


class YieldResponseModelingService:
    """
    Sophisticated yield-fertilizer response curves modeling service.
    
    Features:
    - Advanced curve fitting with multiple mathematical models
    - Nutrient interaction effects modeling
    - Diminishing returns analysis
    - Integration with research data and field trials
    - Optimal rate calculations with confidence intervals
    - Economic threshold analysis
    """
    
    def __init__(self):
        """Initialize the yield response modeling service."""
        self.logger = logging.getLogger(__name__)
        
        # Model parameters and constraints
        self.model_constraints = {
            ResponseModelType.MITSCHERLICH_BAULE: {
                'bounds': [(0, 1000), (0, 1000), (0, 1000)],  # A, b, c
                'initial_guess': [200, 0.1, 0.01]
            },
            ResponseModelType.QUADRATIC_PLATEAU: {
                'bounds': [(0, 1000), (-10, 10), (-0.1, 0.1)],  # a, b, c
                'initial_guess': [150, 1.0, -0.001]
            },
            ResponseModelType.LINEAR_PLATEAU: {
                'bounds': [(0, 1000), (0, 10), (0, 1000)],  # a, b, plateau_x
                'initial_guess': [100, 0.5, 200]
            },
            ResponseModelType.EXPONENTIAL: {
                'bounds': [(0, 1000), (0, 10), (0, 1)],  # a, b, c
                'initial_guess': [150, 0.01, 0.1]
            }
        }
        
        # Crop-specific response parameters
        self.crop_response_parameters = {
            'corn': {
                'typical_max_yield': 250.0,
                'typical_response_range': (0, 300),
                'nutrient_interactions': {
                    'N_P': 0.15,
                    'N_K': 0.12,
                    'P_K': 0.08
                }
            },
            'soybean': {
                'typical_max_yield': 80.0,
                'typical_response_range': (0, 150),
                'nutrient_interactions': {
                    'N_P': 0.10,
                    'N_K': 0.08,
                    'P_K': 0.06
                }
            },
            'wheat': {
                'typical_max_yield': 100.0,
                'typical_response_range': (0, 200),
                'nutrient_interactions': {
                    'N_P': 0.12,
                    'N_K': 0.10,
                    'P_K': 0.07
                }
            }
        }
    
    async def analyze_yield_response(self, request: YieldResponseRequest) -> YieldResponseAnalysis:
        """
        Perform comprehensive yield response analysis.
        
        Args:
            request: Yield response analysis request
            
        Returns:
            Comprehensive yield response analysis
        """
        try:
            analysis_id = uuid4()
            
            # 1. Validate input data
            validation_result = await self._validate_input_data(request)
            
            # 2. Fit response curves for each nutrient
            nutrient_curves = {}
            for nutrient in request.nutrients:
                curve_data = await self._extract_nutrient_data(request.response_data, nutrient)
                if len(curve_data) >= 3:  # Minimum data points for curve fitting
                    curve = await self._fit_response_curve(curve_data, nutrient, request.crop_type)
                    nutrient_curves[nutrient] = curve
            
            # 3. Analyze nutrient interactions
            interaction_effects = await self._analyze_nutrient_interactions(
                request.response_data, request.nutrients, request.crop_type
            )
            
            # 4. Calculate optimal rates
            optimal_rates = await self._calculate_optimal_rates(
                nutrient_curves, request.economic_parameters, request.crop_type
            )
            
            # 5. Perform economic threshold analysis
            economic_thresholds = await self._calculate_economic_thresholds(
                nutrient_curves, request.economic_parameters, request.crop_type
            )
            
            # 6. Validate models
            model_validations = await self._validate_models(nutrient_curves, request.response_data)
            
            # 7. Compare models
            model_comparison = await self._compare_models(nutrient_curves)
            
            # 8. Calculate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                nutrient_curves, request.response_data
            )
            
            analysis = YieldResponseAnalysis(
                analysis_id=analysis_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                nutrient_curves=nutrient_curves,
                interaction_effects=interaction_effects,
                optimal_rates=optimal_rates,
                economic_thresholds=economic_thresholds,
                model_validations=model_validations,
                model_comparison=model_comparison,
                confidence_intervals=confidence_intervals,
                validation_result=validation_result,
                analysis_timestamp=datetime.utcnow()
            )
            
            self.logger.info(f"Yield response analysis completed for field {request.field_id}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in yield response analysis: {e}")
            raise
    
    async def _validate_input_data(self, request: YieldResponseRequest) -> ModelValidation:
        """Validate input data quality and completeness."""
        issues = []
        warnings = []
        
        # Check minimum data points
        if len(request.response_data) < 3:
            issues.append("Insufficient data points for curve fitting (minimum 3 required)")
        
        # Check nutrient coverage
        for nutrient in request.nutrients:
            nutrient_data = [d for d in request.response_data if nutrient in d.nutrient_rates]
            if len(nutrient_data) < 3:
                warnings.append(f"Insufficient data points for {nutrient} analysis")
        
        # Check yield range validity
        yields = [d.yield_per_acre for d in request.response_data]
        if max(yields) - min(yields) < 10:
            warnings.append("Limited yield variation may affect curve fitting accuracy")
        
        # Check for extreme nutrient rates
        for nutrient in request.nutrients:
            nutrient_rates = [d.nutrient_rates.get(nutrient, 0) for d in request.response_data if nutrient in d.nutrient_rates]
            if nutrient_rates:
                max_rate = max(nutrient_rates)
                if max_rate > 500:  # Extremely high rates
                    warnings.append(f"Extreme nutrient rates detected for {nutrient} (max: {max_rate})")
        
        # Check for outliers
        outlier_count = await self._detect_outliers(yields)
        if outlier_count > len(yields) * 0.2:
            warnings.append(f"High number of outliers detected ({outlier_count})")
        
        # Check for limited variation in nutrient rates
        for nutrient in request.nutrients:
            nutrient_rates = [d.nutrient_rates.get(nutrient, 0) for d in request.response_data if nutrient in d.nutrient_rates]
            if len(set(nutrient_rates)) < 3:  # Less than 3 unique rates
                warnings.append(f"Limited variation in {nutrient} rates may affect curve fitting")
        
        # Calculate data quality score
        quality_score = 1.0
        quality_score -= len(issues) * 0.3
        quality_score -= len(warnings) * 0.1
        quality_score = max(0.0, quality_score)
        
        return ModelValidation(
            is_valid=len(issues) == 0,
            quality_score=quality_score,
            issues=issues,
            warnings=warnings,
            data_points=len(request.response_data),
            nutrient_coverage=len(request.nutrients)
        )
    
    async def _extract_nutrient_data(
        self, 
        response_data: List[NutrientResponseData], 
        nutrient: str
    ) -> List[Tuple[float, float]]:
        """Extract data points for a specific nutrient."""
        data_points = []
        
        for data in response_data:
            if nutrient in data.nutrient_rates:
                rate = data.nutrient_rates[nutrient]
                yield_value = data.yield_per_acre
                data_points.append((rate, yield_value))
        
        return sorted(data_points, key=lambda x: x[0])
    
    async def _fit_response_curve(
        self, 
        data_points: List[Tuple[float, float]], 
        nutrient: str, 
        crop_type: str
    ) -> YieldResponseCurve:
        """Fit response curve using multiple models and select the best one."""
        
        x_data = np.array([point[0] for point in data_points])
        y_data = np.array([point[1] for point in data_points])
        
        best_model = None
        best_r_squared = -1
        best_fit_result = None
        
        # Try each model type
        for model_type in ResponseModelType:
            try:
                fit_result = await self._fit_single_model(x_data, y_data, model_type)
                if fit_result.r_squared > best_r_squared:
                    best_r_squared = fit_result.r_squared
                    best_model = model_type
                    best_fit_result = fit_result
            except Exception as e:
                self.logger.warning(f"Failed to fit {model_type} model for {nutrient}: {e}")
                continue
        
        if best_fit_result is None:
            raise ValueError(f"Unable to fit any model for {nutrient}")
        
        # Generate curve predictions
        x_range = np.linspace(0, max(x_data) * 1.2, 100)
        y_predicted = self._predict_yield_sync(x_range, best_model, best_fit_result.parameters)
        
        # Calculate additional metrics
        mse = np.mean((y_data - self._predict_yield_sync(x_data, best_model, best_fit_result.parameters)) ** 2)
        rmse = np.sqrt(mse)
        
        # Calculate economic metrics
        crop_params = self.crop_response_parameters.get(crop_type, self.crop_response_parameters['corn'])
        
        return YieldResponseCurve(
            nutrient=nutrient,
            model_type=best_model,
            parameters=best_fit_result.parameters,
            r_squared=best_fit_result.r_squared,
            rmse=rmse,
            mse=mse,
            data_points=data_points,
            predicted_curve=list(zip(x_range, y_predicted)),
            max_yield=crop_params['typical_max_yield'],
            response_range=crop_params['typical_response_range']
        )
    
    async def _fit_single_model(
        self, 
        x_data: np.ndarray, 
        y_data: np.ndarray, 
        model_type: ResponseModelType
    ) -> CurveFitResult:
        """Fit a single model type to the data."""
        
        def mitscherlich_baule(x, A, b, c):
            """Mitscherlich-Baule model: y = A * (1 - exp(-b * (x + c)))"""
            return A * (1 - np.exp(-b * (x + c)))
        
        def quadratic_plateau(x, a, b, c):
            """Quadratic plateau model: y = a + b*x + c*x^2 (with plateau)"""
            plateau_x = -b / (2 * c) if c != 0 else 0
            plateau_y = a + b * plateau_x + c * plateau_x**2
            return np.where(x <= plateau_x, a + b*x + c*x**2, plateau_y)
        
        def linear_plateau(x, a, b, plateau_x):
            """Linear plateau model: y = a + b*x for x <= plateau_x, then plateau"""
            plateau_y = a + b * plateau_x
            return np.where(x <= plateau_x, a + b*x, plateau_y)
        
        def exponential(x, a, b, c):
            """Exponential model: y = a * (1 - exp(-b * x)) + c"""
            return a * (1 - np.exp(-b * x)) + c
        
        # Select model function
        model_functions = {
            ResponseModelType.MITSCHERLICH_BAULE: mitscherlich_baule,
            ResponseModelType.QUADRATIC_PLATEAU: quadratic_plateau,
            ResponseModelType.LINEAR_PLATEAU: linear_plateau,
            ResponseModelType.EXPONENTIAL: exponential
        }
        
        model_func = model_functions[model_type]
        constraints = self.model_constraints[model_type]
        
        try:
            # Fit the model
            popt, pcov = curve_fit(
                model_func, 
                x_data, 
                y_data, 
                p0=constraints['initial_guess'],
                maxfev=10000
            )
            
            # Calculate R-squared
            y_pred = model_func(x_data, *popt)
            ss_res = np.sum((y_data - y_pred) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            # Ensure R-squared is non-negative
            r_squared = max(0.0, r_squared)
            
            # Calculate parameter standard errors
            param_errors = np.sqrt(np.diag(pcov))
            
            return CurveFitResult(
                model_type=model_type,
                parameters=popt.tolist(),
                parameter_errors=param_errors.tolist(),
                r_squared=r_squared,
                covariance_matrix=pcov.tolist()
            )
            
        except Exception as e:
            self.logger.error(f"Error fitting {model_type} model: {e}")
            raise
    
    async def _predict_yield(
        self, 
        x_values: np.ndarray, 
        model_type: ResponseModelType, 
        parameters: List[float]
    ) -> np.ndarray:
        """Predict yield values using fitted model."""
        return self._predict_yield_sync(x_values, model_type, parameters)
    
    def _predict_yield_sync(
        self, 
        x_values: np.ndarray, 
        model_type: ResponseModelType, 
        parameters: List[float]
    ) -> np.ndarray:
        """Predict yield values using fitted model (synchronous version)."""
        
        def mitscherlich_baule(x, A, b, c):
            return A * (1 - np.exp(-b * (x + c)))
        
        def quadratic_plateau(x, a, b, c):
            plateau_x = -b / (2 * c) if c != 0 else 0
            plateau_y = a + b * plateau_x + c * plateau_x**2
            return np.where(x <= plateau_x, a + b*x + c*x**2, plateau_y)
        
        def linear_plateau(x, a, b, plateau_x):
            plateau_y = a + b * plateau_x
            return np.where(x <= plateau_x, a + b*x, plateau_y)
        
        def exponential(x, a, b, c):
            return a * (1 - np.exp(-b * x)) + c
        
        model_functions = {
            ResponseModelType.MITSCHERLICH_BAULE: mitscherlich_baule,
            ResponseModelType.QUADRATIC_PLATEAU: quadratic_plateau,
            ResponseModelType.LINEAR_PLATEAU: linear_plateau,
            ResponseModelType.EXPONENTIAL: exponential
        }
        
        model_func = model_functions[model_type]
        return model_func(x_values, *parameters)
    
    async def _analyze_nutrient_interactions(
        self, 
        response_data: List[NutrientResponseData], 
        nutrients: List[str], 
        crop_type: str
    ) -> List[InteractionEffect]:
        """Analyze interactions between nutrients."""
        interactions = []
        
        crop_params = self.crop_response_parameters.get(crop_type, self.crop_response_parameters['corn'])
        
        # Analyze pairwise interactions
        for i, nutrient1 in enumerate(nutrients):
            for j, nutrient2 in enumerate(nutrients[i+1:], i+1):
                interaction_strength = await self._calculate_interaction_strength(
                    response_data, nutrient1, nutrient2
                )
                
                # Get expected interaction from crop parameters
                expected_interaction = crop_params['nutrient_interactions'].get(
                    f"{nutrient1}_{nutrient2}", 0.1
                )
                
                interaction_type = "synergistic" if interaction_strength > 0 else "antagonistic"
                significance = "high" if abs(interaction_strength) > 0.15 else "moderate" if abs(interaction_strength) > 0.05 else "low"
                
                interactions.append(InteractionEffect(
                    nutrient1=nutrient1,
                    nutrient2=nutrient2,
                    interaction_strength=interaction_strength,
                    interaction_type=interaction_type,
                    significance=significance,
                    expected_interaction=expected_interaction,
                    deviation_from_expected=interaction_strength - expected_interaction
                ))
        
        return interactions
    
    async def _calculate_interaction_strength(
        self, 
        response_data: List[NutrientResponseData], 
        nutrient1: str, 
        nutrient2: str
    ) -> float:
        """Calculate interaction strength between two nutrients."""
        # This is a simplified interaction calculation
        # In practice, this would use more sophisticated statistical methods
        
        # Find data points with both nutrients
        dual_nutrient_data = [
            d for d in response_data 
            if nutrient1 in d.nutrient_rates and nutrient2 in d.nutrient_rates
        ]
        
        if len(dual_nutrient_data) < 3:
            return 0.0  # Insufficient data
        
        # Calculate correlation between nutrient rates
        rates1 = [d.nutrient_rates[nutrient1] for d in dual_nutrient_data]
        rates2 = [d.nutrient_rates[nutrient2] for d in dual_nutrient_data]
        yields = [d.yield_per_acre for d in dual_nutrient_data]
        
        # Calculate interaction as deviation from additive effect
        # This is a simplified approach - real interaction analysis would be more complex
        correlation = np.corrcoef(rates1, yields)[0, 1] if len(rates1) > 1 else 0
        correlation2 = np.corrcoef(rates2, yields)[0, 1] if len(rates2) > 1 else 0
        
        # Interaction strength as deviation from expected additive effect
        interaction_strength = (correlation + correlation2) / 2 - 0.1  # Adjust baseline
        
        return interaction_strength
    
    async def _calculate_optimal_rates(
        self, 
        nutrient_curves: Dict[str, YieldResponseCurve], 
        economic_params: Dict[str, Any], 
        crop_type: str
    ) -> Dict[str, OptimalRateAnalysis]:
        """Calculate optimal nutrient application rates."""
        optimal_rates = {}
        
        for nutrient, curve in nutrient_curves.items():
            # Calculate economic optimal rate
            fertilizer_price = economic_params.get(f"{nutrient}_price_per_unit", 1.0)
            crop_price = economic_params.get("crop_price_per_unit", 5.0)
            
            # Find rate where marginal revenue equals marginal cost
            optimal_rate = await self._find_economic_optimal_rate(
                curve, fertilizer_price, crop_price
            )
            
            # Calculate maximum yield rate (where response curve plateaus)
            max_yield_rate = await self._find_max_yield_rate(curve)
            
            # Calculate 95% of maximum yield rate
            target_yield = curve.max_yield * 0.95
            target_yield_rate = await self._find_rate_for_target_yield(curve, target_yield)
            
            optimal_rates[nutrient] = OptimalRateAnalysis(
                nutrient=nutrient,
                economic_optimal_rate=optimal_rate,
                max_yield_rate=max_yield_rate,
                target_yield_rate=target_yield_rate,
                economic_optimal_yield=self._predict_yield_sync(
                    np.array([optimal_rate]), curve.model_type, curve.parameters
                )[0],
                max_yield=curve.max_yield,
                target_yield=target_yield,
                marginal_revenue_at_optimal=crop_price * await self._calculate_marginal_response(
                    curve, optimal_rate
                ),
                marginal_cost_at_optimal=fertilizer_price
            )
        
        return optimal_rates
    
    async def _find_economic_optimal_rate(
        self, 
        curve: YieldResponseCurve, 
        fertilizer_price: float, 
        crop_price: float
    ) -> float:
        """Find the economic optimal rate where marginal revenue equals marginal cost."""
        
        def profit_function(rate):
            yield_value = self._predict_yield_sync(np.array([rate]), curve.model_type, curve.parameters)[0]
            revenue = yield_value * crop_price
            cost = rate * fertilizer_price
            return revenue - cost
        
        # Find maximum profit rate
        x_range = np.linspace(0, 300, 1000)  # Search up to 300 units
        profits = [profit_function(x) for x in x_range]
        optimal_rate = x_range[np.argmax(profits)]
        
        return optimal_rate
    
    async def _find_max_yield_rate(self, curve: YieldResponseCurve) -> float:
        """Find the rate that produces maximum yield."""
        x_range = np.linspace(0, 300, 1000)
        yields = self._predict_yield_sync(x_range, curve.model_type, curve.parameters)
        max_yield_idx = np.argmax(yields)
        return x_range[max_yield_idx]
    
    async def _find_rate_for_target_yield(self, curve: YieldResponseCurve, target_yield: float) -> float:
        """Find the rate needed to achieve a target yield."""
        x_range = np.linspace(0, 300, 1000)
        yields = self._predict_yield_sync(x_range, curve.model_type, curve.parameters)
        
        # Find closest yield to target
        diff = np.abs(yields - target_yield)
        closest_idx = np.argmin(diff)
        return x_range[closest_idx]
    
    async def _calculate_marginal_response(self, curve: YieldResponseCurve, rate: float) -> float:
        """Calculate marginal response (derivative) at a given rate."""
        # Numerical derivative
        delta = 1.0
        y1 = self._predict_yield_sync(np.array([rate]), curve.model_type, curve.parameters)[0]
        y2 = self._predict_yield_sync(np.array([rate + delta]), curve.model_type, curve.parameters)[0]
        return (y2 - y1) / delta
    
    async def _calculate_economic_thresholds(
        self, 
        nutrient_curves: Dict[str, YieldResponseCurve], 
        economic_params: Dict[str, Any], 
        crop_type: str
    ) -> Dict[str, EconomicThreshold]:
        """Calculate economic thresholds for nutrient application."""
        thresholds = {}
        
        for nutrient, curve in nutrient_curves.items():
            fertilizer_price = economic_params.get(f"{nutrient}_price_per_unit", 1.0)
            crop_price = economic_params.get("crop_price_per_unit", 5.0)
            
            # Calculate break-even rate (where marginal revenue = marginal cost)
            break_even_rate = await self._find_break_even_rate(curve, fertilizer_price, crop_price)
            
            # Calculate minimum profitable rate
            min_profitable_rate = await self._find_minimum_profitable_rate(curve, fertilizer_price, crop_price)
            
            # Calculate maximum profitable rate
            max_profitable_rate = await self._find_maximum_profitable_rate(curve, fertilizer_price, crop_price)
            
            thresholds[nutrient] = EconomicThreshold(
                nutrient=nutrient,
                break_even_rate=break_even_rate,
                minimum_profitable_rate=min_profitable_rate,
                maximum_profitable_rate=max_profitable_rate,
                fertilizer_price=fertilizer_price,
                crop_price=crop_price,
                price_ratio=crop_price / fertilizer_price if fertilizer_price > 0 else 0
            )
        
        return thresholds
    
    async def _find_break_even_rate(
        self, 
        curve: YieldResponseCurve, 
        fertilizer_price: float, 
        crop_price: float
    ) -> float:
        """Find the break-even rate where marginal revenue equals marginal cost."""
        x_range = np.linspace(0, 300, 1000)
        
        for rate in x_range:
            marginal_response = await self._calculate_marginal_response(curve, rate)
            marginal_revenue = marginal_response * crop_price
            
            if abs(marginal_revenue - fertilizer_price) < 0.01:
                return rate
        
        return 0.0  # No break-even point found
    
    async def _find_minimum_profitable_rate(
        self, 
        curve: YieldResponseCurve, 
        fertilizer_price: float, 
        crop_price: float
    ) -> float:
        """Find the minimum rate that produces positive profit."""
        x_range = np.linspace(0, 300, 1000)
        
        for rate in x_range:
            yield_value = self._predict_yield_sync(np.array([rate]), curve.model_type, curve.parameters)[0]
            revenue = yield_value * crop_price
            cost = rate * fertilizer_price
            profit = revenue - cost
            
            if profit > 0:
                return rate
        
        return 0.0
    
    async def _find_maximum_profitable_rate(
        self, 
        curve: YieldResponseCurve, 
        fertilizer_price: float, 
        crop_price: float
    ) -> float:
        """Find the maximum rate that still produces positive profit."""
        x_range = np.linspace(300, 0, 1000)  # Search backwards
        
        for rate in x_range:
            yield_value = self._predict_yield_sync(np.array([rate]), curve.model_type, curve.parameters)[0]
            revenue = yield_value * crop_price
            cost = rate * fertilizer_price
            profit = revenue - cost
            
            if profit > 0:
                return rate
        
        return 0.0
    
    async def _validate_models(
        self, 
        nutrient_curves: Dict[str, YieldResponseCurve], 
        response_data: List[NutrientResponseData]
    ) -> Dict[str, ModelValidation]:
        """Validate fitted models."""
        validations = {}
        
        for nutrient, curve in nutrient_curves.items():
            # Extract actual data for this nutrient
            nutrient_data = await self._extract_nutrient_data(response_data, nutrient)
            x_actual = np.array([point[0] for point in nutrient_data])
            y_actual = np.array([point[1] for point in nutrient_data])
            
            # Calculate predictions
            y_predicted = self._predict_yield_sync(x_actual, curve.model_type, curve.parameters)
            
            # Calculate validation metrics
            mse = np.mean((y_actual - y_predicted) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(y_actual - y_predicted))
            
            # Calculate R-squared for validation
            ss_res = np.sum((y_actual - y_predicted) ** 2)
            ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Assess model quality
            issues = []
            warnings = []
            
            if r_squared < 0.5:
                issues.append(f"Low R-squared ({r_squared:.3f}) indicates poor model fit")
            elif r_squared < 0.7:
                warnings.append(f"Moderate R-squared ({r_squared:.3f}) indicates fair model fit")
            
            if rmse > np.std(y_actual):
                warnings.append(f"High RMSE ({rmse:.2f}) relative to data variability")
            
            # Calculate quality score
            quality_score = r_squared * 0.6 + (1 - rmse / np.std(y_actual)) * 0.4
            quality_score = max(0.0, min(1.0, quality_score))
            
            validations[nutrient] = ModelValidation(
                is_valid=len(issues) == 0,
                quality_score=quality_score,
                issues=issues,
                warnings=warnings,
                data_points=len(nutrient_data),
                nutrient_coverage=1,
                validation_metrics={
                    'r_squared': r_squared,
                    'rmse': rmse,
                    'mae': mae,
                    'mse': mse
                }
            )
        
        return validations
    
    async def _compare_models(self, nutrient_curves: Dict[str, YieldResponseCurve]) -> ResponseCurveComparison:
        """Compare different models across nutrients."""
        model_performance = {}
        
        for nutrient, curve in nutrient_curves.items():
            if curve.model_type not in model_performance:
                model_performance[curve.model_type] = []
            
            model_performance[curve.model_type].append({
                'nutrient': nutrient,
                'r_squared': curve.r_squared,
                'rmse': curve.rmse,
                'mse': curve.mse
            })
        
        # Calculate average performance for each model
        model_averages = {}
        for model_type, performances in model_performance.items():
            avg_r_squared = np.mean([p['r_squared'] for p in performances])
            avg_rmse = np.mean([p['rmse'] for p in performances])
            avg_mse = np.mean([p['mse'] for p in performances])
            
            model_averages[model_type] = {
                'average_r_squared': avg_r_squared,
                'average_rmse': avg_rmse,
                'average_mse': avg_mse,
                'nutrient_count': len(performances)
            }
        
        # Find best performing model (handle empty case)
        if model_averages:
            best_model = max(model_averages.keys(), key=lambda x: model_averages[x]['average_r_squared'])
        else:
            best_model = ResponseModelType.MITSCHERLICH_BAULE  # Default fallback
        
        return ResponseCurveComparison(
            model_performance=model_performance,
            model_averages=model_averages,
            best_performing_model=best_model,
            comparison_timestamp=datetime.utcnow()
        )
    
    async def _calculate_confidence_intervals(
        self, 
        nutrient_curves: Dict[str, YieldResponseCurve], 
        response_data: List[NutrientResponseData]
    ) -> Dict[str, List[ConfidenceInterval]]:
        """Calculate confidence intervals for response curves."""
        confidence_intervals = {}
        
        for nutrient, curve in nutrient_curves.items():
            # Generate x values for confidence interval calculation
            x_range = np.linspace(0, 300, 100)
            
            # Calculate confidence intervals (simplified approach)
            # In practice, this would use bootstrap or analytical methods
            y_predicted = self._predict_yield_sync(x_range, curve.model_type, curve.parameters)
            
            # Calculate standard error (simplified)
            std_error = curve.rmse * np.sqrt(1 + 1/len(curve.data_points))
            
            # Calculate confidence intervals
            confidence_level = 0.95
            t_value = stats.t.ppf(1 - (1 - confidence_level) / 2, len(curve.data_points) - 1)
            margin_of_error = t_value * std_error
            
            intervals = []
            for i, x_val in enumerate(x_range):
                y_val = y_predicted[i]
                # Ensure predictions are non-negative
                y_val = max(0, y_val)
                lower_bound = max(0, y_val - margin_of_error)
                upper_bound = max(0, y_val + margin_of_error)
                
                intervals.append(ConfidenceInterval(
                    x_value=x_val,
                    predicted_yield=y_val,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    confidence_level=confidence_level,
                    margin_of_error=margin_of_error
                ))
            
            confidence_intervals[nutrient] = intervals
        
        return confidence_intervals
    
    async def _detect_outliers(self, yields: List[float]) -> int:
        """Detect outliers in yield data using IQR method."""
        if len(yields) < 4:
            return 0
        
        q1 = np.percentile(yields, 25)
        q3 = np.percentile(yields, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [y for y in yields if y < lower_bound or y > upper_bound]
        return len(outliers)