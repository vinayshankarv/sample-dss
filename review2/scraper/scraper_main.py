"""
Main scraper class for Review II implementation.
"""

import logging
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import Config
from .session_manager import SessionManager
from .url_handler import UrlHandler
from .parser import Parser
from .retry_handler import RetryHandler
from .output_handler import OutputHandler


class ReviewScraper:
    """Main scraper class that orchestrates the scraping process."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session_manager = SessionManager(config)
        self.url_handler = UrlHandler(config)
        self.parser = Parser(config)
        self.retry_handler = RetryHandler(config)
        self.output_handler = OutputHandler(config)
        
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Configure logging for the scraper."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL and return structured data."""
        self.logger.info(f"Scraping URL: {url}")
        
        try:
            # Make request with retry logic
            @self.retry_handler.retry_on_failure
            def make_request_with_retry():
                return self.session_manager.make_request(url)
            
            response = make_request_with_retry()
            
            if not response:
                return {
                    'id': None,
                    'title': None,
                    'url': url,
                    'text': None,
                    'sections': [],
                    'metadata': {},
                    'scraped_at': datetime.utcnow().isoformat(),
                    'error': 'Failed to fetch URL after retries'
                }
            
            # Parse the content
            data = self.parser.parse_page(response.text, url)
            
            # Save HTML if configured
            if self.config.save_html and data.get('id'):
                self.output_handler.save_html(url, response.text, data['id'])
            
            self.logger.info(f"Successfully scraped: {url}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
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
    
    def scrape_urls_concurrent(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        self.logger.info(f"Starting concurrent scraping of {len(urls)} URLs")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.concurrency_level) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self.scrape_url, url): url for url in urls}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Exception occurred for {url}: {str(e)}")
                    results.append({
                        'id': None,
                        'title': None,
                        'url': url,
                        'text': None,
                        'sections': [],
                        'metadata': {},
                        'scraped_at': datetime.utcnow().isoformat(),
                        'error': str(e)
                    })
        
        self.logger.info(f"Completed scraping {len(results)} URLs")
        return results
    
    def run_dry_run(self, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run scraper in dry-run mode (no file writes)."""
        urls = urls or self.config.start_urls
        
        if not urls:
            raise ValueError("No URLs provided for dry run")
        
        self.logger.info(f"Starting dry run with {len(urls)} URLs")
        
        # Filter to final pages only
        final_urls = self.url_handler.filter_final_pages(urls)
        
        if not final_urls:
            self.logger.warning("No final page URLs found in provided URLs")
            return {
                'total_urls': len(urls),
                'final_page_urls': 0,
                'sample_data': [],
                'errors': ['No final page URLs found']
            }
        
        # Scrape a sample (first 3 URLs for dry run)
        sample_urls = final_urls[:3]
        sample_data = []
        
        for url in sample_urls:
            data = self.scrape_url(url)
            sample_data.append(data)
        
        # Generate summary
        successful = [d for d in sample_data if not d.get('error')]
        
        summary = {
            'total_urls': len(urls),
            'final_page_urls': len(final_urls),
            'sample_scraped': len(sample_data),
            'successful_samples': len(successful),
            'sample_data': sample_data,
            'dry_run': True
        }
        
        self.logger.info(f"Dry run completed: {len(successful)}/{len(sample_data)} successful")
        return summary
    
    def run_full_scrape(self, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run full scraping process with file outputs."""
        urls = urls or self.config.start_urls
        
        if not urls:
            raise ValueError("No URLs provided for scraping")
        
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger.info(f"Starting full scrape run {run_id} with {len(urls)} URLs")
        
        # Filter to final pages only
        final_urls = self.url_handler.filter_final_pages(urls)
        
        if not final_urls:
            self.logger.warning("No final page URLs found")
            return {
                'run_id': run_id,
                'total_urls': len(urls),
                'final_page_urls': 0,
                'scraped_data': [],
                'saved_files': {},
                'errors': ['No final page URLs found']
            }
        
        # Scrape all URLs
        scraped_data = self.scrape_urls_concurrent(final_urls)
        
        # Save results
        saved_files = self.output_handler.save_results(scraped_data, run_id)
        
        # Generate summary report
        report_file = self.output_handler.generate_summary_report(scraped_data, run_id)
        saved_files['report'] = report_file
        
        successful = [d for d in scraped_data if not d.get('error')]
        
        summary = {
            'run_id': run_id,
            'total_urls': len(urls),
            'final_page_urls': len(final_urls),
            'scraped_records': len(scraped_data),
            'successful_scrapes': len(successful),
            'saved_files': saved_files,
            'dry_run': False
        }
        
        self.logger.info(f"Full scrape completed: {len(successful)}/{len(scraped_data)} successful")
        return summary
    
    def close(self):
        """Clean up resources."""
        self.session_manager.close()