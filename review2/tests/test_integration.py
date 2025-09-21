"""
Integration tests for the Review II scraper.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from review2.scraper.config import Config
from review2.scraper.scraper_main import ReviewScraper


class TestIntegration:
    
    @pytest.fixture
    def temp_output_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def test_config(self, temp_output_dir):
        return Config(
            start_urls=[
                "https://example.com/rule/123",
                "https://example.com/regulation/456",
                "https://example.com/document/789"
            ],
            output_folder=temp_output_dir,
            concurrency_level=1,
            max_retries=1,
            output_format="json",
            save_html=False
        )
    
    @pytest.fixture
    def mock_response(self):
        mock_resp = Mock()
        mock_resp.text = """
        <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Test Rule</h1>
            <div class="content">
                <p>This is test content for the rule.</p>
            </div>
        </body>
        </html>
        """
        mock_resp.raise_for_status.return_value = None
        return mock_resp
    
    @patch('review2.scraper.session_manager.requests.Session.get')
    def test_dry_run_integration(self, mock_get, test_config, mock_response):
        """Test dry run mode with mocked HTTP requests."""
        mock_get.return_value = mock_response
        
        scraper = ReviewScraper(test_config)
        
        try:
            result = scraper.run_dry_run()
            
            # Verify dry run results
            assert result['dry_run'] is True
            assert result['total_urls'] == 3
            assert result['final_page_urls'] == 3
            assert result['sample_scraped'] == 3
            assert len(result['sample_data']) == 3
            
            # Verify sample data structure
            for data in result['sample_data']:
                assert 'id' in data
                assert 'title' in data
                assert 'url' in data
                assert 'text' in data
                assert 'scraped_at' in data
                
                # Should have extracted content
                if not data.get('error'):
                    assert data['title'] == "Test Rule"
                    assert "test content" in data['text'].lower()
        
        finally:
            scraper.close()
    
    @patch('review2.scraper.session_manager.requests.Session.get')
    def test_full_run_integration(self, mock_get, test_config, mock_response):
        """Test full run mode with mocked HTTP requests."""
        mock_get.return_value = mock_response
        
        scraper = ReviewScraper(test_config)
        
        try:
            result = scraper.run_full_scrape()
            
            # Verify full run results
            assert result['dry_run'] is False
            assert result['total_urls'] == 3
            assert result['final_page_urls'] == 3
            assert result['scraped_records'] == 3
            assert 'saved_files' in result
            
            # Verify output files were created
            assert 'json' in result['saved_files']
            json_file = result['saved_files']['json']
            assert os.path.exists(json_file)
            
            # Verify report file was created
            assert 'report' in result['saved_files']
            report_file = result['saved_files']['report']
            assert os.path.exists(report_file)
        
        finally:
            scraper.close()
    
    def test_config_validation_integration(self):
        """Test that invalid configurations are properly rejected."""
        # Test empty URLs
        with pytest.raises(ValueError):
            config = Config(start_urls=[])
            config.validate()
        
        # Test invalid concurrency
        with pytest.raises(ValueError):
            config = Config(
                start_urls=["https://example.com/test"],
                concurrency_level=0
            )
            config.validate()
    
    @patch('review2.scraper.session_manager.requests.Session.get')
    def test_error_handling_integration(self, mock_get, test_config):
        """Test error handling in integration scenario."""
        # Mock a failed request
        mock_get.side_effect = Exception("Network error")
        
        scraper = ReviewScraper(test_config)
        
        try:
            result = scraper.run_dry_run()
            
            # Should handle errors gracefully
            assert result['sample_scraped'] == 3
            
            # All samples should have errors
            for data in result['sample_data']:
                assert 'error' in data
                assert data['error'] is not None
        
        finally:
            scraper.close()