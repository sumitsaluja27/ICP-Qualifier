import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
def perform_web_search_google(query: str, api_key: str, cse_id: str, num_results: int = 5, retries: int = 3) -> list[dict]:
    """
    Performs a web search using Google Custom Search API.
   
    Args:
        query: Search query string
        api_key: Google API key
        cse_id: Custom Search Engine ID
        num_results: Number of results to return (max 10 per request)
        retries: Number of retry attempts on failure
       
    Returns:
        List of search results with 'title', 'link', and 'snippet' keys
    """
    print(f"🔍 Performing Google Custom Search for: {query}")
   
    if not api_key or not cse_id:
        print("❌ Google API key or CSE ID not provided")
        return []
   
    for attempt in range(retries):
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(
                q=query,
                cx=cse_id,
                num=min(num_results, 10) # Google API max is 10 per request
            ).execute()
           
            items = result.get('items', [])
            results = []
            for item in items:
                results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet')
                })
           
            return results
           
        except HttpError as e:
            print(f"⚠️ Google API error (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print("❌ Search failed after multiple retries.")
        except Exception as e:
            print(f"⚠️ Unexpected error (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2)
   
    return []
