import sqlite3

class CellDataLoader:
    """
    Create the main database tables for the project.

    This class creates the following tables:
        - projects
        - subjects
        - samples
        - cell_counts
    """

    def __init__(self, db_path="code/cell_data.db"):
        # Initalize the database connection and the cursor
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_projects_table(self):
        """
        Create the 'projects' table in the database to store project information.
        """

        # Drops the table if it already exists
        self.cursor.execute("DROP TABLE IF EXISTS projects")

        # Create the 'projects' table in the database
        self.cursor.execute("""
        CREATE TABLE projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL UNIQUE
        )
        """)

    def create_subjects_table(self):
        """
        Create the 'subjects' table in the database to store subject information.
        """

        # Drops the table if it already exists
        self.cursor.execute("DROP TABLE IF EXISTS subjects")

        # Create the 'subjects' table in the database
        self.cursor.execute("""
        CREATE TABLE subjects (
            subject TEXT PRIMARY KEY,
            age INTEGER,
            sex TEXT
        )
        """)

    def create_samples_table(self):
        """
        Create the 'samples' table in the database to store sample information.
        """

        # Drops the table if it already exists
        self.cursor.execute("DROP TABLE IF EXISTS samples")

        # Create the 'samples' table in the database
        self.cursor.execute("""
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            sample_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            time_from_treatment_start REAL NOT NULL,
            treatment TEXT NOT NULL,
            condition TEXT NOT NULL,
            response TEXT,
            FOREIGN KEY (subject) REFERENCES subjects(subject),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """)

    def create_cell_counts_table(self):
        """
        Create the 'cell_counts' table in the database to store cell_counts information.
        """

        # Drops the table if it already exists
        self.cursor.execute("DROP TABLE IF EXISTS cell_counts")

        # Create the 'cell_counts' table in the database
        self.cursor.execute("""
        CREATE TABLE cell_counts (
            cell_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample TEXT NOT NULL,
            cell_type TEXT NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY (sample) REFERENCES samples(sample),
            UNIQUE(sample, cell_type)
        )
        """)

    def close(self):
        # Commit the change and close the connection
        self.conn.commit()
        self.conn.close()

def main():
    # Create an instance of CellDataLoader
    loader = CellDataLoader()

    # Create all the tables to store in the database
    loader.create_projects_table()
    loader.create_subjects_table()
    loader.create_samples_table()
    loader.create_cell_counts_table()

    # Commit the change and close the database connection
    loader.close()

if __name__ == "__main__":
    main()
