## 🚀 Getting Started

1. Clone this repository
   ```bash
   git clone https://github.com/rsrini7/CodeViz
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up LLM & GitHub credentials
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   GITHUB_TOKEN=your_github_token
   ```

5. Generate a complete codebase tutorial by running the main script:
    ```bash
    # Analyze a GitHub repository
    python main.py --repo https://github.com/username/repo --include "*.py" "*.js" --exclude "tests/*" --max-size 50000

    # Or, analyze a local directory
    python main.py --dir /path/to/your/codebase --include "*.py" --exclude "*test*"

    # Or, generate a tutorial in Chinese
    python main.py --repo https://github.com/username/repo --language "Chinese"
    ```

    - `--repo` or `--dir` - Specify either a GitHub repo URL or a local directory path (required, mutually exclusive)
    - `-n, --name` - Project name (optional, derived from URL/directory if omitted)
    - `-t, --token` - GitHub token (or set GITHUB_TOKEN environment variable)
    - `-o, --output` - Output directory (default: ./output)
    - `-i, --include` - Files to include (e.g., "`*.py`" "`*.js`")
    - `-e, --exclude` - Files to exclude (e.g., "`tests/*`" "`docs/*`")
    - `-s, --max-size` - Maximum file size in bytes (default: 100KB)
    - `--language` - Language for the generated tutorial (default: "english")
    - `--max-abstractions` - Maximum number of abstractions to identify (default: 10)
    - `--no-cache` - Disable LLM response caching (default: caching enabled)

The application will crawl the repository, analyze the codebase structure, generate tutorial content in the specified language, and save the output in the specified directory (default: ./output).


<details>
 
<summary> 🐳 <b>Running with Docker</b> </summary>

To run this project in a Docker container, you'll need to pass your API keys as environment variables. 

1. Build the Docker image
   ```bash
   docker build -t codeviz-app .
   ```

2. Run the container

   You'll need to provide your `OPENROUTER_API_KEY` for the LLM to function. If you're analyzing private GitHub repositories or want to avoid rate limits, also provide your `GITHUB_TOKEN`.
   
   Mount a local directory to `/app/output` inside the container to access the generated tutorials on your host machine.
   
   **Example for analyzing a public GitHub repository:**
   
   ```bash
   docker run -it --rm \
     -e OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY_HERE" \
     -v "$(pwd)/output_tutorials":/app/output \
     codeviz-app --repo https://github.com/username/repo
   ```
   
   **Example for analyzing a local directory:**
   
   ```bash
   docker run -it --rm \
     -e OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY_HERE" \
     -v "/path/to/your/local_codebase":/app/code_to_analyze \
     -v "$(pwd)/output_tutorials":/app/output \
     codeviz-app --dir /app/code_to_analyze
   ```
</details>

### Sample Output Generation
python main.py --repo https://github.com/rsrini7/ai-travel-agent --include "*.py" "*.sql" --exclude "tests/*" --max-size 50000
Warning: No GitHub token provided. You might hit rate limits for public repositories.
Starting tutorial generation for: https://github.com/rsrini7/ai-travel-agent in English language
LLM caching: Enabled
Crawling repository: https://github.com/rsrini7/ai-travel-agent...
Skipping .env.example: Does not match include/exclude patterns
Skipping .gitignore: Does not match include/exclude patterns
Skipping .python-version: Does not match include/exclude patterns
Skipping README.md: Does not match include/exclude patterns
Downloaded: app.py (992 bytes) 
Skipping assets/fonts/DejaVuSansCondensed-Bold.ttf: Does not match include/exclude patterns
Skipping assets/fonts/DejaVuSansCondensed-Oblique.ttf: Does not match include/exclude patterns
Skipping assets/fonts/DejaVuSansCondensed.ttf: Does not match include/exclude patterns
Skipping assets/top_banner.png: Does not match include/exclude patterns
Skipping assets/tripexplore-logo-with-rating.png: Does not match include/exclude patterns
Skipping requirements.txt: Does not match include/exclude patterns
Downloaded: schema-drop.sql (1009 bytes) 
Downloaded: schema.sql (5488 bytes) 
Downloaded: src/__init__.py (0 bytes) 
Downloaded: src/core/__init__.py (0 bytes) 
Downloaded: src/core/itinerary_generator.py (11423 bytes) 
Downloaded: src/core/quotation_graph_builder.py (27273 bytes) 
Downloaded: src/llm/__init__.py (0 bytes) 
Downloaded: src/llm/llm_prompts.py (12443 bytes) 
Downloaded: src/llm/llm_providers.py (5171 bytes) 
Downloaded: src/models.py (1559 bytes) 
Downloaded: src/ui/__init__.py (0 bytes) 
Downloaded: src/ui/components/__init__.py (0 bytes) 
Downloaded: src/ui/components/tab3_actions.py (17807 bytes) 
Downloaded: src/ui/components/tab3_ui_components.py (8001 bytes) 
Downloaded: src/ui/sidebar.py (7600 bytes) 
Downloaded: src/ui/tabs/__init__.py (0 bytes) 
Downloaded: src/ui/tabs/tab1_new_enquiry.py (4378 bytes) 
Downloaded: src/ui/tabs/tab2_manage_itinerary.py (6496 bytes) 
Downloaded: src/ui/tabs/tab3_vendor_quotation.py (8282 bytes) 
Downloaded: src/ui/ui_helpers.py (5059 bytes) 
Downloaded: src/utils/__init__.py (0 bytes) 
Downloaded: src/utils/constants.py (1261 bytes) 
Downloaded: src/utils/docx_utils.py (651 bytes) 
Downloaded: src/utils/pdf_utils.py (16097 bytes) 
Downloaded: src/utils/supabase_utils.py (10702 bytes) 
Downloaded: storage.sql (399 bytes) 
Skipping tests/llm/test_llm_providers.py: Does not match include/exclude patterns
Fetched 27 files.
Identifying abstractions using LLM...
Identifying abstractions using LLM...
Identified 8 abstractions.
Analyzing relationships using LLM...
Analyzing relationships using LLM...
Analyzing relationships using LLM...
Generated project summary and relationship details.
Determining chapter order using LLM...
Determined chapter order (indices): [5, 0, 1, 2, 3, 4, 6, 7]
Preparing to write 8 chapters...
Writing chapter 1 for: UI Tab Rendering (render_tab1, render_tab2, render_tab3)
 using LLM...
Writing chapter 2 for: App Session State (AppSessionState)
 using LLM...
Writing chapter 3 for: AI Configuration (AIConfigState)
 using LLM...
Writing chapter 4 for: Langchain Integration (Itinerary and Quotation Generation)
 using LLM...
Writing chapter 5 for: Quotation Generation Graph (StateGraph)
 using LLM...
Writing chapter 6 for: Supabase Utilities (supabase_utils.py)
 using LLM...
Writing chapter 7 for: Utility Functions (pdf_utils.py, docx_utils.py)
 using LLM...
Writing chapter 8 for: Error Handling (_extract_error_message_from_payload)
 using LLM...
Finished writing 8 chapters.
Combining tutorial into directory: output/ai-travel-agent
  - Wrote output/ai-travel-agent/index.md
  - Wrote output/ai-travel-agent/01_ui_tab_rendering__render_tab1__render_tab2__render_tab3__.md
  - Wrote output/ai-travel-agent/02_app_session_state__appsessionstate__.md
  - Wrote output/ai-travel-agent/03_ai_configuration__aiconfigstate__.md
  - Wrote output/ai-travel-agent/04_langchain_integration__itinerary_and_quotation_generation__.md
  - Wrote output/ai-travel-agent/05_quotation_generation_graph__stategraph__.md
  - Wrote output/ai-travel-agent/06_supabase_utilities__supabase_utils_py__.md
  - Wrote output/ai-travel-agent/07_utility_functions__pdf_utils_py__docx_utils_py__.md
  - Wrote output/ai-travel-agent/08_error_handling___extract_error_message_from_payload__.md

Tutorial generation complete! Files are in: output/ai-travel-agent

### References
Combined from below code bases.
https://github.com/The-Pocket/PocketFlow
https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge