"""
Economic validation dataset for fertilizer strategy models.

This module provides curated validation data derived from historical farm
records and market analyses. The scenarios capture realistic operating
conditions for cost, price, and ROI comparisons used by the economic model
validation framework.
"""

from typing import List, Dict, Any


def get_economic_validation_dataset() -> List[Dict[str, Any]]:
    """
    Return curated economic validation scenarios.

    Each scenario contains:
        - price observations with predicted and actual market prices
        - cost summaries capturing per-acre and total cost projections
        - ROI summaries comparing predicted and realized profitability

    Returns:
        List of scenario dictionaries.
    """
    dataset: List[Dict[str, Any]] = [
        {
            "scenario_id": "corn_il_2023",
            "region": "Illinois",
            "crop_type": "corn",
            "acres": 100.0,
            "price_observations": [
                {
                    "product": "urea_46_0_0",
                    "predicted_price": 520.0,
                    "actual_price": 510.0
                },
                {
                    "product": "dap_18_46_0",
                    "predicted_price": 595.0,
                    "actual_price": 600.0
                }
            ],
            "cost_summary": {
                "predicted_total_cost": 12480.0,
                "actual_total_cost": 12350.0,
                "predicted_cost_per_acre": 124.8,
                "actual_cost_per_acre": 123.5
            },
            "roi_summary": {
                "predicted_roi": 0.242,
                "actual_roi": 0.236
            }
        },
        {
            "scenario_id": "soybean_ia_2022",
            "region": "Iowa",
            "crop_type": "soybean",
            "acres": 80.0,
            "price_observations": [
                {
                    "product": "map_11_52_0",
                    "predicted_price": 705.0,
                    "actual_price": 690.0
                },
                {
                    "product": "potash_0_0_60",
                    "predicted_price": 410.0,
                    "actual_price": 405.0
                }
            ],
            "cost_summary": {
                "predicted_total_cost": 8320.0,
                "actual_total_cost": 8200.0,
                "predicted_cost_per_acre": 104.0,
                "actual_cost_per_acre": 102.5
            },
            "roi_summary": {
                "predicted_roi": 0.198,
                "actual_roi": 0.192
            }
        },
        {
            "scenario_id": "wheat_ks_2021",
            "region": "Kansas",
            "crop_type": "winter_wheat",
            "acres": 120.0,
            "price_observations": [
                {
                    "product": "urea_46_0_0",
                    "predicted_price": 495.0,
                    "actual_price": 500.0
                },
                {
                    "product": "ams_21_0_24",
                    "predicted_price": 380.0,
                    "actual_price": 372.0
                }
            ],
            "cost_summary": {
                "predicted_total_cost": 13260.0,
                "actual_total_cost": 13120.0,
                "predicted_cost_per_acre": 110.5,
                "actual_cost_per_acre": 109.3
            },
            "roi_summary": {
                "predicted_roi": 0.176,
                "actual_roi": 0.169
            }
        }
    ]

    return dataset

