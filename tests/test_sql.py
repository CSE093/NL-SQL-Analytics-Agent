import sqlite3
import pytest
import pandas as pd
from services.sqlite_service import execute_query, get_readonly_connection
from services.upload_service import process_and_import_file
from database.db_manager import get_engine, init_db, reset_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db(tmp_path_factory):
    """Initializes the database and pre-populates dummy test tables."""
    reset_db()
    init_db()
    
    # Ingest a mock table for queries
    csv_file = tmp_path_factory.mktemp("data") / "sales.csv"
    df = pd.DataFrame({
        "item_id": [1, 2, 3],
        "item_name": ["Widget A", "Widget B", "Widget C"],
        "price": [10.5, 20.0, 5.25]
    })
    df.to_csv(csv_file, index=False)
    process_and_import_file(str(csv_file))
    
    yield
    reset_db()

def test_execute_readonly_select():
    # Execute valid SELECT query
    df, exec_time = execute_query("SELECT * FROM sales")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "item_name" in df.columns
    assert exec_time > 0.0

def test_sqlite_driver_enforces_readonly():
    # Attempting to run a modifying query on the readonly driver connection should raise a database error
    conn = get_readonly_connection()
    cursor = conn.cursor()
    
    # Try inserting via the read-only connection
    with pytest.raises(sqlite3.OperationalError) as exc_info:
        cursor.execute("INSERT INTO sales (item_id, item_name, price) VALUES (4, 'Widget D', 15.0)")
    
    # SQLite error when DB is opened in read-only mode
    assert "attempt to write a readonly database" in str(exc_info.value).lower()
    conn.close()

def test_execute_query_failure():
    # Attempt executing query on non-existing table
    with pytest.raises((sqlite3.Error, pd.errors.DatabaseError)):
        execute_query("SELECT * FROM non_existent_table")
