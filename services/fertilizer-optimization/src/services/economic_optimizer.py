import numpy as np
from scipy.optimize import linprog
import logging

logger = logging.getLogger(__name__)

class EconomicOptimizer:
    """
    EconomicOptimizer class for optimizing fertilizer strategies and calculating ROI.
    """

    def __init__(self):
        """
        Initialize the EconomicOptimizer.
        """
        pass

    def optimize_fertilizer_strategy(self, field_requirements, available_fertilizers, budget_per_acre):
        """
        Optimize fertilizer application strategy using linear programming.

        Args:
            field_requirements (dict): Dictionary of nutrient requirements, e.g., {'N': 100, 'P': 50, 'K': 20}
            available_fertilizers (list): List of dictionaries, each containing:
                - 'name' (str): Fertilizer name
                - 'nutrients' (dict): Nutrients per unit, e.g., {'N': 10, 'P': 5}
                - 'cost_per_unit' (float): Cost per unit of fertilizer
            budget_per_acre (float): Budget per acre for fertilizers

        Returns:
            dict: Dictionary of fertilizer names to recommended amounts

        Raises:
            ValueError: If inputs are invalid or optimization fails
        """
        try:
            # Input validation
            if not isinstance(field_requirements, dict) or not field_requirements:
                raise ValueError("field_requirements must be a non-empty dictionary")
            if not isinstance(available_fertilizers, list) or not available_fertilizers:
                raise ValueError("available_fertilizers must be a non-empty list")
            if not isinstance(budget_per_acre, (int, float)) or budget_per_acre <= 0:
                raise ValueError("budget_per_acre must be a positive number")

            # Extract nutrients and number of fertilizers
            nutrients = list(field_requirements.keys())
            num_fertilizers = len(available_fertilizers)

            # Objective function: minimize total cost
            # Handle different cost field names for compatibility
            c = np.array([f.get('cost_per_unit', f.get('price_per_ton', 0)) for f in available_fertilizers])

            # Equality constraints for nutrient requirements (A_eq for = constraints)
            A_eq = []
            b_eq = []
            for nut in nutrients:
                row = np.array([f['nutrients'].get(nut, 0) for f in available_fertilizers])
                A_eq.append(row)
                b_eq.append(field_requirements[nut])

            # Budget constraint (cost <= budget)
            A_ub = np.array([[f.get('cost_per_unit', f.get('price_per_ton', 0)) for f in available_fertilizers]])
            b_ub = np.array([budget_per_acre])

            # Bounds: non-negative amounts
            bounds = [(0, None) for _ in range(num_fertilizers)]

            # Solve linear programming problem (minimize cost with equality constraints)
            res = linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

            if res.success:
                recommendations = {f['name']: res.x[i] for i, f in enumerate(available_fertilizers)}
                logger.info("Optimization successful")
                return recommendations
            else:
                raise ValueError(f"Optimization failed: {res.message}")

        except Exception as e:
            logger.error(f"Error in optimize_fertilizer_strategy: {str(e)}")
            raise ValueError(f"Optimization error: {str(e)}")

    def calculate_roi(self, recommendations, field_data, crop_price_per_bu):
        """
        Calculate the Return on Investment (ROI) for fertilizer recommendations.

        Args:
            recommendations (dict): Dictionary of fertilizer names to amounts (from optimize_fertilizer_strategy)
            field_data (dict): Dictionary containing field data, must include:
                - 'yield_bu_per_acre' (float): Yield in bushels per acre
                - 'total_fertilizer_cost' (float): Total cost of fertilizers applied
            crop_price_per_bu (float): Price per bushel of the crop

        Returns:
            float: ROI value ((revenue - cost) / cost)

        Raises:
            ValueError: If inputs are invalid
        """
        try:
            # Input validation
            if not isinstance(recommendations, (dict, list)):
                raise ValueError("recommendations must be a dictionary or list")
            if not isinstance(field_data, dict):
                raise ValueError("field_data must be a dictionary")
            if not isinstance(crop_price_per_bu, (int, float)) or crop_price_per_bu <= 0:
                raise ValueError("crop_price_per_bu must be a positive number")

            # Handle different field data formats
            if isinstance(recommendations, list):
                # Calculate total cost from recommendations list
                total_cost = sum(rec.get('cost', 0) for rec in recommendations)
                # Get yield from field_data
                yield_bu = field_data.get('expected_yield_improvement', 0) * field_data.get('field_acres', 1)
            else:
                # Original dict format
                if 'yield_bu_per_acre' not in field_data or 'total_fertilizer_cost' not in field_data:
                    raise ValueError("field_data must contain 'yield_bu_per_acre' and 'total_fertilizer_cost' for dict format")
                yield_bu = field_data['yield_bu_per_acre']
                total_cost = field_data['total_fertilizer_cost']

            if not isinstance(yield_bu, (int, float)) or yield_bu < 0:
                raise ValueError("yield_bu_per_acre must be a non-negative number")
            if not isinstance(total_cost, (int, float)) or total_cost < 0:
                raise ValueError("total_fertilizer_cost must be a non-negative number")

            # Calculate revenue
            revenue = yield_bu * crop_price_per_bu

            # Calculate ROI
            if total_cost > 0:
                roi = (revenue - total_cost) / total_cost
            else:
                roi = float('inf')  # Infinite ROI if no cost (edge case)

            logger.info(f"Calculated ROI: {roi}")
            return roi

        except Exception as e:
            logger.error(f"Error in calculate_roi: {str(e)}")
            raise ValueError(f"ROI calculation error: {str(e)}")