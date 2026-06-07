# System Architecture: AnalyticsGPT

This document details the module design, data flow, and security layers implemented in AnalyticsGPT.

## 1. System Module Relationships
The following block architecture illustrates how components are decoupled:

```mermaid
graph TD
    %% UI Layer
    subgraph UI_Layer [Streamlit UI]
        App[app.py]
        Sidebar[ui/sidebar.py]
        Dashboard[ui/dashboard.py]
        Comp[ui/components.py]
    end

    %% Agent Controller
    subgraph Agent_Layer [LangGraph Execution Agent]
        Ctrl[agent/controller.py]
        Graph[agent/graph.py]
        Workflow[agent/workflow.py]
        State[agent/state.py]
        Retry[agent/retry_logic.py]
    end

    %% Tools Layer
    subgraph Tools_Layer [Tool Integrations]
        SchemaTool[tools/schema_tool.py]
        ValTool[tools/validator.py]
        SqlTool[tools/sql_tool.py]
        ExpTool[tools/explanation_tool.py]
        ChartTool[tools/chart_tool.py]
    end

    %% Service Integrations
    subgraph Service_Layer [Platform Services]
        UploadSvc[services/upload_service.py]
        SqliteSvc[services/sqlite_service.py]
        HistSvc[services/history_service.py]
        LlmSvc[services/llm_service.py]
    end

    %% Storage Layer
    subgraph Storage_Layer [Storage & Models]
        DB[database/user_data.db]
        Models[models/models.py]
        Ollama[Ollama local LLM API]
    end

    %% Connections
    App --> Sidebar
    App --> Dashboard
    Sidebar --> UploadSvc
    Sidebar --> HistSvc
    Dashboard --> Ctrl
    Ctrl --> Graph
    Graph --> Workflow
    Workflow --> State
    Workflow --> Retry

    %% Node connections to tools
    Workflow --> SchemaTool
    Workflow --> ValTool
    Workflow --> SqlTool
    Workflow --> ExpTool
    Workflow --> ChartTool

    %% Tools to Services
    SchemaTool --> get_engine
    ValTool --> sqlparse
    SqlTool --> SqliteSvc
    ExpTool --> LlmSvc
    ChartTool --> Plotly

    %% Service to storage
    UploadSvc --> DB
    SqliteSvc --> DB
    HistSvc --> DB
    LlmSvc --> Ollama
```

---

## 2. Component Design Specifications

### User Interface (Streamlit)
The frontend utilizes a modular structure. `app.py` acts as the root orchestrator:
- **`sidebar.py`**: Manages the upload input files, registers new tables into the engine, displays tables' structural metadata columns, and displays past queries.
- **`dashboard.py`**: Reads prompt triggers, initializes the LangGraph stream, visualizes final chart figures, displays tables of the resulting datasets, and renders copy-friendly SQL commands.

### Agent Workflow (LangGraph)
Uses Python's `langgraph` framework to orchestrate query processing. States are managed inside an `AgentState` TypedDict:
- Linear execution flows from Schema discovery to SQL generation, validation, and database queries.
- Incorporates conditional routing hooks for self-healing error cycles. If a query syntax exception occurs, control flows back to SQL refinement.

### Security Layers (sqlparse & URI mode=ro)
We maintain a strict double-layer read-only constraint:
1. **Static AST Analysis**: The query string is processed by `sqlparse`, separating and removing comments. It verifies that only `SELECT` and `WITH` query types are present.
2. **SQLite Connection Constraint**: Database queries execute over a connection opened in read-only mode (`file:db?mode=ro`), preventing query-injection mutations directly at the SQLite driver layer.
