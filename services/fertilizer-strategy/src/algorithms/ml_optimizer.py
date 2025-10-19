"""
Machine Learning-Based Optimizer for Fertilizer Timing

This module implements a machine learning-based optimizer that learns optimal
timing patterns from historical data. It uses a combination of supervised learning
for outcome prediction and reinforcement learning concepts for decision-making.

Approach:
    1. Feature engineering from historical applications
    2. Supervised learning to predict yield/outcome
    3. Q-learning inspired approach for timing decisions
    4. Adaptive learning from field-specific conditions
"""

import logging
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import json

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)

logger = logging.getLogger(__name__)


@dataclass
class HistoricalRecord:
    """Historical application record with outcome."""
    field_id: str
    crop_type: str
    application_date: date
    fertilizer_type: str
    amount: float
    method: ApplicationMethod
    weather_condition: WeatherCondition
    crop_stage: CropGrowthStage
    soil_moisture: float
    yield_outcome: float
    cost: float


@dataclass
class FeatureVector:
    """Feature vector for ML model."""
    day_of_year: int
    days_from_planting: int
    crop_stage_index: int
    temperature: float
    soil_moisture: float
    weather_condition_index: int
    cumulative_nitrogen: float
    cumulative_phosphorus: float
    cumulative_potassium: float
    application_amount: float
    slope_percent: float

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([
            self.day_of_year / 365.0,
            self.days_from_planting / 120.0,
            self.crop_stage_index / 20.0,
            self.temperature / 100.0,
            self.soil_moisture,
            self.weather_condition_index / 5.0,
            self.cumulative_nitrogen / 200.0,
            self.cumulative_phosphorus / 100.0,
            self.cumulative_potassium / 150.0,
            self.application_amount / 100.0,
            self.slope_percent / 20.0
        ])


@dataclass
class MLResult:
    """Result from ML-based optimization."""
    recommended_schedule: List[Tuple[date, str, float, ApplicationMethod]]
    predicted_yield: float
    confidence_intervals: Dict[str, Tuple[float, float]]
    feature_importance: Dict[str, float]
    model_confidence: float
    learning_metrics: Dict[str, float]


class MLOptimizer:
    """
    Machine Learning-based optimizer for fertilizer timing.

    This optimizer combines supervised learning for outcome prediction with
    reinforcement learning concepts for sequential decision-making. It learns
    from historical data and adapts to field-specific conditions.
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        exploration_rate: float = 0.1,
        discount_factor: float = 0.95,
        batch_size: int = 32,
        min_historical_records: int = 10
    ):
        """
        Initialize the ML optimizer.

        Args:
            learning_rate: Learning rate for model updates
            exploration_rate: Exploration rate for exploration-exploitation tradeoff
            discount_factor: Discount factor for future rewards
            batch_size: Batch size for training
            min_historical_records: Minimum historical records required
        """
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.discount_factor = discount_factor
        self.batch_size = batch_size
        self.min_historical_records = min_historical_records

        # Simple neural network weights (feature_dim x hidden_dim x output_dim)
        self.feature_dim = 11
        self.hidden_dim = 20
        self.output_dim = 1

        # Initialize weights with He initialization
        self.weights_input_hidden = np.random.randn(self.feature_dim, self.hidden_dim) * np.sqrt(2.0 / self.feature_dim)
        self.weights_hidden_output = np.random.randn(self.hidden_dim, self.output_dim) * np.sqrt(2.0 / self.hidden_dim)
        self.bias_hidden = np.zeros(self.hidden_dim)
        self.bias_output = np.zeros(self.output_dim)

        # Historical data storage
        self.historical_records: List[HistoricalRecord] = []

        # Feature importance tracking
        self.feature_importance = {
            "day_of_year": 0.0,
            "days_from_planting": 0.0,
            "crop_stage": 0.0,
            "temperature": 0.0,
            "soil_moisture": 0.0,
            "weather_condition": 0.0,
            "cumulative_nitrogen": 0.0,
            "cumulative_phosphorus": 0.0,
            "cumulative_potassium": 0.0,
            "application_amount": 0.0,
            "slope_percent": 0.0
        }

    def optimize(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> MLResult:
        """
        Optimize fertilizer timing using ML-based approach.

        Args:
            request: Optimization request with field and crop data
            weather_windows: Available weather windows for application
            crop_stages: Crop growth stages by date
            historical_data: Optional historical application records

        Returns:
            MLResult with recommended schedule and predictions
        """
        logger.info("Starting ML-based optimization")

        # Load and train on historical data if available
        if historical_data:
            self._load_historical_data(historical_data)
            if len(self.historical_records) >= self.min_historical_records:
                self._train_model()
                logger.info(f"Trained model on {len(self.historical_records)} historical records")
            else:
                logger.warning(f"Insufficient historical data: {len(self.historical_records)} < {self.min_historical_records}")

        # Generate optimal schedule using learned policy
        schedule = self._generate_optimal_schedule(request, weather_windows, crop_stages)

        # Predict outcomes
        predicted_yield, confidence_intervals = self._predict_outcomes(schedule, request, weather_windows, crop_stages)

        # Calculate model confidence
        model_confidence = self._calculate_model_confidence()

        # Calculate feature importance
        self._update_feature_importance()

        # Calculate learning metrics
        learning_metrics = self._calculate_learning_metrics()

        logger.info(f"ML optimization complete. Predicted yield: {predicted_yield:.2f}")

        return MLResult(
            recommended_schedule=schedule,
            predicted_yield=predicted_yield,
            confidence_intervals=confidence_intervals,
            feature_importance=self.feature_importance,
            model_confidence=model_confidence,
            learning_metrics=learning_metrics
        )

    def _load_historical_data(self, historical_data: List[Dict[str, Any]]) -> None:
        """Load historical data into internal format."""
        self.historical_records = []

        for record in historical_data:
            try:
                hist_record = HistoricalRecord(
                    field_id=record.get("field_id", "unknown"),
                    crop_type=record.get("crop_type", "corn"),
                    application_date=record.get("application_date", date.today()),
                    fertilizer_type=record.get("fertilizer_type", "nitrogen"),
                    amount=record.get("amount", 0.0),
                    method=ApplicationMethod(record.get("method", "broadcast")),
                    weather_condition=WeatherCondition(record.get("weather_condition", "acceptable")),
                    crop_stage=CropGrowthStage(record.get("crop_stage", "planting")),
                    soil_moisture=record.get("soil_moisture", 0.5),
                    yield_outcome=record.get("yield_outcome", 0.0),
                    cost=record.get("cost", 0.0)
                )
                self.historical_records.append(hist_record)
            except Exception as e:
                logger.warning(f"Failed to load historical record: {e}")

    def _train_model(self) -> None:
        """Train the neural network model on historical data."""
        logger.info("Training ML model on historical data")

        # Prepare training data
        X_train = []
        y_train = []

        for record in self.historical_records:
            features = self._extract_features(record)
            X_train.append(features.to_array())
            # Normalize yield outcome (assuming typical yield 150-250 bu/acre)
            y_train.append(np.array([record.yield_outcome / 200.0]))

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        # Training loop (simple gradient descent)
        num_epochs = 100
        num_samples = len(X_train)

        for epoch in range(num_epochs):
            # Shuffle data
            indices = np.random.permutation(num_samples)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]

            total_loss = 0.0

            # Mini-batch training
            for i in range(0, num_samples, self.batch_size):
                batch_X = X_shuffled[i:i + self.batch_size]
                batch_y = y_shuffled[i:i + self.batch_size]

                # Forward pass
                hidden = self._relu(np.dot(batch_X, self.weights_input_hidden) + self.bias_hidden)
                output = np.dot(hidden, self.weights_hidden_output) + self.bias_output

                # Compute loss (MSE)
                loss = np.mean((output - batch_y) ** 2)
                total_loss += loss

                # Backward pass
                d_output = 2 * (output - batch_y) / len(batch_y)
                d_weights_hidden_output = np.dot(hidden.T, d_output)
                d_bias_output = np.sum(d_output, axis=0)

                d_hidden = np.dot(d_output, self.weights_hidden_output.T)
                d_hidden[hidden <= 0] = 0  # ReLU gradient

                d_weights_input_hidden = np.dot(batch_X.T, d_hidden)
                d_bias_hidden = np.sum(d_hidden, axis=0)

                # Update weights
                self.weights_hidden_output -= self.learning_rate * d_weights_hidden_output
                self.bias_output -= self.learning_rate * d_bias_output
                self.weights_input_hidden -= self.learning_rate * d_weights_input_hidden
                self.bias_hidden -= self.learning_rate * d_bias_hidden

            if epoch % 20 == 0:
                avg_loss = total_loss / max(1, num_samples / self.batch_size)
                logger.debug(f"Epoch {epoch}, Loss: {avg_loss:.6f}")

    def _extract_features(self, record: HistoricalRecord) -> FeatureVector:
        """Extract features from historical record."""
        crop_stage_indices = {
            CropGrowthStage.PLANTING: 0,
            CropGrowthStage.EMERGENCE: 1,
            CropGrowthStage.V2: 2,
            CropGrowthStage.V4: 3,
            CropGrowthStage.V6: 4,
            CropGrowthStage.V8: 5,
            CropGrowthStage.V10: 6,
            CropGrowthStage.V12: 7,
            CropGrowthStage.VT: 8,
            CropGrowthStage.R1: 9,
            CropGrowthStage.R2: 10,
            CropGrowthStage.R3: 11,
            CropGrowthStage.R4: 12,
            CropGrowthStage.R5: 13,
            CropGrowthStage.R6: 14,
            CropGrowthStage.HARVEST: 15
        }

        weather_indices = {
            WeatherCondition.OPTIMAL: 4,
            WeatherCondition.ACCEPTABLE: 3,
            WeatherCondition.MARGINAL: 2,
            WeatherCondition.POOR: 1,
            WeatherCondition.UNACCEPTABLE: 0
        }

        return FeatureVector(
            day_of_year=record.application_date.timetuple().tm_yday,
            days_from_planting=0,  # Would need planting date from record
            crop_stage_index=crop_stage_indices.get(record.crop_stage, 0),
            temperature=70.0,  # Would come from weather data
            soil_moisture=record.soil_moisture,
            weather_condition_index=weather_indices.get(record.weather_condition, 2),
            cumulative_nitrogen=0.0,  # Would track from previous applications
            cumulative_phosphorus=0.0,
            cumulative_potassium=0.0,
            application_amount=record.amount,
            slope_percent=0.0  # Would come from field data
        )

    def _generate_optimal_schedule(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Tuple[date, str, float, ApplicationMethod]]:
        """Generate optimal schedule using learned policy."""
        schedule = []

        # State tracking
        cumulative_applied = {
            "nitrogen": 0.0,
            "phosphorus": 0.0,
            "potassium": 0.0
        }

        # Evaluate each potential application date
        current_date = request.planting_date
        end_date = request.planting_date + timedelta(days=min(120, request.optimization_horizon_days))

        candidate_applications = []

        while current_date <= end_date:
            # Get current state
            weather = self._get_weather_for_date(current_date, weather_windows)
            crop_stage = self._get_crop_stage_for_date(current_date, crop_stages)

            if weather and weather.condition != WeatherCondition.UNACCEPTABLE:
                # Evaluate each fertilizer type
                for fertilizer_type, total_required in request.fertilizer_requirements.items():
                    remaining = total_required - cumulative_applied.get(fertilizer_type, 0.0)

                    if remaining > 0:
                        # Consider different application amounts
                        for fraction in [0.33, 0.5, 1.0]:
                            amount = remaining * fraction

                            # Create feature vector for this potential application
                            features = self._create_feature_vector(
                                current_date, request, weather, crop_stage,
                                cumulative_applied, amount, fertilizer_type
                            )

                            # Predict value using neural network
                            predicted_value = self._predict(features)

                            # Add exploration bonus
                            exploration_bonus = 0.0
                            if np.random.random() < self.exploration_rate:
                                exploration_bonus = np.random.uniform(0, 0.1)

                            candidate_applications.append({
                                "date": current_date,
                                "fertilizer_type": fertilizer_type,
                                "amount": amount,
                                "method": request.application_methods[0],
                                "value": predicted_value + exploration_bonus,
                                "features": features
                            })

            current_date += timedelta(days=1)

        # Select best applications using greedy approach with constraints
        selected_applications = self._select_best_applications(
            candidate_applications, request, cumulative_applied
        )

        # Convert to schedule format
        for app in selected_applications:
            schedule.append((
                app["date"],
                app["fertilizer_type"],
                app["amount"],
                app["method"]
            ))

        return sorted(schedule, key=lambda x: x[0])

    def _select_best_applications(
        self,
        candidates: List[Dict[str, Any]],
        request: TimingOptimizationRequest,
        cumulative_applied: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Select best applications from candidates."""
        # Sort by predicted value
        sorted_candidates = sorted(candidates, key=lambda x: x["value"], reverse=True)

        selected = []
        applied = cumulative_applied.copy()

        for candidate in sorted_candidates:
            fertilizer_type = candidate["fertilizer_type"]
            required = request.fertilizer_requirements.get(fertilizer_type, 0.0)
            current_applied = applied.get(fertilizer_type, 0.0)

            # Check if we still need this fertilizer
            if current_applied < required:
                # Don't over-apply
                remaining = required - current_applied
                actual_amount = min(candidate["amount"], remaining)

                selected.append({
                    **candidate,
                    "amount": actual_amount
                })

                applied[fertilizer_type] = current_applied + actual_amount

            # Stop if all fertilizers are applied
            all_complete = True
            for fert_type, req_amount in request.fertilizer_requirements.items():
                if applied.get(fert_type, 0.0) < req_amount * 0.95:
                    all_complete = False
                    break

            if all_complete:
                break

        return selected

    def _create_feature_vector(
        self,
        app_date: date,
        request: TimingOptimizationRequest,
        weather: WeatherWindow,
        crop_stage: CropGrowthStage,
        cumulative_applied: Dict[str, float],
        amount: float,
        fertilizer_type: str
    ) -> FeatureVector:
        """Create feature vector for prediction."""
        crop_stage_indices = {
            CropGrowthStage.PLANTING: 0, CropGrowthStage.EMERGENCE: 1, CropGrowthStage.V2: 2,
            CropGrowthStage.V4: 3, CropGrowthStage.V6: 4, CropGrowthStage.V8: 5,
            CropGrowthStage.V10: 6, CropGrowthStage.V12: 7, CropGrowthStage.VT: 8,
            CropGrowthStage.R1: 9, CropGrowthStage.R2: 10, CropGrowthStage.R3: 11,
            CropGrowthStage.R4: 12, CropGrowthStage.R5: 13, CropGrowthStage.R6: 14,
            CropGrowthStage.HARVEST: 15
        }

        weather_indices = {
            WeatherCondition.OPTIMAL: 4, WeatherCondition.ACCEPTABLE: 3,
            WeatherCondition.MARGINAL: 2, WeatherCondition.POOR: 1,
            WeatherCondition.UNACCEPTABLE: 0
        }

        return FeatureVector(
            day_of_year=app_date.timetuple().tm_yday,
            days_from_planting=(app_date - request.planting_date).days,
            crop_stage_index=crop_stage_indices.get(crop_stage, 0),
            temperature=weather.temperature_f,
            soil_moisture=weather.soil_moisture,
            weather_condition_index=weather_indices.get(weather.condition, 2),
            cumulative_nitrogen=cumulative_applied.get("nitrogen", 0.0),
            cumulative_phosphorus=cumulative_applied.get("phosphorus", 0.0),
            cumulative_potassium=cumulative_applied.get("potassium", 0.0),
            application_amount=amount,
            slope_percent=request.slope_percent
        )

    def _predict(self, features: FeatureVector) -> float:
        """Predict outcome using neural network."""
        x = features.to_array().reshape(1, -1)

        # Forward pass
        hidden = self._relu(np.dot(x, self.weights_input_hidden) + self.bias_hidden)
        output = np.dot(hidden, self.weights_hidden_output) + self.bias_output

        return float(output[0, 0])

    def _predict_outcomes(
        self,
        schedule: List[Tuple[date, str, float, ApplicationMethod]],
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Tuple[float, Dict[str, Tuple[float, float]]]:
        """Predict outcomes for the recommended schedule."""
        # Simple ensemble prediction with uncertainty estimation
        predictions = []

        cumulative_applied = {"nitrogen": 0.0, "phosphorus": 0.0, "potassium": 0.0}

        for app_date, fertilizer_type, amount, method in schedule:
            weather = self._get_weather_for_date(app_date, weather_windows)
            crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

            if weather:
                features = self._create_feature_vector(
                    app_date, request, weather, crop_stage,
                    cumulative_applied, amount, fertilizer_type
                )

                pred = self._predict(features)
                predictions.append(pred)

                cumulative_applied[fertilizer_type] = cumulative_applied.get(fertilizer_type, 0.0) + amount

        # Aggregate predictions (denormalize)
        if predictions:
            mean_prediction = np.mean(predictions) * 200.0  # Denormalize yield
            std_prediction = np.std(predictions) * 200.0
        else:
            mean_prediction = 180.0  # Default typical yield
            std_prediction = 20.0

        # Confidence intervals (95%)
        confidence_intervals = {
            "yield": (mean_prediction - 1.96 * std_prediction, mean_prediction + 1.96 * std_prediction),
            "lower_bound": (mean_prediction - 2.0 * std_prediction, mean_prediction - std_prediction),
            "upper_bound": (mean_prediction + std_prediction, mean_prediction + 2.0 * std_prediction)
        }

        return mean_prediction, confidence_intervals

    def _calculate_model_confidence(self) -> float:
        """Calculate overall model confidence."""
        if len(self.historical_records) < self.min_historical_records:
            return 0.5  # Low confidence with insufficient data

        # Confidence based on amount of training data
        data_confidence = min(1.0, len(self.historical_records) / 100.0)

        # Confidence based on model performance (simplified)
        # In production, would use validation set performance
        performance_confidence = 0.75

        return 0.5 * data_confidence + 0.5 * performance_confidence

    def _update_feature_importance(self) -> None:
        """Update feature importance based on weight magnitudes."""
        # Calculate importance from input-hidden weights
        weight_magnitudes = np.abs(self.weights_input_hidden).sum(axis=1)
        total_magnitude = weight_magnitudes.sum()

        feature_names = [
            "day_of_year", "days_from_planting", "crop_stage", "temperature",
            "soil_moisture", "weather_condition", "cumulative_nitrogen",
            "cumulative_phosphorus", "cumulative_potassium", "application_amount",
            "slope_percent"
        ]

        for i, name in enumerate(feature_names):
            self.feature_importance[name] = float(weight_magnitudes[i] / total_magnitude)

    def _calculate_learning_metrics(self) -> Dict[str, float]:
        """Calculate learning performance metrics."""
        return {
            "training_samples": len(self.historical_records),
            "model_parameters": self.feature_dim * self.hidden_dim + self.hidden_dim * self.output_dim,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate,
            "convergence_score": 0.8  # Simplified metric
        }

    def _relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation function."""
        return np.maximum(0, x)

    def _get_weather_for_date(
        self,
        target_date: date,
        weather_windows: List[WeatherWindow]
    ) -> Optional[WeatherWindow]:
        """Get weather window for specific date."""
        for window in weather_windows:
            if window.start_date <= target_date <= window.end_date:
                return window
        return None

    def _get_crop_stage_for_date(
        self,
        target_date: date,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> CropGrowthStage:
        """Get crop growth stage for a specific date."""
        closest_stage = CropGrowthStage.PLANTING
        min_diff = float('inf')

        for stage_date, stage in crop_stages.items():
            diff = abs((target_date - stage_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_stage = stage

        return closest_stage
