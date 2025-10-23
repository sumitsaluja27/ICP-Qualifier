import argparse
import json
import re
import time
from typing import Optional, List, Dict, Set
import concurrent.futures
import itertools
from src.advanced_dashcam_rag import AdvancedDashcamRAG
from src.utils import perform_web_search, parse_json_from_llm_response, get_website_text
from src.config import CONFIG, RESULTS_FILE
class DashcamCompanyFinder:
    def __init__(self):
        print("🚀 Initializing DashcamCompanyFinder V6...")
        self.rag = AdvancedDashcamRAG()
        self.rag.setup_vector_database()
       
        # Load configuration
        self.discovery_config = CONFIG.get('discovery', {})
        self.scoring_config = CONFIG.get('scoring', {})
        self.revenue_config = CONFIG.get('revenue', {})
        self.processing_config = CONFIG.get('processing', {})
       
        # Extract commonly used values
        self.discovery_sources = self.discovery_config.get('sources', {})
        self.positive_keywords = self.discovery_config.get('positive_keywords', [])
        self.heuristic_keywords = self.discovery_config.get('heuristic_keywords', [])
        self.exemplar_companies = self.scoring_config.get('exemplar_companies', [])
        self.financial_sources = self.revenue_config.get('financial_sources', [])
        self.relevance_threshold = self.scoring_config.get('relevance_threshold', 7)
        self.revenue_threshold = self.revenue_config.get('minimum_threshold_millions', 15)
        self.fallback_enabled = self.revenue_config.get('fallback_enabled', True)
    def _verify_is_company(self, item: dict, retries: int = 2) -> Optional[str]:
        """
        Verify if a search result is a real company.
       
        Args:
            item: Search result item with 'title' and 'snippet'
            retries: Number of retry attempts
           
        Returns:
            Company name if verified, None otherwise
        """
        question = '''
        Analyze the search result. Is this a direct link to a specific company that sells products or services?
        Do not be fooled by blog posts, news articles, or directories.
        Return a JSON object like {"is_company": true, "company_name": "Corrected Company Name"} or {"is_company": false, "company_name": null}.
        '''
        context = f"Title: {item.get('title', '')}\nSnippet: {item.get('snippet', '')}"
        for attempt in range(retries):
            llm_response = self.rag.analyze_text(context, question, model_type='fast')
            data = parse_json_from_llm_response(llm_response)
            if data and isinstance(data, dict) and "is_company" in data:
                if data.get("is_company"):
                    return data.get("company_name")
                else:
                    return None # Explicitly not a company
           
            print(f" ⚠️ _verify_is_company failed (Attempt {attempt + 1}/{retries}). Retrying...")
            time.sleep(0.5)
        return None
    def _passes_heuristic_filter(self, website_text: str) -> bool:
        """
        Quick keyword-based filter to avoid expensive LLM calls.
       
        Args:
            website_text: Text content from company website
           
        Returns:
            True if website contains relevant keywords
        """
        if not website_text:
            return False
        text_lower = website_text.lower()
        for keyword in self.heuristic_keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    def _score_relevance(self, company_name: str, website_text: str, retries: int = 2) -> int:
        """
        Score company relevance using LLM analysis.
       
        Args:
            company_name: Name of the company
            website_text: Text content from company website
            retries: Number of retry attempts
           
        Returns:
            Relevance score from 0-10
        """
        question = f'''
        My ideal customer works in fleet management, telematics, or automotive electronics. Examples of perfect-fit companies: {str(self.exemplar_companies)}.
        Analyze the text from the website of a candidate company called "{company_name}".
        Important: Companies primarily in China, Hong Kong, or Taiwan should get a score of 0.
        Based on all rules, how relevant is this company? Return JSON with a score from 0-10 and reasoning.
        Example: {{'relevance_score': 8, 'reasoning': 'The website focuses on fleet telematics, a direct fit.'}}
        '''
        for attempt in range(retries):
            llm_response = self.rag.analyze_text(website_text, question, model_type='creative')
            data = parse_json_from_llm_response(llm_response)
            if data and isinstance(data, dict) and "relevance_score" in data:
                return int(data.get("relevance_score", 0))
            print(f" ⚠️ _score_relevance failed (Attempt {attempt + 1}/{retries}). Retrying...")
            time.sleep(0.5)
        return 0
    def _get_revenue_from_financial_sites(self, company_name: str) -> Optional[float]:
        """
        Search financial data sources for company revenue.
       
        Args:
            company_name: Name of the company
           
        Returns:
            Annual revenue in millions USD, or None if not found
        """
        print(f" 💰 Performing financial analysis for '{company_name}'...")
       
        for source in self.financial_sources:
            search_results = perform_web_search(f'site:{source} "{company_name}" annual revenue', num_results=2)
            if not search_results:
                continue
           
            context = "\n".join([f"Snippet: {item.get('snippet', '')}" for item in search_results])
            question = '''Analyze the text to find the annual revenue. Return JSON like {"revenue_in_millions": 50.5} or null.'''
            llm_response = self.rag.analyze_text(context, question, model_type='fast')
            data = parse_json_from_llm_response(llm_response)
           
            if data and isinstance(data, dict) and isinstance(data.get("revenue_in_millions"), (int, float)):
                revenue = data.get("revenue_in_millions")
                print(f" 💵 Found potential revenue on {source}: ${revenue}M")
                return revenue
       
        return None
    def _get_revenue_from_website_fallback(self, company_name: str, website_text: str) -> Optional[float]:
        """
        Fallback: Try to estimate revenue from website text analysis.
       
        Args:
            company_name: Name of the company
            website_text: Text content from company website
           
        Returns:
            Estimated annual revenue in millions USD, or None if not found
        """
        print(f" 🔍 Attempting fallback revenue detection for '{company_name}'...")
       
        question = f'''
        Analyze the website text for "{company_name}" to find any indicators of company size or revenue:
        - Direct revenue mentions
        - Funding announcements (e.g., "raised $50M")
        - Employee count (rough estimate: 100 employees ≈ $10M revenue)
        - Number of customers or contracts
        - Company size descriptions ("leading provider", "startup", etc.)
       
        Return JSON with your best estimate:
        {{"revenue_in_millions": 25.0, "confidence": "low/medium/high", "reasoning": "..."}}
       
        If no indicators found, return null.
        '''
       
        llm_response = self.rag.analyze_text(website_text, question, model_type='creative')
        data = parse_json_from_llm_response(llm_response)
       
        if data and isinstance(data, dict) and isinstance(data.get("revenue_in_millions"), (int, float)):
            revenue = data.get("revenue_in_millions")
            confidence = data.get("confidence", "unknown")
            reasoning = data.get("reasoning", "No reasoning provided")
            print(f" 💡 Fallback estimate: ${revenue}M (confidence: {confidence})")
            print(f" Reasoning: {reasoning}")
            return revenue
       
        return None
    def _process_search_item(self, item: Dict, existing_company_names: Set[str]) -> Optional[Dict]:
        """
        Process a single search result item.
       
        Args:
            item: Search result dictionary
            existing_company_names: Set of already processed company names
           
        Returns:
            Company dict if relevant, None otherwise
        """
        link = item.get('link')
        if not link:
            return None
        company_name = self._verify_is_company(item)
        if not company_name or company_name in existing_company_names:
            return None
        print(f" ✓ Verified as company: {company_name}")
        website_text = get_website_text(link)
       
        if self._passes_heuristic_filter(website_text):
            relevance_score = self._score_relevance(company_name, website_text)
            if relevance_score >= self.relevance_threshold:
                print(f" 🎯 RELEVANT (Score: {relevance_score}/10). Adding to list for revenue check.")
                return {"name": company_name, "website": link, "website_text": website_text}
            else:
                print(f" ⚠️ SKIPPED: {company_name} (Not relevant, score: {relevance_score}/10).")
        else:
            print(f" ⚠️ SKIPPED: {company_name} (Failed heuristic filter).")
       
        return None
    def _enrich_company(self, company: Dict) -> Optional[Dict]:
        """
        Enrich company data with revenue information.
       
        Args:
            company: Company dictionary with 'name', 'website', and optionally 'website_text'
           
        Returns:
            Enriched company dict if qualified, None otherwise
        """
        company_name = company["name"]
       
        # Try premium financial sources first
        estimated_revenue_m = self._get_revenue_from_financial_sites(company_name)
       
        # Fallback to website analysis if enabled and premium sources failed
        if estimated_revenue_m is None and self.fallback_enabled:
            website_text = company.get("website_text", "")
            if website_text:
                estimated_revenue_m = self._get_revenue_from_website_fallback(company_name, website_text)
       
        # Clean up website_text before saving (it's large and no longer needed)
        if "website_text" in company:
            del company["website_text"]
       
        if estimated_revenue_m and estimated_revenue_m >= self.revenue_threshold:
            company["estimated_revenue_in_millions"] = estimated_revenue_m
            print(f" 🏆 QUALIFIED: {company_name} | Revenue ~${estimated_revenue_m:.2f}M")
            return company
        else:
            print(f" ⚠️ DISCARDED: {company_name} (Revenue not found or < ${self.revenue_threshold}M).")
            return None
    def find_companies(self, territory: str, limit: int | None = None) -> list[dict]:
        """
        Find and qualify companies in the specified territory.
       
        Args:
            territory: Geographic territory (e.g., "USA", "Europe", "Middle_East")
            limit: Maximum number of new companies to find (None for unlimited)
           
        Returns:
            List of qualified company dictionaries
        """
        # Load existing results
        try:
            with open(RESULTS_FILE, 'r') as f:
                all_found_companies = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_found_companies = []
       
        existing_company_names = {comp.get('name') for comp in all_found_companies}
        print(f"📊 Loaded {len(existing_company_names)} previously found companies.")
        # --- STAGE 1: DISCOVERY & RELEVANCE SCORING (Profile-by-Profile Batches) ---
        print("\n--- STAGE 1: DISCOVERY & RELEVANCE SCORING ---")
        company_profiles = self.rag.get_target_company_profiles(territory)
        discovery_sources = self.discovery_sources.get(territory, self.discovery_sources.get("USA", []))
        all_relevant_companies = []
        processed_in_run = set()
        for profile in company_profiles:
            print(f"\n--- Processing Profile Batch: '{profile}' ---")
            profile_queries = [f'site:{source} "{profile} {keyword}"'
                               for keyword in self.positive_keywords
                               for source in discovery_sources]
            print(f" 🔎 Performing {len(profile_queries)} web searches in parallel...")
            search_items = []
           
            max_search_workers = self.processing_config.get('max_parallel_searches', 15)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_search_workers) as executor:
                future_to_query = {executor.submit(perform_web_search, query, 2): query for query in profile_queries}
                for future in concurrent.futures.as_completed(future_to_query):
                    try:
                        results = future.result()
                        if results:
                            search_items.extend(results)
                    except Exception as exc:
                        print(f' ⚠️ A search query generated an exception: {exc}')
            print(f" 📝 Found {len(search_items)} potential items. Processing in parallel...")
           
            names_to_skip = existing_company_names | processed_in_run
           
            max_process_workers = self.processing_config.get('max_parallel_processing', 10)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_process_workers) as executor:
                future_to_item = {executor.submit(self._process_search_item, item, names_to_skip): item for item in search_items}
                for future in concurrent.futures.as_completed(future_to_item):
                    try:
                        result = future.result()
                        if result:
                            if result['name'] not in names_to_skip:
                                all_relevant_companies.append(result)
                                processed_in_run.add(result['name'])
                    except Exception as exc:
                        print(f' ⚠️ An item processing generated an exception: {exc}')
        # --- STAGE 2: REVENUE ENRICHMENT (Parallelized) ---
        print(f"\n--- STAGE 2: REVENUE ENRICHMENT for {len(all_relevant_companies)} relevant companies ---")
        qualified_companies = []
       
        if not all_relevant_companies:
            print("No new relevant companies found to enrich.")
        else:
            max_enrich_workers = self.processing_config.get('max_parallel_enrichment', 10)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_enrich_workers) as executor:
                future_to_company = {executor.submit(self._enrich_company, company): company for company in all_relevant_companies}
                for future in concurrent.futures.as_completed(future_to_company):
                    if limit is not None and len(qualified_companies) >= limit:
                        print(f"\n🎯 Reached limit of {limit} new companies. Cancelling remaining tasks.")
                        # Attempt to cancel remaining futures
                        for f in future_to_company:
                            f.cancel()
                        break
                   
                    try:
                        result = future.result()
                        if result:
                            qualified_companies.append(result)
                    except Exception as exc:
                        print(f'⚠️ An enrichment task generated an exception: {exc}')
       
        # Save results
        if qualified_companies:
            all_found_companies.extend(qualified_companies)
            with open(RESULTS_FILE, 'w') as f:
                json.dump(all_found_companies, f, indent=4)
            print(f"\n💾 Saved {len(qualified_companies)} new qualified companies to {RESULTS_FILE}.")
        return qualified_companies
def main():
    parser = argparse.ArgumentParser(description="Find potential dashcam customers.")
    parser.add_argument("territory", type=str, nargs='?', default="USA",
                       help="The geographical territory to search in (e.g., 'USA', 'Europe', 'Middle_East').")
    parser.add_argument("--test-profiles", action="store_true",
                       help="Run the company profile generation test and exit.")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit the number of new companies to find.")
    args = parser.parse_args()
    if args.test_profiles:
        rag = AdvancedDashcamRAG()
        rag.setup_vector_database()
        profiles = rag.get_target_company_profiles(territory=args.territory)
        print("\n--- CUSTOMER PROFILE TEST RESULT ---")
        print(json.dumps(profiles, indent=4))
        return
    finder = DashcamCompanyFinder()
    companies = finder.find_companies(args.territory, limit=args.limit)
    print("\n--- FINAL RESULT ---")
    print(json.dumps(companies, indent=4))
if __name__ == "__main__":
    main()
