import time
from ddgs import DDGS
def perform_web_search_ddgs(query: str, num_results: int = 5, retries: int = 3) -> list[dict]:
    """
    Performs a web search using DuckDuckGo and returns the results, with retry logic.
   
    Args:
        query: Search query string
        num_results: Number of results to return
        retries: Number of retry attempts on failure
       
    Returns:
        List of search results with 'title', 'link', and 'snippet' keys
    """
    print(f"🔍 Performing DuckDuckGo search for: {query}")
    for attempt in range(retries):
        try:
            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y')):
                    if i >= num_results:
                        break
                    results.append({
                        'title': r.get('title'),
                        'link': r.get('href'),
                        'snippet': r.get('body')
                    })
            return results
        except Exception as e:
            print(f"⚠️ DuckDuckGo Search error (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print("❌ Search failed after multiple retries.")
    return []
