# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Automatischer Handbuch-Generator (AHG)** - An automated documentation tool that creates illustrated technical manuals from real usage scenarios of software applications. The system monitors Windows applications, captures screenshots, performs OCR, and uses AI (OpenAI GPT) to generate comprehensive documentation in multiple formats.

**Current State:** Production-ready Python desktop application (Version 1.0.0) with comprehensive test coverage and robust implementation.

## Development Commands

### Running the Application

```bash
# Start the application
python main.py

# Activate virtual environment first (recommended)
.venv\Scripts\activate  # Windows
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests

# Run specific test file
pytest tests/test_monitor.py

# Run with verbose output
pytest -v

# Run single test function
pytest tests/test_ai.py::test_text_generation
```

### Setup and Configuration

```bash
# Create virtual environment
python -m venv .venv

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy env.example .env
# Edit .env and add OPENAI_API_KEY

# Validate startup environment
python scripts/validate_startup.py
```

## Architecture Overview

### Layered Architecture

The application follows a **layered architecture pattern** with clear separation of concerns:

**1. Presentation Layer** (`src/gui/`)
- All Tkinter GUI components
- Main window, dialogs, panels
- User interaction handling

**2. Business Logic Layer** (core `src/` modules)
- `monitor/` - Windows monitoring and session management
- `capture/` - Screenshot capture, OCR, privacy masking
- `ai/` - OpenAI integration and text generation
- `document/` - Document generation and export
- `automation/` - Automated application exploration
- `audit/` - Audit trail and compliance

**3. Data Layer**
- File system storage in `data/` directory
- JSON for session data
- PNG for screenshots
- YAML for configuration

### Key Components and Their Responsibilities

**SessionManager** (`src/monitor/session_manager.py`)
- Central orchestrator for all session operations
- Manages session lifecycle (start, pause, resume, stop)
- Coordinates WindowMonitor, ActionDetector, ScreenshotCapture, OCR, and AI
- Implements undo/redo with history stacks
- All session operations MUST go through SessionManager

**WindowMonitor** (`src/monitor/window_monitor.py`)
- Detects window changes and triggers screenshot capture
- Uses pywin32/pywinauto for Windows integration
- Respects trigger configuration thresholds

**ScreenshotCapture** (`src/capture/screenshot.py`)
- Uses mss library for efficient cross-platform screenshot capture
- Uses pywinctl for window-specific capture
- Integrates with PrivacyMask for automatic data masking
- Screenshots stored with unique identifiers in `data/screenshots/{session_id}/`

**OCREngine** (`src/capture/ocr_engine.py`)
- Tesseract OCR integration via pytesseract
- Image preprocessing for better accuracy
- Asynchronous processing to avoid UI blocking
- Supports multiple languages (default: deu+eng)

**TextGenerator** (`src/ai/text_generator.py`)
- OpenAI API integration for AI-powered text generation
- Uses PromptTemplateSystem for configurable prompt profiles
- Implements retry logic with exponential backoff for API calls
- Generates step descriptions, introductions, and conclusions
- Temperature: 0.7, Max tokens: 500

**TemplateEngine** (`src/document/template_engine.py`)
- Orchestrates document generation across multiple formats
- Supports DOCX, PDF, Markdown, HTML, LaTeX
- Uses TemplateManager for document template configuration
- Integrates optional annotation and UI element detection

### Data Flow

```
User Action → WindowMonitor → ActionDetector
                ↓
         SessionManager (orchestrator)
                ↓
      ScreenshotCapture → PrivacyMask → Save PNG
                ↓
         OCREngine → Extract Text
                ↓
       TextGenerator (OpenAI) → Generate Description
                ↓
          Add Step to Session
                ↓
       TemplateEngine → DOCXBuilder/PDFExporter/etc.
                ↓
         Export Document(s)
```

## Important Patterns and Conventions

### Session State Management

- Session state stored as JSON in `data/sessions/{session_id}.json`
- State is immutable except through SessionManager methods
- Session recovery uses same state structure
- Undo/redo maintains complete state history (max 50 entries)
- Always save state immediately after changes for crash recovery

### Error Handling

- Exception-based error handling throughout
- Retry logic for external API calls (OpenAI, OCR)
- Exponential backoff strategy: max 3 retries
- All errors logged with full context via centralized logger
- User-facing errors must be translated to friendly messages
- Technical errors logged with exc_info=True

### Logging

- Centralized logging via `src/utils/logger.py`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log files in `logs/ahg.log` with rotation
- Always include context: session_id, step_number, component name
- Performance metrics logged for operations >1 second

### Configuration Management

- YAML for structured configuration files in `config/`
- `.env` for secrets (API keys) - NEVER commit secrets
- Environment variables loaded via python-dotenv
- Configuration validated on startup via StartupValidator
- Prompt profiles in `config/prompt_profiles/` (sop.yml, technical.yml, training.yml)

### Naming Conventions

**Python Code:**
- `snake_case` for modules, functions, variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Dialogs end with `Dialog` (e.g., `SettingsDialog`)
- Panels end with `Panel` (e.g., `PreviewPanel`)

**Files:**
- Session files: `{session_id}.json`
- Screenshot files: `{session_id}_{step_number}_{timestamp}.png`
- Audit trail: `{session_id}_audit.json`

## Technology Stack Details

### Core Dependencies

**GUI:** Tkinter (built-in, no external deps)
**Screenshot:** mss + pywinctl
**OCR:** Tesseract (pytesseract wrapper) - requires external Tesseract binary
**AI:** OpenAI API (GPT-5 model)
**Document:** python-docx, docx2pdf
**Windows:** pywin32, pywinauto
**Config:** PyYAML, python-dotenv
**Testing:** pytest, pytest-cov, pytest-mock

### Environment Variables

Required in `.env`:
- `OPENAI_API_KEY` - OpenAI API key for text generation

Optional:
- `TESSDATA_PREFIX` - Tesseract data directory path
- `TESSERACT_CMD` - Tesseract executable path
- `AUTO_ANNOTATIONS` - Enable automatic screenshot annotations (true/false)
- `ANNOTATION_STYLE` - Annotation style (modern/minimal/detailed)
- `UI_ELEMENT_DETECTION` - Enable UI element detection (true/false)

## Working with Tests

### Test Structure

- `tests/conftest.py` - Shared pytest fixtures
- `tests/test_*.py` - Test modules by component
- Use markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Mock external dependencies (OpenAI API, Tesseract) in tests
- Use fixtures for common test data (sessions, screenshots, configs)

### Testing Guidelines

- Mock expensive operations (API calls, OCR, file I/O) in unit tests
- Integration tests should test actual component integration
- Use `pytest-mock` for mocking
- Always clean up test artifacts in teardown
- Use `tmp_path` fixture for temporary test files

## Common Development Scenarios

### Adding a New Export Format

1. Create new exporter class in `src/document/` (e.g., `json_exporter.py`)
2. Implement export interface consistent with existing exporters
3. Integrate in `TemplateEngine.generate_document()` method
4. Add format to export options in GUI (`settings_dialog.py`)
5. Add tests in `tests/test_document.py`

### Adding a New Prompt Profile

1. Create YAML file in `config/prompt_profiles/{name}.yml`
2. Include: language, style, system_prompt, step_template, introduction_template, conclusion_template
3. Profile automatically detected and shown in GUI
4. Test with `TextGenerator` class

### Extending Monitoring Capabilities

1. Extend `WindowMonitor` or create new monitor class in `src/monitor/`
2. Integrate into `SessionManager.__init__()` and session lifecycle methods
3. Add callback methods (e.g., `_on_window_change`, `_on_mouse_click`)
4. Update trigger configuration in `config/trigger_config.yml`
5. Add tests in `tests/test_monitor.py`

### Implementing Privacy Features

1. Update patterns in `PrivacyMask` (`src/capture/privacy_mask.py`)
2. Configure rules in `config/privacy_mask.yml`
3. Auto-detection uses OCR text pattern matching
4. Applied before screenshot storage (non-reversible)

## Troubleshooting

### Common Issues

**OpenAI API Errors:**
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API credits and rate limits
- Review retry logic in `OpenAIClient`

**Tesseract Not Found:**
- Install Tesseract OCR binary from https://github.com/UB-Mannheim/tesseract/wiki
- Set `TESSERACT_CMD` or `TESSDATA_PREFIX` in environment
- Use `StartupValidator` to check installation

**Screenshots Not Capturing:**
- Check trigger configuration thresholds in `config/trigger_config.yml`
- Ensure target application is in foreground
- Verify no other applications blocking capture
- Check WindowMonitor is running (`active=True`)

**Session Recovery Failure:**
- Verify session files exist in `data/sessions/`
- Check JSON file integrity
- Review logs in `logs/ahg.log` for corruption errors
- Use `SessionRecovery.validate_session()` to check

## Performance Considerations

**Target Performance:**
- Screenshot capture: <100ms
- Screenshot storage: <50ms
- OCR processing: <2s per screenshot
- AI text generation: <5s per step
- Document generation: <10s for 50 steps, <30s for 200+ steps
- Memory usage: <500MB for typical sessions

**Optimization Strategies:**
- Screenshot compression before storage
- Async OCR and AI processing
- Batch processing where possible
- Result caching for repeated operations
- Connection pooling for API calls

## Security and Compliance

**Privacy Protection:**
- PrivacyMask applies automatic pattern detection (email, SSN, credit card, etc.)
- Manual masking regions configurable in `config/privacy_mask.yml`
- Masking irreversible - applied before storage

**Audit Trail:**
- SHA-256 hash for every screenshot
- Complete action logging in audit trail JSON
- Tamper-evident documentation
- Export to JSON/CSV for compliance

**API Security:**
- API keys in environment variables only
- HTTPS for all API communication
- Keys never logged or exposed in code
- Validate keys on startup

## File and Directory Structure

```
data/
├── sessions/           # Session JSON files
├── screenshots/        # Screenshots organized by session_id
└── output/            # Generated documents (DOCX, PDF, etc.)

config/
├── prompt_profiles/   # AI prompt profiles (YAML)
├── document_templates/  # Document templates (YAML)
├── cleanup_config.yml  # Cleanup retention settings
├── privacy_mask.yml    # Privacy masking rules
├── trigger_config.yml  # Trigger thresholds
└── exploration_config.yml  # Automation settings

src/
├── gui/               # Tkinter GUI components
├── monitor/           # Session and window monitoring
├── capture/           # Screenshot, OCR, privacy
├── ai/                # OpenAI integration
├── document/          # Document generation/export
├── automation/        # Automated exploration
├── audit/             # Audit logging
├── config/            # Configuration management
└── utils/             # Shared utilities

tests/                 # Test suite
logs/                  # Application logs
scripts/               # Utility scripts
```

## Important Notes

- This is a Windows-specific application (uses pywin32/pywinauto)
- Requires external Tesseract OCR installation
- Requires OpenAI API key with sufficient credits
- Session state persisted immediately for crash recovery
- All file operations use Path objects (pathlib)
- German language is primary (UI, logs, comments) but code follows English conventions
- Production-ready codebase - comprehensive error handling and logging already in place
