"""
HTML parsing and content extraction for Review II scraper.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup, Tag
from datetime import datetime


class Parser:
    """Handles HTML parsing and content extraction."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def parse_page(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse a page and extract structured data."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            data = {
                'id': self._extract_id(url, soup),
                'title': self._extract_title(soup),
                'url': url,
                'text': self._extract_text(soup),
                'sections': self._extract_sections(soup),
                'metadata': self._extract_metadata(soup),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing page {url}: {str(e)}")
            return {
                'id': None,
                'title': None,
                'url': url,
                'text': None,
                'sections': [],
                'metadata': {},
                'scraped_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _extract_id(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        """Extract unique identifier from URL or page content."""
        # Try to extract ID from URL patterns
        id_patterns = [
            r'/rule/(\d+)',
            r'/regulation/(\d+)',
            r'/document/(\d+)',
            r'id=(\d+)',
            r'/(\d+)/?$'
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try to find ID in meta tags or data attributes
        meta_id = soup.find('meta', {'name': 'document-id'})
        if meta_id and meta_id.get('content'):
            return meta_id['content']
        
        # Try data-id attributes
        element_with_id = soup.find(attrs={'data-id': True})
        if element_with_id:
            return element_with_id['data-id']
        
        # Generate ID from URL hash as fallback
        return str(hash(url))
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        # Try different title sources in order of preference
        title_selectors = [
            'h1.document-title',
            'h1.rule-title',
            '.page-title h1',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = self.clean_text(element.get_text())
                if title:
                    return title
        
        return None
    
    def _extract_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main text content."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            '.document-content',
            '.rule-content',
            '.main-content',
            'main',
            '.content',
            'article'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = self.clean_text(element.get_text())
                if text and len(text) > 100:  # Ensure substantial content
                    return text
        
        # Fallback to body text
        body = soup.find('body')
        if body:
            return self.clean_text(body.get_text())
        
        return None
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract document sections."""
        sections = []
        
        # Look for section headers and content
        section_headers = soup.find_all(['h2', 'h3', 'h4'], class_=re.compile(r'section|heading'))
        
        for i, header in enumerate(section_headers):
            section_id = header.get('id') or f"section_{i+1}"
            section_title = self.clean_text(header.get_text())
            
            # Find content until next header
            content_elements = []
            current = header.next_sibling
            
            while current and current.name not in ['h2', 'h3', 'h4']:
                if hasattr(current, 'get_text'):
                    content_elements.append(current)
                current = current.next_sibling
            
            section_text = ' '.join([self.clean_text(elem.get_text()) 
                                   for elem in content_elements if hasattr(elem, 'get_text')])
            
            if section_title or section_text:
                sections.append({
                    'id': section_id,
                    'title': section_title,
                    'text': section_text
                })
        
        return sections
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {}
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Extract specific document metadata
        date_published = soup.find('time', {'class': 'published'})
        if date_published:
            metadata['date_published'] = date_published.get('datetime') or date_published.get_text()
        
        # Extract author information
        author = soup.find(class_=re.compile(r'author|byline'))
        if author:
            metadata['author'] = self.clean_text(author.get_text())
        
        # Extract document type
        doc_type = soup.find(class_=re.compile(r'document-type|rule-type'))
        if doc_type:
            metadata['document_type'] = self.clean_text(doc_type.get_text())
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        return text