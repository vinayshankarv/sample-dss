"""
URL handling and pattern matching for Review II scraper.
"""

import re
import logging
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class UrlHandler:
    """Handles URL discovery and pattern matching."""
    
    def __init__(self, config):
        self.config = config
        self.final_page_patterns = [re.compile(pattern) for pattern in config.final_page_patterns]
        self.visited_urls: Set[str] = set()
        self.logger = logging.getLogger(__name__)
    
    def is_final_page(self, url: str) -> bool:
        """Check if URL matches final page patterns."""
        for pattern in self.final_page_patterns:
            if pattern.search(url):
                return True
        return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format and accessibility."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except Exception:
            return False
    
    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract all links from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                
                if self.validate_url(absolute_url) and absolute_url not in self.visited_urls:
                    links.append(absolute_url)
            
            return links
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {base_url}: {str(e)}")
            return []
    
    def discover_urls(self, start_urls: List[str], max_depth: int = 2) -> List[str]:
        """Discover URLs through crawling with depth limit."""
        discovered = set(start_urls)
        to_crawl = list(start_urls)
        depth = 0
        
        while to_crawl and depth < max_depth:
            current_batch = to_crawl.copy()
            to_crawl.clear()
            
            for url in current_batch:
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                
                # If this is a final page, don't crawl further
                if self.is_final_page(url):
                    continue
                
                # Extract links from this page
                # Note: This would require making a request, which should be done
                # through the session manager in the main scraper
                
            depth += 1
        
        return list(discovered)
    
    def filter_final_pages(self, urls: List[str]) -> List[str]:
        """Filter URLs to only include final pages."""
        return [url for url in urls if self.is_final_page(url)]
    
    def get_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            return urlparse(url).netloc
        except Exception:
            return None