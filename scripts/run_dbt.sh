#!/bin/bash

echo "Running DBT commands"
echo "Run all dependencies to collect the required packages before dbt model execution"

dbt deps

# Run dbt
dbt run --target dev --profiles-dir .
RUN_EXIT_CODE=$?

# If run command failed. Exit early
if [ $RUN_EXIT_CODE -ne 0 ]; then
  echo "dbt run failed"
  exit $RUN_EXIT_CODE
fi

# exit with the test exit code
echo "dbt run complete"
exit $TEST_EXIT_CODE