import pandas as pd

# Read the input and output CSV files
input_df = pd.read_csv("input/cell_counts.csv")
output_df = pd.read_csv("output/cell_summary.csv")

# Store the samples and populations in lists
samples = ["sample00000", "sample01369", "sample09929"]
populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

# Iterate over the samples
for sample in samples:
    # Obtain the row from the input file
    real_row = input_df[input_df["sample"] == sample]

    # If the real row is empty, print a notification
    if real_row.empty:
        print(f"No data found for {sample} in input file.")
        continue

    # Calculate the actual popuation total for the sample
    real_total = real_row[populations].sum(axis=1).iloc[0]

    # Iterate over the populations
    for population in populations:
        # Obtain the row that has the sample and population
        my_row = output_df[
            (output_df['sample'] == sample) & (output_df['population'] == population)
        ]

        # If the row is empty print a notification
        if my_row.empty:
            print(f"No summary data for {population} in {sample}.")
            continue

        # Obtain the real and actual cell population frequencies
        real_percentage = round(real_row[population].iloc[0] / real_total * 100, 2)
        my_percentage = round(my_row["percentage"].iloc[0], 2)

        # Compare my population frequency to theirs and print a notification if the tests passed
        if my_percentage == real_percentage:
            print(f"{population} passed the cell population test for {sample}!")
        else:
            print(f"{population} FAILED for {sample}: expected {real_percentage}, got {my_percentage}")
    print()
