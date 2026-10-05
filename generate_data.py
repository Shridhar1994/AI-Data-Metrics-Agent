import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)
os.makedirs("./data", exist_ok=True)

# ── 1. Sales data → SQLite database ───────────────────────────
dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
sales_df = pd.DataFrame({
    "date": dates,
    "region": np.random.choice(["North", "South", "East", "West"], len(dates)),
    "product": np.random.choice(["Widget A", "Widget B", "Widget C", "Premium X"], len(dates)),
    "revenue": np.round(np.random.uniform(500, 15000, len(dates)), 2),
    "units_sold": np.random.randint(10, 500, len(dates)),
    "cost": np.round(np.random.uniform(200, 8000, len(dates)), 2),
})
sales_df["profit"] = sales_df["revenue"] - sales_df["cost"]
sales_df["quarter"] = sales_df["date"].dt.to_period("Q").astype(str)
sales_df["month"] = sales_df["date"].dt.to_period("M").astype(str)

conn = sqlite3.connect("./data/sales.db")
sales_df.to_sql("sales", conn, if_exists="replace", index=False)
conn.close()
print(f"✅ SQLite: ./data/sales.db — {len(sales_df)} rows")

# ── 2. Employee data → Excel file ─────────────────────────────
departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
emp_df = pd.DataFrame({
    "employee_id": range(1, 201),
    "name": [f"Employee_{i}" for i in range(1, 201)],
    "department": np.random.choice(departments, 200),
    "salary": np.round(np.random.uniform(45000, 180000, 200), 2),
    "hire_date": pd.date_range("2018-01-01", periods=200, freq="11D"),
    "performance_score": np.random.choice(["Exceeds", "Meets", "Below"], 200, p=[0.25, 0.55, 0.20]),
})
emp_df.to_excel("./data/employees.xlsx", index=False)
print(f"✅ Excel : ./data/employees.xlsx — {len(emp_df)} rows")

# ── 3. Website analytics → CSV file ───────────────────────────
web_dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
web_df = pd.DataFrame({
    "date": web_dates,
    "page_views": np.random.randint(1000, 50000, len(web_dates)),
    "unique_visitors": np.random.randint(500, 20000, len(web_dates)),
    "bounce_rate": np.round(np.random.uniform(0.20, 0.75, len(web_dates)), 3),
    "avg_session_duration_sec": np.random.randint(30, 600, len(web_dates)),
    "conversions": np.random.randint(5, 500, len(web_dates)),
    "channel": np.random.choice(["Organic", "Paid", "Social", "Email", "Direct"], len(web_dates)),
})
web_df.to_csv("./data/web_analytics.csv", index=False)
print(f"✅ CSV   : ./data/web_analytics.csv — {len(web_df)} rows")

print("\n📂 Sample data created in ./data/")
