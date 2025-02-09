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

    