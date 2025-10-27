import sqlite3

conn = sqlite3.connect("cell_data.db")
cursor = conn.cursor()

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
cursor.execute(query)

rows = cursor.fetchall()

for row in rows:
    print(row)
