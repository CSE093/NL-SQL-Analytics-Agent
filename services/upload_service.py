import os
import re
import logging
import pandas as pd
from typing import List, Dict, Any, Tuple
from sqlalchemy import inspect, text
from database.db_manager import get_engine, get_db_path
from tools.schema_tool import invalidate_schema_cache

logger = logging.getLogger(__name__)

# Reserved SQLite keywords to avoid naming tables after them
RESERVED_KEYWORDS = {
    "select", "table", "from", "where", "join", "group", "order", "by", 
    "index", "view", "alter", "create", "drop", "insert", "delete", "update",
    "with", "as", "into", "values", "on", "limit", "offset", "having"
}

def sanitize_table_name(filename: str) -> str:
    """
    Sanitizes file names into valid SQLite table names:
    - Converts to lowercase
    - Replaces spaces, dashes, and special characters with underscores
    - Removes extension
    - Prevents table name starting with a number (prepends 't_')
    - Avoids conflict with SQL keywords
    """
    # Get filename without path and extension
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Lowercase and replace non-alphanumeric with underscore
    clean_name = base_name.lower().strip()
    clean_name = re.sub(r'[^a-z0-9_]', '_', clean_name)
    # Replace multiple consecutive underscores with single underscore
    clean_name = re.sub(r'_+', '_', clean_name)
    # Trim leading/trailing underscores
    clean_name = clean_name.strip('_')
    
    # Handle empty names after sanitization
    if not clean_name:
        clean_name = "uploaded_table"
        
    # Check if table name starts with a digit
    if clean_name[0].isdigit():
        clean_name = f"t_{clean_name}"
        
    # If the name is a SQL keyword, prepend 't_'
    if clean_name in RESERVED_KEYWORDS:
        clean_name = f"t_{clean_name}"
        
    return clean_name

def save_uploaded_file(file_name: str, file_bytes: bytes, upload_dir: str = "uploads") -> str:
    """
    Saves raw file bytes into the uploads/ directory for audit purposes.
    Returns the absolute path to the saved file.
    """
    # Ensure uploads directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid overwrites
    name, ext = os.path.splitext(file_name)
    counter = 1
    unique_name = file_name
    while os.path.exists(os.path.join(upload_dir, unique_name)):
        unique_name = f"{name}_{counter}{ext}"
        counter += 1
        
    save_path = os.path.join(upload_dir, unique_name)
    with open(save_path, "wb") as f:
        f.write(file_bytes)
        
    logger.info(f"Saved uploaded file to {save_path}")
    return os.path.abspath(save_path)

def process_and_import_file(file_path: str, table_name_override: str = None) -> Tuple[str, int]:
    """
    Reads CSV or Excel files from disk, converts them to a Pandas DataFrame,
    and inserts them into SQLite.
    
    Returns:
        Tuple of (sanitized_table_name, row_count_imported)
    """
    # Determine table name
    table_name = table_name_override or sanitize_table_name(file_path)
    
    # Determine loader
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        if ext == ".csv":
            # Read CSV with fallback encoding options
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
        elif ext in [".xlsx", ".xls"]:
            # Load Excel sheets
            xls = pd.ExcelFile(file_path)
            # If Excel has multiple sheets, we load the first sheet for simplicity,
            # or handle multiple sheet parsing separately. Here we import sheet 0.
            df = pd.read_excel(file_path, sheet_name=0)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only CSV and Excel (.xlsx) are supported.")
            
        if df.empty:
            raise ValueError("Uploaded file contains no data.")

        # Clean column names to make SQL querying easy
        # Strip whitespace, convert to lowercase, replace special characters with underscores
        cleaned_columns = []
        for col in df.columns:
            cleaned_col = str(col).strip().lower()
            cleaned_col = re.sub(r'[^a-z0-9_]', '_', cleaned_col)
            cleaned_col = re.sub(r'_+', '_', cleaned_col).strip('_')
            # Prepend 'c_' if it starts with digit
            if not cleaned_col or cleaned_col[0].isdigit():
                cleaned_col = f"c_{cleaned_col or 'col'}"
            # Ensure uniqueness of columns
            base_col = cleaned_col
            idx = 1
            while cleaned_col in cleaned_columns:
                cleaned_col = f"{base_col}_{idx}"
                idx += 1
            cleaned_columns.append(cleaned_col)
            
        df.columns = cleaned_columns
        
        # Write to SQLite
        engine = get_engine()
        
        # We replace the table if it already exists to allow simple re-uploads
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        logger.info(f"Successfully imported table '{table_name}' with {len(df)} rows.")
        
        invalidate_schema_cache()
        
        return table_name, len(df)
        
    except Exception as e:
        logger.error(f"Error importing file {file_path} to SQLite: {str(e)}")
        raise e

def list_user_tables() -> List[str]:
    """Lists all user uploaded tables in the SQLite database."""
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    # Exclude system and framework tables (like query_history)
    exclude_tables = {"query_history", "sqlite_sequence"}
    return [t for t in tables if t not in exclude_tables]

def delete_user_table(table_name: str) -> None:
    """Drops a user table from SQLite and refreshes cached schema metadata."""
    if not table_name:
        raise ValueError("Table name is required.")

    engine = get_engine()
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise ValueError(f"Table '{table_name}' does not exist.")

    safe_table_name = table_name.replace('"', '""')
    with engine.begin() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS "{safe_table_name}"'))

    invalidate_schema_cache()
    logger.info(f"Dropped table '{table_name}'.")
