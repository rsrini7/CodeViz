import os
import unittest
from unittest.mock import patch, mock_open, call
import json

# Adjust import path to go up one level from utils then into src.utils
# This assumes tests are run from the root directory of the project.
from unittest.mock import MagicMock # Added import
from src.utils.call_llm import call_llm, CACHE_FILE, PROVIDER_MAP
from src.utils.llm_providers.openrouter import call_openrouter
from src.utils.llm_providers.groq import call_groq
from src.utils.llm_providers.togetherai import call_togetherai

# Define a logger that the llm_logger can attach to for testing purposes
# This helps in capturing log messages if needed, but for these tests,
# we'll mostly be asserting behavior and mock calls.
import logging
test_logger = logging.getLogger("llm_logger")
if not test_logger.handlers:
    test_logger.addHandler(logging.NullHandler()) # Prevent "No handler found" warnings

class TestCallLLM(unittest.TestCase):

    def setUp(self):
        # Clear relevant environment variables before each test
        # to ensure a clean testing state.
        self.original_env_vars = {}
        vars_to_clear = [
            "OPENROUTER_API_KEY", "OPENROUTER_MODEL",
            "GROQ_API_KEY", "GROQ_MODEL",
            "TOGETHERAI_API_KEY", "TOGETHERAI_MODEL",
            "DEFAULT_LLM_PROVIDER"
        ]
        for var in vars_to_clear:
            if var in os.environ:
                self.original_env_vars[var] = os.environ[var]
                del os.environ[var]
        
        # Default test API keys
        os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key"
        os.environ["GROQ_API_KEY"] = "test_groq_key"
        os.environ["TOGETHERAI_API_KEY"] = "test_togetherai_key"

        # Reset cache file if it exists by mocking its deletion
        # For actual file operations, we'd use mock_open or ensure the file is cleaned up.
        # For these tests, we primarily mock os.path.exists and open.
        if os.path.exists(CACHE_FILE):
            try:
                os.remove(CACHE_FILE) # Try to remove if it's a real file from previous failed test
            except OSError:
                pass # Ignore if it fails (e.g. permissions, or it's already mocked)


    def tearDown(self):
        # Restore original environment variables
        for var, value in self.original_env_vars.items():
            os.environ[var] = value
        
        # Clean up keys set during setUp if they weren't in original_env_vars
        vars_to_remove = ["OPENROUTER_API_KEY", "GROQ_API_KEY", "TOGETHERAI_API_KEY"]
        for var in vars_to_remove:
            if var not in self.original_env_vars and var in os.environ:
                del os.environ[var]

        # Clean up cache file if created by a test that didn't mock file IO properly
        if os.path.exists(CACHE_FILE):
            try:
                os.remove(CACHE_FILE)
            except OSError:
                pass


    @patch("src.utils.llm_providers.openrouter.requests.post")
    def test_call_openrouter_direct(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenRouter says hello"}}]}
        
        result = call_openrouter("Hello")
        self.assertEqual(result, "OpenRouter says hello")
        mock_post.assert_called_once()
        # Add more assertions here based on expected headers, data, etc.

    @patch("src.utils.llm_providers.groq.ChatGroq") 
    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_call_groq_direct(self, mock_chain_invoke, MockChatGroq):
        mock_chain_invoke.return_value = "Groq says hello"
        
        result = call_groq("Hello") 
        self.assertEqual(result, "Groq says hello")
        MockChatGroq.assert_called_once() 
        mock_chain_invoke.assert_called_once()

    @patch("src.utils.llm_providers.togetherai.ChatOpenAI")
    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_call_togetherai_direct(self, mock_chain_invoke, MockChatOpenAI):
        mock_chain_invoke.return_value = "TogetherAI says hello"

        result = call_togetherai("Hello")
        self.assertEqual(result, "TogetherAI says hello")
        MockChatOpenAI.assert_called_once()
        mock_chain_invoke.assert_called_once()

    @patch("src.utils.call_llm.DEFAULT_PROVIDER", "openrouter")
    def test_call_llm_selects_openrouter_default(self):
        expected_response = "Default OpenRouter response"
        tracker_mock = MagicMock(name="tracker_openrouter")
        def lambda_mock_openrouter(prompt_arg):
            tracker_mock(prompt_arg)
            return expected_response

        mock_groq_func = MagicMock(name="mock_groq_func")
        mock_togetherai_func = MagicMock(name="mock_togetherai_func")

        with patch.dict(PROVIDER_MAP, {"openrouter": lambda_mock_openrouter, 
                                       "groq": mock_groq_func, 
                                       "togetherai": mock_togetherai_func}):
            response = call_llm("Test prompt", use_cache=False) # provider=None uses DEFAULT_PROVIDER
        self.assertEqual(response, expected_response)
        tracker_mock.assert_called_once_with("Test prompt")
        mock_groq_func.assert_not_called()
        mock_togetherai_func.assert_not_called()

    @patch("src.utils.call_llm.DEFAULT_PROVIDER", "groq")
    def test_call_llm_selects_groq_default(self):
        expected_response = "Default Groq response"
        tracker_mock = MagicMock(name="tracker_groq")
        def lambda_mock_groq(prompt_arg):
            tracker_mock(prompt_arg)
            return expected_response
        
        mock_openrouter_func = MagicMock(name="mock_openrouter_func")
        mock_togetherai_func = MagicMock(name="mock_togetherai_func")

        with patch.dict(PROVIDER_MAP, {"openrouter": mock_openrouter_func, 
                                       "groq": lambda_mock_groq, 
                                       "togetherai": mock_togetherai_func}):
            response = call_llm("Test prompt", use_cache=False) # provider=None uses DEFAULT_PROVIDER
        self.assertEqual(response, expected_response)
        tracker_mock.assert_called_once_with("Test prompt")
        mock_openrouter_func.assert_not_called()
        mock_togetherai_func.assert_not_called()

    @patch("src.utils.call_llm.DEFAULT_PROVIDER", "togetherai")
    def test_call_llm_selects_togetherai_default(self):
        expected_response = "Default TogetherAI response"
        tracker_mock = MagicMock(name="tracker_togetherai")
        def lambda_mock_togetherai(prompt_arg):
            tracker_mock(prompt_arg)
            return expected_response

        mock_openrouter_func = MagicMock(name="mock_openrouter_func")
        mock_groq_func = MagicMock(name="mock_groq_func")

        with patch.dict(PROVIDER_MAP, {"openrouter": mock_openrouter_func, 
                                       "groq": mock_groq_func, 
                                       "togetherai": lambda_mock_togetherai}):
            response = call_llm("Test prompt", use_cache=False) # provider=None uses DEFAULT_PROVIDER
        self.assertEqual(response, expected_response)
        tracker_mock.assert_called_once_with("Test prompt")
        mock_openrouter_func.assert_not_called()
        mock_groq_func.assert_not_called()

    def test_call_llm_selects_groq_explicit(self):
        mock_groq_func = MagicMock(return_value="Explicit Groq response")
        with patch.dict(PROVIDER_MAP, {"openrouter": MagicMock(), "groq": mock_groq_func, "togetherai": MagicMock()}):
            response = call_llm("Test prompt", provider="groq", use_cache=False)
        self.assertEqual(response, "Explicit Groq response")
        mock_groq_func.assert_called_once_with("Test prompt")

    def test_call_llm_invalid_provider(self):
        with self.assertRaises(ValueError) as context:
            call_llm("Test prompt", provider="unknown_provider", use_cache=False)
        self.assertIn("Invalid provider: unknown_provider", str(context.exception))
    
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_cache_save_and_load(self, mock_file_open, mock_exists):
        prompt = "Cache test prompt"
        expected_response = "Cached response"
        
        mock_openrouter_function = MagicMock(return_value=expected_response)
        
        with patch.dict(PROVIDER_MAP, {"openrouter": mock_openrouter_function}):
            # First call: API call, save to cache
            mock_exists.return_value = False 
            call_llm(prompt, provider="openrouter", use_cache=True)
            
            mock_openrouter_function.assert_called_once_with(prompt)
            mock_file_open.assert_any_call(CACHE_FILE, "w", encoding="utf-8")
            
            # Simulate cache content for the next call by having mock_open read it
            # The actual dump call by call_llm will use the mock_file_open handle
            # We need to ensure that when call_llm tries to read next, it gets this.
            # This means the handle mock_file_open() needs to simulate this content.
            # When json.dump(current_cache, f, indent=2) is called by call_llm,
            # it writes to the object from mock_file_open.
            # Then, when call_llm is called again, and it tries to open and json.load(f),
            # mock_file_open needs to provide the previously written data.

            # Simplification: We assume json.dump worked.
            # For the second call, we set up mock_open to return the expected cache.
            cache_content_for_load = json.dumps({f"openrouter_{prompt}": expected_response})

            # Second call: Load from cache
            mock_exists.return_value = True 
            # Reset side_effect to control read then potential write
            mock_file_open.side_effect = [
                mock_open(read_data=cache_content_for_load).return_value, # For reading cache
                mock_open().return_value  # For potential write if cache was missed (should not happen)
            ]
            response_from_cache = call_llm(prompt, provider="openrouter", use_cache=True)
            
            self.assertEqual(response_from_cache, expected_response)
            mock_openrouter_function.assert_called_once() # Assert it wasn't called again
            # Check that open was called to read the cache
            # The first call in side_effect is the read call.
            self.assertEqual(mock_file_open.call_args_list[1], call(CACHE_FILE, "r", encoding="utf-8"))


    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_cache_different_providers_no_collision(self, mock_file_open, mock_exists):
        prompt = "Shared prompt"
        response_openrouter_val = "OpenRouter reply"
        response_groq_val = "Groq reply"

        mock_openrouter_func = MagicMock(return_value=response_openrouter_val)
        mock_groq_func = MagicMock(return_value=response_groq_val)

        with patch.dict(PROVIDER_MAP, {"openrouter": mock_openrouter_func, "groq": mock_groq_func}):
            # --- OpenRouter call ---
            mock_exists.return_value = False 
            call_llm(prompt, provider="openrouter", use_cache=True)
            mock_openrouter_func.assert_called_once_with(prompt)
            
            # Simulate cache content after OpenRouter call for subsequent read
            cache_after_or_str = json.dumps({f"openrouter_{prompt}": response_openrouter_val})
            
            # --- Groq call ---
            mock_exists.return_value = True 
            # open is called for read, then for write
            mock_file_open.side_effect = [
                mock_open(read_data=cache_after_or_str).return_value, # Read (Groq won't find its key)
                mock_open().return_value  # Write (Groq saves its response)
            ]
            call_llm(prompt, provider="groq", use_cache=True)
            mock_groq_func.assert_called_once_with(prompt)

            # Simulate cache content after Groq call
            cache_after_groq_str = json.dumps({
                f"openrouter_{prompt}": response_openrouter_val,
                f"groq_{prompt}": response_groq_val
            })
            
            # --- Verify OpenRouter still gets its cached value ---
            mock_exists.return_value = True
            mock_file_open.side_effect = [mock_open(read_data=cache_after_groq_str).return_value]
            cached_or_response = call_llm(prompt, provider="openrouter", use_cache=True)
            self.assertEqual(cached_or_response, response_openrouter_val)
            mock_openrouter_func.assert_called_once() # Still only called once initially

            # --- Verify Groq still gets its cached value ---
            mock_file_open.side_effect = [mock_open(read_data=cache_after_groq_str).return_value]
            cached_groq_response = call_llm(prompt, provider="groq", use_cache=True)
            self.assertEqual(cached_groq_response, response_groq_val)
            mock_groq_func.assert_called_once() # Still only called once initially


    @patch("src.utils.llm_providers.openrouter.requests.post")
    def test_openrouter_api_error(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with self.assertRaisesRegex(Exception, "OpenRouter API call failed with status 500: Internal Server Error"):
            call_openrouter("test")

    @patch("src.utils.llm_providers.groq.ChatGroq")
    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_groq_api_error(self, mock_chain_invoke, MockChatGroq):
        mock_chain_invoke.side_effect = Exception("Groq network error")
        
        with self.assertRaisesRegex(Exception, "Groq API call failed: Groq network error"):
            call_groq("test")
        MockChatGroq.assert_called_once() # Ensure model was initialized
        mock_chain_invoke.assert_called_once()

    @patch("src.utils.llm_providers.togetherai.ChatOpenAI")
    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_togetherai_api_error(self, mock_chain_invoke, MockChatOpenAI):
        mock_chain_invoke.side_effect = Exception("TogetherAI auth error")
        
        with self.assertRaisesRegex(Exception, "TogetherAI API call failed: TogetherAI auth error"):
            call_togetherai("test")
        MockChatOpenAI.assert_called_once()
        mock_chain_invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()
