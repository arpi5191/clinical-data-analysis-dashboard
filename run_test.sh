#!/bin/bash

# Give a space before running tests
echo ""

# Run tests for Part II
echo "Running tests to verify per-sample cell population frequencies (Part II)..."
python3 testing/test_cell_population_summary.py
echo ""

# Run tests for Part III
echo "Running tests to verify cell population frequencies per subject (Part III)..."
python3 testing/test_cell_response_analysis.py
echo ""

# Run analysis for Part IV
echo "Running analysis to verify cell subsets (Part IV)..."
python3 testing/test_cell_subset_analysis.py

# Final message
echo ""
echo "Ran all tests!"
