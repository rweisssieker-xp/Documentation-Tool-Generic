# Source Tree Analysis

## Directory Structure

```
Documentation-Tool-Generic/
├── main.py                          # Entry point - starts GUI application
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
├── env.example                      # Environment variables template
│
├── config/                          # Configuration files
│   ├── cleanup_config.yml.example   # Cleanup configuration template
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
│   │   └── annotation_engine.py     # Screenshot annotation
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
│   ├── test_capture.py               # Capture module tests
│   ├── test_config.py               # Config module tests
│   ├── test_document.py              # Document module tests
│   ├── test_e2e.py                  # End-to-end tests
│   ├── test_integration.py           # Integration tests
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
├── scripts/                         # Utility Scripts
│   └── validate_startup.py          # Startup validation script
│
└── [Root Documentation Files]
    ├── README.md                    # Main project documentation
    ├── QUICKSTART.md                # Quick start guide
    ├── USER_MANUAL.md               # User manual
    ├── PROJECT_SUMMARY.md           # Project summary
    └── CHANGELOG.md                 # Change log
```

## Critical Directories

### `src/gui/` - Presentation Layer
**Purpose:** Tkinter-based GUI components
**Key Files:**
- `main_window.py` - Main application window and orchestration
- `preview_panel.py` - Live preview of generated documentation
- `settings_dialog.py` - Application settings

### `src/monitor/` - Monitoring Layer
**Purpose:** Windows monitoring and session management
**Key Files:**
- `session_manager.py` - Core session lifecycle management
- `window_monitor.py` - Window change detection
- `action_detector.py` - User action detection

### `src/capture/` - Capture Layer
**Purpose:** Screenshot capture and OCR
**Key Files:**
- `screenshot.py` - Cross-platform screenshot capture
- `ocr_engine.py` - Tesseract OCR integration
- `privacy_mask.py` - Privacy data masking

### `src/ai/` - AI Integration Layer
**Purpose:** OpenAI API integration for text generation
**Key Files:**
- `openai_client.py` - OpenAI API client wrapper
- `text_generator.py` - AI text generation logic
- `step_consolidator.py` - Step consolidation using AI

### `src/document/` - Document Generation Layer
**Purpose:** Multi-format document generation
**Key Files:**
- `docx_builder.py` - DOCX document builder
- `pdf_exporter.py` - PDF export
- `template_engine.py` - Template processing

### `src/automation/` - Automation Layer
**Purpose:** Automated application exploration
**Key Files:**
- `automation_controller.py` - Automation orchestration
- `exploration_manager.py` - Exploration session management
- `ai_navigator.py` - AI-guided navigation

## Entry Points

1. **Application Entry:** `main.py`
   - Validates startup environment
   - Initializes GUI
   - Starts Tkinter main loop

2. **GUI Entry:** `src/gui/main_window.py`
   - MainWindow class initialization
   - Menu setup
   - Session management

## Integration Points

- **GUI ↔ Monitor:** MainWindow creates SessionManager
- **Monitor ↔ Capture:** SessionManager orchestrates ScreenshotCapture and OCREngine
- **Capture ↔ AI:** Screenshots passed to AI for text generation
- **AI ↔ Document:** Generated text passed to document builders
- **Document ↔ Export:** Multiple exporters handle different formats

## Key Patterns

- **Layered Architecture:** Clear separation between GUI, Business Logic, and Data layers
- **Session-Based:** All operations organized around sessions
- **Event-Driven:** Window monitoring triggers capture events
- **Template-Based:** Document generation uses configurable templates
- **Modular Design:** Each module has clear responsibilities

