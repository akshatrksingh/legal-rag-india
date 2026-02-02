"""
Indian Kanoon Data Scraper
Fetches judgments from Indian Kanoon API for RAG system
"""

import requests
import json
import time
from typing import List, Dict, Optional
from pathlib import Path


class IndianKanoonScraper:
    """Scraper for Indian Kanoon API - supports both token and unauthenticated access"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.base_url = "https://api.indiankanoon.org"
        self.api_token = api_token
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "LegalRAG-Research-Bot/1.0"
        }
        
        # Add token auth if provided
        if api_token:
            self.headers["Authorization"] = f"Token {api_token}"
    
    def search_judgments(
        self, 
        query: str, 
        page: int = 0,
        doctypes: Optional[str] = None,
        fromdate: Optional[str] = None,
        todate: Optional[str] = None
    ) -> Dict:
        """
        Search for judgments using Indian Kanoon search API
        
        Args:
            query: Search query (can use ANDD, ORR, NOTT operators)
            page: Page number (starts from 0)
            doctypes: Filter by document types (e.g., "supremecourt,bombay")
            fromdate: Minimum date in DD-MM-YYYY format
            todate: Maximum date in DD-MM-YYYY format
        
        Returns:
            Dict with search results including docs, found count, categories
        """
        url = f"{self.base_url}/search/"
        params = {
            "formInput": query,
            "pagenum": page
        }
        
        if doctypes:
            params["doctypes"] = doctypes
        if fromdate:
            params["fromdate"] = fromdate
        if todate:
            params["todate"] = todate
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching judgments: {e}")
            return {"error": str(e), "docs": [], "found": 0}
    
    def get_document(self, doc_id: str, maxcites: int = 10) -> Dict:
        """
        Fetch full judgment document by ID
        
        Args:
            doc_id: Document ID (e.g., "123456")
            maxcites: Maximum number of citations to retrieve
        
        Returns:
            Dict with document content, title, citations, etc.
        """
        url = f"{self.base_url}/doc/{doc_id}/"
        params = {"maxcites": maxcites, "maxcitedby": maxcites}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching document {doc_id}: {e}")
            return {"error": str(e), "doc": None}
    
    def bulk_download(
        self, 
        query: str,
        max_docs: int = 1000,
        doctypes: Optional[str] = None,
        output_dir: str = "../data/raw",
        delay: float = 0.5
    ) -> List[Dict]:
        """
        Download multiple judgments for a query
        
        Args:
            query: Search query
            max_docs: Maximum number of documents to download
            doctypes: Filter by document types
            output_dir: Directory to save raw JSON files
            delay: Delay between requests (seconds) to avoid rate limiting
        
        Returns:
            List of downloaded documents
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        documents = []
        page = 0
        docs_per_page = 10  # Indian Kanoon returns ~10 results per page
        
        print(f"Starting bulk download for query: '{query}'")
        print(f"Target: {max_docs} documents")
        
        while len(documents) < max_docs:
            # Search for documents
            print(f"\nFetching page {page}...")
            search_results = self.search_judgments(
                query=query,
                page=page,
                doctypes=doctypes
            )
            
            if "error" in search_results or not search_results.get("docs"):
                print(f"No more results found. Stopping at {len(documents)} documents.")
                break
            
            docs = search_results["docs"]
            print(f"Found {len(docs)} documents on page {page}")
            
            # Fetch full content for each document
            for i, doc_summary in enumerate(docs):
                if len(documents) >= max_docs:
                    break
                
                doc_id = doc_summary.get("tid")
                if not doc_id:
                    continue
                
                print(f"  [{len(documents)+1}/{max_docs}] Downloading doc {doc_id}...", end=" ")
                
                # Get full document
                full_doc = self.get_document(doc_id)
                
                if "error" not in full_doc and full_doc.get("doc"):
                    # Add metadata from search results
                    full_doc["search_metadata"] = {
                        "title": doc_summary.get("title"),
                        "headline": doc_summary.get("headline"),
                        "docsource": doc_summary.get("docsource"),
                        "docsize": doc_summary.get("docsize")
                    }
                    
                    documents.append(full_doc)
                    
                    # Save individual document
                    doc_file = output_path / f"{doc_id}.json"
                    with open(doc_file, "w", encoding="utf-8") as f:
                        json.dump(full_doc, f, ensure_ascii=False, indent=2)
                    
                    print(f"Saved")
                else:
                    print(f"Failed")
                
                # Rate limiting
                time.sleep(delay)
            
            page += 1
            
            # Safety check: stop if we've tried too many pages
            if page > (max_docs // docs_per_page) + 10:
                print(f"\nReached page limit. Stopping at {len(documents)} documents.")
                break
        
        print(f"\nDownload complete! Total documents: {len(documents)}")
        
        # Save summary file
        summary_file = output_path / "_download_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({
                "query": query,
                "total_downloaded": len(documents),
                "doctypes": doctypes,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        
        return documents


def test_scraper():
    """Test the scraper with a few sample queries"""
    print("=" * 60)
    print("Testing Indian Kanoon Scraper")
    print("=" * 60)
    
    # Initialize without token (will use unauthenticated access)
    scraper = IndianKanoonScraper()
    
    # Test 1: Search for Supreme Court cases
    print("\nTEST 1: Searching for 'contract law' cases...")
    results = scraper.search_judgments("contract law", page=0, doctypes="supremecourt")
    
    if results.get("docs"):
        print(f"Found {results.get('found', 0)} total results")
        print(f"Retrieved {len(results['docs'])} documents on this page")
        print("\nFirst result:")
        first_doc = results["docs"][0]
        print(f"  Title: {first_doc.get('title', 'N/A')[:100]}...")
        print(f"  Doc ID: {first_doc.get('tid', 'N/A')}")
    else:
        print("No results found or error occurred")
        print(f"Response: {results}")
        return
    
    # Test 2: Fetch a full document
    print("\nTEST 2: Fetching full document...")
    doc_id = results["docs"][0]["tid"]
    full_doc = scraper.get_document(doc_id)
    
    if full_doc.get("doc"):
        print(f"Successfully retrieved document {doc_id}")
        print(f"  Title: {full_doc.get('title', 'N/A')[:100]}...")
        print(f"  Content length: {len(full_doc['doc'])} characters")
        print(f"  Citations: {len(full_doc.get('citeList', []))} cites")
    else:
        print("Failed to fetch document")
        print(f"Response: {full_doc}")
    
    print("\n" + "=" * 60)
    print("All tests passed! Scraper is working.")
    print("=" * 60)


if __name__ == "__main__":
    test_scraper()