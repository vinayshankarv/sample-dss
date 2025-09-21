# Review II Web Scraper

A robust web scraper adapted from e-commerce scraping logic for Review II requirements. This scraper extracts structured data from regulatory documents, rules, and similar content with configurable patterns and robust error handling.

## Overview

Review II continues the architecture and design patterns established in Review I, adapting proven e-commerce scraping techniques for regulatory document extraction. The scraper supports both dry-run and full-run modes, concurrent processing, and multiple output formats.

## Features

- **Configurable URL Patterns**: Define regex patterns to identify final pages
- **Concurrent Scraping**: Multi-threaded processing with configurable concurrency
- **Robust Error Handling**: Retry logic with exponential backoff
- **Multiple Output Formats**: JSON, CSV, or both
- **HTML Archiving**: Optional raw HTML storage
- **Dry Run Mode**: Test configuration without writing files
- **Structured Logging**: Comprehensive logging with configurable levels

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Installation

1. Clone or extract the Review II package
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

1. **Configure URLs and patterns** in `config.yml`:
   ```yaml
   start_urls:
     - "https://example.com/rule/123"
     - "https://example.com/regulation/456"
   
   final_page_patterns:
     - '/rule/\d+'
     - '/regulation/\d+'
   ```

2. **Run a dry-run test**:
   ```bash
   python review2/scraper/run_scraper.py --config config.yml --mode dry-run
   ```

3. **Run full scraping**:
   ```bash
   python review2/scraper/run_scraper.py --config config.yml --mode full-run
   ```

## Configuration

The scraper uses YAML configuration files. Key settings:

### URLs and Patterns
- `start_urls`: List of URLs to scrape
- `final_page_patterns`: Regex patterns to identify target pages

### Scraping Behavior
- `concurrency_level`: Number of concurrent threads (default: 3)
- `max_retries`: Maximum retry attempts (default: 3)
- `request_timeout`: Request timeout in seconds (default: 30)

### Output Settings
- `output_folder`: Directory for output files (default: "review2/data")
- `output_format`: "json", "csv", or "both" (default: "json")
- `save_html`: Save raw HTML files (default: true)

### Example Configuration
```yaml
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

user_agents:
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

log_level: "INFO"
```

## Command Line Interface

```bash
python review2/scraper/run_scraper.py [OPTIONS]

Options:
  --config, -c PATH     Configuration file path (default: config.yml)
  --mode, -m MODE       Scraping mode: dry-run or full-run (default: dry-run)
  --urls, -u URL [URL...] URLs to scrape (overrides config)
  --output, -o PATH     Output directory (overrides config)
  --verbose, -v         Enable verbose logging
  --help               Show help message
```

### Examples

```bash
# Dry run with default config
python review2/scraper/run_scraper.py --mode dry-run

# Full run with specific URLs
python review2/scraper/run_scraper.py --mode full-run --urls https://example.com/rule/123

# Verbose dry run with custom output
python review2/scraper/run_scraper.py --mode dry-run --output test_output/ --verbose
```

## Output Format

### JSON Output Structure
```json
{
  "metadata": {
    "run_id": "20241201_143022",
    "timestamp": "2024-12-01T14:30:22.123456",
    "total_records": 10,
    "successful_scrapes": 8,
    "failed_scrapes": 2
  },
  "data": [
    {
      "id": "123",
      "title": "Sample Rule Document",
      "url": "https://example.com/rule/123",
      "text": "Full document text content...",
      "sections": [
        {
          "id": "section_1",
          "title": "Section 1 Title",
          "text": "Section content..."
        }
      ],
      "metadata": {
        "author": "Regulatory Agency",
        "date_published": "2024-01-15"
      },
      "scraped_at": "2024-12-01T14:30:22.123456"
    }
  ]
}
```

### Required Output Fields
Each scraped record contains:
- `id`: Unique identifier
- `title`: Document title
- `url`: Source URL
- `text`: Main content text
- `scraped_at`: ISO timestamp

## Testing

Run the complete test suite:
```bash
./run_tests.sh
```

This script will:
1. Create a virtual environment
2. Install dependencies
3. Run unit tests
4. Execute integration tests with sample URLs
5. Validate output format

### Manual Testing
```bash
# Unit tests only
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_parser.py -v

# Integration test
python review2/scraper/run_scraper.py --config config.yml --mode dry-run
```

## Architecture

Review II follows a modular architecture adapted from Review I:

```
review2/
├── scraper/                 # Core scraping package
│   ├── config.py           # Configuration management
│   ├── session_manager.py  # HTTP session handling
│   ├── url_handler.py      # URL pattern matching
│   ├── parser.py           # HTML parsing and extraction
│   ├── retry_handler.py    # Retry and backoff logic
│   ├── output_handler.py   # Data serialization
│   ├── scraper_main.py     # Main scraper orchestration
│   └── run_scraper.py      # CLI interface
├── tests/                  # Test suite
├── data/                   # Output directory
├── docs/                   # Documentation
└── examples/               # Usage examples
```

### Key Components

1. **SessionManager**: HTTP request handling with user-agent rotation and rate limiting
2. **UrlHandler**: Pattern-based URL filtering and validation
3. **Parser**: HTML content extraction with BeautifulSoup
4. **RetryHandler**: Exponential backoff and circuit breaker patterns
5. **OutputHandler**: Multi-format data serialization (JSON/CSV)

## Continuation from Review I

Review II maintains compatibility with Review I patterns:

### Shared Design Principles
- Modular architecture with clear separation of concerns
- Configuration-driven behavior
- Robust error handling and logging
- Concurrent processing capabilities
- Multiple output format support

### Adapted Components
- **Request Management**: Enhanced session handling from e-commerce scraper
- **URL Discovery**: Pattern-based filtering adapted for regulatory documents
- **Content Parsing**: BeautifulSoup pipeline optimized for document structure
- **Output Format**: Structured JSON/CSV compatible with Review I expectations

### Migration Path
Existing Review I configurations can be adapted by:
1. Updating URL patterns for new target sites
2. Adjusting parser selectors for document structure
3. Maintaining output schema compatibility

## Error Handling

The scraper implements multiple layers of error handling:

1. **Request Level**: HTTP errors, timeouts, connection issues
2. **Parsing Level**: Malformed HTML, missing elements
3. **Output Level**: File system errors, serialization issues
4. **Configuration Level**: Invalid settings, missing files

### Error Recovery
- Exponential backoff for transient failures
- Circuit breaker for persistent issues
- Graceful degradation with partial results
- Comprehensive error logging

## Performance Considerations

- **Concurrency**: Configurable thread pool (default: 3 threads)
- **Rate Limiting**: Adaptive delays between requests
- **Memory Usage**: Streaming output for large datasets
- **Disk Space**: Optional HTML archiving

### Recommended Settings
- Small sites (< 100 pages): concurrency_level = 2
- Medium sites (100-1000 pages): concurrency_level = 3-5
- Large sites (> 1000 pages): concurrency_level = 5-10

## Troubleshooting

### Common Issues

1. **No URLs found**: Check `final_page_patterns` regex syntax
2. **Connection errors**: Verify URLs are accessible and check rate limiting
3. **Parsing failures**: Inspect HTML structure and adjust parser selectors
4. **Permission errors**: Ensure output directory is writable

### Debug Mode
Enable verbose logging for troubleshooting:
```bash
python review2/scraper/run_scraper.py --verbose --mode dry-run
```

### Log Files
Check `scraper.log` for detailed execution logs including:
- Request/response details
- Parsing errors and warnings
- Retry attempts and failures
- Performance metrics

## Contributing

When extending Review II:

1. Follow the existing modular architecture
2. Add comprehensive tests for new features
3. Update configuration schema as needed
4. Maintain backward compatibility with Review I patterns
5. Document new functionality in README

## License

This project continues under the same license terms as Review I.