# Architecture

## Executive Summary

This architecture document provides a **decision-focused solution design** for the Documentation-Tool-Generic (Automatischer Handbuch-Generator) project. As a brownfield desktop application, this document distills the existing codebase context into focused architectural decisions that guide future enhancements and ensure consistency across AI agent implementations.

**Current State:** Production-ready Python desktop application (Version 1.0.0) with layered architecture, comprehensive feature set, and robust implementation.

**Architecture Purpose:** Establish consistency contract for AI agents implementing enhancements, preventing conflicts and ensuring coherent technical decisions.

---

## Decision Summary

| Category | Decision | Version | Affects FR Categories | Rationale |
| -------- | -------- | ------- | --------------------- | --------- |
| **Language** | Python | 3.10+ | All | Existing codebase, excellent library ecosystem |
| **GUI Framework** | Tkinter | Built-in | GUI Layer | Current implementation, no external dependencies |
| **Screenshot Capture** | mss + pywinctl | Latest | Capture Layer | Cross-platform support, efficient capture |
| **OCR Engine** | Tesseract (pytesseract) | Latest | Capture Layer | Mature, reliable, well-supported |
| **AI Integration** | OpenAI API | GPT-5 | AI Layer | State-of-the-art text generation |
| **Document Generation** | python-docx | Latest | Document Layer | Mature library, good formatting support |
| **PDF Export** | docx2pdf | Latest | Document Layer | Simple conversion from DOCX |
| **Windows Integration** | pywin32 + pywinauto | Latest | Monitor Layer | Windows-specific monitoring required |
| **Configuration** | PyYAML + python-dotenv | Latest | Config Layer | YAML for configs, env vars for secrets |
| **Testing** | pytest + pytest-cov | Latest | All | Standard Python testing framework |
| **Architecture Pattern** | Layered Architecture | N/A | All | Clear separation of concerns |
| **Error Handling** | Exception-based with retry logic | N/A | All | Comprehensive error handling |
| **Logging** | Structured logging (logger.py) | N/A | All | Centralized logging system |
| **Session Storage** | JSON files | N/A | Monitor Layer | Simple, human-readable format |
| **Screenshot Storage** | File system (PNG) | N/A | Capture Layer | Efficient image storage |

---

## Project Structure

```
Documentation-Tool-Generic/
├── main.py                          # Entry point - starts GUI application
├── requirements.txt                  # Python dependencies
├── pytest.ini                       # Pytest configuration
├── env.example                      # Environment variables template
│
├── config/                          # Configuration files
│   ├── cleanup_config.yml.example  # Cleanup configuration template
│   ├── exploration_config.yml       # Exploration settings
│   ├── privacy_mask.yml.example     # Privacy masking rules template
│   ├── trigger_config.yml.example   # Trigger thresholds template
│   ├── document_templates/
│   │   └── standard.yml             # Document template configuration
│   └── prompt_profiles/             # AI prompt profiles
│       ├── sop.yml                  # Standard Operating Procedure profile
│       ├── technical.yml            # Technical documentation profile
│       └── training.yml             # Training manual profile
│
├── src/                             # Source code
│   ├── gui/                         # GUI Layer (Tkinter)
│   │   ├── main_window.py           # Main application window
│   │   ├── settings_dialog.py      # Settings configuration dialog
│   │   ├── preview_panel.py         # Live preview panel
│   │   ├── recovery_dialog.py      # Session recovery dialog
│   │   ├── batch_dialog.py          # Batch processing dialog
│   │   ├── export_filter_dialog.py # Export filter options
│   │   ├── stats_dashboard.py       # Statistics dashboard
│   │   ├── multilang_export_dialog.py # Multi-language export
│   │   ├── cloud_upload_dialog.py   # Cloud upload dialog
│   │   ├── quickref_export_dialog.py # Quick reference export
│   │   ├── video_export_dialog.py   # Video export dialog
│   │   ├── consolidation_dialog.py  # Step consolidation dialog
│   │   ├── session_compare_dialog.py # Session comparison
│   │   ├── test_checklist_dialog.py # Test checklist generator
│   │   ├── app_selector_dialog.py   # Application selector
│   │   ├── exploration_progress_dialog.py # Exploration progress
│   │   ├── progress_dialog.py       # Progress indicator
│   │   ├── comment_panel.py         # Comment/annotation panel
│   │   └── platform_export_dialog.py # Platform-specific export
│   │
│   ├── monitor/                     # Monitoring Layer
│   │   ├── session_manager.py       # Session lifecycle management
│   │   ├── window_monitor.py        # Window change detection
│   │   ├── action_detector.py       # User action detection
│   │   ├── mouse_keyboard_monitor.py # Mouse/keyboard tracking
│   │   ├── session_recovery.py      # Crash recovery system
│   │   └── batch_processor.py       # Batch session processing
│   │
│   ├── capture/                     # Capture Layer
│   │   ├── screenshot.py            # Screenshot capture (mss/pywinctl)
│   │   ├── ocr_engine.py            # OCR text extraction (Tesseract)
│   │   ├── privacy_mask.py          # Privacy data masking
│   │   ├── ui_element_detector.py   # UI element detection
│   │   └── annotation_engine.py    # Screenshot annotation
│   │
│   ├── ai/                          # AI Integration Layer
│   │   ├── openai_client.py         # OpenAI API client
│   │   ├── text_generator.py        # AI text generation
│   │   ├── prompt_templates.py      # Prompt template management
│   │   └── step_consolidator.py     # Step consolidation logic
│   │
│   ├── document/                    # Document Generation Layer
│   │   ├── docx_builder.py          # DOCX document builder
│   │   ├── pdf_exporter.py          # PDF export
│   │   ├── markdown_exporter.py     # Markdown export
│   │   ├── html_exporter.py         # HTML export
│   │   ├── latex_exporter.py        # LaTeX export
│   │   ├── multilang_exporter.py    # Multi-language export
│   │   ├── cloud_exporter.py        # Cloud upload export
│   │   ├── quickref_exporter.py     # Quick reference export
│   │   ├── video_exporter.py        # Video export
│   │   ├── platform_exporters.py   # Platform-specific exports
│   │   ├── template_engine.py      # Template processing
│   │   ├── template_manager.py     # Template management
│   │   ├── export_filter.py        # Export filtering
│   │   ├── quality_checker.py      # Document quality validation
│   │   ├── session_comparator.py   # Session comparison
│   │   └── test_checklist_generator.py # Test checklist generation
│   │
│   ├── automation/                  # Automation Layer
│   │   ├── automation_controller.py # Automation orchestration
│   │   ├── exploration_manager.py  # Exploration session management
│   │   ├── exploration_session.py  # Exploration session state
│   │   ├── exploration_strategy.py # Exploration strategies
│   │   ├── ai_navigator.py         # AI-guided navigation
│   │   ├── element_discovery.py    # UI element discovery
│   │   ├── window_discovery.py     # Window discovery
│   │   └── navigation_state.py     # Navigation state tracking
│   │
│   ├── audit/                       # Audit Layer
│   │   ├── audit_logger.py          # Audit trail logging
│   │   └── compliance.py           # Compliance validation
│   │
│   ├── config/                      # Configuration Layer
│   │   ├── config_manager.py        # Configuration management
│   │   ├── config_validator.py     # Configuration validation
│   │   └── trigger_config.py       # Trigger configuration
│   │
│   └── utils/                       # Utilities Layer
│       ├── logger.py                # Logging system
│       ├── cleanup_manager.py       # File cleanup management
│       └── startup_validator.py     # Startup validation
│
├── tests/                           # Test Suite
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_ai.py                   # AI module tests
│   ├── test_audit.py                # Audit module tests
│   ├── test_capture.py              # Capture module tests
│   ├── test_config.py              # Config module tests
│   ├── test_document.py             # Document module tests
│   ├── test_e2e.py                 # End-to-end tests
│   ├── test_integration.py          # Integration tests
│   └── test_monitor.py              # Monitor module tests
│
├── data/                            # Data Directory
│   ├── sessions/                    # Session data storage
│   ├── screenshots/                 # Screenshot storage
│   └── output/                      # Generated document output
│
├── docs/                            # Documentation
│   ├── sprint-artifacts/            # Sprint artifacts
│   └── [generated documentation]   # BMM-generated docs
│
└── scripts/                         # Utility Scripts
    └── validate_startup.py          # Startup validation script
```

---

## Epic to Architecture Mapping

**Note:** Epics not yet created. Mapping based on FR categories:

| FR Category | Architecture Location | Key Components |
| ---------- | -------------------- | -------------- |
| **Screenshot Capture** | `src/capture/screenshot.py` | ScreenshotCapture class |
| **OCR Text Extraction** | `src/capture/ocr_engine.py` | OCREngine class |
| **AI Text Generation** | `src/ai/text_generator.py` | TextGenerator class |
| **Document Export** | `src/document/` | Multiple exporters (DOCX, PDF, Markdown, HTML, LaTeX) |
| **Session Management** | `src/monitor/session_manager.py` | SessionManager class |
| **Privacy Masking** | `src/capture/privacy_mask.py` | PrivacyMask class |
| **Audit Trail** | `src/audit/audit_logger.py` | AuditLogger class |
| **Batch Processing** | `src/monitor/batch_processor.py` | BatchProcessor class |
| **Automation** | `src/automation/` | AutomationController, ExplorationManager |
| **Configuration** | `src/config/config_manager.py` | ConfigManager class |

---

## Technology Stack Details

### Core Technologies

**Language: Python 3.10+**
- **Rationale:** Existing codebase, excellent library ecosystem
- **Usage:** All application code
- **Version Management:** Specify minimum version in requirements.txt

**GUI Framework: Tkinter**
- **Rationale:** Built-in Python library, no external dependencies, current implementation
- **Usage:** All user interface components
- **Pattern:** Model-View separation with Tkinter widgets

**Screenshot Capture: mss + pywinctl**
- **Rationale:** Cross-platform support, efficient capture, window-specific capture
- **Usage:** `src/capture/screenshot.py`
- **Pattern:** Strategy pattern for different capture methods

**OCR Engine: Tesseract (pytesseract)**
- **Rationale:** Mature, reliable, well-supported OCR solution
- **Usage:** `src/capture/ocr_engine.py`
- **Pattern:** Adapter pattern for OCR integration

**AI Integration: OpenAI API (GPT-5)**
- **Rationale:** State-of-the-art text generation capabilities
- **Usage:** `src/ai/openai_client.py`, `src/ai/text_generator.py`
- **Pattern:** Adapter pattern for API integration, Template pattern for prompts

**Document Generation: python-docx**
- **Rationale:** Mature library for DOCX generation, good formatting support
- **Usage:** `src/document/docx_builder.py`
- **Pattern:** Builder pattern for document construction

**PDF Export: docx2pdf**
- **Rationale:** Simple conversion from DOCX to PDF
- **Usage:** `src/document/pdf_exporter.py`
- **Pattern:** Adapter pattern for PDF conversion

**Windows Integration: pywin32 + pywinauto**
- **Rationale:** Windows-specific monitoring and automation required
- **Usage:** `src/monitor/window_monitor.py`, `src/monitor/mouse_keyboard_monitor.py`
- **Pattern:** Platform-specific adapters

**Configuration: PyYAML + python-dotenv**
- **Rationale:** YAML for structured configs, env vars for secrets
- **Usage:** `src/config/config_manager.py`
- **Pattern:** Singleton pattern for configuration

**Testing: pytest + pytest-cov**
- **Rationale:** Standard Python testing framework
- **Usage:** All test files in `tests/`
- **Pattern:** Fixture-based testing

### Integration Points

**External Services:**
- **OpenAI API:** REST API integration via `src/ai/openai_client.py`
- **Tesseract OCR:** Local binary integration via `src/capture/ocr_engine.py`

**Internal Integration:**
- **GUI ↔ Monitor:** MainWindow creates and manages SessionManager
- **Monitor ↔ Capture:** SessionManager orchestrates capture components
- **Capture ↔ AI:** Screenshots passed to AI for processing
- **AI ↔ Document:** Generated text passed to document builders
- **Document ↔ Export:** Multiple exporters handle different formats

---

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### 1. Layered Architecture Pattern

**Structure:**
- **Presentation Layer:** `src/gui/` - Tkinter GUI components
- **Business Logic Layer:** `src/monitor/`, `src/capture/`, `src/ai/`, `src/document/` - Core functionality
- **Data Layer:** File system storage, configuration management

**Rules:**
- Layers communicate only with adjacent layers
- GUI layer never directly accesses file system
- Business logic layer is independent of GUI framework
- Data layer provides abstraction for storage

### 2. Session Management Pattern

**Structure:**
- SessionManager orchestrates all session-related operations
- Session state stored in JSON format
- State changes trigger appropriate actions (screenshot, OCR, AI generation)

**Rules:**
- All session operations go through SessionManager
- Session state is immutable except through SessionManager methods
- Session recovery uses same state structure
- Undo/redo maintains complete state history

### 3. Screenshot Capture Pattern

**Structure:**
- ScreenshotCapture handles all screenshot operations
- Uses mss for cross-platform support
- Uses pywinctl for window-specific capture

**Rules:**
- Screenshots stored with unique identifiers
- Screenshots associated with session steps
- Screenshot metadata stored separately
- Screenshot compression applied before storage

### 4. OCR Processing Pattern

**Structure:**
- OCREngine handles all OCR operations
- Image preprocessing before OCR
- Text post-processing after OCR

**Rules:**
- OCR processing is asynchronous to avoid UI blocking
- OCR errors handled gracefully
- OCR results cached when possible
- OCR preprocessing configurable

### 5. AI Text Generation Pattern

**Structure:**
- TextGenerator orchestrates AI text generation
- Prompt templates loaded from YAML files
- OpenAI client handles API communication

**Rules:**
- All AI calls go through TextGenerator
- Prompt templates are externalized (YAML)
- API errors handled with retry logic
- API rate limits respected

### 6. Document Generation Pattern

**Structure:**
- Multiple exporters for different formats
- TemplateEngine processes document templates
- DOCXBuilder creates primary format

**Rules:**
- All exporters implement common interface
- Template processing is consistent across formats
- Format-specific optimizations isolated to exporters
- Document quality validated before export

### 7. Error Handling Pattern

**Structure:**
- Exception-based error handling
- Retry logic for external API calls
- User-friendly error messages
- Comprehensive logging

**Rules:**
- All errors logged with context
- User-facing errors are user-friendly
- Technical errors logged with full details
- Retry logic uses exponential backoff

### 8. Configuration Pattern

**Structure:**
- ConfigManager loads YAML configuration files
- Environment variables for secrets
- ConfigValidator validates configuration

**Rules:**
- Configuration files are externalized
- Secrets never in configuration files
- Configuration validation on startup
- Default values provided for optional settings

---

## Consistency Rules

### Naming Conventions

**Python Modules:**
- Use snake_case for file names: `session_manager.py`
- Use PascalCase for class names: `SessionManager`
- Use snake_case for function names: `start_session()`
- Use UPPER_CASE for constants: `MAX_RETRIES`

**GUI Components:**
- Dialog classes end with `Dialog`: `SettingsDialog`
- Panel classes end with `Panel`: `PreviewPanel`
- Window classes end with `Window`: `MainWindow`

**Session Data:**
- Session IDs: UUID format
- Screenshot files: `{session_id}_{step_number}_{timestamp}.png`
- Session files: `{session_id}.json`

### Code Organization

**Module Structure:**
- One class per file (when possible)
- Related classes in same module
- Utilities in `utils/` module
- Configuration in `config/` module

**Import Organization:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**File Organization:**
- Configuration files in `config/`
- Data files in `data/`
- Source code in `src/`
- Tests in `tests/`

### Error Handling

**Approach:**
- Use Python exceptions for error handling
- Log all errors with context
- Provide user-friendly error messages
- Implement retry logic for external API calls

**Error Types:**
- **Configuration Errors:** Validation errors, missing config
- **API Errors:** OpenAI API failures, network issues
- **File System Errors:** Permission errors, disk full
- **OCR Errors:** Tesseract failures, image processing errors

**Retry Strategy:**
- Exponential backoff for API calls
- Maximum retry count: 3
- Retry only for transient errors
- Log all retry attempts

### Logging Strategy

**Approach:**
- Structured logging via `src/utils/logger.py`
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log files: `logs/ahg.log`
- Rotating log files

**Logging Rules:**
- Log all user actions
- Log all API calls
- Log all errors with stack traces
- Log performance metrics for long operations

**Log Format:**
- Timestamp, level, module, message
- Include context (session_id, step_number, etc.)
- Structured data for easy parsing

---

## Data Architecture

### Data Models

**Session Model:**
```python
{
    "session_id": "uuid",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "prompt_profile": "string",
    "steps": [
        {
            "step_number": "int",
            "timestamp": "timestamp",
            "screenshot_path": "string",
            "ocr_text": "string",
            "ai_description": "string",
            "window_title": "string",
            "actions": ["list of actions"]
        }
    ],
    "metadata": {
        "total_steps": "int",
        "total_screenshots": "int",
        "status": "active|paused|completed"
    }
}
```

**Screenshot Metadata:**
```python
{
    "screenshot_id": "uuid",
    "session_id": "uuid",
    "step_number": "int",
    "file_path": "string",
    "sha256_hash": "string",
    "timestamp": "timestamp",
    "window_title": "string",
    "dimensions": {"width": "int", "height": "int"}
}
```

**Audit Trail:**
```python
{
    "session_id": "uuid",
    "actions": [
        {
            "timestamp": "timestamp",
            "action_type": "string",
            "details": "dict",
            "user": "string"
        }
    ],
    "screenshots": [
        {
            "screenshot_id": "uuid",
            "sha256_hash": "string",
            "timestamp": "timestamp"
        }
    ]
}
```

### Data Relationships

**Session → Steps:** One-to-many
- Each session contains multiple steps
- Steps are ordered by step_number
- Steps reference screenshots

**Session → Screenshots:** One-to-many
- Each session contains multiple screenshots
- Screenshots stored in `data/screenshots/{session_id}/`
- Screenshots referenced by steps

**Session → Audit Trail:** One-to-one
- Each session has one audit trail
- Audit trail stored separately
- Audit trail includes all actions

### Data Storage

**Session Storage:**
- Location: `data/sessions/{session_id}.json`
- Format: JSON
- Structure: Session model above

**Screenshot Storage:**
- Location: `data/screenshots/{session_id}/{screenshot_id}.png`
- Format: PNG
- Compression: Applied before storage

**Audit Trail Storage:**
- Location: `data/sessions/{session_id}_audit.json`
- Format: JSON
- Structure: Audit trail model above

**Output Storage:**
- Location: `data/output/{document_name}.{format}`
- Formats: DOCX, PDF, Markdown, HTML, LaTeX
- Naming: Based on session and export settings

---

## API Contracts

**Note:** This is a desktop application, not a web API. However, there are internal API contracts between modules:

### SessionManager API

**Methods:**
- `start_session(session_id, prompt_profile)` → Creates new session
- `stop_session()` → Stops active session
- `pause_session()` → Pauses active session
- `resume_session()` → Resumes paused session
- `add_step(step_data)` → Adds step to session
- `undo_step()` → Removes last step
- `redo_step()` → Restores undone step
- `get_session_state()` → Returns current session state

### ScreenshotCapture API

**Methods:**
- `capture_screenshot(window_handle=None)` → Captures screenshot
- `save_screenshot(image, session_id, step_number)` → Saves screenshot
- `get_screenshot_path(session_id, screenshot_id)` → Returns screenshot path

### OCREngine API

**Methods:**
- `extract_text(image_path)` → Extracts text from image
- `preprocess_image(image)` → Preprocesses image for OCR
- `postprocess_text(text)` → Postprocesses OCR text

### TextGenerator API

**Methods:**
- `generate_description(screenshot_path, ocr_text, context)` → Generates AI description
- `consolidate_steps(steps)` → Consolidates similar steps
- `apply_prompt_template(template_name, context)` → Applies prompt template

### DocumentBuilder API

**Methods:**
- `create_document(session_data, template_config)` → Creates document
- `add_step(step_data)` → Adds step to document
- `export(format)` → Exports document in specified format

---

## Security Architecture

### Data Protection

**Privacy Masking:**
- Automatic detection of sensitive data patterns
- Configurable masking rules in `config/privacy_mask.yml`
- Masking applied before screenshot storage
- Masking preserves document readability

**API Key Security:**
- API keys stored in environment variables (`.env`)
- API keys never logged or exposed
- API keys validated on startup
- Secure API communication (HTTPS)

### Audit Trail

**SHA-256 Hashing:**
- All screenshots hashed with SHA-256
- Hashes stored in audit trail
- Hashes used for integrity verification
- Tamper-evident documentation

**Action Logging:**
- All user actions logged
- All system actions logged
- Complete audit trail for traceability
- Audit trail exportable (JSON/CSV)

### Access Control

**File System:**
- Application files readable/writable by user only
- Screenshots stored securely
- Session data protected
- Output files with appropriate permissions

**Network:**
- Only OpenAI API calls made
- No other network communication
- API calls encrypted (HTTPS)
- No data transmission except to OpenAI API

---

## Performance Considerations

### Screenshot Processing

**Optimization:**
- Screenshot compression before storage
- Efficient image formats (PNG)
- Batch screenshot processing
- Async screenshot capture

**Performance Targets:**
- Screenshot capture: <100ms
- Screenshot storage: <50ms
- Screenshot compression: <200ms

### OCR Processing

**Optimization:**
- Image preprocessing for better accuracy
- Async OCR processing
- OCR result caching
- Batch OCR processing

**Performance Targets:**
- OCR processing: <2 seconds per screenshot
- OCR preprocessing: <500ms
- OCR postprocessing: <100ms

### AI Text Generation

**Optimization:**
- Prompt optimization
- API call batching (when possible)
- Response caching (when applicable)
- Retry logic with exponential backoff

**Performance Targets:**
- AI text generation: <5 seconds per step
- API call overhead: <1 second
- Prompt processing: <100ms

### Document Generation

**Optimization:**
- Efficient document building
- Memory-efficient processing
- Batch document generation
- Template caching

**Performance Targets:**
- Document generation: <10 seconds for 50 steps
- Large sessions (200+ steps): <30 seconds
- Memory usage: <500MB for typical sessions

---

## Deployment Architecture

### Current Deployment

**Standalone Application:**
- Python application with dependencies
- No server infrastructure required
- Local file system storage
- User-installed dependencies

**Installation:**
- Python 3.10+ runtime
- Tesseract OCR binary
- Python dependencies via pip
- Configuration files

### Future Deployment Considerations

**Cross-Platform Support:**
- Linux support (evaluate PyQt/wxPython)
- macOS support (evaluate PyQt/wxPython)
- Platform-specific installers
- Platform-specific optimizations

**Distribution:**
- PyInstaller for standalone executables
- Platform-specific packages
- Auto-update mechanism (future)
- Version management

---

## Development Environment

### Prerequisites

**Required Software:**
- Python 3.10 or higher
- Tesseract OCR
- Git (for version control)
- IDE (VS Code, PyCharm, or similar)

**Python Dependencies:**
- Listed in `requirements.txt`
- Install via: `pip install -r requirements.txt`

### Setup Commands

```bash
# Clone repository
git clone <repository-url>
cd Documentation-Tool-Generic

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy env.example .env
# Edit .env and add OpenAI API key

# Run application
python main.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Python as Primary Language

**Status:** Accepted

**Context:**
Desktop application requiring GUI, screenshot capture, OCR, AI integration, and document generation.

**Decision:**
Use Python 3.10+ as the primary programming language.

**Rationale:**
- Existing codebase is Python
- Excellent library ecosystem for all requirements
- Good cross-platform support potential
- Mature tooling and testing frameworks

**Consequences:**
- **Positive:** Rich library ecosystem, good developer experience
- **Negative:** Performance may be slower than compiled languages (acceptable for desktop app)
- **Neutral:** Standard Python practices apply

---

### ADR-002: Tkinter as GUI Framework

**Status:** Accepted

**Context:**
Desktop application requiring cross-platform GUI support.

**Decision:**
Use Tkinter as the GUI framework.

**Rationale:**
- Built-in Python library, no external dependencies
- Current implementation uses Tkinter
- Sufficient for application needs
- Good for rapid development

**Consequences:**
- **Positive:** No external dependencies, simple deployment
- **Negative:** GUI may feel dated compared to modern frameworks
- **Neutral:** Can migrate to PyQt/wxPython in future if needed

---

### ADR-003: Layered Architecture Pattern

**Status:** Accepted

**Context:**
Desktop application with multiple concerns (GUI, monitoring, capture, AI, document generation).

**Decision:**
Use Layered Architecture pattern with clear separation between presentation, business logic, and data layers.

**Rationale:**
- Clear separation of concerns
- Easy to test and maintain
- Good for desktop applications
- Allows for future refactoring

**Consequences:**
- **Positive:** Clear structure, easy to understand and maintain
- **Negative:** Some overhead in layer communication
- **Neutral:** Standard pattern for desktop applications

---

### ADR-004: OpenAI API for AI Text Generation

**Status:** Accepted

**Context:**
Need for high-quality AI text generation for documentation.

**Decision:**
Use OpenAI API (GPT-5) for AI text generation.

**Rationale:**
- State-of-the-art text generation capabilities
- Good API documentation and support
- Reliable service
- Cost-effective for use case

**Consequences:**
- **Positive:** High-quality text generation, active development
- **Negative:** Requires internet connection, API costs
- **Neutral:** Standard approach for AI text generation

---

### ADR-005: Tesseract OCR for Text Extraction

**Status:** Accepted

**Context:**
Need for OCR text extraction from screenshots.

**Decision:**
Use Tesseract OCR (pytesseract) for text extraction.

**Rationale:**
- Mature, reliable OCR engine
- Good accuracy for typical screenshots
- Well-supported and documented
- Open source

**Consequences:**
- **Positive:** Reliable, well-supported, good accuracy
- **Negative:** Accuracy depends on image quality
- **Neutral:** Can consider alternatives (EasyOCR/PaddleOCR) if needed

---

### ADR-006: JSON for Session Storage

**Status:** Accepted

**Context:**
Need for session data persistence.

**Decision:**
Use JSON format for session storage.

**Rationale:**
- Human-readable format
- Easy to parse and validate
- Good for debugging
- Standard Python support

**Consequences:**
- **Positive:** Human-readable, easy to debug
- **Negative:** Not as efficient as binary formats
- **Neutral:** Sufficient for desktop application use case

---

### ADR-007: File System for Data Storage

**Status:** Accepted

**Context:**
Need for session, screenshot, and output storage.

**Decision:**
Use local file system for all data storage.

**Rationale:**
- Simple and reliable
- No external dependencies
- Good performance for desktop app
- Easy to backup and manage

**Consequences:**
- **Positive:** Simple, reliable, no external dependencies
- **Negative:** Limited scalability, no cloud sync
- **Neutral:** Sufficient for single-user desktop application

---

### ADR-008: Exception-Based Error Handling

**Status:** Accepted

**Context:**
Need for comprehensive error handling across all layers.

**Decision:**
Use Python exception-based error handling with retry logic for external API calls.

**Rationale:**
- Standard Python approach
- Good for error propagation
- Allows for retry logic
- Comprehensive error information

**Consequences:**
- **Positive:** Standard approach, good error information
- **Negative:** Requires careful exception handling
- **Neutral:** Standard Python practice

---

### ADR-009: Structured Logging

**Status:** Accepted

**Context:**
Need for application logging and debugging.

**Decision:**
Use structured logging via centralized logger module.

**Rationale:**
- Centralized logging configuration
- Easy to debug and troubleshoot
- Good for production use
- Standard Python approach

**Consequences:**
- **Positive:** Centralized, easy to configure and debug
- **Negative:** Requires logging setup
- **Neutral:** Standard practice

---

### ADR-010: YAML for Configuration

**Status:** Accepted

**Context:**
Need for application configuration management.

**Decision:**
Use YAML format for configuration files.

**Rationale:**
- Human-readable format
- Good for structured data
- Easy to edit and validate
- Standard Python support

**Consequences:**
- **Positive:** Human-readable, easy to edit
- **Negative:** Requires YAML parsing library
- **Neutral:** Standard approach for configuration

---

_Generated by BMAD Decision Architecture Workflow v1.0_
_Date: 2025-11-20_
_For: BMad_
