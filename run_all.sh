#!/bin/bash

# Running code to set up the database
echo "Setting up tables in database..."
python3 code/db.py

echo ""

# Running code to load the data into the database
echo "Loading information into tables..."
python3 code/load_data.py

echo ""

# Running code to obtain cell population frequencies per sample
echo "Computing cell population frequencies per sample..."
python3 code/cell_population_summary.py

echo ""

# Running code to obtain cell population frequencies per subject
echo "Computing cell population frequencies of melanoma patients..."
python3 code/cell_response_analysis.py

echo ""

# Running code to obtain cell subsets
echo "Computing cell subsets..."
python3 code/cell_subset_analysis.py

# If the script ran successfully, notify user
echo ""
echo "All done!"
