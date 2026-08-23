import sqlite3
import os

TEST_DB = "test_expenses.db"

if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

conn = sqlite3.connect(TEST_DB)
conn.execute("""
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT
)
""")

# Known, fixed test data — so we know exactly what the correct answers should be
test_data = [
    ("2026-08-01", "food", 100, "Test lunch"),
    ("2026-08-05", "food", 200, "Test groceries"),
    ("2026-07-15", "food", 50, "Test July food"),
    ("2026-08-10", "transport", 75, "Test cab"),
]
conn.executemany(
    "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
    test_data,
)
conn.commit()
conn.close()
print("Test database created with known data.")