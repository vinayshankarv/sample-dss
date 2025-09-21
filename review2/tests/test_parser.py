"""
Unit tests for the parser module.
"""

import pytest
from bs4 import BeautifulSoup
from review2.scraper.parser import Parser
from review2.scraper.config import Config


class TestParser:
    
    @pytest.fixture
    def parser(self):
        config = Config.default()
        return Parser(config)
    
    @pytest.fixture
    def sample_html(self):
        return """
        <html>
        <head>
            <title>Test Document</title>
            <meta name="document-id" content="12345">
            <meta name="author" content="Test Author">
        </head>
        <body>
            <h1 class="document-title">Sample Rule Document</h1>
            <div class="document-content">
                <h2 class="section-heading">Section 1</h2>
                <p>This is the content of section 1.</p>
                <h2 class="section-heading">Section 2</h2>
                <p>This is the content of section 2.</p>
            </div>
        </body>
        </html>
        """
    
    def test_extract_title(self, parser, sample_html):
        soup = BeautifulSoup(sample_html, 'html.parser')
        title = parser._extract_title(soup)
        assert title == "Sample Rule Document"
    
    def test_extract_id_from_meta(self, parser, sample_html):
        soup = BeautifulSoup(sample_html, 'html.parser')
        url = "https://example.com/rule/12345"
        doc_id = parser._extract_id(url, soup)
        assert doc_id == "12345"
    
    def test_extract_id_from_url(self, parser):
        soup = BeautifulSoup("<html></html>", 'html.parser')
        url = "https://example.com/rule/67890"
        doc_id = parser._extract_id(url, soup)
        assert doc_id == "67890"
    
    def test_extract_text(self, parser, sample_html):
        soup = BeautifulSoup(sample_html, 'html.parser')
        text = parser._extract_text(soup)
        assert "This is the content of section 1" in text
        assert "This is the content of section 2" in text
    
    def test_extract_sections(self, parser, sample_html):
        soup = BeautifulSoup(sample_html, 'html.parser')
        sections = parser._extract_sections(soup)
        assert len(sections) >= 2
        assert any("Section 1" in section['title'] for section in sections)
        assert any("Section 2" in section['title'] for section in sections)
    
    def test_extract_metadata(self, parser, sample_html):
        soup = BeautifulSoup(sample_html, 'html.parser')
        metadata = parser._extract_metadata(soup)
        assert metadata.get('document-id') == "12345"
        assert metadata.get('author') == "Test Author"
    
    def test_clean_text(self, parser):
        dirty_text = "  This   has\n\n  extra   whitespace  \t"
        clean = parser.clean_text(dirty_text)
        assert clean == "This has extra whitespace"
    
    def test_parse_page_complete(self, parser, sample_html):
        url = "https://example.com/rule/12345"
        data = parser.parse_page(sample_html, url)
        
        assert data['id'] == "12345"
        assert data['title'] == "Sample Rule Document"
        assert data['url'] == url
        assert data['text'] is not None
        assert len(data['sections']) >= 2
        assert 'scraped_at' in data
        assert 'metadata' in data
    
    def test_parse_page_with_error(self, parser):
        invalid_html = "This is not valid HTML"
        url = "https://example.com/test"
        data = parser.parse_page(invalid_html, url)
        
        # Should still return a valid structure even with parsing errors
        assert data['url'] == url
        assert 'scraped_at' in data
        assert isinstance(data['sections'], list)