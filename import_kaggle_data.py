import sqlite3
import pandas as pd

df = pd.read_csv("kaggle_expenses.csv")

# Keep only actual expenses (not income entries)
df = df[df["Income/Expense"] == "Expense"]

# Convert the date into YYYY-MM-DD format
df["date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%Y-%m-%d")

# Standardize category names to lowercase, matching your existing style
df["category"] = df["Category"].str.lower().str.strip()

# Build the final table matching your schema
clean_df = pd.DataFrame({
    "date": df["date"],
    "category": df["category"],
    "amount": df["Amount"],
    "description": df["Note"].fillna(""),
})

# Drop any rows with missing critical data
clean_df = clean_df.dropna(subset=["date", "category", "amount"])

conn = sqlite3.connect("expenses.db")
clean_df.to_sql("expenses", conn, if_exists="append", index=False)
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
print(f"Imported {len(clean_df)} real expense records from Kaggle dataset.")
print(f"Total expenses in database now: {total}")

# Show what categories we actually have now
categories = conn.execute("SELECT DISTINCT category FROM expenses").fetchall()
print(f"Categories in database: {[c[0] for c in categories]}")

conn.close()