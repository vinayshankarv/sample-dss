"""
Session and request management for Review II scraper.
"""

import requests
import random
import time
import logging
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SessionManager:
    """Manages HTTP sessions with retry logic and rate limiting."""
    
    def __init__(self, config):
        self.config = config
        self.session = self._create_session()
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """Create a configured requests session."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the configured list."""
        return random.choice(self.config.user_agents)
    
    def _rate_limit(self) -> None:
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_delay = 1.0 / self.config.concurrency_level  # Adaptive delay
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a rate-limited HTTP request with retry logic."""
        self._rate_limit()
        
        # Set random user agent for each request
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self._get_random_user_agent()
        kwargs['headers'] = headers
        
        # Set timeout
        kwargs.setdefault('timeout', self.config.request_timeout)
        
        try:
            self.logger.debug(f"Making request to: {url}")
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()