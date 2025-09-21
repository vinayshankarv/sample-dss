"""
Output handling and data serialization for Review II scraper.
"""

import json
import csv
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class OutputHandler:
    """Handles data output in various formats."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        Path(self.config.output_folder).mkdir(parents=True, exist_ok=True)
    
    def save_results(self, data: List[Dict[str, Any]], run_id: str = None) -> Dict[str, str]:
        """Save scraped data in configured format(s)."""
        if not data:
            self.logger.warning("No data to save")
            return {}
        
        run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        try:
            if self.config.output_format in ['json', 'both']:
                json_file = self._save_json(data, run_id)
                saved_files['json'] = json_file
            
            if self.config.output_format in ['csv', 'both']:
                csv_file = self._save_csv(data, run_id)
                saved_files['csv'] = csv_file
            
            self.logger.info(f"Saved {len(data)} records to {len(saved_files)} file(s)")
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            raise
    
    def _save_json(self, data: List[Dict[str, Any]], run_id: str) -> str:
        """Save data as JSON file."""
        filename = f"scraped_data_{run_id}.json"
        filepath = os.path.join(self.config.output_folder, filename)
        
        # Create summary metadata
        summary = {
            'metadata': {
                'run_id': run_id,
                'timestamp': datetime.utcnow().isoformat(),
                'total_records': len(data),
                'successful_scrapes': len([d for d in data if not d.get('error')]),
                'failed_scrapes': len([d for d in data if d.get('error')])
            },
            'data': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved JSON data to {filepath}")
        return filepath
    
    def _save_csv(self, data: List[Dict[str, Any]], run_id: str) -> str:
        """Save data as CSV file."""
        filename = f"scraped_data_{run_id}.csv"
        filepath = os.path.join(self.config.output_folder, filename)
        
        if not data:
            return filepath
        
        # Flatten nested data for CSV
        flattened_data = []
        for record in data:
            flat_record = self._flatten_dict(record)
            flattened_data.append(flat_record)
        
        # Get all unique keys for CSV headers
        all_keys = set()
        for record in flattened_data:
            all_keys.update(record.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        self.logger.info(f"Saved CSV data to {filepath}")
        return filepath
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary for CSV output."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings for CSV
                items.append((new_key, json.dumps(v) if v else ''))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def save_html(self, url: str, html_content: str, record_id: str) -> str:
        """Save raw HTML content to file."""
        if not self.config.save_html:
            return ""
        
        # Create HTML subdirectory
        html_dir = os.path.join(self.config.output_folder, 'html')
        Path(html_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename
        safe_id = "".join(c for c in str(record_id) if c.isalnum() or c in ('-', '_'))
        filename = f"{safe_id}.html"
        filepath = os.path.join(html_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Source URL: {url} -->\n")
                f.write(f"<!-- Scraped at: {datetime.utcnow().isoformat()} -->\n")
                f.write(html_content)
            
            self.logger.debug(f"Saved HTML for {record_id} to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving HTML for {record_id}: {str(e)}")
            return ""
    
    def generate_summary_report(self, data: List[Dict[str, Any]], run_id: str) -> str:
        """Generate a summary report of the scraping run."""
        report_filename = f"scraping_report_{run_id}.txt"
        report_path = os.path.join(self.config.output_folder, report_filename)
        
        successful = [d for d in data if not d.get('error')]
        failed = [d for d in data if d.get('error')]
        
        report_content = f"""
Review II Scraping Report
========================
Run ID: {run_id}
Timestamp: {datetime.utcnow().isoformat()}

Summary:
--------
Total URLs processed: {len(data)}
Successful scrapes: {len(successful)}
Failed scrapes: {len(failed)}
Success rate: {len(successful)/len(data)*100:.1f}%

Configuration:
--------------
Concurrency level: {self.config.concurrency_level}
Max retries: {self.config.max_retries}
Output format: {self.config.output_format}
Save HTML: {self.config.save_html}

Failed URLs:
------------
"""
        
        for failed_record in failed[:10]:  # Show first 10 failures
            report_content += f"- {failed_record.get('url', 'Unknown URL')}: {failed_record.get('error', 'Unknown error')}\n"
        
        if len(failed) > 10:
            report_content += f"... and {len(failed) - 10} more failures\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Generated summary report: {report_path}")
        return report_path