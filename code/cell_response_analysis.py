from db import CellDataLoader
import pandas as pd

class CellResponseAnalysis:
    """
    Compute the relative cell population frequencies of PBMC samples from melanoma patients
    treated with miraclib, stratified by response (yes/no).
    """

    def __init__(self, db_path="code/cell_data.db"):
        self.loader = CellDataLoader(db_path)

    def compute_response(self):
        """
        Compute the relative cell population frequencies of PBMC samples from melanoma patients
        treated with miraclib, stratified by response (yes/no).

        Output:
            A CSV file 'cell_response.csv' containing the following columns:
            - subject: ID of the subject
            - response: the subject's response to miraclib treatment ('yes' or 'no')
            - population: immune cell type for which the frequency is calculated
            - total_population_count: total count of the specific cell type for that subject across all relevant samples
            - total_count: total count of all cell types for that subject across all relevant samples
            - percentage: relative frequency of the cell type for the subject (%)
        """

        # Write the query to compute the cell population frequencies for melanoma patients
        query = """
                    SELECT
                        su.subject,
                        sa.response,
                        c.population,
                        SUM(c.count) AS total_population_count,
                        SUM(c.total_count) AS total_count,
                        ROUND(100.0 * SUM(c.count) / SUM(c.total_count), 2) AS percentage
                    FROM subjects AS su
                    JOIN samples AS sa ON sa.subject = su.subject
                    JOIN cell_summary AS c ON c.sample = sa.sample
                    WHERE sa.condition = "melanoma" AND sa.treatment = "miraclib" AND sa.sample_type = "PBMC"
                          AND (sa.response = "yes" OR sa.response = "no")
                    GROUP BY su.subject, c.population, sa.response
                    ORDER BY su.subject, c.population;
                """

        # Execute the query
        self.loader.cursor.execute(query)

        # Fetch the rows from the database
        rows = self.loader.cursor.fetchall()

        # Create a DataFrame based on the information in the database
        cell_response_df = pd.DataFrame(rows, columns=['subject', 'response', 'population',
                                                       'total_population_count', 'total_count', 'percentage'])

        # Save the DataFrame information in a CSV file
        csv_filename = "output/cell_response.csv"
        cell_response_df.to_csv(csv_filename, index=False)

def main():
    # Create an instance of CellResponseAnalysis
    responder = CellResponseAnalysis()

    # Compute the cell population frequencies based on response
    responder.compute_response()

if __name__ == "__main__":
    main()
