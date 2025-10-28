from db import CellDataLoader
import pandas as pd

class CellSubsetAnalysis:
    """
    Analyze and summarize subsets of melanoma PBMC baseline samples treated with Miraclib.

    This class provides methods to:
        1. Count the number of samples per project.
        2. Count the number of subjects who are responders or non-responders.
        3. Count the number of subjects by sex (male/female).
    """

    def __init__(self, db_path="code/cell_data.db"):
        self.loader = CellDataLoader(db_path)

    def samples_per_project(self):
        """
        Compute number of samples per project.

        Output:
            A CSV file 'cell_samples_per_project.csv' containing the following columns:
            - project: project name
            - sample_count: number of samples in each project
        """

        # Write the query to compute the number of samples in each project for melanoma patients
        query = """
                    SELECT
                        p.project,
                        COUNT(sa.sample)
                    FROM subjects AS su
                    JOIN samples AS sa ON sa.subject = su.subject
                    JOIN projects AS p ON p.project_id = sa.project_id
                    WHERE sa.condition = "melanoma"
                      AND sa.treatment = "miraclib"
                      AND sa.sample_type = "PBMC"
                      AND sa.time_from_treatment_start = 0
                    GROUP BY sa.project_id
                """

        # Execute the query
        self.loader.cursor.execute(query)

        # Fetch the rows from the database
        rows = self.loader.cursor.fetchall()

        # Create a DataFrame based on the information in the database
        cell_samples_per_project_df = pd.DataFrame(rows, columns=['project', 'sample_count'])

        # Save the DataFrame information in a CSV file
        csv_filename = "output/cell_project_summary.csv"
        cell_samples_per_project_df.to_csv(csv_filename, index=False)

    def subjects_by_response(self):
        """
        Compute number of subjects in each response.

        Output:
            A CSV file 'cell_subjects_by_response.csv' containing the following columns:
            - response: ways a subject could respond after miraclib treatment
            - subject_count: number of subjects in each response
        """

        # Write a query to find how many melanoma patients were responders/non-responders
        query = """
                    SELECT
                        sa.response,
                        COUNT(sa.subject)
                    FROM subjects AS su
                    JOIN samples AS sa ON sa.subject = su.subject
                    WHERE sa.condition = "melanoma"
                      AND sa.treatment = "miraclib"
                      AND sa.sample_type = "PBMC"
                      AND sa.time_from_treatment_start = 0
                      AND sa.response IN ("yes", "no")
                     GROUP BY sa.response
                """

        # Execute the query
        self.loader.cursor.execute(query)

        # Fetch the rows from the database
        rows = self.loader.cursor.fetchall()

        # Create a DataFrame based on the information in the database
        cell_subjects_by_response_df = pd.DataFrame(rows, columns=['response', 'subject_count'])

        # Save the DataFrame information in a CSV file
        csv_filename = "output/cell_response_summary.csv"
        cell_subjects_by_response_df .to_csv(csv_filename, index=False)

    def subjects_by_sex(self):
        """
        Compute number of subjects in each gender.

        Output:
            A CSV file 'cell_subjects_by_gender.csv' containing the following columns:
            - gender: the gender of the subject
            - subject_count: number of subjects in each gender
        """

        # Write a query to find how many melanoma patients were male/female
        query = """
                    SELECT
                        su.sex,
                        COUNT(sa.subject)
                    FROM subjects AS su
                    JOIN samples AS sa ON sa.subject = su.subject
                    WHERE sa.condition = "melanoma"
                      AND sa.treatment = "miraclib"
                      AND sa.sample_type = "PBMC"
                      AND sa.time_from_treatment_start = 0
                     GROUP BY su.sex
                """

        # Execute the query
        self.loader.cursor.execute(query)

        # Fetch the rows from the database
        rows = self.loader.cursor.fetchall()

        # Create a DataFrame based on the information in the database
        cell_subjects_by_gender_df = pd.DataFrame(rows, columns=['gender', 'subject_count'])

        # Save the DataFrame information in a CSV file
        csv_filename = "output/cell_gender_summary.csv"
        cell_subjects_by_gender_df.to_csv(csv_filename, index=False)

def main():
    # Create an instance of CellSubsetAnalysis
    analyzer = CellSubsetAnalysis()

    # Compute the number of relevant samples in each project
    analyzer.samples_per_project()

    # Compute the number of subjects in the yes/no response
    analyzer.subjects_by_response()

    # Compute the number of subjects in M/F
    analyzer.subjects_by_sex()

if __name__ == "__main__":
    main()
