import logging
from typing import List, Dict, Any
from sqlalchemy import desc
from database.db_manager import get_session
from models.models import QueryHistory

logger = logging.getLogger(__name__)

def log_query(
    question: str,
    sql_query: str = None,
    explanation: str = None,
    success: bool = False,
    error_message: str = None,
    execution_time_ms: float = None
) -> None:
    """Logs a single NL query attempt and outcome to the query_history table."""
    try:
        # Get session using the generator context manager
        session_gen = get_session()
        session = next(session_gen)
        
        history_entry = QueryHistory(
            question=question,
            sql_query=sql_query,
            explanation=explanation,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
        session.add(history_entry)
        # Session commit is automatically called by our generator on success
        try:
            next(session_gen)
        except StopIteration:
            pass
        logger.info(f"Logged query history entry. Success: {success}")
    except Exception as e:
        logger.error(f"Failed to log query history: {str(e)}")

def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves list of previous queries, sorted from newest to oldest."""
    try:
        session_gen = get_session()
        session = next(session_gen)
        
        records = session.query(QueryHistory).order_by(desc(QueryHistory.timestamp)).limit(limit).all()
        result = [rec.to_dict() for rec in records]
        
        try:
            next(session_gen)
        except StopIteration:
            pass
        return result
    except Exception as e:
        logger.error(f"Failed to fetch query history: {str(e)}")
        return []

def clear_history() -> None:
    """Deletes all entries from the query_history table."""
    try:
        session_gen = get_session()
        session = next(session_gen)
        
        session.query(QueryHistory).delete()
        
        try:
            next(session_gen)
        except StopIteration:
            pass
        logger.info("Cleared all query history.")
    except Exception as e:
        logger.error(f"Failed to clear query history: {str(e)}")
        raise e
