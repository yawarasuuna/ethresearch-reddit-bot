# SPDX-License-Identifier: MIT 
# ETH Research Socials Bot - Scraper Script 
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
    
    def _extract_topic_id(self, url:str) -> str:
        """
        Extract topic ID from URL.

        Args: 
            url: Topic URL

        Returns:
            Topic ID string

        Raises: 
            ValueError: If topic ID cannot be extracted
        """
        try:
            url = url.rstrip('/')  ###
            return url.split('/')[-1]
        except (IndexError, AttributeError) as e:
            raise ValueError(f"Could not extract topic ID from {url}") from e

    def _parse_post_details(self, soup: BeautifulSoup, url:str) -> Optional[dict]:
        """
        Parse post details from BeautifulSoup object.

        Args:
            soup: BeatifulSoup object of the post page
            url: URL of the post

        Returns:
            Dictionary containing post details or None if Parsing fails
        """
        first_post = soup.find('div', {
            'id':'post_1',
            'class':'topic-body crawler-post'
        })
        if not isinstance(first_post, Tag):
            self.logger.warning("Could not find post #1 for {url}")
            return None

        author_element = first_post.select_one(
            'span[itemprop="author"] span[itemprop = "name]'
        )
        time_element = first_post.select_one('time[datetime]')

        if not all(isinstance(elem, Tag) for elem in [author_element, time_element]):
            self.logger.warning(f"Missing required elements for {url}")

        timestamp = time_element.get('datetime')
        if not timestamp:
            self.logger.warning(f"No datetime found for {url}")
            return None
        
        return {
            'author': author_element.get_text(strip=True),
            'timestamp': timestamp,
            'is_post_1': True
        }

    def get_topic_details(self, url: str) -> Optional[dict]:
        """
        Fetch and parse topic details from a given URL
        
        Args:
            url: Topic URL to fetch
            
        Returns:
            Dictionary containing topic details or None if fetching or parsing fails

        Raises:
            NetworkError: if network operations fail
            ParseError: if HTML parsing fails
        """
        try:
            html_content = self._fetch_with_retry(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            return self._parse_post_details(soup, url)
        except (NetworkError, ParseError) as e:
            self.logger.error(f"Error fetching topic details for {url}: {str(e)}")
            return None

    def get_latest_post(self) -> Optional[PostDetails]:
        """
        Fetch the latest Post #1 from ethresear.ch/latest.

        Returns: 
            PostDetails object for the latest post or None if no valid post is found

        Raises:
            NetworkError: if network operations fail
            ParseError: if HTML parsing fails
        """
        try:
            latest_url = urljoin(self.BASE_URL, self.LATEST_PATH)
            html_content = self._fetch_with_retry(latest_url)
            soup = BeautifulSoup(html_content, 'html.parser')

            topics = soup.select('tr.topic-list-item:not(.sticky)')
            self.logger.info(f"Found {len(topics)} topic rows")

            valid_posts = []
            for topic in topics[:self.MAX_TOPICS_TO_CHECK]:
                if not isinstance(topic, Tag):
                    continue

                title_element = topic.select_one('td.main-link a.title')
                if not isinstance(title_element, Tag):
                    continue

                title = title_element.get_text(strip=True)
                if any(phrase in title.lower() for phrase in self.SKIP_PHRASES):
                    self.logger.info(f"Skipping filtered posts {title}")
                    continue

                link = urljoin(self.BASE_URL, title_element.get('href', ''))
                topic_id = self._extract_topic_id(link)

                details = self.get_topic_details(link)
                if not details or not details.get('is_post_1'):
                    continue

                valid_posts.append({
                    'title': title,
                    'link': link,
                    'topic_id': topic_id,
                    'authors': [details['author']],
                    'timestamp': details['timestamp']
                })

            if not valid_posts:
                self.logger.warning("No valid Post #1s found")
                return None

            latest_post = max(
                valid_posts, key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')
                )
            )

            return PostDetails.from_dict(latest_post)

        except Exception as e:
            self.logger.error(f"Error in get_latest_post: {str(e)}")
            raise