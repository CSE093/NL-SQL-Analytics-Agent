import logging
from typing import Dict, Any, List
from sqlalchemy import inspect
from database.db_manager import get_engine

logger = logging.getLogger(__name__)

# Cache store for database schemas to satisfy caching requirement
_schema_cache: Dict[str, Any] = {}

def get_schema(force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    """
    Discovers the database schema and columns.
    Returns a dictionary mapping table names to their lists of column metadata:
        {
            "table_name": [
                {"name": "col1", "type": "INTEGER", "primary_key": True},
                ...
            ]
        }
    Implements in-memory caching to avoid repeated filesystem reads.
    """
    global _schema_cache
    
    if _schema_cache and not force_refresh:
        logger.debug("Schema fetched from cache.")
        return _schema_cache

    logger.info("Discovering database schema...")
    try:
        engine = get_engine()
        inspector = inspect(engine)
        
        # Exclude system tables
        exclude_tables = {"query_history", "sqlite_sequence"}
        tables = [t for t in inspector.get_table_names() if t not in exclude_tables]
        
        discovered_schema = {}
        for table in tables:
            columns = inspector.get_columns(table)
            column_info_list = []
            
            # Retrieve primary key columns
            pk_cols = set(inspector.get_pk_constraint(table).get("constrained_columns", []))
            
            for col in columns:
                column_info_list.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "primary_key": col["name"] in pk_cols
                })
            discovered_schema[table] = column_info_list
            
        _schema_cache = discovered_schema
        logger.info(f"Schema discovered successfully: {list(discovered_schema.keys())}")
        return discovered_schema
        
    except Exception as e:
        logger.error(f"Error during schema discovery: {str(e)}")
        # If schema fetch fails, return empty to prevent agent failure
        return {}

def invalidate_schema_cache() -> None:
    """Invalidates the in-memory schema cache."""
    global _schema_cache
    _schema_cache.clear()
    logger.info("Database schema cache invalidated.")

def get_schema_string() -> str:
    """
    Generates a clear text-based representation of the SQLite schema,
    suitable for injection into LLM prompts.
    """
    schema = get_schema()
    if not schema:
        return "No user tables exist in the database. Please upload data."
        
    schema_lines = []
    for table_name, columns in schema.items():
        schema_lines.append(f"Table: {table_name}")
        schema_lines.append("Columns:")
        for col in columns:
            pk_suffix = " (PRIMARY KEY)" if col["primary_key"] else ""
            schema_lines.append(f"  - {col['name']} {col['type']}{pk_suffix}")
        schema_lines.append("")  # Empty line separator between tables
        
    return "\n".join(schema_lines)
