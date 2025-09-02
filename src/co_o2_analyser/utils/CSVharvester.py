import sqlite3
import csv

DB_FILE = "data.sqlite"
O2_TAG_ID = 705
CO_TAG_ID = 398
CSV_OUTPUT = "concentrations_last_30min.csv"

# Connect to the database
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# SQL query to fetch O2 and CO values from last 30 minutes, matched by DateTime
query = f"""
SELECT O2.DateTime as DataTime, O2.Value as O2_CONC, CO.Value as CO_CONC
FROM TagValues O2
JOIN TagValues CO ON O2.DateTime = CO.DateTime
WHERE O2.TagName_id = {O2_TAG_ID}
  AND CO.TagName_id = {CO_TAG_ID}
  AND O2.DateTime >= datetime('now', '-30 minutes')
ORDER BY O2.DateTime DESC;
"""

cur.execute(query)
rows = cur.fetchall()

# Close the database connection
conn.close()

# Write the data to a CSV file
# CSV columns: DataTime, O2_CONC, CO_CONC
with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(["DataTime", "O2_CONC", "CO_CONC"])
    # Write each row
    for row in rows:
        # row is (DataTime, O2_CONC, CO_CONC)
        writer.writerow(row)

print(f"Data successfully written to {CSV_OUTPUT}.")
