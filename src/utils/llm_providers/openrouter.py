import os
import requests
import logging

# Get the logger instance from the main call_llm module
# This assumes logger is configured in the main script that calls this provider
logger = logging.getLogger("openrouter")

def call_openrouter(prompt: str) -> str:
    # OpenRouter API configuration
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        error_msg = "OPENROUTER_API_KEY is not set."
        logger.error(error_msg)
        raise ValueError(error_msg)

    model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-0528-qwen3-8b:free") # Updated to a common free model
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    logger.info(f"Calling OpenRouter API with model: {model}")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        error_msg = f"OpenRouter API call failed with status {response.status_code}: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    try:
        response_json = response.json()
        if "choices" not in response_json or not response_json["choices"]:
            error_msg = f"OpenRouter response does not contain 'choices': {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        message = response_json["choices"][0].get("message", {})
        response_text = message.get("content")

        if response_text is None:
            error_msg = f"Failed to parse OpenRouter response, 'content' is missing: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except Exception as e:
        error_msg = f"Failed to parse OpenRouter response: {e}; Response: {response.text}"
        logger.error(error_msg)        
        raise Exception(error_msg)
    
    return response_text

if __name__ == '__main__':
    # This is for testing the module directly
    # Ensure OPENROUTER_API_KEY is set as an environment variable
    # You might also want to set OPENROUTER_MODEL
    # e.g., export OPENROUTER_API_KEY="your_api_key"
    # e.g., export OPENROUTER_MODEL="mistralai/mistral-7b-instruct:free"
    
    # Basic logging setup for testing
    logging.basicConfig(level=logging.INFO)
    logger.addHandler(logging.StreamHandler()) # Log to console for testing

    test_prompt = "What is the capital of France?"
    print(f"Testing OpenRouter call with prompt: '{test_prompt}'")
    try:
        # For direct testing, ensure the logger used by call_openrouter is configured
        # or it might not output logs as expected.
        # The getLogger("llm_logger") will get a logger that might not have handlers if not run via main script.
        # For standalone test, it's better to pass a logger or use a default one.
        # However, for this subtask, we'll keep it as is, assuming it's part of a larger system.
        
        # A simple way to ensure logger works for standalone test:
        if not logger.hasHandlers():
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(logging.INFO)

        response = call_openrouter(test_prompt)
        print(f"Response from OpenRouter: {response}")
    except Exception as e:
        print(f"Error during OpenRouter test call: {e}")
