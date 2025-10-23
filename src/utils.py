import json
import re
import asyncio
from typing import Union, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LXMLWebScrapingStrategy
from src.config import CONFIG
def perform_web_search(query: str, num_results: int = 5, retries: int = 3) -> list[dict]:
    """
    Performs a web search using the configured provider (DuckDuckGo or Google).
   
    This function acts as an abstraction layer - it automatically uses the correct
    search provider based on the config.yaml settings.
   
    Args:
        query: Search query string
        num_results: Number of results to return
        retries: Number of retry attempts on failure
       
    Returns:
        List of search results with 'title', 'link', and 'snippet' keys
    """
    provider = CONFIG.get('search', {}).get('provider', 'ddgs')
   
    if provider == 'google':
        from src.utils_google import perform_web_search_google
       
        google_config = CONFIG.get('search', {}).get('google', {})
        api_key = google_config.get('api_key')
        cse_id = google_config.get('search_engine_id')
       
        if not api_key or not cse_id:
            print("⚠️ Google API credentials not configured. Falling back to DuckDuckGo.")
            provider = 'ddgs'
        else:
            return perform_web_search_google(query, api_key, cse_id, num_results, retries)
   
    # Default to DuckDuckGo
    from src.utils_ddgs import perform_web_search_ddgs
    return perform_web_search_ddgs(query, num_results, retries)
async def scrape_website_with_crawl4ai_async(url: str) -> str:
    """
    Asynchronously scrapes a website using crawl4ai to get the markdown content.
    """
    print(f" 🕷️ Scraping with crawl4ai from {url}...")
    try:
        browser_cfg = BrowserConfig(
            headless=True,
            user_agent_mode='random'
        )
        crawler_cfg = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy()
        )
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=crawler_cfg)
           
            if result and getattr(result, 'success', False) and result.markdown and result.markdown.raw_markdown:
                print(" ✅ crawl4ai scraping successful.")
                return result.markdown.raw_markdown
            else:
                error_info = getattr(result, 'error', 'Unknown error') if result else 'No result object'
                print(f" ⚠️ crawl4ai scraping failed. Reason: {error_info}")
                return ""
    except Exception as e:
        print(f" ⚠️ An error occurred during crawl4ai scraping: {e}")
        return ""
def get_website_text(url: str) -> str:
    """
    Synchronous wrapper for the async crawl4ai scraper.
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            future = asyncio.ensure_future(scrape_website_with_crawl4ai_async(url))
            return asyncio.get_event_loop().run_until_complete(future)
        else:
            return loop.run_until_complete(scrape_website_with_crawl4ai_async(url))
    except RuntimeError:
        return asyncio.run(scrape_website_with_crawl4ai_async(url))
def parse_json_from_llm_response(llm_output: str) -> Optional[Union[dict, list]]:
    """
    Finds, cleans, and parses a JSON object or list from a string,
    including handling markdown code blocks and common LLM errors.
    """
    match = re.search(r'''```json\s*(\{.*\}|\[.*\])\s*```|(\{.*\}|\[.*\])''', llm_output, re.DOTALL)
    if not match:
        return None
   
    json_string = match.group(1) or match.group(2)
    # Replace single-quoted keys with double-quoted keys
    json_string = re.sub(r"(?<=[{\[,])\s*'([a-zA-Z_][a-zA-Z0-9_]*)'\s*:", r'"\1":', json_string)
   
    # Remove trailing commas
    json_string = re.sub(r',\s*([\}\]])', r'\1', json_string)
   
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        try:
            # Fallback: try to replace all remaining single quotes
            return json.loads(json_string.replace("'", '"'))
        except json.JSONDecodeError:
            return None
