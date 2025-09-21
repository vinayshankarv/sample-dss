#!/bin/bash

# Review II Scraper Test Runner
# This script sets up a virtual environment and runs all tests

set -e  # Exit on any error

echo "Review II Scraper - Test Runner"
echo "==============================="

# Check if Python 3.10+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 10 ]); then
    echo "Error: Python 3.10+ is required. Found Python $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run unit tests
echo ""
echo "Running unit tests..."
echo "--------------------"
python -m pytest tests/ -v --tb=short

# Run integration test (dry-run mode)
echo ""
echo "Running integration test (dry-run)..."
echo "------------------------------------"

# Create a test config file
cat > test_config.yml << EOF
start_urls:
  - "https://httpbin.org/html"
  - "https://httpbin.org/json"
  - "https://httpbin.org/xml"

final_page_patterns:
  - '/html'
  - '/json'
  - '/xml'

concurrency_level: 1
max_retries: 2
output_folder: "test_output"
output_format: "json"
save_html: false
log_level: "WARNING"
EOF

# Run the scraper in dry-run mode
echo "Testing scraper with sample URLs..."
cd review2/scraper
python run_scraper.py --config ../../test_config.yml --mode dry-run --verbose

# Clean up
cd ../..
rm -f test_config.yml
rm -rf test_output

echo ""
echo "✓ All tests completed successfully!"
echo ""
echo "To run the scraper manually:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Configure URLs in config.yml"
echo "  3. Run: python review2/scraper/run_scraper.py --config config.yml --mode dry-run"