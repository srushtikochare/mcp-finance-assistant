import pandas as pd

df = pd.read_csv("expenses.csv")

def get_total_by_category(category, month=None):
    filtered = df[df["category"] == category]
    if month:
        filtered = filtered[filtered["date"].str.startswith(month)]
    return filtered["amount"].sum()

def compare_months(month1, month2):
    total1 = df[df["date"].str.startswith(month1)]["amount"].sum()
    total2 = df[df["date"].str.startswith(month2)]["amount"].sum()
    return {"month1": month1, "total1": total1, "month2": month2, "total2": total2}

def get_recent_expenses(count=5):
    return df.sort_values("date", ascending=False).head(count)

# Test all three functions
print("Food total:", get_total_by_category("food"))
print("Food total in August 2026:", get_total_by_category("food", "2026-08"))
print("\nRecent expenses:")
print(get_recent_expenses(3))