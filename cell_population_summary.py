from db import CellDataLoader
import pandas as pd

class CellPopulationSummary:
    def __init__(self, db_path="cell_data.db"):
        self.loader = CellDataLoader(db_path)

    def compute_summary(self):
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

        self.loader.cursor.execute(query)
        rows = self.loader.cursor.fetchall()

        cell_summary_df = pd.DataFrame(rows, columns=['sample', 'total_count', 'population', 'count', 'percentage'])

        cell_summary_df.to_sql('cell_summary', self.loader.conn, if_exists='replace', index=False)

        csv_filename = "cell_summary.csv"
        cell_summary_df.to_csv(csv_filename, index=False)

def main():
    summarizer = CellPopulationSummary()
    summarizer.compute_summary()

if __name__ == "__main__":
    main()
