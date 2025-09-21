#!/bin/bash

# Sample run commands for Review II scraper

echo "Review II Scraper - Sample Commands"
echo "==================================="

# Dry run with default config
echo "1. Dry run with default configuration:"
echo "python review2/scraper/run_scraper.py --config config.yml --mode dry-run"
echo ""

# Dry run with specific URLs
echo "2. Dry run with specific URLs:"
echo "python review2/scraper/run_scraper.py --mode dry-run --urls https://example.com/rule/123 https://example.com/rule/456"
echo ""

# Full run with custom output directory
echo "3. Full run with custom output directory:"
echo "python review2/scraper/run_scraper.py --config config.yml --mode full-run --output custom_output/"
echo ""

# Verbose logging
echo "4. Dry run with verbose logging:"
echo "python review2/scraper/run_scraper.py --config config.yml --mode dry-run --verbose"
echo ""

echo "Sample configuration (config.yml):"
echo "-----------------------------------"
cat << 'EOF'
start_urls:
  - "https://example.com/rule/123"
  - "https://example.com/regulation/456"

final_page_patterns:
  - '/rule/\d+'
  - '/regulation/\d+'

concurrency_level: 3
max_retries: 3
output_format: "both"
save_html: true
EOF