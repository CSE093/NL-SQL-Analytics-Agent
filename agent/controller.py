import logging
import time
from typing import Dict, Any, Generator
from agent.graph import graph
from agent.state import AgentState

logger = logging.getLogger(__name__)

def run_agent_stream(question: str) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """
    Runs the LangGraph agent for a user's question, yielding state updates
    after each node execution. This allows the frontend to display live
    step-by-step status checks.
    """
    logger.info(f"Controller starting stream for query: '{question}'")
    start_time = time.perf_counter()
    
    initial_state: AgentState = {
        "question": question,
        "schema": "",
        "generated_sql": None,
        "sql_history": [],
        "errors": [],
        "retry_count": 0,
        "success": False,
        "data": None,
        "explanation": None,
        "visualization": None,
        "status": "Initializing workflow..."
    }
    
    final_state = initial_state
    try:
        # Stream events from LangGraph
        for event in graph.stream(initial_state, stream_mode="updates"):
            # The event format is: {node_name: {state_updates}}
            node_name = list(event.keys())[0]
            node_updates = event[node_name]
            
            # Merge updates into the local state tracking
            for key, val in node_updates.items():
                final_state[key] = val
                
            yield {
                "node": node_name,
                "status": final_state.get("status", f"Completed {node_name}."),
                "state": final_state
            }
            
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        final_state["execution_time_ms"] = elapsed_time
        return final_state
        
    except Exception as e:
        logger.error(f"Stream execution failed: {str(e)}")
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        error_state = {
            "success": False,
            "generated_sql": None,
            "sql_history": [],
            "errors": [f"Critical workflow failure: {str(e)}"],
            "retry_count": 0,
            "data": None,
            "explanation": "Could not complete analysis due to an internal system error.",
            "visualization": None,
            "schema": "",
            "execution_time_ms": elapsed_time
        }
        yield {
            "node": "error",
            "status": "Critical execution error occurred.",
            "state": error_state
        }
        return error_state

def run_agent(question: str) -> Dict[str, Any]:
    """
    Invokes the LangGraph agent for a user's question synchronously.
    
    Returns:
        Dict representation of final AgentState containing query results and explanations.
    """
    logger.info(f"Controller received query: '{question}'")
    start_time = time.perf_counter()
    
    initial_state: AgentState = {
        "question": question,
        "schema": "",
        "generated_sql": None,
        "sql_history": [],
        "errors": [],
        "retry_count": 0,
        "success": False,
        "data": None,
        "explanation": None,
        "visualization": None,
        "status": "Initializing workflow..."
    }
    
    try:
        # Run graph synchronously
        final_state = graph.invoke(initial_state)
        
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        logger.info(f"LangGraph execution completed in {elapsed_time:.2f}ms.")
        
        return {
            "success": final_state.get("success", False),
            "generated_sql": final_state.get("generated_sql"),
            "sql_history": final_state.get("sql_history", []),
            "errors": final_state.get("errors", []),
            "retry_count": final_state.get("retry_count", 0),
            "data": final_state.get("data"),
            "explanation": final_state.get("explanation"),
            "visualization": final_state.get("visualization"),
            "schema": final_state.get("schema"),
            "execution_time_ms": elapsed_time
        }
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        return {
            "success": False,
            "generated_sql": None,
            "sql_history": [],
            "errors": [f"Critical workflow failure: {str(e)}"],
            "retry_count": 0,
            "data": None,
            "explanation": "Could not complete analysis due to an internal system error.",
            "visualization": None,
            "schema": "",
            "execution_time_ms": elapsed_time
        }
