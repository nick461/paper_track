"""Semantic Scholar API client for fetching paper citation data.

This module provides functionality to fetch citation counts and other metrics
from Semantic Scholar API to help identify classic/influential papers.
"""

import logging
import time
from typing import Dict, Any, Optional, List
import requests
from urllib.parse import quote

from src.logging_config import get_logger

logger = get_logger(__name__)


class ScholarClient:
    def __init__(self, base_url: str = "https://api.semanticscholar.org/graph/v1"):
        self.base_url = base_url
        self.timeout = 30  # seconds
        self.request_delay = 1.0  # seconds between requests (to avoid rate limiting)
        self.last_request_time = 0  # track last request time

    def _wait_for_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.request_delay:
            wait_time = self.request_delay - time_since_last_request
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next request")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def search_paper_by_title(self, title: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        # Wait to respect rate limiting
        self._wait_for_rate_limit()

        for attempt in range(max_retries):
            try:
                # Build search URL
                search_url = f"{self.base_url}/paper/search"
                params = {
                    "query": title,
                    "fields": "title,citationCount,influentialCitationCount,year,authors,venue",
                    "limit": 1
                }

                logger.debug(f"Searching Semantic Scholar for: {title[:50]}... (attempt {attempt + 1}/{max_retries})")

                response = requests.get(
                    search_url,
                    params=params,
                    timeout=self.timeout
                )

                # Handle rate limiting (429 status code)
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                        logger.warning(
                            f"Rate limit hit (429). Waiting {wait_time}s before retry "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} attempts for: {title[:50]}...")
                        return None

                response.raise_for_status()

                data = response.json()

                if data.get("data") and len(data["data"]) > 0:
                    paper_data = data["data"][0]
                    logger.debug(
                        f"Found paper: {paper_data.get('title', 'N/A')}, "
                        f"citations: {paper_data.get('citationCount', 0)}"
                    )
                    return paper_data
                else:
                    logger.debug(f"No results found for: {title[:50]}...")
                    return None

            except requests.exceptions.Timeout as e:
                logger.warning(f"Semantic Scholar API timeout for '{title[:50]}...': {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"Semantic Scholar API error for '{title[:50]}...': {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return None

            except Exception as e:
                logger.error(f"Unexpected error searching Semantic Scholar: {e}")
                return None

        return None

    def get_paper_metrics(self, title: str) -> Dict[str, Any]:
        paper_data = self.search_paper_by_title(title)

        if not paper_data:
            return {
                "citation_count": 0,
                "influential_citation_count": 0,
                "year": None,
                "found": False
            }

        return {
            "citation_count": paper_data.get("citationCount", 0),
            "influential_citation_count": paper_data.get("influentialCitationCount", 0),
            "year": paper_data.get("year"),
            "found": True
        }

    def is_classic_paper(
        self,
        title: str,
        min_citations: int = 10,
        min_influential_citations: int = 5
    ) -> bool:
        metrics = self.get_paper_metrics(title)

        if not metrics["found"]:
            logger.debug(f"Paper not found in Semantic Scholar: {title[:50]}...")
            return False

        citation_count = metrics["citation_count"]
        influential_count = metrics["influential_citation_count"]

        # Check if paper meets classic criteria
        is_classic = (
            citation_count >= min_citations and
            influential_count >= min_influential_citations
        )

        if is_classic:
            logger.info(
                f"Classic paper identified: '{title[:50]}...' "
                f"(citations: {citation_count}, influential: {influential_count})"
            )

        return is_classic

    def filter_classic_papers(
        self,
        titles: List[str],
        min_citations: int = 10,
        min_influential_citations: int = 5
    ) -> List[str]:
        classic_titles = []

        for title in titles:
            if self.is_classic_paper(title, min_citations, min_influential_citations):
                classic_titles.append(title)

        logger.info(
            f"Filtered {len(classic_titles)} classic papers from {len(titles)} candidates"
        )

        return classic_titles
