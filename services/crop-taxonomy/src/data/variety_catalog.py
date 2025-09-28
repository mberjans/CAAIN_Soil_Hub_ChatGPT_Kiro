"""Comprehensive crop variety catalog generation utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import copy

VARIETY_LIBRARY_VERSION = "2025.03.20"
_CACHED_LIBRARY: Optional[Dict[str, Any]] = None

RESISTANCE_SEQUENCE = [
    "susceptible",
    "moderate",
    "tolerant",
    "resistant",
    "immune"
]

SEED_STATUS_ROTATION = [
    "in_stock",
    "in_stock",
    "limited",
    "preorder",
    "in_stock",
    "retired"
]

SEED_AVAILABILITY_ROTATION = [
    "widely_available",
    "widely_available",
    "limited",
    "specialty"
]

RELATIVE_SEED_COST_ROTATION = [
    "moderate",
    "moderate",
    "high",
    "premium"
]

CROP_CONFIG: Dict[str, Dict[str, Any]] = {}
