"""
Unit tests for the configuration module.
"""

import pytest
import tempfile
import os
from review2.scraper.config import Config


class TestConfig:
    
    def test_default_config(self):
        config = Config.default()
        assert isinstance(config.start_urls, list)
        assert config.concurrency_level > 0
        assert config.max_retries >= 0
        assert config.output_format in ['json', 'csv', 'both']
    
    def test_config_validation_valid(self):
        config = Config(
            start_urls=["https://example.com/test"],
            concurrency_level=2,
            max_retries=3,
            output_format="json"
        )
        # Should not raise an exception
        config.validate()
    
    def test_config_validation_empty_urls(self):
        config = Config(start_urls=[])
        with pytest.raises(ValueError, match="start_urls cannot be empty"):
            config.validate()
    
    def test_config_validation_invalid_concurrency(self):
        config = Config(
            start_urls=["https://example.com/test"],
            concurrency_level=0
        )
        with pytest.raises(ValueError, match="concurrency_level must be >= 1"):
            config.validate()
    
    def test_config_validation_invalid_retries(self):
        config = Config(
            start_urls=["https://example.com/test"],
            max_retries=-1
        )
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            config.validate()
    
    def test_config_validation_invalid_output_format(self):
        config = Config(
            start_urls=["https://example.com/test"],
            output_format="invalid"
        )
        with pytest.raises(ValueError, match="output_format must be"):
            config.validate()
    
    def test_config_from_yaml(self):
        yaml_content = """
start_urls:
  - "https://example.com/rule/123"
  - "https://example.com/rule/456"
concurrency_level: 5
max_retries: 2
output_format: "csv"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                config = Config.from_yaml(f.name)
                assert len(config.start_urls) == 2
                assert config.concurrency_level == 5
                assert config.max_retries == 2
                assert config.output_format == "csv"
            finally:
                os.unlink(f.name)
    
    def test_config_from_yaml_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("nonexistent_file.yml")