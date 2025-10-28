#!/bin/bash

# Give a space before running analyses
echo ""

# Running code to set up the database
echo "Setting up tables in database (Part I)..."
python3 code/db.py

echo ""

# Running code to load the data into the database
echo "Loading information into tables (Part I)..."
python3 code/load_data.py

echo ""

# Running code to obtain cell population frequencies per sample
echo "Computing cell population frequencies per sample (Part II)..."
python3 code/cell_population_summary.py

echo ""

# Running code to obtain cell population frequencies per subject
echo "Computing cell population frequencies of melanoma patients (Part III)..."
python3 code/cell_response_analysis.py

echo ""

# Running code to obtain cell subsets
echo "Computing cell subsets (Part IV)..."
python3 code/cell_subset_analysis.py

# If the script ran successfully, notify user
echo ""
echo "Ran all analyses!"
