from db import CellDataLoader
import pandas as pd

class CellPopulationSummary:
    """
    Compute the relative frequencies of immune cell populations for each sample.
    """

    def __init__(self, db_path="code/cell_data.db"):
        self.loader = CellDataLoader(db_path)

    def compute_summary(self):
        """
        Compute the relative frequencies of immune cell populations for each sample.

        Output:
            A CSV file 'cell_summary.csv' containing the following columns:
            - subject: ID of the subject
            - total_count: total number of cells in the sample
            - population: immune cell type
            - count: number of cells of that type in the sample
            - percentage: relative frequency of the cell type within the sample (%)
        """

        # Write the query to compute the cell population frequencies per sample
        query = """
                    SELECT
                        c.sample,
                        SUM(c.count) OVER (PARTITION BY c.sample) AS total_count,
                        c.cell_type AS population,
                        c.count,
                        ROUND(100.0 * c.count / SUM(c.count) OVER (PARTITION BY c.sample), 2) AS percentage
                    FROM cell_counts AS c
                    ORDER BY c.sample, c.cell_type
                """

        # Execute the query
        self.loader.cursor.execute(query)

        # Fetch the rows from the database
        rows = self.loader.cursor.fetchall()

        # Create a DataFrame based on the information in the database
        cell_summary_df = pd.DataFrame(rows, columns=['sample', 'total_count', 'population', 'count', 'percentage'])

        # Store the DataFrame information in a database
        cell_summary_df.to_sql('cell_summary', self.loader.conn, if_exists='replace', index=False)

        # Save the DataFrame information in a CSV file
        csv_filename = "output/cell_summary.csv"
        cell_summary_df.to_csv(csv_filename, index=False)

def main():
    # Create an instance of CellPopulationSummary
    summarizer = CellPopulationSummary()

    # Compute the cell population frequencies per sample
    summarizer.compute_summary()

if __name__ == "__main__":
    main()
