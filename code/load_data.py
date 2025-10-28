from db import CellDataLoader
import pandas as pd

class CellDataInserter:
    """
    Load data into the main database tables for the project.
    """

    def __init__(self, file_name="input/cell_counts.csv", db_path="code/cell_data.db"):
        # Initialize the database connection and cursor, and load the CSV data
        self.data = pd.read_csv(file_name)
        self.loader = CellDataLoader(db_path)

    def insert_projects(self):
        """
        Insert project information from the CSV file into the 'projects' table in the database.
        """

        # Delete the 'projects' table if it already exists
        self.loader.cursor.execute("DELETE FROM projects")
        self.loader.cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
        self.loader.conn.commit()

        # Obtain all the unique projects
        unique_projects = self.data["project"].unique()

        # Load each project name into the 'projects' table
        for prj in unique_projects:
            self.loader.cursor.execute(
                "INSERT INTO projects (project) VALUES (?)", (prj,)
            )

        # Commit the change
        self.loader.conn.commit()

    def insert_subjects(self):
        """
        Insert subject information from the CSV file into the 'subjects' table in the database.
        """

        # Delete the 'subjects' table if it already exists
        self.loader.cursor.execute("DELETE FROM subjects")
        self.loader.conn.commit()

        # Obtain the preferred cols from the CSV file
        subjects_df = self.data[['subject', 'age', 'sex']]

        # Obtain all the unique subjects
        unique_subjects = subjects_df.drop_duplicates(subset=['subject'])

        # Load each row into the 'subjects' table
        for _, row in unique_subjects.iterrows():
            self.loader.cursor.execute(
                "INSERT INTO subjects (subject, age, sex) VALUES (?, ?, ?)", (row['subject'], row['age'], row['sex'])
            )

        # Commit the change
        self.loader.conn.commit()

    def insert_samples(self):
        """
        Insert samples information from the CSV file into the 'samples' table in the database.
        """

        # Delete the 'samples' table if it already exists
        self.loader.cursor.execute("DELETE FROM samples")
        self.loader.conn.commit()

        # Obtain the preferred cols from the CSV file
        samples_df = self.data[['sample', 'sample_type', 'subject', 'project', 'time_from_treatment_start',
                                'treatment', 'condition', 'response']]

        # Load each row into the 'samples' table
        for _, row in samples_df.iterrows():

            # Obtain the project id from the 'samples' table
            self.loader.cursor.execute(
                "SELECT project_id FROM projects WHERE project = ?", (row['project'],)
            )
            project_id = self.loader.cursor.fetchone()

            # Load the information into the 'samples' table
            self.loader.cursor.execute(
                """
                INSERT INTO samples (
                    sample,
                    sample_type,
                    subject,
                    project_id,
                    time_from_treatment_start,
                    treatment,
                    condition,
                    response
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row['sample'],
                    row['sample_type'],
                    row['subject'],
                    project_id[0],
                    row['time_from_treatment_start'],
                    row['treatment'],
                    row['condition'],
                    row['response']
                )
            )

        # Commit the change
        self.loader.conn.commit()

    def insert_cell_types(self):
        """
        Insert cell_types information from the CSV file into the 'cell_types' table in the database.
        """

        # Delete the 'cell_counts' table if it already exists
        self.loader.cursor.execute("DELETE FROM cell_counts")
        self.loader.cursor.execute("DELETE FROM sqlite_sequence WHERE name='cell_counts'")
        self.loader.conn.commit()

        # Obtain the preferred cols from the CSV file
        cell_types = [col for col in self.data.columns if col not in ['sample', 'sample_type', 'subject', 'project',
                                                                      'age', 'sex', 'treatment', 'condition',
                                                                      'response', 'time_from_treatment_start']]

        # Transform the data into a DataFrame containing the count of each cell type per sample
        cell_df = self.data.melt(id_vars=['sample'], value_vars = cell_types,
                                 var_name = 'cell_type', value_name = 'count'
        )

        # Load each row into the 'cell_counts' table
        for _, row in cell_df.iterrows():
            self.loader.cursor.execute(
                "INSERT INTO cell_counts (sample, cell_type, count) VALUES (?, ?, ?)",
                (row['sample'], row['cell_type'], row['count'])
            )

        # Commit the change
        self.loader.conn.commit()

    def close(self):
        # Close the connection
        self.loader.close()

def main():
    # Create an instance of CellDataInserter
    inserter = CellDataInserter()

    # Insert the information into all tables in the Database
    inserter.insert_projects()
    inserter.insert_subjects()
    inserter.insert_samples()
    inserter.insert_cell_types()

    # Close the database connection
    inserter.close()

if __name__ == "__main__":
    main()
