"""
Configuration management for Review II scraper.
"""

import yaml
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for Review II scraper."""
    
    # URLs and patterns
    start_urls: List[str] = field(default_factory=list)
    final_page_patterns: List[str] = field(default_factory=lambda: [
        r'/rule/\d+',
        r'/regulation/\d+',
        r'/document/\d+'
    ])
    
    # Scraping behavior
    concurrency_level: int = 3
    max_retries: int = 3
    retry_delay: float = 1.0
    request_timeout: int = 30
    
    # Output settings
    output_folder: str = "review2/data"
    output_format: str = "json"  # json, csv, both
    save_html: bool = True
    
    # Request settings
    user_agents: List[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ])
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "scraper.log"
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    @classmethod
    def default(cls) -> 'Config':
        """Create default configuration."""
        return cls()
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.start_urls:
            raise ValueError("start_urls cannot be empty")
        
        if self.concurrency_level < 1:
            raise ValueError("concurrency_level must be >= 1")
        
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        
        if self.output_format not in ['json', 'csv', 'both']:
            raise ValueError("output_format must be 'json', 'csv', or 'both'")