#!/bin/bash



echo "Running DUCKLAKE PIPELINE"
echo "Run all dependencies to collect the required packages before ducklake pipeline execution"
uv build
uv sync
echo "Dependencies Installed"

cd ./src
echo "Changed directory to src"

uv run etl/ingestion/main.py
scripts/run_dbt.sh