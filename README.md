# AnalyticsGPT: Natural Language to SQL Analytics Agent

AnalyticsGPT is a production-ready Business Intelligence agent built with Streamlit, LangGraph, and SQLite. It allows business managers and analysts to upload CSV or Excel datasets and query them using plain natural language questions.

The agent automatically discovers the database schema, constructs valid SQL queries, validates query safety to prevent modifications, executes them, visualizes data in Plotly charts, and writes plain-English summaries.

---

## Demo Video

https://youtu.be/s5QdFiCZPCc

---

## 🛠️ Architecture Overview

The system utilizes a multi-layered design separating frontend dashboard layouts, LangGraph workflow loops, database services, and safety tools:

```text
analytics-agent/
│
├── app.py
├── requirements.txt
├── .env.example
│
├── database/
│   └── db_manager.py
│
├── uploads/
│
├── agent/
│   ├── state.py
│   ├── prompts.py
│   ├── workflow.py
│   ├── graph.py
│   ├── controller.py
│   └── retry_logic.py
│
├── tools/
│   ├── schema_tool.py
│   ├── validator.py
│   ├── sql_tool.py
│   ├── chart_tool.py
│   └── explanation_tool.py
│
├── services/
│   ├── upload_service.py
│   ├── sqlite_service.py
│   ├── history_service.py
│   └── llm_service.py
│
├── ui/
│   ├── sidebar.py
│   ├── dashboard.py
│   └── components.py
│
└── tests/
```

---

## 🚀 Installation & Setup

### 1. Prerequisites (Ollama LLM)

1. Install Ollama.
2. Start Ollama.
3. Pull a model:

```bash
ollama pull llama3.1
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
DATABASE_PATH=database/user_data.db
LOG_LEVEL=INFO
```

---

## 🖥️ Running the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## ✨ Features

- Natural Language to SQL conversion
- CSV and Excel upload support
- Dynamic schema discovery
- SQLite database integration
- SQL safety validation
- Automatic chart generation
- Business insights and explanations
- CSV and Excel export
- Query history tracking
- Streamlit dashboard UI

---

## 🔮 Future Improvements

1. Multi-turn chat conversations
2. Schema relationship detection
3. Advanced CSV cleaning
4. User authentication
5. Cloud deployment

---

## 👥 Team Resumes

Create a folder named:

```text
resumes/
```

Add all team resumes as PDF files.

Example:

```text
resumes/
├── Mohana_Priya_Resume.pdf
├── Member2_Resume.pdf
├── Member3_Resume.pdf
```

---

## 📌 Tech Stack

- Python
- Streamlit
- LangGraph
- SQLite
- Pandas
- Plotly
- Ollama