import sqlite3

conn = sqlite3.connect("expenses.db")
conn.execute("UPDATE expenses SET category = 'transport' WHERE category = 'transportation'")
conn.commit()
print("Merged transportation into transport")

# Show the updated breakdown
results = conn.execute("SELECT category, COUNT(*) FROM expenses GROUP BY category").fetchall()
for category, count in results:
    print(f"{category}: {count}")

conn.close()