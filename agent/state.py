from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd

class AgentState(TypedDict):
    """
    State representing the context of a single query request
    running through the LangGraph analytics workflow.
    """
    question: str
    schema: str
    generated_sql: Optional[str]
    sql_history: List[str]
    errors: List[str]
    retry_count: int
    success: bool
    data: Optional[pd.DataFrame]
    explanation: Optional[str]
    visualization: Optional[Any]  # Plotly Figure object
    status: str
