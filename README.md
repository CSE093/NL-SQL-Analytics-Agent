# AnalyticsGPT: Natural Language to SQL Analytics Agent

AnalyticsGPT is a production-ready Business Intelligence agent built with **Streamlit**, **LangGraph**, and **SQLite**. It allows business managers and analysts to upload CSV or Excel datasets and query them using plain natural language questions.

The agent automatically discovers the database schema, constructs valid SQL queries, validates query safety to prevent modifications, executes them, visualizes data in Plotly charts, and writes plain-English summaries.

---

## 🛠️ Architecture Overview

The system utilizes a multi-layered design separating frontend dashboard layouts, LangGraph workflow loops, database services, and safety tools:

```
analytics-agent/
│
├── app.py                  # Streamlit entry point
├── requirements.txt        # Package dependencies
├── .env.example            # Configuration template
│
├── database/
│   └── db_manager.py       # SQLAlchemy engine & session configurations
│
├── uploads/                # Saved copy of uploaded file raw bytes
│
├── agent/                  # LangGraph orchestrator
│   ├── state.py            # TypedDict state structure
│   ├── prompts.py          # Prompt templates registry
│   ├── workflow.py         # Graph node actions and edge routing
│   ├── graph.py            # Graph compilation
│   ├── controller.py       # Streaming workflow controller
│   └── retry_logic.py      # Retry evaluation counts
│
├── tools/                  # Analytical tools
│   ├── schema_tool.py      # Database schema discoverer (cached)
│   ├── validator.py        # sqlparse AST parser protection
│   ├── sql_tool.py         # SQL execution wrapper
│   ├── chart_tool.py       # Heuristic Plotly express chart builder
│   └── explanation_tool.py # Business explanation generator
│
├── services/               # Platform services
│   ├── upload_service.py   # File validation & Pandas database ingestion
│   ├── sqlite_service.py   # Read-only database executor (?mode=ro)
│   ├── history_service.py  # Session state history SQLite logger
│   └── llm_service.py      # Ollama HTTP REST interface
│
├── ui/                     # UI Layout segments
│   ├── sidebar.py          # Uploader, schema catalog & query recall
│   ├── dashboard.py        # Query inputs, status indicators & display card
│   └── components.py       # Metric cards & CSV/Excel download actions
│
└── tests/                  # Pytest verification suite
```

---

## 🚀 Installation & Setup

Follow these steps to run AnalyticsGPT locally.

### 1. Prerequisites (Ollama LLM)
AnalyticsGPT is configured to query local models via the Ollama REST API.
1. Download and install Ollama from [https://ollama.com](https://ollama.com).
2. Start the Ollama application.
3. Open a terminal and pull the default model (`llama3.1` or `mistral`):
   ```bash
   ollama pull llama3.1
   ```

### 2. Set Up Virtual Environment
Clone the repository, navigate to the folder, and create a virtual environment:
```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all package dependencies:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and verify the settings:
```bash
copy .env.example .env
```
Ensure your `.env` contains:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
DATABASE_PATH=database/user_data.db
LOG_LEVEL=INFO
```

---

## 🖥️ Running the Application

Start the Streamlit dashboard server:
```bash
streamlit run app.py
```
This will start the development server and automatically open the dashboard in your default browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

To run the full suite of automated unit tests:
```bash
pytest tests/
```

---

## ✨ Features Checklist
- [x] **Multi-File CSV & Excel Ingestion**: Automatically cleans columns and maps filenames to SQLite tables.
- [x] **Dynamic Schema Discovery**: Discovers tables, columns, and primary keys, feeding them as context to the LLM.
- [x] **Double-Layer Safety Validation**: Uses `sqlparse` AST validation alongside read-only connection limits (`?mode=ro`).
- [x] **Self-Healing agent**: Retries up to 3 times on SQL exceptions, forwarding the crash traceback back to LLM for auto-debugging.
- [x] **Business Interpretation summaries**: Generates natural summaries explaining query findings.
- [x] **Dynamic Visual charts**: Plots Plotly line, bar, pie, and scatter charts by analyzing returned data types.
- [x] **Result Exporting**: Provides download action buttons for both CSV and Excel formatting.
- [x] **Persistent Session History**: Logs past interactions into metadata tables for sidebar recall triggers.
- [x] **Premium Dark styling**: Incorporates typography (Inter/Outfit) and micro-interactions.

---

## 🔮 Future Improvements
1. **Multi-turn Chat conversations**: Support follow-up query contexts (e.g. "Now filter it by Chicago").
2. **Schema Relationship detection**: Use schema indexing or LLM entity mapping to infer foreign keys automatically and suggest joins.
3. **Advanced CSV Cleanups**: Auto-handle null fields, custom currency formats, and mixed datatypes on file ingestion.
