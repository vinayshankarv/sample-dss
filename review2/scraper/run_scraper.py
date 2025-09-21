#!/usr/bin/env python3
"""
Command-line interface for Review II scraper.
"""

import argparse
import sys
import json
from pathlib import Path

from config import Config
from scraper_main import ReviewScraper


def main():
    parser = argparse.ArgumentParser(description='Review II Web Scraper')
    parser.add_argument('--config', '-c', 
                       default='config.yml',
                       help='Path to configuration file (default: config.yml)')
    parser.add_argument('--mode', '-m',
                       choices=['dry-run', 'full-run'],
                       default='dry-run',
                       help='Scraping mode (default: dry-run)')
    parser.add_argument('--urls', '-u',
                       nargs='+',
                       help='URLs to scrape (overrides config file)')
    parser.add_argument('--output', '-o',
                       help='Output directory (overrides config file)')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if Path(args.config).exists():
            config = Config.from_yaml(args.config)
        else:
            print(f"Warning: Config file {args.config} not found, using defaults")
            config = Config.default()
        
        # Override config with command line arguments
        if args.urls:
            config.start_urls = args.urls
        
        if args.output:
            config.output_folder = args.output
        
        if args.verbose:
            config.log_level = 'DEBUG'
        
        # Validate configuration
        config.validate()
        
        # Create and run scraper
        scraper = ReviewScraper(config)
        
        try:
            if args.mode == 'dry-run':
                print("Running in dry-run mode...")
                result = scraper.run_dry_run()
                
                print(f"\nDry Run Results:")
                print(f"Total URLs: {result['total_urls']}")
                print(f"Final page URLs: {result['final_page_urls']}")
                print(f"Sample scraped: {result['sample_scraped']}")
                print(f"Successful samples: {result['successful_samples']}")
                
                if result['sample_data']:
                    print(f"\nSample extracted data:")
                    for i, data in enumerate(result['sample_data'][:2], 1):
                        print(f"  {i}. {data.get('title', 'No title')} ({data.get('url', 'No URL')})")
                        if data.get('error'):
                            print(f"     Error: {data['error']}")
                
                # Output JSON for programmatic use
                print(f"\nJSON Output:")
                print(json.dumps(result, indent=2))
                
            else:  # full-run
                print("Running full scrape...")
                result = scraper.run_full_scrape()
                
                print(f"\nFull Scrape Results:")
                print(f"Run ID: {result['run_id']}")
                print(f"Total URLs: {result['total_urls']}")
                print(f"Final page URLs: {result['final_page_urls']}")
                print(f"Scraped records: {result['scraped_records']}")
                print(f"Successful scrapes: {result['successful_scrapes']}")
                
                if result['saved_files']:
                    print(f"\nSaved files:")
                    for file_type, filepath in result['saved_files'].items():
                        print(f"  {file_type}: {filepath}")
                
                print(f"\nSuccess rate: {result['successful_scrapes']/result['scraped_records']*100:.1f}%")
        
        finally:
            scraper.close()
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()