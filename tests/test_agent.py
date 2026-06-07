import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from agent.controller import run_agent
from services.upload_service import process_and_import_file
from database.db_manager import init_db, reset_db, get_engine

@pytest.fixture(scope="module", autouse=True)
def setup_test_db(tmp_path_factory):
    """Setup a sample test database for agent execution."""
    reset_db()
    init_db()
    
    # Ingest a mock table: customers
    csv_file = tmp_path_factory.mktemp("agent_data") / "customers.csv"
    df = pd.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"],
        "city": ["New York", "Chicago"]
    })
    df.to_csv(csv_file, index=False)
    process_and_import_file(str(csv_file))
    
    yield
    reset_db()

@patch("agent.workflow.generate_completion")
@patch("tools.explanation_tool.generate_completion")
def test_successful_agent_flow(mock_explain, mock_gen):
    """Tests that the agent discovers schema, generates correct SQL, and explains it."""
    # Mock SQL generation response
    mock_gen.return_value = "```sql\nSELECT * FROM customers WHERE city = 'New York';\n```"
    # Mock explanation response
    mock_explain.return_value = "This query retrieves all customers located in New York. The results show Alice."

    result = run_agent("Show customers in New York")
    
    assert result["success"] is True
    assert result["generated_sql"] == "SELECT * FROM customers WHERE city = 'New York';"
    assert result["retry_count"] == 0
    assert result["data"] is not None
    assert len(result["data"]) == 1
    assert result["explanation"] == "This query retrieves all customers located in New York. The results show Alice."

@patch("agent.workflow.generate_completion")
@patch("tools.explanation_tool.generate_completion")
def test_agent_self_correction_loop(mock_explain, mock_gen):
    """
    Tests the self-correction loop where LLM generates bad SQL first,
    re-tries based on execution error, and succeeds on the second attempt.
    """
    # First call returns bad SQL (syntax error: double WHERE)
    # Second call returns corrected SQL
    mock_gen.side_effect = [
        "```sql\nSELECT * FROM customers WHERE WHERE name = 'Alice';\n```",
        "```sql\nSELECT * FROM customers WHERE name = 'Alice';\n```"
    ]
    mock_explain.return_value = "This explains the customer record for Alice."
    
    result = run_agent("Find customer named Alice")
    
    # Assert it retried and succeeded on 2nd attempt (retry_count = 1)
    assert result["success"] is True
    assert result["generated_sql"] == "SELECT * FROM customers WHERE name = 'Alice';"
    assert result["retry_count"] == 1
    assert len(result["errors"]) == 1
    assert "syntax error" in result["errors"][0].lower() or "execution failure" in result["errors"][0].lower()
    assert result["data"] is not None
    assert len(result["data"]) == 1
