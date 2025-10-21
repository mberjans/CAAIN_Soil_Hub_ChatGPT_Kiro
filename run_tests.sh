#!/bin/bash
export PYTHONPATH=$(pwd):$(pwd)/services/micronutrient-management/src
pytest "$@"