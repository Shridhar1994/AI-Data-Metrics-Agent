"""
AI Data Metrics Agent - Streamlit Cloud Edition

Architecture:
    Streamlit UI
        -> Query router
        -> SQL / Excel / CSV data tool
        -> Pandas / SQLite computation
        -> Optional OpenAI explanation
        -> Plotly visualization

The app works without Ollama. If OPENAI_API_KEY is configured in Streamlit
Secrets, the app uses the configured OpenAI model for natural-language
explanations. Without a key, it runs in Demo Mode so the deployment remains
usable for demonstrations.
"""

from pathlib import Path
import os
import sqlite3
import re

import pandas as pd
import plotly.express as px
import streamlit as st

from generate_data import generate_all


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "sales.db"
EMPLOYEES_PATH = DATA_DIR / "employees.xlsx"
WEB_PATH = DATA_DIR / "web_analytics.csv"

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Data Metrics Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Metrics Agent")
st.caption(
    "Natural-language analytics across SQL, Excel, and CSV — "
    "built with Streamlit, Pandas, SQLite, Plotly, and an optional cloud LLM."
)


# ---------------------------------------------------------
# Data preparation
# ---------------------------------------------------------
@st.cache_resource
def ensure_demo_data():
    required = [DB_PATH, EMPLOYEES_PATH, WEB_PATH]
    if not all(path.exists() for path in required):
        generate_all()
    return True


ensure_demo_data()


@st.cache_data
def load_employees():
    return pd.read_excel(EMPLOYEES_PATH)


@st.cache_data
def load_web_analytics():
    return pd.read_csv(WEB_PATH)


# ---------------------------------------------------------
# Optional cloud LLM
# ---------------------------------------------------------
def get_openai_key():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        return key

    try:
        key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
    except Exception:
        key = ""

    return key


def ai_explanation(question: str, source: str, result_df: pd.DataFrame) -> str:
    """Generate a short explanation with OpenAI when a key is configured."""
    api_key = get_openai_key()

    if not api_key:
        return demo_explanation(question, source, result_df)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        table_text = result_df.head(30).to_string(index=False)

        response = client.responses.create(
            model=MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are the explanation component of an analytics agent. "
                        "Explain the computed result clearly and briefly. "
                        "Never invent values. Use only the supplied result table. "
                        "Mention the selected data source."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Data source: {source}\n"
                        f"Computed result:\n{table_text}\n\n"
                        "Give a concise business-friendly explanation."
                    ),
                },
            ],
        )

        return response.output_text.strip()

    except Exception as exc:
        st.warning(
            "OpenAI explanation was unavailable, so the app used its built-in "
            "explanation instead."
        )
        return demo_explanation(question, source, result_df)


def demo_explanation(question: str, source: str, result_df: pd.DataFrame) -> str:
    if result_df.empty:
        return f"No matching records were found in the {source} data source."

    return (
        f"The query was routed to the {source} data source. "
        f"The result contains {len(result_df):,} row(s). "
        "The table and visualization below show the computed metric."
    )


# ---------------------------------------------------------
# Query routing
# ---------------------------------------------------------
def route_query(question: str) -> str:
    q = question.lower()

    if any(
        word in q
        for word in [
            "salary",
            "employee",
            "employees",
            "department",
            "performance",
        ]
    ):
        return "Excel"

    if any(
        word in q
        for word in [
            "conversion",
            "conversions",
            "bounce",
            "bounce rate",
            "channel",
            "website",
            "web analytics",
            "visits",
        ]
    ):
        return "CSV"

    if any(
        word in q
        for word in [
            "revenue",
            "sales",
            "region",
            "product",
            "monthly",
            "yearly",
        ]
    ):
        return "SQL"

    return "Unknown"


# ---------------------------------------------------------
# Data tools
# ---------------------------------------------------------
def sql_query(question: str):
    q = question.lower()

    with sqlite3.connect(DB_PATH) as conn:
        if "region" in q and "revenue" in q:
            query = """
                SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
                FROM sales
                GROUP BY region
                ORDER BY total_revenue DESC
            """
            return pd.read_sql_query(query, conn), "SQL"

        if "monthly" in q and "revenue" in q:
            query = """
                SELECT
                    substr(date, 1, 7) AS month,
                    ROUND(SUM(revenue), 2) AS total_revenue
                FROM sales
                WHERE date >= '2025-01-01' AND date <= '2025-12-31'
                GROUP BY substr(date, 1, 7)
                ORDER BY month
            """
            return pd.read_sql_query(query, conn), "SQL"

        if "revenue" in q:
            query = """
                SELECT ROUND(SUM(revenue), 2) AS total_revenue
                FROM sales
            """
            return pd.read_sql_query(query, conn), "SQL"

    return pd.DataFrame(), "SQL"


def excel_query(question: str):
    df = load_employees()
    q = question.lower()

    if "average" in q and "salary" in q and "department" in q:
        result = (
            df.groupby("department", as_index=False)["salary"]
            .mean()
            .rename(columns={"salary": "average_salary"})
        )
        result["average_salary"] = result["average_salary"].round(2)
        return result.sort_values("average_salary", ascending=False), "Excel"

    if "exceeds" in q:
        count = int((df["performance"].str.lower() == "exceeds").sum())
        return pd.DataFrame({"performance": ["Exceeds"], "employee_count": [count]}), "Excel"

    if "salary" in q:
        return (
            pd.DataFrame({"average_salary": [round(float(df["salary"].mean()), 2)]}),
            "Excel",
        )

    return pd.DataFrame(), "Excel"


def csv_query(question: str):
    df = load_web_analytics()
    q = question.lower()

    if "conversion" in q and "channel" in q:
        result = (
            df.groupby("channel", as_index=False)["conversions"]
            .sum()
            .sort_values("conversions", ascending=False)
        )
        return result, "CSV"

    if "bounce" in q and "channel" in q:
        result = (
            df.groupby("channel", as_index=False)["bounce_rate"]
            .mean()
            .rename(columns={"bounce_rate": "average_bounce_rate"})
            .sort_values("average_bounce_rate")
        )
        result["average_bounce_rate"] = result["average_bounce_rate"].round(2)
        return result, "CSV"

    if "conversion" in q:
        return (
            pd.DataFrame({"total_conversions": [int(df["conversions"].sum())]}),
            "CSV",
        )

    return pd.DataFrame(), "CSV"


# ---------------------------------------------------------
# Visualization
# ---------------------------------------------------------
def render_chart(result: pd.DataFrame, question: str):
    if result.empty or len(result.columns) < 2:
        return

    q = question.lower()
    cols = result.columns.tolist()
    x = cols[0]
    y = cols[1]

    if "monthly" in q or "trend" in q:
        fig = px.line(result, x=x, y=y, markers=True, title="Metric Trend")
    elif len(result) <= 10:
        fig = px.bar(result, x=x, y=y, title="Metric by Category")
    else:
        fig = px.line(result, x=x, y=y, title="Metric")

    fig.update_layout(
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.header("Data Sources")
    st.success("SQL — sales.db")
    st.success("Excel — employees.xlsx")
    st.success("CSV — web_analytics.csv")

    if get_openai_key():
        st.success(f"Cloud AI enabled: {MODEL}")
    else:
        st.info("Demo Mode: no OpenAI API key configured.")

    st.markdown("---")
    st.subheader("Try these questions")
    examples = [
        "What is the total revenue by region?",
        "What is the average salary by department?",
        "What are the total conversions by channel?",
        "Show me monthly revenue trends for 2025",
        "How many employees have 'Exceeds' performance?",
        "What is the average bounce rate by channel?",
    ]

    for example in examples:
        st.caption("• " + example)


# ---------------------------------------------------------
# Chat session
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("result") is not None:
            st.dataframe(message["result"], use_container_width=True)
            if message.get("show_chart"):
                render_chart(message["result"], message["question"])


question = st.chat_input("Ask a question about revenue, employees, or web analytics...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            source = route_query(question)

            if source == "SQL":
                result, source = sql_query(question)
            elif source == "Excel":
                result, source = excel_query(question)
            elif source == "CSV":
                result, source = csv_query(question)
            else:
                result = pd.DataFrame()

            if result.empty:
                answer = (
                    "I couldn't confidently map that question to one of the "
                    "available datasets.\n\n"
                    "Try a revenue, employee/salary, or conversion/bounce-rate "
                    "question from the examples in the sidebar."
                )
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                explanation = ai_explanation(question, source, result)
                answer = f"**Source selected:** `{source}`\n\n{explanation}"
                st.markdown(answer)
                st.dataframe(result, use_container_width=True)
                render_chart(result, question)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "result": result,
                        "question": question,
                        "show_chart": True,
                    }
                )
