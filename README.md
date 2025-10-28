# Clinical Data Analysis Dashboard

## Project Description

### Motivation

This project analyzes PBMC samples from melanoma patients treated with Miraclib and generates 
an interactive dashboard to explore and visualize key trends in immune cell populations.

### Architecture and Dashboard Overview

#### Database Schema Design Rationale

I created a table called samples in the database schema with the following fields: sample, sample_type, subject, project_id, time_from_treatment_start, treatment, condition, and response. Each sample is designated as a primary key to uniquely identify every row. The subject field is a foreign key referencing the subjects table, allowing each sample to be associated with its corresponding subject, since a subject can have multiple samples. Similarly, the project_id field is a foreign key referencing the projects table. Using an integer index for project_id rather than a string improves database performance, especially for operations such as counting the number of samples per project in large datasets.
The sample_type and time_from_treatment_start fields are included because they pertain specifically to each sample rather than the subject as a whole. The fields treatment, condition, and response are also stored in the samples table rather than the subjects table. This design accounts for potential edge cases where a patient could have mixed treatments, conditions, or responses. While this dataset does not currently contain such cases (each subject has a single treatment, condition, and response), this schema ensures scalability and flexibility for future data.

I created a table called subjects with the following fields: subject, age, and sex. Each subject is designated as a primary key to uniquely identify every row. The age and sex fields are included because they directly correspond to each individual subject. Treatments, conditions, and responses were intentionally not included in this table to account for potential edge cases where a subject might have multiple treatments, conditions, or responses.

I also created a table called projects in which each project name is assigned a unique auto-incrementing integer. This allows each project to be uniquely identified and enables faster searches when querying the samples table, as integer indexes are more efficient than string-based searches.

Lastly, I created a table called cell_counts with the following fields: cell_id, cell_type, sample, and count. This table stores the counts of each cell population for every sample, which is useful for identifying trends and computing per-sample frequencies. The cell_id field is an auto-incrementing primary key to uniquely identify each row. The combination of sample and cell_type is set to be unique to prevent duplicate entries. The sample field is a foreign key referencing the samples table, establishing a direct association between cell counts and their corresponding samples. This structure makes it straightforward to compute cell population frequencies for each sample.

#### Scalability and Performance

## Project Structure

- **Root Folder**  
  Contains scripts to run the entire project end-to-end:
  - `run_all.sh` — runs all code scripts to perform the analyses and generate output files.  
  - `run_test.sh` — runs all test scripts to verify the analyses.  
  - `README.md` — this project documentation.  
  - `requirements.txt` — lists all required Python packages.

- **.streamlit/**  
  Contains configuration for the Streamlit app:
  - `config.toml` — sets the theme, colors, and fonts for the dashboard.

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

## Key Tasks

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
   `code/dashboard.py`. The app’s appearance, including theme and colors, is configured in 
   the `.streamlit/config.toml` file.

