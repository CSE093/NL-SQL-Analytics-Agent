import os
import pytest
import pandas as pd
from services.upload_service import sanitize_table_name, process_and_import_file, list_user_tables, delete_user_table
from database.db_manager import get_engine, init_db, reset_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Initializes the database before running tests."""
    reset_db()
    init_db()
    yield
    reset_db()

def test_sanitize_table_name():
    # Standard CSV
    assert sanitize_table_name("Sales_Data_2025.csv") == "sales_data_2025"
    # Spaces and upper chars
    assert sanitize_table_name("Customers Info Table.xlsx") == "customers_info_table"
    # Special characters
    assert sanitize_table_name("Products-Catalog!#%&.csv") == "products_catalog"
    # Numeric prefix should prepend 't_'
    assert sanitize_table_name("123orders.csv") == "t_123orders"
    # SQL Keyword conflict
    assert sanitize_table_name("Select.csv") == "t_select"
    # Strip multiple underscores
    assert sanitize_table_name("___orders___data___.csv") == "orders_data"

def test_csv_ingestion(tmp_path):
    # Create temp CSV file
    csv_file = tmp_path / "test_csv_data.csv"
    df_original = pd.DataFrame({
        "First Name": ["John", "Jane"],
        "Age": [28, 34],
        "City/Region": ["New York", "Chicago"]
    })
    df_original.to_csv(csv_file, index=False)
    
    table_name, rows = process_and_import_file(str(csv_file))
    
    assert table_name == "test_csv_data"
    assert rows == 2
    
    # Verify table structure in SQLite
    engine = get_engine()
    df_db = pd.read_sql_table(table_name, engine)
    
    # Assert columns were cleaned: lowercase, alphanumeric
    assert "first_name" in df_db.columns
    assert "age" in df_db.columns
    assert "city_region" in df_db.columns
    assert len(df_db) == 2
    
    # Assert listed as user table
    assert "test_csv_data" in list_user_tables()

def test_delete_user_table(tmp_path):
    csv_file = tmp_path / "table_to_delete.csv"
    pd.DataFrame({"name": ["Alpha"], "value": [1]}).to_csv(csv_file, index=False)

    table_name, rows = process_and_import_file(str(csv_file))
    assert rows == 1
    assert table_name in list_user_tables()

    delete_user_table(table_name)

    assert table_name not in list_user_tables()
