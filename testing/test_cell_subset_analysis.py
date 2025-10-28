import pandas as pd

# Read input and output CSV files
input_df = pd.read_csv("input/cell_counts.csv")
project_output_df = pd.read_csv("output/cell_project_summary.csv")
response_output_df = pd.read_csv("output/cell_response_summary.csv")
gender_output_df = pd.read_csv("output/cell_gender_summary.csv")

# Filter the input dataframe with the criteria
filtered_df = input_df[
    (input_df['condition'] == 'melanoma') &
    (input_df['treatment'] == 'miraclib') &
    (input_df['sample_type'] == 'PBMC') &
    (input_df['time_from_treatment_start'] == 0)
]

# ------------------ Projects ------------------
# Get the sample counts for each project in the filtered DataFrame
project_counts = filtered_df['project'].value_counts()

# Iterate through each project and count
for project, count in project_counts.items():
    # Obtain the row from my result
    my_row = project_output_df[project_output_df['project'] == project]
    if my_row.empty:
        continue
    # Get my sample count
    my_count = my_row['sample_count'].tolist()[0]
    # Compare my count to the actual count
    if count == my_count:
        print(f"{project} passed the cell subset test for projects!")

print()

# ------------------ Responses ------------------
# Get the subject counts for each response in the filtered DataFrame
response_counts = filtered_df['response'].value_counts()

# Iterate through each response and count
for response, count in response_counts.items():
    # Obtain the row from my result
    my_row = response_output_df[response_output_df['response'] == response]
    if my_row.empty:
        continue
    # Get my subject count
    my_count = my_row['subject_count'].tolist()[0]
    # Compare my count to the actual count
    if count == my_count:
        print(f"{response} passed the cell subset test for responses!")

print()

# ------------------ Gender ------------------
# Get the subject counts for each gender in the filtered DataFrame
gender_counts = filtered_df['sex'].value_counts()

# Iterate through each gender and count
for gender, count in gender_counts.items():
    # Obtain the row from my result
    my_row = gender_output_df[gender_output_df['gender'] == gender]
    if my_row.empty:
        continue
    # Get my subject count
    my_count = my_row['subject_count'].tolist()[0]
    # Compare my count to the actual count
    if count == my_count:
        print(f"{gender} passed the cell subset test for gender!")

print()
