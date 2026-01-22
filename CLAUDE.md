# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Paper Tracker Analyzer is a Python-based CLI tool that searches arXiv for academic papers, downloads them, extracts text content from PDFs, and generates professional reading reports using LLM APIs.

**Key Architecture**: The system follows a modular pipeline design where each component handles a specific stage of the workflow:
1. **Search & Discovery** (`PaperFetcher`) - Searches arXiv for recent or classic papers
2. **Download & Extraction** (`ContentExtractor`) - Downloads PDFs and extracts text
3. **Analysis** (`LLMClient`) - Sends content to LLM API for analysis
4. **Report Generation** (`ReportGenerator`) - Creates formatted Markdown reports
5. **Coordination** (`main.py`) - Orchestrates the complete workflow

## Common Development Commands

### Running the Application
```bash
# Basic usage - search recent papers
python main.py --category cs.AI --days 7 --max-results 5

# Classic paper search mode
python main.py --category cs.LG --classic --years-back 3 --keywords "deep learning" --max-results 5

# With custom config
python main.py --config my_config.yaml

# Debug logging
python main.py --log-level DEBUG
```

### Testing
```bash
# Run all tests (if tests directory exists)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run property-based tests
pytest -m property_test
```

### Code Quality
```bash
# Format code
black src/ tests/

# Run linter
pylint src/

# Type checking
mypy src/
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"
```

## Architecture Deep Dive

### Data Flow
```
main.py (CLI & orchestration)
    ↓
ConfigManager (loads config.yaml)
    ↓
PaperFetcher (arXiv API → Paper objects)
    ├─→ search_papers() - Recent papers by date range
    └─→ search_classic_papers() - Classic papers with optional citation filtering
    ↓
ContentExtractor (PDF → text)
    └─→ extract_text_from_pdf() - Uses pdfplumber, handles large PDFs
    ↓
LLMClient (text + metadata → API → analysis)
    └─→ analyze_paper() - Builds prompt, calls LLM API with retry logic
    ↓
ReportGenerator (analysis → Markdown files)
    ├─→ generate_report() - Single paper report
    └─→ generate_index() - Index file for batch results
```

### Module Responsibilities

**main.py**: Entry point and workflow orchestration
- Defines `process_paper()` - processes a single paper through the complete pipeline
- Defines `main_workflow()` - coordinates all modules for batch processing
- CLI interface with Click (all command-line options defined here)

**src/models.py**: Core data structures
- `Paper` dataclass: Immutable paper metadata from arXiv
- `AnalysisResult` dataclass: Analysis output with metadata

**src/config_manager.py**: Configuration management
- Loads from `config.yaml` with fallback to `DEFAULT_CONFIG`
- Supports CLI parameter overrides via `override_config()`
- Key sections: `llm`, `search`, `output`, `logging`

**src/paper_fetcher.py**: arXiv search and download
- Uses `arxiv` Python library for arXiv API interaction
- Optionally uses `ScholarClient` for citation-based filtering (disabled by default due to rate limits)
- `search_papers()`: Recent papers within N days
- `search_classic_papers()`: Papers from N years back with optional keyword/citation filtering
- `download_pdf()`: Downloads with retry logic for rate limits

**src/content_extractor.py**: PDF text extraction
- Uses `pdfplumber` for PDF parsing
- Handles large PDFs (>50 pages) by extracting first 10 + last 5 pages only
- Text cleaning: fixes hyphenation, normalizes whitespace, handles multi-column layouts
- Optional section extraction (abstract/intro/conclusion) via regex heuristics

**src/llm_client.py**: LLM API communication
- Prompt template defined as `PROMPT_TEMPLATE` (Chinese language, structured analysis format)
- `analyze_paper()`: Main entry point, handles content truncation if needed
- `_call_api()`: API calls with exponential backoff retry logic
- Supports any OpenAI-compatible API endpoint (configurable)

**src/scholar_client.py**: Semantic Scholar API client (optional)
- Fetches citation counts for classic paper identification
- Implements rate limiting with `request_delay` parameter
- Disabled by default to avoid 429 errors

**src/report_generator.py**: Markdown report generation
- Creates individual paper reports with metadata + LLM analysis
- Generates index file for batch processing results
- Sanitizes filenames for cross-platform compatibility

**src/logging_config.py**: Logging setup
- Dual output: detailed file logs + concise console logs
- Timestamped log files in `logs/` directory
- Module-specific loggers via `get_logger(__name__)`

**src/error_handler.py**: Centralized error handling
- `handle_network_error()`: Detailed logging for network/HTTP errors
- `handle_parsing_error()`: Paper-specific error context
- `should_retry()`: Determines retryability with exponential backoff
- Used by most modules for consistent error handling

## Configuration

### config.yaml Structure
```yaml
llm:
  api_endpoint: "https://api.siliconflow.cn/v1/chat/completions"  # Or OpenAI, etc.
  api_key: "your-api-key"
  model: "Pro/zai-org/GLM-4.7"  # Or gpt-4, etc.
  max_tokens: 20000
  temperature: 0.3
  max_content_length: -1  # -1 = unlimited, or set to limit characters sent to LLM

search:
  default_category: "cs.AI"
  default_days: 7
  default_max_results: 3
  classic:
    enabled: false
    years_back: 3
    use_scholar_api: false  # WARNING: Semantic Scholar has strict rate limits
    request_delay: 2.0      # Increase if using scholar_api and getting 429s
    min_citations: 10       # Only used if use_scholar_api is true
    min_influential_citations: 5
    sort_by: "relevance"    # or "lastUpdatedDate", "submittedDate"

output:
  directory: "./reports"

logging:
  level: "INFO"
  file: "./logs/paper_tracker.log"
```

### Important Configuration Notes

1. **Semantic Scholar API (`use_scholar_api`)**: Default is `false`. The Semantic Scholar API has strict rate limits (429 errors). Enable only if you need citation-based filtering and are willing to accept slow processing or errors.

2. **Content Length (`max_content_length`)**: Set to `-1` for unlimited (recommended for long papers). If set to a positive number, content sent to LLM will be truncated to that many characters.

3. **Request Delay (`request_delay`)**: When `use_scholar_api: true`, increase this (try 3.0-5.0 seconds) if encountering 429 errors.

## arXiv Categories

The system supports all arXiv categories. Common ones:
- **AI/ML**: `cs.AI`, `cs.LG` (machine learning), `cs.NE` (neural networks), `cs.CV` (computer vision)
- **NLP**: `cs.CL` (computational linguistics)
- **Systems**: `cs.DC` (distributed/parallel), `cs.AR` (architecture), `cs.DB` (databases)
- **Theory**: `cs.CR` (crypto), `cs.DS` (data structures), `cs.IT` (information theory)

See `ARXIV_CATEGORIES.md` for a complete list.

## Classic Paper Search

The system supports two modes for identifying classic papers:

### Mode 1: Relevance-Based (Default, Recommended)
- Uses arXiv's built-in relevance ranking
- Filters by keywords if provided
- No rate limiting issues
- Configuration: `use_scholar_api: false`

### Mode 2: Citation-Based (Optional, Rate Limited)
- Uses Semantic Scholar API for citation counts
- Filters by `min_citations` and `min_influential_citations`
- Prone to 429 errors (rate limits)
- Configuration: `use_scholar_api: true` with increased `request_delay`

### Classic Paper Criteria
When citation filtering is enabled, a paper is considered "classic" if:
- Total citations ≥ `min_citations` (default: 10)
- Influential citations ≥ `min_influential_citations` (default: 5)

## Error Handling Strategy

The system is designed to be resilient to errors:
- **Network errors**: Automatic retry with exponential backoff (up to 3 attempts)
- **PDF download failures**: Logged and skipped, continue with next paper
- **Parsing failures**: Logged and skipped, continue with next paper
- **LLM API failures**: Logged and skipped, continue with next paper
- **Exit codes**: 0 (success), 1 (all failed), 2 (some failed), 130 (user interrupt)

## Development Considerations

### Adding New Features

1. **New arXiv search filters**: Modify `PaperFetcher.search_papers()` or `search_classic_papers()`
2. **New LLM providers**: Add endpoint to `config.yaml` and ensure `LLMClient._call_api()` supports the API format
3. **Custom prompt templates**: Pass custom template to `LLMClient.analyze_paper(prompt_template=...)`
4. **New report formats**: Extend `ReportGenerator` or create a new generator class

### Testing Notes

- The `tests/` directory is referenced in README but may not exist in the repository
- Property-based tests use Hypothesis (marked with `@pytest.mark.property_test`)
- Tests should mock external API calls (arXiv, LLM, Semantic Scholar) using `requests-mock`

### Logging

- Use `get_logger(__name__)` in all modules for consistent logging
- Debug-level logs include detailed operation info
- Info-level logs include high-level progress
- Warning/Error logs include context for troubleshooting
- Log files are timestamped and stored in `logs/` directory
