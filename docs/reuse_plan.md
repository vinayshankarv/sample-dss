# Reuse Plan for Review II Implementation

## Core Components to Adapt from First ZIP

### 1. Request/Session Management
**Source**: `scraper.py` - session handling functions
**Target**: `review2/scraper/session_manager.py`
- User-agent rotation
- Request headers management
- Session persistence
- Rate limiting implementation

### 2. URL Discovery and Pattern Matching
**Source**: URL generation logic in main scraper
**Target**: `review2/scraper/url_handler.py`
- Pattern-based URL detection
- Final page identification rules
- URL validation and filtering
- Sitemap parsing capabilities

### 3. HTML Parsing Pipeline
**Source**: BeautifulSoup parsing functions
**Target**: `review2/scraper/parser.py`
- HTML content extraction
- Metadata parsing (title, sections, text)
- Error handling for malformed HTML
- Content cleaning and normalization

### 4. Retry and Backoff Logic
**Source**: Error handling in main scraper
**Target**: `review2/scraper/retry_handler.py`
- Exponential backoff implementation
- Configurable retry attempts
- Different retry strategies for different error types
- Circuit breaker pattern for persistent failures

### 5. Concurrency Management
**Source**: Threading/async implementation
**Target**: `review2/scraper/concurrent_scraper.py`
- Thread pool management
- Async request handling
- Rate limiting across concurrent requests
- Resource cleanup and error propagation

### 6. Output and Serialization
**Source**: Data export functions
**Target**: `review2/scraper/output_handler.py`
- JSON/CSV output formats
- File naming conventions
- Data validation before export
- Incremental data updates

### 7. Configuration Management
**Source**: `config.py`
**Target**: `review2/scraper/config.py`
- YAML configuration loading
- Environment variable support
- Configuration validation
- Default value management

## Adaptation Strategy

### Phase 1: Core Infrastructure
1. Extract session management and request handling
2. Implement configuration system with YAML support
3. Set up logging and error handling framework

### Phase 2: Scraping Logic
1. Adapt URL discovery for Review II patterns
2. Implement Review II specific parsers
3. Add retry and backoff mechanisms

### Phase 3: Output and Testing
1. Implement output handlers for JSON/CSV
2. Add dry-run mode support
3. Create comprehensive test suite

## Key Functions to Port

### From scraper.py:
- `create_session()` → `SessionManager.create_session()`
- `make_request()` → `SessionManager.make_request()`
- `parse_page()` → `Parser.parse_page()`
- `extract_data()` → `Parser.extract_data()`
- `save_results()` → `OutputHandler.save_results()`

### From utils.py:
- `retry_on_failure()` → `RetryHandler.retry_on_failure()`
- `validate_url()` → `UrlHandler.validate_url()`
- `clean_text()` → `Parser.clean_text()`

## Configuration Mapping

### Original Config → Review II Config
- `target_sites` → `start_urls`
- `scraping_rules` → `final_page_patterns`
- `output_format` → `output_format`
- `concurrent_requests` → `concurrency_level`
- `retry_attempts` → `max_retries`

## Testing Strategy
1. Unit tests for each adapted component
2. Integration tests with sample URLs
3. Performance tests for concurrency
4. Error handling validation tests