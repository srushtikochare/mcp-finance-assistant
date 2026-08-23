import sqlite3
import logging
import os
from mcp.server import MCPServer

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

mcp = MCPServer("finance-assistant")

DB_PATH = os.environ.get("FINANCE_DB_PATH", "expenses.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

@mcp.tool()
def get_total_by_category(category: str, month: str = None) -> str:
    """Get total amount spent in a category, optionally filtered by month (format: YYYY-MM)."""
    logging.info(f"get_total_by_category called with category={category}, month={month}")
    try:
        if not category or not category.strip():
            logging.warning("get_total_by_category rejected: empty category")
            return "Error: category cannot be empty."
        conn = get_connection()
        if month:
            query = "SELECT SUM(amount) FROM expenses WHERE category = ? AND date LIKE ?"
            result = conn.execute(query, (category, f"{month}%")).fetchone()
        else:
            query = "SELECT SUM(amount) FROM expenses WHERE category = ?"
            result = conn.execute(query, (category,)).fetchone()
        conn.close()
        total = result[0] if result[0] is not None else 0
        if total == 0:
            return f"No expenses found for category '{category}'" + (f" in {month}" if month else "") + "."
        return f"Total spent on {category}" + (f" in {month}" if month else "") + f": {total}"
    except sqlite3.Error as e:
        logging.error(f"Database error in get_total_by_category: {e}")
        return f"Database error while looking up category totals: {e}"
    except Exception as e:
        logging.error(f"Unexpected error in get_total_by_category: {e}")
        return f"Unexpected error in get_total_by_category: {e}"

@mcp.tool()
def compare_months(month1: str, month2: str) -> str:
    """Compare total spending between two months (format: YYYY-MM)."""
    logging.info(f"compare_months called with month1={month1}, month2={month2}")
    try:
        conn = get_connection()
        query = "SELECT SUM(amount) FROM expenses WHERE date LIKE ?"
        total1 = conn.execute(query, (f"{month1}%",)).fetchone()[0] or 0
        total2 = conn.execute(query, (f"{month2}%",)).fetchone()[0] or 0
        conn.close()
        return f"{month1}: {total1} | {month2}: {total2}"
    except sqlite3.Error as e:
        logging.error(f"Database error in compare_months: {e}")
        return f"Database error while comparing months: {e}"
    except Exception as e:
        logging.error(f"Unexpected error in compare_months: {e}")
        return f"Unexpected error in compare_months: {e}"

@mcp.tool()
def get_recent_expenses(count: int = 5) -> str:
    """Get the most recent N expenses."""
    logging.info(f"get_recent_expenses called with count={count}")
    try:
        if count <= 0:
            logging.warning("get_recent_expenses rejected: non-positive count")
            return "Error: count must be a positive number."
        conn = get_connection()
        query = "SELECT date, category, amount, description FROM expenses ORDER BY date DESC LIMIT ?"
        rows = conn.execute(query, (count,)).fetchall()
        conn.close()
        if not rows:
            return "No expenses found."
        lines = [f"{r[0]} | {r[1]} | {r[2]} | {r[3]}" for r in rows]
        return "\n".join(lines)
    except sqlite3.Error as e:
        logging.error(f"Database error in get_recent_expenses: {e}")
        return f"Database error while fetching recent expenses: {e}"
    except Exception as e:
        logging.error(f"Unexpected error in get_recent_expenses: {e}")
        return f"Unexpected error in get_recent_expenses: {e}"

@mcp.tool()
def add_expense(date: str, category: str, amount: float, description: str = "") -> str:
    """Add a new expense. Date format: YYYY-MM-DD."""
    logging.info(f"add_expense called with date={date}, category={category}, amount={amount}")
    try:
        if amount <= 0:
            logging.warning("add_expense rejected: non-positive amount")
            return "Error: amount must be greater than zero."
        if not category or not category.strip():
            logging.warning("add_expense rejected: empty category")
            return "Error: category cannot be empty."
        conn = get_connection()
        conn.execute(
            "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
            (date, category, amount, description),
        )
        conn.commit()
        conn.close()
        logging.info(f"Expense added successfully: {date} | {category} | {amount}")
        return f"Added expense: {date} | {category} | {amount} | {description}"
    except sqlite3.Error as e:
        logging.error(f"Database error in add_expense: {e}")
        return f"Database error while adding expense: {e}"
    except Exception as e:
        logging.error(f"Unexpected error in add_expense: {e}")
        return f"Unexpected error in add_expense: {e}"

@mcp.tool()
def get_existing_categories() -> str:
    """Get the list of categories already used in the expense database, to help with categorization."""
    logging.info("get_existing_categories called")
    try:
        conn = get_connection()
        categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM expenses").fetchall()]
        conn.close()
        return ", ".join(categories) if categories else "No categories yet."
    except Exception as e:
        logging.error(f"Error in get_existing_categories: {e}")
        return f"Error fetching categories: {e}"

@mcp.tool()
def forecast_next_month(category: str) -> str:
    """Forecast next month's spending for a category using linear regression on historical trends."""
    logging.info(f"forecast_next_month called with category={category}")
    try:
        conn = get_connection()
        query = """
            SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
            FROM expenses WHERE category = ?
            GROUP BY month ORDER BY month
        """
        rows = conn.execute(query, (category,)).fetchall()
        conn.close()

        if len(rows) < 2:
            return f"Not enough historical data to forecast '{category}' — need at least 2 months of history."

        from sklearn.linear_model import LinearRegression
        import numpy as np

        totals = [r[1] for r in rows]

        X = np.array(range(len(totals))).reshape(-1, 1)
        y = np.array(totals)

        model = LinearRegression()
        model.fit(X, y)

        next_index = np.array([[len(totals)]])
        forecast = model.predict(next_index)[0]
        forecast = max(0, forecast)

        trend = "increasing" if model.coef_[0] > 0 else "decreasing" if model.coef_[0] < 0 else "stable"

        return (
            f"Using linear regression on {len(totals)} months of history, "
            f"forecasted spending on {category} next month: {forecast:.2f} "
            f"(trend: {trend}, recent totals: {[round(t, 2) for t in totals[-3:]]})"
        )
    except Exception as e:
        logging.error(f"Error in forecast_next_month: {e}")
        return f"Error forecasting for {category}: {e}"

@mcp.tool()
def detect_anomaly(category: str) -> str:
    """Check if recent spending in a category is anomalous using an Isolation Forest model trained on historical data."""
    logging.info(f"detect_anomaly called with category={category}")
    try:
        conn = get_connection()
        query = """
            SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
            FROM expenses WHERE category = ?
            GROUP BY month ORDER BY month
        """
        rows = conn.execute(query, (category,)).fetchall()
        conn.close()

        if len(rows) < 3:
            return f"Not enough historical data to detect anomalies for '{category}'."

        from sklearn.ensemble import IsolationForest
        import numpy as np

        totals = [r[1] for r in rows]
        X = np.array(totals).reshape(-1, 1)

        # contamination='auto' lets the model decide a reasonable anomaly rate
        model = IsolationForest(contamination=0.2, random_state=42)
        model.fit(X)

        predictions = model.predict(X)  # -1 = anomaly, 1 = normal
        latest_prediction = predictions[-1]
        latest_value = totals[-1]
        avg_historical = sum(totals[:-1]) / len(totals[:-1])

        if latest_prediction == -1:
            pct = round(((latest_value / avg_historical) - 1) * 100) if avg_historical > 0 else 0
            direction = "higher" if latest_value > avg_historical else "lower"
            return (
                f"⚠️ Anomaly detected (Isolation Forest): {category} spending this month "
                f"({latest_value:.2f}) is unusual — {abs(pct)}% {direction} than your typical pattern "
                f"({avg_historical:.2f})."
            )
        else:
            return f"No anomaly detected for {category}. Latest: {latest_value:.2f}, historical average: {avg_historical:.2f}."
    except Exception as e:
        logging.error(f"Error in detect_anomaly: {e}")
        return f"Error detecting anomaly for {category}: {e}"

if __name__ == "__main__":
    mcp.run(transport="stdio")