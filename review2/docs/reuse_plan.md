# Reuse Plan for Review II Implementation

Based on the analysis of the e-commerce web scraper, this document outlines the specific components and functions that will be adapted for Review II.

## Core Components to Adapt from First ZIP

### 1. Session Management and HTTP Handling
**Source**: `scraper.py` - Session creation and request handling
**Target**: `review2/scraper/session_manager.py`

#### Functions to Port:
- `create_session()` → `SessionManager.create_session()`
  - Retry strategy configuration
  - Connection pooling setup
  - Default headers management
- `make_request_with_retry()` → `SessionManager.make_request()`
  - Exponential backoff implementation
  - Error categorization and handling
  - Rate limiting between requests

#### Adaptations Required:
- User-agent rotation for regulatory sites
- Respect for robots.txt and rate limiting
- Custom headers for government/regulatory sites
- Session persistence across document scraping

### 2. URL Discovery and Pattern Matching
**Source**: `utils.py` - URL validation and classification
**Target**: `review2/scraper/url_handler.py`

#### Functions to Port:
- `is_product_page()` → `UrlHandler.is_final_page()`
  - Regex pattern matching for document URLs
  - URL validation and normalization
- `extract_domain()` → `UrlHandler.get_domain()`
  - Domain extraction for site-specific logic
- `validate_url()` → `UrlHandler.validate_url()`
  - URL format validation and accessibility checks

#### Pattern Adaptations:
```python
# Original e-commerce patterns
PRODUCT_PATTERNS = [
    r'/product/\d+',
    r'/item/[a-zA-Z0-9-]+',
    r'/p/\d+'
]

# Adapted regulatory document patterns
DOCUMENT_PATTERNS = [
    r'/rule/\d+',
    r'/regulation/\d+',
    r'/document/\d+',
    r'/final-rule/\d+',
    r'/cfr/title-\d+/section-[\d\.]+'
]
```

### 3. HTML Parsing and Content Extraction
**Source**: `parser.py` - BeautifulSoup-based data extraction
**Target**: `review2/scraper/parser.py`

#### Functions to Port:
- `extract_product_data()` → `Parser.parse_page()`
  - Main parsing orchestration
  - Error handling for malformed HTML
- `extract_title()` → `Parser._extract_title()`
  - Title extraction with fallback selectors
- `extract_description()` → `Parser._extract_text()`
  - Main content extraction and cleaning
- `extract_metadata()` → `Parser._extract_metadata()`
  - Metadata extraction from various sources

#### Selector Adaptations:
```python
# Original e-commerce selectors
PRODUCT_SELECTORS = {
    'title': ['h1.product-title', '.product-name', 'h1'],
    'price': ['.price', '.cost', '.amount'],
    'description': ['.description', '.product-details']
}

# Adapted document selectors
DOCUMENT_SELECTORS = {
    'title': ['h1.document-title', 'h1.rule-title', '.page-title h1', 'h1'],
    'content': ['.document-content', '.rule-content', 'main', '.content'],
    'sections': ['h2.section-heading', 'h3.subsection', '.section-title']
}
```

### 4. Retry and Error Handling
**Source**: `scraper.py` - Robust error handling patterns
**Target**: `review2/scraper/retry_handler.py`

#### Functions to Port:
- `retry_on_failure()` decorator → `RetryHandler.retry_on_failure()`
  - Configurable retry attempts and backoff
  - Exception categorization and handling
- `handle_request_error()` → `RetryHandler.handle_error()`
  - Error logging and classification
  - Circuit breaker pattern for persistent failures

#### Error Handling Enhancements:
- Document-specific error patterns (404 for removed regulations)
- Government site rate limiting responses
- SSL certificate issues with older regulatory sites

### 5. Concurrent Processing
**Source**: `main.py` - Multi-threaded scraping coordination
**Target**: `review2/scraper/scraper_main.py`

#### Functions to Port:
- `scrape_concurrent()` → `ReviewScraper.scrape_urls_concurrent()`
  - ThreadPoolExecutor management
  - Result aggregation and error handling
- `process_batch()` → `ReviewScraper._process_batch()`
  - Batch processing logic
  - Progress tracking and logging

#### Concurrency Adaptations:
- Lower default concurrency for government sites (3 vs 10)
- Adaptive rate limiting based on response times
- Respectful crawling delays for regulatory sites

### 6. Configuration Management
**Source**: `config.py` - YAML-based configuration system
**Target**: `review2/scraper/config.py`

#### Classes to Port:
- `ScraperConfig` → `Config`
  - YAML file loading and validation
  - Environment variable integration
  - Default value management

#### Configuration Schema Mapping:
```yaml
# Original e-commerce config
target_sites:
  - "https://shop.example.com"
product_patterns:
  - "/product/\\d+"
concurrent_requests: 10
output_format: "csv"

# Adapted Review II config
start_urls:
  - "https://regulations.gov/rule/123"
final_page_patterns:
  - "/rule/\\d+"
concurrency_level: 3
output_format: "both"
```

### 7. Output and Data Serialization
**Source**: `utils.py` - Data export and file management
**Target**: `review2/scraper/output_handler.py`

#### Functions to Port:
- `save_results()` → `OutputHandler.save_results()`
  - Multi-format output (JSON/CSV)
  - File naming and organization
- `generate_report()` → `OutputHandler.generate_summary_report()`
  - Scraping run summaries and statistics
- `save_html()` → `OutputHandler.save_html()`
  - Raw HTML archiving for debugging

#### Output Format Adaptations:
```python
# Original product data structure
{
    'id': 'product_123',
    'name': 'Product Name',
    'price': '$19.99',
    'description': 'Product description...',
    'url': 'https://shop.example.com/product/123',
    'scraped_at': '2024-01-01T12:00:00'
}

# Adapted document data structure
{
    'id': 'rule_123',
    'title': 'Environmental Protection Rule',
    'text': 'Full rule text content...',
    'sections': [{'id': 'sec1', 'title': 'Section 1', 'text': '...'}],
    'metadata': {'author': 'EPA', 'date_published': '2024-01-01'},
    'url': 'https://regulations.gov/rule/123',
    'scraped_at': '2024-01-01T12:00:00'
}
```

## Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)
**Priority**: High - Foundation components
**Effort**: 2-3 days

1. **Session Management**
   - Port HTTP session handling
   - Implement rate limiting for regulatory sites
   - Add user-agent rotation

2. **Configuration System**
   - Adapt YAML configuration loading
   - Add Review II specific settings
   - Implement validation logic

3. **Basic Error Handling**
   - Port retry mechanisms
   - Add logging infrastructure
   - Implement circuit breaker pattern

### Phase 2: Scraping Logic (Week 1-2)
**Priority**: High - Core functionality
**Effort**: 3-4 days

1. **URL Handling**
   - Adapt pattern matching for regulatory URLs
   - Implement final page detection
   - Add URL validation and filtering

2. **HTML Parsing**
   - Port BeautifulSoup parsing pipeline
   - Adapt selectors for document structure
   - Implement section extraction logic

3. **Content Extraction**
   - Adapt data extraction functions
   - Implement document-specific metadata parsing
   - Add text cleaning and normalization

### Phase 3: Integration and Testing (Week 2)
**Priority**: Medium - Quality assurance
**Effort**: 2-3 days

1. **Main Scraper Class**
   - Integrate all components
   - Implement dry-run and full-run modes
   - Add concurrent processing

2. **Output Handling**
   - Port multi-format output
   - Implement HTML archiving
   - Add summary report generation

3. **Testing and Validation**
   - Create unit tests for adapted components
   - Implement integration tests
   - Validate against sample URLs

## Code Reuse Metrics

### Direct Reuse (90%+ unchanged)
- Session management and HTTP handling: **95%**
- Configuration loading and validation: **90%**
- Retry and error handling logic: **95%**
- Output file management: **90%**

### Modified Reuse (50-90% unchanged)
- URL pattern matching: **70%** (pattern changes only)
- HTML parsing infrastructure: **80%** (selector changes)
- Concurrent processing: **85%** (rate limiting adjustments)

### New Implementation (< 50% reuse)
- Document-specific parsers: **30%** (new selectors and logic)
- Section extraction: **20%** (new functionality)
- Regulatory metadata handling: **40%** (adapted from product metadata)

### Overall Reuse Estimate: **75%**

## Risk Mitigation

### Technical Risks
1. **Government Site Blocking**: Implement respectful crawling with longer delays
2. **SSL Certificate Issues**: Add certificate validation bypass for older sites
3. **Rate Limiting**: Implement adaptive delays and respect robots.txt

### Implementation Risks
1. **Parsing Failures**: Extensive testing with sample documents
2. **Configuration Complexity**: Comprehensive validation and error messages
3. **Performance Issues**: Profiling and optimization of parsing logic

## Success Criteria

### Functional Requirements
- [ ] Successfully scrape sample regulatory documents
- [ ] Extract required fields (id, title, text, sections, metadata)
- [ ] Support both dry-run and full-run modes
- [ ] Generate JSON and CSV outputs
- [ ] Handle errors gracefully with retry logic

### Performance Requirements
- [ ] Process 100+ documents within 10 minutes
- [ ] Maintain < 5% failure rate on valid URLs
- [ ] Respect rate limits (< 1 request per second per domain)
- [ ] Memory usage < 500MB for typical runs

### Quality Requirements
- [ ] 90%+ test coverage for adapted components
- [ ] Comprehensive error logging and reporting
- [ ] Clear documentation and usage examples
- [ ] Backward compatibility with Review I patterns

This reuse plan provides a clear roadmap for adapting the proven e-commerce scraper architecture to Review II requirements while maintaining code quality and reliability.