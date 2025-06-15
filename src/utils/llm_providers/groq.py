import os
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Get the logger instance from the main call_llm module
logger = logging.getLogger("groq")

def call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        error_msg = "GROQ_API_KEY is not set."
        logger.error(error_msg)
        raise ValueError(error_msg)

    model_name = os.getenv("GROQ_MODEL", "llama3-8b-8192") # Default model

    logger.info(f"Calling Groq API with model: {model_name}")

    try:
        chat = ChatGroq(temperature=0, groq_api_key=api_key, model_name=model_name)
        
        # Using a simple prompt template
        prompt_template = ChatPromptTemplate.from_messages([("user", "{prompt}")])
        output_parser = StrOutputParser()
        
        chain = prompt_template | chat | output_parser
        
        response_text = chain.invoke({"prompt": prompt})
        
    except Exception as e:
        error_msg = f"Groq API call failed: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    return response_text

if __name__ == '__main__':
    # This is for testing the module directly
    # Ensure GROQ_API_KEY is set as an environment variable
    # You might also want to set GROQ_MODEL
    # e.g., export GROQ_API_KEY="your_api_key"
    # e.g., export GROQ_MODEL="llama3-70b-8192"

    logging.basicConfig(level=logging.INFO) # Basic logging setup for testing
    # Ensure the logger used by call_groq has handlers for standalone testing
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler()) # Log to console
        logger.setLevel(logging.INFO)

    test_prompt = "Explain the concept of Zero-Knowledge Proofs in simple terms."
    print(f"Testing Groq call with prompt: '{test_prompt}'")
    
    # Example of setting env var for testing if not set globally
    # if not os.getenv("GROQ_API_KEY"):
    #     print("Warning: GROQ_API_KEY not set. Please set it to run this test.")
    #     # os.environ["GROQ_API_KEY"] = "your_test_key" # For local testing only

    try:
        response = call_groq(test_prompt)
        print(f"Response from Groq: {response}")
    except Exception as e:
        print(f"Error during Groq test call: {e}")
