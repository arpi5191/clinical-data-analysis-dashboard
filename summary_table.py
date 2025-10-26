# from db import CellDataLoader
# from db import CellDataInserter

import sqlite3

# Part II

# Connect to the database
conn = sqlite3.connect("cell_data.db")
cursor = conn.cursor()

# # Execute the query
# cursor.execute("""
#     SELECT
#         c.sample,
#         SUM(c.count) OVER (PARTITION BY c.sample) AS total_count,
#         c.cell_type AS population,
#         c.count,
#         ROUND(100.0 * c.count / SUM(c.count) OVER (PARTITION BY c.sample),
#         2) AS percentage
#     FROM cell_counts AS c
#     ORDER BY c.sample, c.cell_type
#     LIMIT 10
# """)
# rows = cursor.fetchall()
#
# # Print all rows
# for row in rows:
#     print(row)

# PART III

cursor.execute("""
    SELECT
         c.cell_type,
         ROUND(100.0 * SUM(CASE WHEN sa.response = 'yes' THEN c.count ELSE 0 END) /
               SUM(SUM(CASE WHEN sa.response = 'yes' THEN c.count ELSE 0 END)) OVER (), 2) AS yes_percentage,
         ROUND(100.0 * SUM(CASE WHEN sa.response = 'no' THEN c.count ELSE 0 END) /
               SUM(SUM(CASE WHEN sa.response = 'no' THEN c.count ELSE 0 END)) OVER (), 2) AS no_percentage
    FROM cell_counts AS c
    JOIN samples AS sa ON sa.sample = c.sample
    WHERE sa.sample_type = 'PBMC'
      AND sa.treatment = 'miraclib'
      AND sa.condition = 'melanoma'
    GROUP BY c.cell_type
""")
rows = cursor.fetchall()

 # SUM(c.count) OVER (PARTITION BY c.sample) AS total_count,

# Print all rows
for row in rows:
    print(row)

# Close the connection
conn.close()
