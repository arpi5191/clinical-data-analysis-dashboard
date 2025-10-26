from db import CellDataLoader
import pandas as pd

class CellDataInserter:

    def __init__(self, file_name="cell_counts.csv", db_path="cell_data.db"):
        self.data = pd.read_csv(file_name)
        self.loader = CellDataLoader(db_path)

    def insert_projects(self):
        self.loader.cursor.execute("DELETE FROM projects")
        self.loader.cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
        self.loader.conn.commit()

        unique_projects = self.data["project"].unique()
        for prj in unique_projects:
            self.loader.cursor.execute(
                "INSERT INTO projects (project) VALUES (?)", (prj,)
            )
        self.loader.conn.commit()

    def insert_subjects(self):
        self.loader.cursor.execute("DELETE FROM subjects")
        self.loader.conn.commit()

        subjects_df = self.data[['subject', 'age', 'sex']]
        unique_subjects = subjects_df.drop_duplicates(subset=['subject'])

        for _, row in unique_subjects.iterrows():
            self.loader.cursor.execute(
                "INSERT INTO subjects (subject, age, sex) VALUES (?, ?, ?)", (row['subject'], row['age'], row['sex'])
            )
        self.loader.conn.commit()

    def insert_samples(self):
        self.loader.cursor.execute("DELETE FROM samples")
        self.loader.conn.commit()

        samples_df = self.data[['sample', 'sample_type', 'subject', 'project', 'time_from_treatment_start',
                                'treatment', 'condition', 'response']]

        for _, row in samples_df.iterrows():
            self.loader.cursor.execute(
                "SELECT project_id FROM projects WHERE project = ?", (row['project'],)
            )
            project_id = self.loader.cursor.fetchone()

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

        self.loader.conn.commit()

    def insert_cell_types(self):
        self.loader.cursor.execute("DELETE FROM cell_counts")
        self.loader.cursor.execute("DELETE FROM sqlite_sequence WHERE name='cell_counts'")
        self.loader.conn.commit()

        cell_types = [col for col in self.data.columns if col not in ['sample', 'sample_type', 'subject', 'project',
                                                                      'age', 'sex', 'treatment', 'condition',
                                                                      'response', 'time_from_treatment_start']]
        cell_df = self.data.melt(id_vars=['sample'], value_vars = cell_types,
                                 var_name = 'cell_type', value_name = 'count'
        )

        for _, row in cell_df.iterrows():
            self.loader.cursor.execute(
                "INSERT INTO cell_counts (sample, cell_type, count) VALUES (?, ?, ?)",
                (row['sample'], row['cell_type'], row['count'])
            )
        self.loader.conn.commit()

    def close(self):
        self.loader.close()

def main():
    inserter = CellDataInserter()
    inserter.insert_projects()
    inserter.insert_subjects()
    inserter.insert_samples()
    inserter.insert_cell_types()
    inserter.close()

if __name__ == "__main__":
    main()
