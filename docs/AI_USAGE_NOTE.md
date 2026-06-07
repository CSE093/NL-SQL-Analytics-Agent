# AI Usage Note: AnalyticsGPT Development

This document outlines the usage of Artificial Intelligence during the design, coding, testing, and documentation phases of building AnalyticsGPT.

## 1. Architectural Planning & Requirements Structuring
AI was utilized to translate the high-level business objectives of natural language querying into a robust modular Python architecture:
- Designed the file layout and separated concerns between services (SQLite connection manager, file uploader), tools (SQL validator, Chart builder), and the agent routing graph.
- Defined state variables needed for a clean LangGraph loop.

## 2. Prompt Engineering Strategies
Three main prompt patterns were developed and optimized:
- **SQL Generation Prompt**: System instructions forcing output only as valid SQLite SELECT queries. Used in-context schemas with columns and primary keys dynamically extracted.
- **SQL Refiner Prompt**: Error-correcting loop prompt that feeds back the syntax/operational exception details to allow self-correction up to 3 times.
- **Business Explanation Prompt**: Zero-shot prompt styling the SQL output and Markdown data snippet into simple, readable executive summaries.

## 3. Code Quality & Standards
AI generated complete files following guidelines:
- Strictly adhered to type hinting (`typing` module types).
- Avoided `TODO` placeholders by writing end-to-end SQLite driver URI mode connections, Pandas type detection, and custom Plotly chart engines.
- Utilized comments and structured PEP8 formatting for maintenance readability.

## 4. Testing & Security
AI assisted in defining rigorous safety controls:
- **sqlparse Token Walker**: Guided development of recursive parse tree token matching to prevent command injection at the application level.
- **Double-Layer SQLite Protection**: Verified security by asserting that the SQLite C extension driver rejects inserts when connections are opened in read-only mode (`?mode=ro`).
- **Mock Tests**: Structured `pytest` mocks to test graph states and retry loops without coupling tests to local Ollama endpoints.
