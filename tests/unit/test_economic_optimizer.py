import pytest
from services.fertilizer_application.economic_optimizer import EconomicOptimizer


def test_optimization_algorithm():
    """
    Test the EconomicOptimizer's ability to optimize fertilizer recommendations
    based on field requirements and available fertilizers.
    """
    optimizer = EconomicOptimizer()

    # Sample field requirements (nutrient needs)
    field_requirements = {
        'nitrogen': 100,
        'phosphorus': 50,
        'potassium': 75
    }

    # Sample available fertilizers with composition and cost
    available_fertilizers = [
        {'name': 'Fert1', 'composition': {'N': 20, 'P': 10, 'K': 5}, 'cost': 10},
        {'name': 'Fert2', 'composition': {'N': 10, 'P': 20, 'K': 10}, 'cost': 15},
        {'name': 'Fert3', 'composition': {'N': 15, 'P': 15, 'K': 15}, 'cost': 12}
    ]

    # Sample market prices (can be a dict or list, adjust based on implementation)
    market_prices = {
        'Fert1': 10,
        'Fert2': 15,
        'Fert3': 12
    }

    # Sample yield goals
    yield_goals = {
        'target_yield': 200,
        'yield_unit': 'bushels'
    }

    # Sample constraints
    constraints = {
        'budget': 1000,
        'environmental_impact': 'low'
    }

    # Call the optimization method
    result = optimizer.optimize_fertilizer_strategy(
        field_data=field_requirements,
        market_prices=market_prices,
        yield_goals=yield_goals,
        constraints=constraints
    )

    # Assertions to verify the optimization result
    assert result is not None
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)
    assert len(result['recommendations']) > 0

    # Check that each recommendation has required fields
    for rec in result['recommendations']:
        assert 'fertilizer' in rec
        assert 'amount' in rec
        assert 'cost' in rec

    # Verify total cost is within budget
    total_cost = sum(rec['cost'] for rec in result['recommendations'])
    assert total_cost <= constraints['budget']

    # Additional checks if result has more fields
    if 'total_cost' in result:
        assert result['total_cost'] == total_cost

    if 'environmental_impact' in result:
        assert result['environmental_impact'] == 'low' or result['environmental_impact'] <= constraints['environmental_impact']

    # Ensure the optimization meets nutrient requirements (basic check)
    total_n = sum(rec['amount'] * available_fertilizers[i]['composition']['N'] for i, rec in enumerate(result['recommendations']))
    total_p = sum(rec['amount'] * available_fertilizers[i]['composition']['P'] for i, rec in enumerate(result['recommendations']))
    total_k = sum(rec['amount'] * available_fertilizers[i]['composition']['K'] for i, rec in enumerate(result['recommendations']))

    # Note: This is a simplified check; actual implementation may vary
    assert total_n >= field_requirements['nitrogen'] * 0.8  # Allow some tolerance
    assert total_p >= field_requirements['phosphorus'] * 0.8
    assert total_k >= field_requirements['potassium'] * 0.8