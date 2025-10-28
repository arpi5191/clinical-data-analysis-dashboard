import pandas as pd

# Read the input and output CSV files
input_df = pd.read_csv("input/cell_counts.csv")
output_df = pd.read_csv("output/cell_response.csv")

# Filter the input dataframe with the criteria
filtered_df = input_df[
    (input_df['condition'] == 'melanoma') &
    (input_df['treatment'] == 'miraclib') &
    (input_df['sample_type'] == 'PBMC')
]

# Store the subjects and populations in lists
subjects = ["sbj002", "sbj020", "sbj422"]
populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

# Iterate through each subject
for subject in subjects:

    # Obtain the rows that have that subject from the input DataFrame
    real_rows = input_df[input_df["subject"] == subject]

    # If the real rows are empty, print a notification
    if real_rows.empty:
        print(f"No data found for {subject} in input file.")
        continue

    # Calculate the actual popuation total for the subject
    real_total = real_rows[populations].sum().sum()

    # Iterate over the populations
    for population in populations:
        # Obtain the row that has the subject and population
        my_row = output_df[
            (output_df['subject'] == subject) & (output_df['population'] == population)
        ]

        # If the row is empty print a notification
        if my_row.empty:
            print(f"No summary data for {population} in {subject}.")
            continue

        # Calculate the real count for that cell population
        real_pop = real_rows[population].sum()

        # Obtain my percentage and the real percentage
        real_percentage = round(real_pop/real_total * 100, 2)
        my_percentage = round(my_row["percentage"].iloc[0], 2)

        # Compare my percentage with the real percentage
        if my_percentage == real_percentage:
            print(f"{population} passed the cell population test for {subject}!")
        else:
            print(f"{population} FAILED for {subject}: expected {real_percentage}, got {my_percentage}")

    print()
