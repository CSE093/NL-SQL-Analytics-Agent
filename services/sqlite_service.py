import os
import sqlite3
import time
import logging
import pandas as pd
from typing import Dict, Any, Tuple
from database.db_manager import get_db_path

logger = logging.getLogger(__name__)

def get_readonly_connection() -> sqlite3.Connection:
    """
    Opens and returns a read-only sqlite3 connection using a URI path.
    Enforces mode=ro at the driver level to prevent any writes/modifications.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}. Please upload data first.")
        
    # Convert absolute path to a safe URI format
    # Windows paths like C:\Users\xxx must be formatted properly as file:///C:/Users/xxx
    abs_path = os.path.abspath(db_path)
    clean_path = abs_path.replace("\\", "/")
    
    # Ensure it starts with a leading slash on Windows for valid URI structure
    if not clean_path.startswith("/"):
        clean_path = "/" + clean_path
        
    uri = f"file:{clean_path}?mode=ro"
    logger.debug(f"Opening read-only SQLite connection: {uri}")
    
    # uri=True enables URI parameter parsing in sqlite3
    conn = sqlite3.connect(uri, uri=True)
    return conn

def execute_query(sql_query: str) -> Tuple[pd.DataFrame, float]:
    """
    Executes a SELECT query on the SQLite database in read-only mode.
    
    Returns:
        Tuple of (Pandas DataFrame of results, execution time in milliseconds)
        
    Raises:
        sqlite3.Error or other Exception if query fails or is blocked.
    """
    start_time = time.perf_counter()
    conn = None
    try:
        conn = get_readonly_connection()
        # Use pandas to read SQL directly into a DataFrame
        df = pd.read_sql_query(sql_query, conn)
        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        return df, execution_time_ms
    except Exception as e:
        logger.error(f"Read-only query execution failed: {str(e)} | Query: {sql_query}")
        raise e
    finally:
        if conn:
            conn.close()
