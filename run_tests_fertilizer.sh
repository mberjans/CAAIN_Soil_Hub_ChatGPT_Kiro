#!/bin/bash

# Activate the virtual environment
source .venv_fertilizer_type_selection/bin/activate

# Change to the service directory
cd services/fertilizer-type-selection

# Run pytest for the specific test file
python -m pytest tests/test_priority_constraint.py
