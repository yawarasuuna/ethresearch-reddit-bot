# SPDX-License-Identifier: WTFPL 
# ETH Research Bot - Main Script 
# See LICENSE file for full license details.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, NoReturn
import logging
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException

# Custom exceptions for better error handling
class ScraperException(Exception):
    """Base exception for scraper-related errors."""

class NetworkError(ScraperException):
    """Raised when network-related operations fail."""

class ParseError(ScraperException):
    """Raised when HTML parsing operations fail."""

@dataclass(frozen=True)
class PostDetails:
    """Immutable data class for post details."""
    title: str
    link: str
    topic_id: str
    authors: List[str]
    timestamp: datetime

@classmethod
def from_dict(cls, data:dict) -> PostDetails:
    """Creat PostDetails from dictionary data."""
    return cls(
        title=data['title'],
        link=data['link'],
        topic_id=date['topic_id'],
        authors=data['authors'],
        timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    )

class EthResearchScraper:
    """Scraper for ethresear.ch website."""
    
    # Class-level constants
    BASE_URL = "https://ethresear.ch"
    LATEST_PATH = "/latest"
    MAX_TOPICS_TO_CHECK = 20
    SKIP_PHRASES = frozenset({
        'read this before posting',
        'read before posting',
        'posting guidelines',
        'posting rules'
    })

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: int = 5,
        timeout: int = 30
    ) -> None:
        """
        Initialize the scraper with configurable retry parameters.

        Args:
            max_retries: Maximum number of retry attemps for failed requests
            retry_delay: Delay in seconds between retry attemps
            timeout: Request timeout in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETHResearchSocialsBot/1.0 (Compatible; Research Project)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _fetch_with_retry(self, url: str) -> str:
        """
        Fetch a URL with retry logic for handling temporary failures

        Args:
            url: The URL to fetch

        Returns:
            The response text content

        Raises:
            NetworkError: If all try attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.text
            except RequestException as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}) for {url}: {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    retry_delay = self.retry_delay * (2 ** attempt)    #testing exponential backoff
                    self.logger.info(f"Waiting {retry_delay}s before retrying...")
                    time.sleep(retry_delay)
                else:
                    raise NetworkError(f"All attempts failed for {url}") from e