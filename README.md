# AI Data Metrics Agent

Natural-language data analytics prototype based on the uploaded `ai_data_metrics_agent (1)(1).ipynb`. It uses local Ollama/Llama 3.1 to route a plain-English question to SQLite, Excel, or CSV, execute the analysis, explain the result, and optionally create a Plotly chart.

## Architecture

Streamlit UI → Ollama/Llama 3.1 → JSON routing plan → SQL / Excel / CSV tool → Pandas DataFrame → LLM explanation → Plotly chart

## Project structure

```text
AI-Data-Metrics-Agent/
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
└── data/
    ├── sales.db
    ├── employees.xlsx
    └── web_analytics.csv
```

## 1. Create/activate the environment

```cmd
call C:\Users\Admin\anaconda3\Scripts\activate.bat
python --version
where python
```

## 2. Install packages

```cmd
python -m pip install -r requirements.txt
```

## 3. Install and verify Ollama

```cmd
ollama list
ollama pull llama3.1
ollama run llama3.1
```

At the Ollama prompt, test it, then type `/bye`. If `ollama serve` says port 11434 is already in use, Ollama is probably already running; do not start a second server.

## 4. Generate demo data

From the repository root:

```cmd
python generate_data.py
```

This creates:
- `data/sales.db` — SQLite sales data
- `data/employees.xlsx` — employee data
- `data/web_analytics.csv` — website analytics data

## 5. Run Streamlit locally

```cmd
python -m streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, normally `http://localhost:8501`.

## 6. Demo questions

SQL:
- What is the total revenue by region?

Excel:
- What is the average salary by department?

CSV:
- What are the total conversions by channel?

Additional examples from the project:
- Show me monthly revenue trends for 2025
- How many employees have 'Exceeds' performance?
- What is the average bounce rate by channel?

## 7. GitHub

Create a new empty repository on GitHub, then from this folder:

```cmd
git init
git add .
git commit -m "Initial AI Data Metrics Agent"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/AI-Data-Metrics-Agent.git
git push -u origin main
```

Do not commit API keys or secrets.

## Important deployment note

The uploaded project is designed for a **local Ollama server** at `http://localhost:11434`. A Streamlit app hosted in the cloud cannot reach Ollama running on your personal Windows machine through localhost. For a public Streamlit deployment, replace the local LLM connection with a cloud-accessible model/API or a securely reachable hosted inference endpoint.

## Interview explanation

The agent receives a natural-language question, builds schema context for the available sources, asks the LLM for a structured JSON routing plan, executes the selected SQL/Pandas operation, sends the result back to the LLM for a concise explanation, and generates a Plotly visualization when appropriate. The current implementation is a local prototype; production improvements include safe query execution, structured-output validation, multi-source orchestration, persistent conversation state, authentication, and monitoring.
