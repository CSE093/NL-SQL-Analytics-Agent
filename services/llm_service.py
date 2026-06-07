import os
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class LLMServiceException(Exception):
    """Custom exception class for Ollama/LLM communication failures."""
    pass

def generate_completion(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    """
    Sends chat prompt containing system and user messages to the configured Ollama API endpoint.
    
    Returns:
        The response content string.
    
    Raises:
        LLMServiceException if connection fails or response status code is not 200.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip().rstrip('/')
    model = os.getenv("OLLAMA_MODEL", "llama3.1").strip()
    
    endpoint = f"{base_url}/api/chat"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": temperature,
            "seed": 42  # For consistent reproducible outputs
        },
        "stream": False
    }
    
    logger.info(f"Invoking Ollama model '{model}' at '{endpoint}'")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=45)
        
        if response.status_code == 404:
            # Check if model issue
            raise LLMServiceException(
                f"Ollama returned 404. Model '{model}' might not be installed. "
                f"Please run 'ollama pull {model}' first."
            )
            
        response.raise_for_status()
        response_data = response.json()
        
        message_content = response_data.get("message", {}).get("content", "").strip()
        if not message_content:
            raise LLMServiceException("Received empty response content from Ollama model.")
            
        return message_content
        
    except requests.exceptions.ConnectionError:
        error_msg = (
            f"Could not connect to Ollama at '{base_url}'. "
            f"Please ensure the Ollama service is running locally on your machine. "
            f"To install or run, visit: https://ollama.com"
        )
        logger.error(error_msg)
        raise LLMServiceException(error_msg)
        
    except requests.exceptions.Timeout:
        error_msg = f"Ollama model query timed out after 45 seconds."
        logger.error(error_msg)
        raise LLMServiceException(error_msg)
        
    except Exception as e:
        if isinstance(e, LLMServiceException):
            raise e
        error_msg = f"An unexpected error occurred during LLM communication: {str(e)}"
        logger.error(error_msg)
        raise LLMServiceException(error_msg)
