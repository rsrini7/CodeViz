import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Get the logger instance from the main call_llm module
logger = logging.getLogger("togetherai")

def call_togetherai(prompt: str) -> str:
    api_key = os.getenv("TOGETHERAI_API_KEY")
    if not api_key:
        error_msg = "TOGETHERAI_API_KEY is not set."
        logger.error(error_msg)
        raise ValueError(error_msg)

    model_name = os.getenv("TOGETHERAI_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free") # Default model

    logger.info(f"Calling TogetherAI API with model: {model_name}")

    try:
        chat = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base="https://api.together.xyz/v1", # TogetherAI API base URL
            temperature=0
        )
        
        prompt_template = ChatPromptTemplate.from_messages([("user", "{prompt}")])
        output_parser = StrOutputParser()
        
        chain = prompt_template | chat | output_parser
        
        response_text = chain.invoke({"prompt": prompt})
        
    except Exception as e:
        error_msg = f"TogetherAI API call failed: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    return response_text

if __name__ == '__main__':
    # This is for testing the module directly
    # Ensure TOGETHERAI_API_KEY is set as an environment variable
    # You might also want to set TOGETHERAI_MODEL
    # e.g., export TOGETHERAI_API_KEY="your_api_key"
    # e.g., export TOGETHERAI_MODEL="Qwen/Qwen1.5-72B-Chat"

    logging.basicConfig(level=logging.INFO) # Basic logging setup for testing
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler()) # Log to console
        logger.setLevel(logging.INFO)

    test_prompt = "What are the main benefits of using renewable energy sources?"
    print(f"Testing TogetherAI call with prompt: '{test_prompt}'")

    # if not os.getenv("TOGETHERAI_API_KEY"):
    #     print("Warning: TOGETHERAI_API_KEY not set. Please set it to run this test.")
        # os.environ["TOGETHERAI_API_KEY"] = "your_test_key" # For local testing only
        
    try:
        response = call_togetherai(test_prompt)
        print(f"Response from TogetherAI: {response}")
    except Exception as e:
        print(f"Error during TogetherAI test call: {e}")
