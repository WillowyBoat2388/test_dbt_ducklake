#!/bin/bash



echo "Running DUCKLAKE PIPELINE"
echo "Run all dependencies to collect the required packages before ducklake pipeline execution"
uv sync
echo "Dependencies Installed"

uv run etl/ingestion/main.py
./scripts/run_dbt.sh