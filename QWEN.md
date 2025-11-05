# Qwen Code Context File: Automatic Documentation Generator (AHG)

## Project Overview

The Automatic Documentation Generator (AHG), also known as "Automatischer Handbuch-Generator" (AHG), is a Python-based tool that creates illustrated technical documentation from real-world software usage scenarios. It monitors user actions, captures screenshots, and uses AI to generate comprehensive step-by-step manuals.

### Core Features
- **Automatic Monitoring**: Tracks user actions (window switches, mouse clicks, keyboard input)
- **Screenshot Capture**: Automatically captures screenshots at relevant steps
- **OCR Integration**: Extracts text from screenshots using Tesseract OCR
- **AI Text Generation**: Uses OpenAI GPT-5 for context-aware descriptions
- **Audit-Safe Documentation**: SHA-256 hashing for each screenshot, complete audit trail
- **Configurable Prompt Profiles**: Various styles (SOP, Training, Technical)
- **Multiple Export Formats**: DOCX, PDF, Markdown, HTML, JSON/CSV for audit trails
- **Privacy Masking**: Automatic detection and masking of sensitive data
- **Session Management**: Pause/Resume, Undo/Redo, recovery after crashes

## Project Structure

```
Documentation-Tool-Generic/
├── src/                    # Source code
│   ├── gui/               # GUI components
│   ├── monitor/           # Windows monitoring
│   ├── capture/           # Screenshot & OCR
│   ├── ai/                # OpenAI integration
│   ├── document/          # Document generation
│   ├── audit/             # Audit trail
│   ├── config/            # Configuration
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── data/                  # Data directory
│   ├── sessions/          # Session data
│   ├── screenshots/       # Captured screenshots
│   └── output/            # Generated documents
├── logs/                  # Log files
└── main.py               # Entry point
```

## Building and Running

### System Requirements
- **OS**: Windows 10/11
- **Python**: Version 3.10 or higher
- **Tesseract OCR**: Required for text recognition
- **OpenAI API Key**: Required for AI text generation

### Installation Steps
1. Clone the repository:
```bash
git clone <repository-url>
cd Documentation-Tool-Generic
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki

5. Configure environment variables:
```bash
copy env.example .env
```
Edit `.env` and add your OpenAI API key

6. Run the application:
```bash
python main.py
```

## Key Dependencies

- `mss>=9.0.1` - Screenshot capture
- `Pillow>=10.0.0` - Image processing
- `pytesseract>=0.3.10` - OCR functionality
- `pywin32>=306` - Windows monitoring
- `openai>=1.12.0` - AI integration
- `python-docx>=1.1.0` - Document generation
- `PyYAML>=6.0.1` - Configuration
- `pytest>=7.4.0` - Testing

## Development Conventions

### Code Structure
- Each module has a specific responsibility (GUI, monitoring, capture, AI, etc.)
- Configuration is stored in YAML files in the `config/` directory
- Test files follow the naming pattern `test_*.py`
- Logging is implemented consistently across modules using `src.utils.logger`

### Configuration
- Prompt profiles determine the style of generated documentation (SOP, Training, Technical)
- Trigger configurations control sensitivity of capture mechanisms
- Privacy masks protect sensitive information in screenshots
- Cleanup configurations manage retention of old files

### Testing
- Unit tests are located in the `tests/` directory
- Integration tests verify complete workflows
- Test markers: `unit`, `integration`, `slow`
- Run tests with `pytest` or `pytest --cov=src --cov-report=html` for coverage

## Configuration Files

### Prompt Profiles
Located in `config/prompt_profiles/`:
- `sop.yml`: Standard Operating Procedure (formal, compliant)
- `training.yml`: Training manual (explanatory, didactic)
- `technical.yml`: Technical manual (precise, concise)

### Trigger Configuration
Located in `config/trigger_config.yml`:
- `poll_interval`: How frequently to check for changes
- `change_threshold`: Sensitivity for detecting content changes
- `size_change_threshold`: Minimum pixel change for capture
- `double_click_delay`: Time window for double-click detection

### Privacy Mask Configuration
Located in `config/privacy_mask.yml`:
- Defines areas to mask in screenshots
- Supports rectangle and circle shapes
- Can mask sensitive information automatically

### Cleanup Configuration
Located in `config/cleanup_config.yml`:
- Controls automatic cleanup of old files
- Sets retention periods for screenshots and sessions

## Main Components

### GUI Module
- Provides the main application interface
- Includes menu system with File, Session, Export, Tools, Automation, and Help menus
- Shows live preview and session statistics
- Implements keyboard shortcuts

### Monitor Module
- Windows monitoring using pywin32
- Tracks active windows and detects changes
- Captures window information including title, position, size

### Capture Module
- Screenshot capture using mss
- OCR integration with pytesseract
- Privacy masking functionality

### AI Module
- OpenAI API integration for text generation
- Prompt templates for different documentation styles
- Context-aware description generation

### Document Module
- Generates documents in multiple formats (DOCX, PDF, Markdown, HTML)
- Creates audit trails in JSON and CSV formats
- Applies document templates

## Troubleshooting

Common issues to watch for:
1. OpenAI API errors - verify API key is set correctly
2. Tesseract OCR not found - ensure proper installation and path configuration
3. Screenshots not captured - check trigger configurations and permissions
4. Document generation failures - verify sufficient disk space and permissions

## Testing

Run all tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test types:
```bash
# Unit tests
pytest tests/test_*.py -m "not integration"

# Integration tests
pytest tests/test_integration.py -m integration
```

## Entry Point

The application starts from `main.py` which:
1. Validates the startup environment
2. Creates necessary directories
3. Runs automatic cleanup
4. Launches the GUI application
5. Implements error handling and logging

## Version

Current version: 1.0.0 (production-ready)