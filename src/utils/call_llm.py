import os
import logging
import json
from datetime import datetime

# Import provider functions
from .llm_providers.openrouter import call_openrouter
from .llm_providers.groq import call_groq
from .llm_providers.togetherai import call_togetherai

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True) # Ensure log directory exists
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger for this module
logger = logging.getLogger("llm_logger")
if not logger.handlers: # Check if handlers are already added
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent propagation to root logger to avoid duplicate logs
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - PROVIDER:%(provider)s - %(message)s")
    )
    logger.addHandler(file_handler)
    
    # Console handler (optional, for easier debugging during development)
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(
    #     logging.Formatter("%(asctime)s - %(levelname)s - PROVIDER:%(provider)s - %(message)s")
    # )
    # logger.addHandler(console_handler)

# Provider mapping
PROVIDER_MAP = {
    "openrouter": call_openrouter,
    "groq": call_groq,
    "togetherai": call_togetherai,
}

# Simple cache configuration
CACHE_FILE = "llm_cache.json"
DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER")
if DEFAULT_PROVIDER not in PROVIDER_MAP:
    raise ValueError(f"Invalid DEFAULT_LLM_PROVIDER: {DEFAULT_PROVIDER}. Available providers: {list(PROVIDER_MAP.keys())}")


def call_llm(prompt: str, provider: str = None, use_cache: bool = True) -> str:
    selected_provider_name = (provider or DEFAULT_PROVIDER).lower()
    
    if selected_provider_name not in PROVIDER_MAP:
        error_msg = f"Invalid provider: {selected_provider_name}. Available providers: {list(PROVIDER_MAP.keys())}"
        # Log with extra context for provider
        logger.error(error_msg, extra={"provider": selected_provider_name})
        raise ValueError(error_msg)

    # Log the prompt with provider information
    log_extra = {"provider": selected_provider_name}
    logger.info(f"PROMPT: {prompt}", extra=log_extra)

    # Cache key now includes provider name
    cache_key = f"{selected_provider_name}_{prompt}"

    if use_cache:
        cache = {}
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}, starting with empty cache", extra=log_extra)
        
        if cache_key in cache:
            cached_response = cache[cache_key]
            logger.info(f"RESPONSE (cached): {cached_response}", extra=log_extra)
            return cached_response

    # Call the selected provider
    provider_function = PROVIDER_MAP[selected_provider_name]
    
    try:
        response_text = provider_function(prompt)
    except Exception as e:
        # Provider-specific functions are expected to log their own errors.
        # This is a fallback or re-raise scenario.
        logger.error(f"Error calling provider {selected_provider_name}: {e}", extra=log_extra)
        raise # Re-raise the exception to the caller

    logger.info(f"RESPONSE (API): {response_text}", extra=log_extra)

    if use_cache:
        current_cache = {} # Load fresh cache to minimize race conditions if any
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    current_cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache before saving: {e}", extra=log_extra)
        
        current_cache[cache_key] = response_text
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(current_cache, f, indent=2) # Added indent for readability
        except Exception as e:
            logger.error(f"Failed to save cache: {e}", extra=log_extra)

    return response_text

if __name__ == "__main__":
    # Ensure logger is set up for standalone testing
    # This setup is slightly different from the module-level one to ensure console output for __main__
    if not logger.handlers or not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        # Clear existing handlers for __main__ to avoid duplicate logs if script is re-run
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        console_handler_main = logging.StreamHandler()
        console_handler_main.setFormatter(
             logging.Formatter("%(asctime)s - %(levelname)s - PROVIDER:%(provider)s - %(message)s")
        )
        logger.addHandler(console_handler_main)
        logger.setLevel(logging.INFO) # Ensure level is set for the logger

    # --- Test Prompts ---
    test_prompt_general = "Hello, how are you today?"
    test_prompt_openrouter = "What is OpenRouter good for?"
    test_prompt_groq = "What is Groq?"
    test_prompt_together = "What is TogetherAI?"

    # --- Environment Variable Setup (Important for Testing) ---
    # To run these tests, you MUST set the following environment variables:
    # export OPENROUTER_API_KEY="your_openrouter_key"
    # export GROQ_API_KEY="your_groq_key"
    # export TOGETHERAI_API_KEY="your_togetherai_key"
    #
    # Optional:
    # export OPENROUTER_MODEL="mistralai/mistral-7b-instruct:free"
    # export GROQ_MODEL="llama3-8b-8192"
    # export TOGETHERAI_MODEL="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    # export DEFAULT_LLM_PROVIDER="openrouter" 
    # export LOG_DIR="mylogs" # Example, will be created if not exists

    print("Starting LLM call tests. Ensure API keys are set in your environment.")
    print(f"Default provider is set to: {DEFAULT_PROVIDER}")
    print(f"Log directory is set to: {log_directory}")
    print(f"Cache file is: {CACHE_FILE}")


    # --- Test Scenarios ---
    providers_to_test = []
    if os.getenv("OPENROUTER_API_KEY"):
        providers_to_test.append(("openrouter", test_prompt_openrouter))
    else:
        print("Skipping OpenRouter test: OPENROUTER_API_KEY not set.")

    if os.getenv("GROQ_API_KEY"):
        providers_to_test.append(("groq", test_prompt_groq))
    else:
        print("Skipping Groq test: GROQ_API_KEY not set.")

    if os.getenv("TOGETHERAI_API_KEY"):
        providers_to_test.append(("togetherai", test_prompt_together))
    else:
        print("Skipping TogetherAI test: TOGETHERAI_API_KEY not set.")

    # Test with default provider
    # This requires at least one API key to be set for the default provider
    # and DEFAULT_LLM_PROVIDER to point to an available provider
    print(f"\n--- Testing with Default Provider ({DEFAULT_PROVIDER}) ---")
    if DEFAULT_PROVIDER in [p[0] for p in providers_to_test] or \
       (DEFAULT_PROVIDER == "openrouter" and os.getenv("OPENROUTER_API_KEY")) or \
       (DEFAULT_PROVIDER == "groq" and os.getenv("GROQ_API_KEY")) or \
       (DEFAULT_PROVIDER == "togetherai" and os.getenv("TOGETHERAI_API_KEY")):
        try:
            response_default = call_llm(test_prompt_general, use_cache=False) # Test API call
            print(f"Default Provider ({DEFAULT_PROVIDER}) Response (API): {response_default[:150]}...")
            response_default_cached = call_llm(test_prompt_general, use_cache=True) # Test cache
            print(f"Default Provider ({DEFAULT_PROVIDER}) Response (Cache): {response_default_cached[:150]}...")
            if response_default == response_default_cached:
                print(f"Cache test for Default Provider ({DEFAULT_PROVIDER}) PASSED.")
            else:
                print(f"Cache test for Default Provider ({DEFAULT_PROVIDER}) FAILED.")
        except Exception as e:
            print(f"Error with Default Provider ({DEFAULT_PROVIDER}): {e}")
    else:
        print(f"Skipping Default Provider test: API key for '{DEFAULT_PROVIDER}' not set or provider not available.")


    # Test each specified provider
    for provider_name, prompt in providers_to_test:
        print(f"\n--- Testing with Provider: {provider_name} ---")
        try:
            # First call - should hit the API
            print(f"Making initial call to {provider_name} (no cache)...")
            response1 = call_llm(prompt, provider=provider_name, use_cache=False)
            print(f"{provider_name} Response 1 (API): {response1[:150]}...")

            # Second call - should use cache
            print(f"Making second call to {provider_name} (with cache)...")
            response2 = call_llm(prompt, provider=provider_name, use_cache=True)
            print(f"{provider_name} Response 2 (Cache): {response2[:150]}...")

            if response1 == response2:
                print(f"Cache test for {provider_name} PASSED.")
            else:
                print(f"Cache test for {provider_name} FAILED. Responses differ.")
        except Exception as e:
            print(f"Error testing {provider_name}: {e}")
    
    print("\nLLM call tests finished.")
