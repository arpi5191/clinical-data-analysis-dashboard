import sqlite3

conn = sqlite3.connect("cell_data.db")
cursor = conn.cursor()

# Table 1: Projects
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL UNIQUE
)
""")

# # Table 2: Subjects
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS subjects (
#     subject TEXT PRIMARY KEY,
#     age INTEGER,
#     sex TEXT
# )
# """)
#
# # Table 3: Samples
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS samples (
#     sample TEXT PRIMARY KEY,
#     sample_type TEXT NOT NULL,
#     subject TEXT NOT NULL,
#     project_id INTEGER NOT NULL,
#     time_from_treatment_start REAL NOT NULL,
#     treatment TEXT NOT NULL,
#     condition TEXT NOT NULL,
#     response TEXT NOT NULL,
#     FOREIGN KEY (subject) REFERENCES subjects(subject),
#     FOREIGN KEY (project_id) REFERENCES projects(project_id)
# )
# """)
#
# # Table 4: Cell Counts
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS cell_counts (
#     cell_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     sample TEXT NOT NULL,
#     cell_type TEXT NOT NULL,
#     count INTEGER NOT NULL,
#     FOREIGN KEY (sample) REFERENCES samples(sample),
#     UNIQUE(sample, cell_type)
# )
# """)

conn.commit()
conn.close()
