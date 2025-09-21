"""
Unit tests for the URL handler module.
"""

import pytest
from review2.scraper.url_handler import UrlHandler
from review2.scraper.config import Config


class TestUrlHandler:
    
    @pytest.fixture
    def url_handler(self):
        config = Config.default()
        return UrlHandler(config)
    
    def test_is_final_page_positive(self, url_handler):
        test_urls = [
            "https://example.com/rule/123",
            "https://example.com/regulation/456",
            "https://example.com/document/789"
        ]
        
        for url in test_urls:
            assert url_handler.is_final_page(url)
    
    def test_is_final_page_negative(self, url_handler):
        test_urls = [
            "https://example.com/home",
            "https://example.com/search",
            "https://example.com/category/rules"
        ]
        
        for url in test_urls:
            assert not url_handler.is_final_page(url)
    
    def test_validate_url_valid(self, url_handler):
        valid_urls = [
            "https://example.com/test",
            "http://example.com/test",
            "https://subdomain.example.com/path/to/page"
        ]
        
        for url in valid_urls:
            assert url_handler.validate_url(url)
    
    def test_validate_url_invalid(self, url_handler):
        invalid_urls = [
            "not-a-url",
            "ftp://example.com/test",
            "",
            "javascript:alert('test')"
        ]
        
        for url in invalid_urls:
            assert not url_handler.validate_url(url)
    
    def test_filter_final_pages(self, url_handler):
        mixed_urls = [
            "https://example.com/rule/123",  # final
            "https://example.com/home",      # not final
            "https://example.com/regulation/456",  # final
            "https://example.com/search"     # not final
        ]
        
        final_urls = url_handler.filter_final_pages(mixed_urls)
        assert len(final_urls) == 2
        assert "https://example.com/rule/123" in final_urls
        assert "https://example.com/regulation/456" in final_urls
    
    def test_get_domain(self, url_handler):
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("http://subdomain.example.com/path", "subdomain.example.com"),
            ("https://example.com:8080/path", "example.com:8080")
        ]
        
        for url, expected_domain in test_cases:
            assert url_handler.get_domain(url) == expected_domain
    
    def test_get_domain_invalid(self, url_handler):
        invalid_urls = ["not-a-url", "", None]
        
        for url in invalid_urls:
            assert url_handler.get_domain(url) is None