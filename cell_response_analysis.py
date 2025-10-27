from db import CellDataLoader
import pandas as pd

class CellResponseAnalysis:
    def __init__(self, db_path="cell_data.db"):
        self.loader = CellDataLoader(db_path)

    def compute_response(self):
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

        self.loader.cursor.execute(query)
        rows = self.loader.cursor.fetchall()

        cell_response_df = pd.DataFrame(rows, columns=['subject', 'response', 'population',
                                                       'total_population_count', 'total_count', 'percentage'])

        csv_filename = "cell_response.csv"
        cell_response_df.to_csv(csv_filename, index=False)

def main():
    responder = CellResponseAnalysis()
    responder.compute_response()

if __name__ == "__main__":
    main()
