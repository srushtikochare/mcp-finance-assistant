import sqlite3
import pandas as pd

conn = sqlite3.connect("expenses.db")

# Create the table
conn.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT
)
""")

# Load your existing CSV data into it (only if the table is empty)
existing_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
if existing_count == 0:
    df = pd.read_csv("expenses.csv")
    df.to_sql("expenses", conn, if_exists="append", index=False)
    print(f"Migrated {len(df)} rows from expenses.csv into expenses.db")
else:
    print(f"Database already has {existing_count} rows — skipping migration")

conn.commit()
conn.close()