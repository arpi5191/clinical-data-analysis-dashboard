# Clinical Data Analysis Dashboard

## Project Description

This project analyzes PBMC samples from melanoma patients treated with Miraclib and generates 
an interactive dashboard to explore and visualize key trends in immune cell populations.

### Project Structure

- **Root Folder**  
  Contains scripts to run the entire project end-to-end:
  - `run_all.sh` — runs all code scripts to perform the analyses and generate output files.  
  - `run_test.sh` — runs all test scripts to verify the analyses.  
  - `README.md` — this project documentation.  
  - `requirements.txt` — lists all required Python packages.

- **input/**  
  Contains input data files:
  - `cell_counts.csv` — raw cell count data for all samples.

- **output/**  
  Stores the generated outputs of the analyses:
  - `cell_summary.csv` — per-sample cell population frequencies.  
  - `cell_response.csv` — per-subject PBMC sample analysis for melanoma patients treated with Miraclib.  
  - `cell_project_summary.csv` — number of samples per project.  
  - `cell_response_summary.csv` — number of subjects with yes/no responses.  
  - `cell_gender_summary.csv` — number of male/female subjects.

- **code/**  
  Contains all analysis scripts:
  - `db.py` — sets up database tables and schema for storing data.  
  - `load_data.py` — loads input files into the database.  
  - `cell_population_summary.py` — computes per-sample cell population frequencies.  
  - `cell_response_analysis.py` — computes PBMC sample frequencies for melanoma patients treated with mircalib.
  - `cell_subset_analysis.py` — computes summary statistics for PBMC samples of melanoma patients treated with miraclib, covering project counts, responder status, and gender distribution.
  - `dashboard.py` — launches the interactive Streamlit dashboard.

- **testing/**  
  Contains test scripts for verifying analysis results:
  - `test_cell_population_summary.py` — tests per-sample cell population frequencies.  
  - `test_cell_response_analysis.py` — tests PBMC sample analysis for melanoma patients treated with mircalib.
  - `test_cell_subset_analysis.py` — tests subset statistics.

### Key Tasks

1. **Database setup:** Database tables are created using a designed schema in `code/db.py` to store 
   cell count and patient information.
2. **Data loading:** Information from the input file `input/cell_counts.csv` is loaded into the database 
   tables using `code/load_data.py`.
3. **Per-sample cell population frequencies:** Frequencies are computed for each sample using 
   `code/cell_population_summary.py` and saved to `output/cell_summary.csv`.
4. **PBMC sample analysis for melanoma patients:** Cell population frequencies for PBMC samples 
   from melanoma patients treated with Miraclib are computed using `code/cell_response_analysis.py` 
   and saved to `output/cell_response.csv`.
5. **Subset statistics:** The number of samples per project, the number of subjects with 
   yes/no responses, and the number of male/female subjects are computed using 
   `code/cell_subset_analysis.py` and saved to `output/cell_project_summary.csv`, 
   `output/cell_response_summary.csv`, and `output/cell_gender_summary.csv`.
6. **Testing:** Verify results using the test scripts in `testing/`:
   - `testing/test_cell_population_summary.py` — tests per-sample frequencies.  
   - `testing/test_cell_response_analysis.py` — tests PBMC sample analysis.  
   - `testing/test_cell_subset_analysis.py` — tests subset statistics.
7. **Interactive visualizations:** The interactive dashboard is launched using Streamlit via 
   `code/dashboard.py`.
