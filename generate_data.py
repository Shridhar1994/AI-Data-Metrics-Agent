"""
Generate deterministic demo data for the AI Data Metrics Agent.

The app imports generate_all() automatically when the expected files are missing,
so Streamlit Community Cloud does not need pre-generated binary data files.
"""
from pathlib import Path
import sqlite3
import random
from datetime import date, timedelta

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def generate_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    random.seed(42)

    # -------------------------
    # 1. Sales -> SQLite
    # -------------------------
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    regions = ["North", "South", "East", "West"]
    products = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headset"]

    sales_rows = []
    for i, d in enumerate(dates):
        region = regions[i % len(regions)]
        product = products[i % len(products)]
        base = 7000 + (i % 17) * 650
        seasonality = 1800 if d.month in (10, 11, 12) else 0
        revenue = round(base + seasonality + random.uniform(-1200, 1800), 2)
        units = max(1, int(revenue / random.uniform(120, 260)))
        sales_rows.append(
            {
                "date": d.date().isoformat(),
                "region": region,
                "product": product,
                "revenue": revenue,
                "units": units,
            }
        )

    sales_df = pd.DataFrame(sales_rows)
    db_path = DATA_DIR / "sales.db"
    with sqlite3.connect(db_path) as conn:
        sales_df.to_sql("sales", conn, if_exists="replace", index=False)

    # -------------------------
    # 2. Employees -> Excel
    # -------------------------
    departments = ["Engineering", "Sales", "HR", "Finance", "Operations"]
    performances = ["Exceeds", "Meets", "Needs Improvement"]

    employee_rows = []
    for i in range(1, 201):
        dept = departments[(i - 1) % len(departments)]
        performance = performances[(i * 7) % len(performances)]
        salary = round(
            45000
            + departments.index(dept) * 5500
            + random.uniform(0, 28000),
            2,
        )
        employee_rows.append(
            {
                "employee_id": i,
                "employee_name": f"Employee {i:03d}",
                "department": dept,
                "salary": salary,
                "performance": performance,
            }
        )

    employees_df = pd.DataFrame(employee_rows)
    employees_df.to_excel(DATA_DIR / "employees.xlsx", index=False)

    # -------------------------
    # 3. Web analytics -> CSV
    # -------------------------
    channels = ["Organic", "Paid Search", "Social", "Email", "Referral"]
    start = date(2025, 1, 1)

    web_rows = []
    for i in range(365):
        d = start + timedelta(days=i)
        channel = channels[i % len(channels)]
        visits = 700 + (i % 21) * 55 + random.randint(0, 350)
        conversions = max(1, int(visits * random.uniform(0.025, 0.09)))
        bounce_rate = round(random.uniform(32, 72), 2)
        web_rows.append(
            {
                "date": d.isoformat(),
                "channel": channel,
                "visits": visits,
                "conversions": conversions,
                "bounce_rate": bounce_rate,
            }
        )

    web_df = pd.DataFrame(web_rows)
    web_df.to_csv(DATA_DIR / "web_analytics.csv", index=False)


if __name__ == "__main__":
    generate_all()
    print("Demo data generated in:", DATA_DIR)
