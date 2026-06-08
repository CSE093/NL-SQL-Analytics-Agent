# AI Usage Note: NL to SQL Analytics Agent

This document describes how AI assisted in building the NL-to-SQL Analytics Agent, including prompt design, model behavior corrections, security decisions, and review checkpoints.

## What AI helped with

- Area: AI contribution
  - Project scaffolding: defined folder structure, module boundaries, and the agent loop design across `agent/controller.py`, `agent/graph.py`, `agent/workflow.py`, and `agent/state.py`.
  - Prompt engineering: created SQL generation and result explanation templates in `agent/prompts.py` and `tools/explanation_tool.py`.
  - Security layer: authored the SQL validator blocklist in `tools/validator.py` and enforced a read-only SQLite execution pattern in `services/sqlite_service.py`.
  - Streamlit UI layout: structured the dashboard and sidebar flows in `app.py`, `ui/components.py`, and `ui/sidebar.py` for question input, model status, and chat history.
  - Sample data: defined ingestion and CSV schema handling in `database/db_manager.py`, `services/upload_service.py`, and `sample_data/*.csv`.
  - Tests: designed the Pytest suite for validation and safety in `tests/test_validator.py`, `tests/test_sql.py`, `tests/test_agent.py`, and `tests/test_upload.py`.
  - Documentation: produced onboarding instructions in `README.md`, `docs/TEST_CASES.md`, and this file.

## Prompts used

### SQL generation (`agent/prompts.py`)

The SQL prompt includes:

- Full database schema context placeholder: `{schema}`
- User question placeholder: `{question}`
- Strict read-only rules: only `SELECT` and `WITH` queries, no `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `ATTACH`, `DETACH`, `PRAGMA`, or other mutating commands.
- Explicit output formatting: respond inside a ```sql ... ``` code block and do not add extra explanation outside the block.
- Error-flow path: if the query is impossible, return `ERROR: <reason>` instead of unsafe SQL.

System instructions in `agent/prompts.py`:

```
You are a SQLite expert database analyst.
Your task is to generate a valid SQLite SELECT query that answers the user's natural language question.
```

### Insight generation (`tools/explanation_tool.py`)

The explanation prompt includes:

- The original question, executed SQL, row count, column names, and a data sample.
- Business-friendly interpretation requirements: summarize the result, highlight key patterns, and keep the explanation concise.
- Result schema guidance: focus on actionable findings rather than raw technical details.

System instructions in `agent/prompts.py`:

```
You are an experienced business intelligence consultant and data analyst.
Respond with a concise business explanation for the executed SQL result.
```

### Agent loop design prompt (conceptual)

The project implements a 7-step pipeline across modules:

1. Discover schema context (`tools/schema_tool.py`)
2. Understand user question (`agent/workflow.py` / `agent/controller.py`)
3. Generate SQL (`agent/prompts.py`, `services/llm_service.py`)
4. Validate SQL (`tools/validator.py`)
5. Execute SQL (`tools/sql_tool.py`, `services/sqlite_service.py`)
6. Analyze result (`tools/explanation_tool.py`)
7. Recommend visualization (`tools/chart_tool.py`)

Each step maps to a dedicated layer, with SQL generation and refinement handled in `agent/workflow.py` and business explanation handled by `tools/explanation_tool.py`.

## AI mistakes and corrections

### 1. Markdown-wrapped SQL

Mistake: Llama output often came back wrapped in ```sql fences or with extra explanation.

Correction: added `extract_sql_from_response()` in `agent/workflow.py` and reinforced the prompt to require SQL inside a ```sql ``` block only.

### 2. Mutating SQL suggestions

Mistake: the model sometimes suggested `CREATE TEMP TABLE`, `ALTER TABLE`, or multiple statements.

Correction: `tools/validator.py` blocks banned keywords and enforces root statement checks for only `SELECT` or `WITH`. The app also runs queries through `services/sqlite_service.py` on a read-only SQLite URI to prevent writes.

### 3. Invalid explanation JSON / business summary issues

Mistake: earlier drafts produced overly technical or incomplete explanations.

Correction: the explanation prompt in `agent/prompts.py` was simplified to request human-readable business commentary only, and fallback messaging is used when the model cannot generate a valid explanation.

### 4. Wrong chart column names

Mistake: chart metadata sometimes referenced non-existent result columns.

Correction: the chart generation flow validates column names against actual DataFrame output in `tools/chart_tool.py` and uses the exact returned schema.

### 5. Ollama connection errors on Windows

Mistake: generic connection failures occurred when Ollama was not running or the host URL was wrong.

Correction: `services/llm_service.py` provides a clear health/error message and recommends starting Ollama locally with `ollama pull <model>`.

### 6. Cloud fallback awareness

Mistake: some early designs assumed generic OpenRouter/OpenAI fallbacks without a concrete project implementation.

Correction: the current repo uses Ollama as the primary LLM path and documents the local model requirement clearly. Future work may add explicit OpenRouter or cloud fallback support.

## Human review checklist

- SELECT-only enforcement implemented and tested in `tools/validator.py` and `tests/test_validator.py`.
- SQL generation examples match schema-aware sample queries in the README.
- Ollama local model path is implemented in `services/llm_service.py`.
- Agent loop nodes and retry handling are visible in `agent/workflow.py`.
- Read-only execution is enforced in `services/sqlite_service.py` and verified by `tests/test_sql.py`.
- Documentation and usage notes are updated in `README.md`, `docs/TEST_CASES.md`, and this file.

## Tools and models

- **Ollama** — local LLM for SQL generation and result explanation.
- **SQLite** — read-only query execution engine via `services/sqlite_service.py`.
- **Pandas** — query results are materialized into DataFrames for analysis and chart generation.
- **Streamlit** — UI layer in `app.py`.
- **Pytest** — test automation for validator, SQL execution, upload, and agent flow.

## Iteration notes

Future improvements identified during AI-assisted development:

1. SQL retry loop: feed validation or execution errors back to the LLM for correction.
2. Schema caching: avoid rebuilding the full schema string on every question.
3. Result caching: reuse repeated query results for faster responses.
4. Stronger SQL parsing: use deeper parser logic beyond regex and keyword matching.
5. Cloud fallback: add explicit OpenRouter/OpenAI support when local Ollama is unavailable.
