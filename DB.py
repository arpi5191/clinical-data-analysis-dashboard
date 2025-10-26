import sqlite3

class CellDataLoader:

    def __init__(self, db_path="cell_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_projects_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL UNIQUE
        )
        """)

    def create_subjects_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject TEXT PRIMARY KEY,
            age INTEGER,
            sex TEXT
        )
        """)

    def create_samples_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            sample TEXT PRIMARY KEY,
            sample_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            time_from_treatment_start REAL NOT NULL,
            treatment TEXT NOT NULL,
            condition TEXT NOT NULL,
            response TEXT NOT NULL,
            FOREIGN KEY (subject) REFERENCES subjects(subject),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """)

    def create_cell_counts_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cell_counts (
            cell_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample TEXT NOT NULL,
            cell_type TEXT NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY (sample) REFERENCES samples(sample),
            UNIQUE(sample, cell_type)
        )
        """)

    def close(self):
        self.conn.commit()
        self.conn.close()

def main():
    loader = CellDataLoader()
    loader.create_projects_table()
    loader.create_subjects_table()
    loader.create_samples_table()
    loader.create_cell_counts_table()
    loader.close()

if __name__ == "__main__":
    main()
