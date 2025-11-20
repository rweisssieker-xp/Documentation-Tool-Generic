# Developer Manual - Documentation-Tool-Generic

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Target Audience:** Software Developers, Contributors, Technical Contributors

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Development Environment](#development-environment)
4. [Code Organization](#code-organization)
5. [API Reference](#api-reference)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Code Style and Standards](#code-style-and-standards)
9. [Contributing](#contributing)
10. [Debugging](#debugging)
11. [Performance Optimization](#performance-optimization)
12. [Appendices](#appendices)

---

## Introduction

### Purpose

This manual provides comprehensive guidance for developers working on the Documentation-Tool-Generic codebase. It covers architecture, APIs, development practices, and contribution guidelines.

### Scope

This manual covers:
- System architecture and design patterns
- Development environment setup
- Code organization and structure
- API documentation
- Development workflow and best practices
- Testing strategies
- Contribution guidelines

### Prerequisites

Developers should have:
- Python 3.10+ programming experience
- Understanding of object-oriented programming
- Familiarity with GUI development (Tkinter)
- Knowledge of Windows APIs (for monitoring features)
- Understanding of REST APIs (OpenAI integration)

---

## Architecture Overview

### System Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│         GUI Layer (Tkinter)         │
│  MainWindow, Dialogs, PreviewPanel  │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│      Business Logic Layer           │
│  SessionManager, TextGenerator,     │
│  TemplateEngine, StepConsolidator   │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│      Integration Layer              │
│  WindowMonitor, OCREngine,          │
│  OpenAIClient, PrivacyMask          │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│         Data Layer                  │
│  File System, Session Storage,      │
│  Screenshot Storage                  │
└─────────────────────────────────────┘
```

### Key Components

**GUI Layer (`src/gui/`):**
- `main_window.py`: Main application window
- `preview_panel.py`: Live preview of captured steps
- `settings_dialog.py`: Configuration dialog
- Various export and tool dialogs

**Business Logic Layer:**
- `src/monitor/session_manager.py`: Session lifecycle management
- `src/ai/text_generator.py`: AI text generation
- `src/document/template_engine.py`: Document generation
- `src/ai/step_consolidator.py`: Step consolidation logic

**Integration Layer:**
- `src/monitor/window_monitor.py`: Window change detection
- `src/capture/ocr_engine.py`: OCR text extraction
- `src/ai/openai_client.py`: OpenAI API integration
- `src/capture/privacy_mask.py`: Privacy data masking

**Data Layer:**
- File system operations
- Session data persistence (JSON)
- Screenshot storage (PNG)
- Output file generation

### Design Patterns

**Observer Pattern:**
- Window monitoring uses observer pattern for change detection
- Event-driven architecture for UI updates

**Factory Pattern:**
- Document exporters use factory pattern for format selection
- Prompt profile loading uses factory pattern

**Strategy Pattern:**
- Privacy masking strategies
- OCR engine strategies
- Export format strategies

**Singleton Pattern:**
- Configuration manager
- Logger instance

---

## Development Environment

### Setup

See [Development Guide](development-guide.md) for detailed setup instructions.

**Quick Setup:**

```bash
# Clone repository
git clone <repository-url>
cd Documentation-Tool-Generic

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If exists

# Configure environment
copy env.example .env
# Edit .env with your API key
```

### IDE Configuration

**VS Code:**

Recommended extensions:
- Python
- Pylance
- Python Test Explorer
- Markdown All in One

**Settings (`.vscode/settings.json`):**

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

**PyCharm:**

- Configure Python interpreter (virtual environment)
- Enable pytest as test runner
- Configure code style (PEP 8)
- Enable type checking

### Development Tools

**Required Tools:**
- Python 3.10+
- Git
- Tesseract OCR
- OpenAI API access

**Recommended Tools:**
- Code formatter: `black` or `autopep8`
- Linter: `pylint` or `flake8`
- Type checker: `mypy`
- Test coverage: `pytest-cov`

---

## Code Organization

### Directory Structure

```
src/
├── gui/                    # GUI components
│   ├── __init__.py
│   ├── main_window.py      # Main window
│   ├── preview_panel.py    # Preview panel
│   ├── settings_dialog.py  # Settings dialog
│   └── ...                 # Other GUI components
├── monitor/                # Monitoring layer
│   ├── __init__.py
│   ├── session_manager.py  # Session management
│   ├── window_monitor.py   # Window monitoring
│   └── ...                 # Other monitoring components
├── capture/                # Capture layer
│   ├── __init__.py
│   ├── screenshot.py       # Screenshot capture
│   ├── ocr_engine.py       # OCR processing
│   └── ...                 # Other capture components
├── ai/                     # AI integration
│   ├── __init__.py
│   ├── openai_client.py    # OpenAI client
│   ├── text_generator.py   # Text generation
│   └── ...                 # Other AI components
├── document/               # Document generation
│   ├── __init__.py
│   ├── docx_builder.py     # DOCX generation
│   ├── template_engine.py  # Template processing
│   └── ...                 # Other document components
├── config/                 # Configuration
│   ├── __init__.py
│   ├── config_manager.py   # Config management
│   └── ...                 # Other config components
├── audit/                  # Audit and compliance
│   ├── __init__.py
│   ├── audit_logger.py     # Audit logging
│   └── ...                 # Other audit components
└── utils/                  # Utilities
    ├── __init__.py
    ├── logger.py           # Logging utilities
    └── ...                 # Other utilities
```

### Module Responsibilities

**GUI Layer:**
- User interface presentation
- User input handling
- Display updates
- Dialog management

**Business Logic Layer:**
- Session management
- Workflow orchestration
- Data processing
- Business rules

**Integration Layer:**
- External API integration
- System API calls
- Third-party library integration
- Platform-specific code

**Data Layer:**
- Data persistence
- File operations
- Data validation
- Storage management

### Import Conventions

**Standard Library First:**
```python
import os
import json
from pathlib import Path
```

**Third-Party Libraries:**
```python
import PIL.Image
import openai
import pytesseract
```

**Local Imports:**
```python
from src.monitor.session_manager import SessionManager
from src.ai.text_generator import TextGenerator
```

---

## API Reference

### SessionManager

**Purpose:** Manages documentation session lifecycle

**Location:** `src/monitor/session_manager.py`

**Key Methods:**

```python
class SessionManager:
    def __init__(self, session_id: str, prompt_profile: str, output_dir: Path):
        """Initialize session manager.
        
        Args:
            session_id: Unique session identifier
            prompt_profile: Prompt profile name
            output_dir: Output directory path
        """
        
    def start(self) -> None:
        """Start a new session."""
        
    def stop(self) -> None:
        """Stop the current session."""
        
    def pause(self) -> None:
        """Pause the current session."""
        
    def resume(self) -> None:
        """Resume a paused session."""
        
    def add_step(self, step_data: dict) -> None:
        """Add a step to the session.
        
        Args:
            step_data: Step data dictionary
        """
        
    def get_steps(self) -> list[dict]:
        """Get all steps in the session.
        
        Returns:
            List of step dictionaries
        """
        
    def undo(self) -> bool:
        """Undo last step.
        
        Returns:
            True if undo successful, False otherwise
        """
        
    def redo(self) -> bool:
        """Redo last undone step.
        
        Returns:
            True if redo successful, False otherwise
        """
        
    def get_session_statistics(self) -> dict:
        """Get session statistics.
        
        Returns:
            Dictionary with statistics
        """
```

**Usage Example:**

```python
from pathlib import Path
from src.monitor.session_manager import SessionManager

# Create session manager
session = SessionManager(
    session_id="20231215_143022",
    prompt_profile="sop",
    output_dir=Path("data/sessions")
)

# Start session
session.start()

# Add steps
session.add_step({
    "step_number": 1,
    "window_title": "Login Dialog",
    "screenshot_path": "data/screenshots/step_0001.png",
    "timestamp": "2023-12-15T14:30:25"
})

# Stop session
session.stop()

# Get statistics
stats = session.get_session_statistics()
print(f"Steps: {stats['step_count']}")
```

### TextGenerator

**Purpose:** Generates AI-powered text descriptions

**Location:** `src/ai/text_generator.py`

**Key Methods:**

```python
class TextGenerator:
    def __init__(self, prompt_profile: str):
        """Initialize text generator.
        
        Args:
            prompt_profile: Prompt profile name
        """
        
    def generate_step_description(
        self, 
        step: dict, 
        previous_steps: list[dict]
    ) -> str:
        """Generate description for a step.
        
        Args:
            step: Step data dictionary
            previous_steps: List of previous steps for context
            
        Returns:
            Generated description text
        """
        
    def generate_introduction(self, steps: list[dict]) -> str:
        """Generate introduction text.
        
        Args:
            steps: List of all steps
            
        Returns:
            Generated introduction text
        """
        
    def generate_conclusion(self, steps: list[dict]) -> str:
        """Generate conclusion text.
        
        Args:
            steps: List of all steps
            
        Returns:
            Generated conclusion text
        """
```

**Usage Example:**

```python
from src.ai.text_generator import TextGenerator

# Create text generator
generator = TextGenerator('sop')

# Generate step description
step = {
    "step_number": 1,
    "window_title": "Login Dialog",
    "ocr_text": "Username: [____]\nPassword: [____]\n[Login Button]"
}

previous_steps = []  # No previous steps for first step

description = generator.generate_step_description(step, previous_steps)
print(description)
```

### TemplateEngine

**Purpose:** Generates documents from session data

**Location:** `src/document/template_engine.py`

**Key Methods:**

```python
class TemplateEngine:
    def __init__(
        self, 
        session_manager: SessionManager,
        output_dir: Path,
        template_name: str = "standard"
    ):
        """Initialize template engine.
        
        Args:
            session_manager: Session manager instance
            output_dir: Output directory path
            template_name: Template name
        """
        
    def generate_document(
        self,
        include_introduction: bool = True,
        include_conclusion: bool = True,
        export_formats: dict = None
    ) -> dict[str, Path]:
        """Generate documents in specified formats.
        
        Args:
            include_introduction: Include introduction section
            include_conclusion: Include conclusion section
            export_formats: Dictionary of format flags
                {'docx': True, 'pdf': True, ...}
                
        Returns:
            Dictionary mapping format to output file path
        """
```

**Usage Example:**

```python
from pathlib import Path
from src.document.template_engine import TemplateEngine
from src.monitor.session_manager import SessionManager

# Create session manager
session = SessionManager(...)

# Create template engine
engine = TemplateEngine(
    session_manager=session,
    output_dir=Path("data/output"),
    template_name="standard"
)

# Generate documents
output_files = engine.generate_document(
    include_introduction=True,
    include_conclusion=True,
    export_formats={
        'docx': True,
        'pdf': True,
        'markdown': False,
        'html': False
    }
)

print(f"DOCX: {output_files['docx']}")
print(f"PDF: {output_files['pdf']}")
```

### WindowMonitor

**Purpose:** Monitors window changes

**Location:** `src/monitor/window_monitor.py`

**Key Methods:**

```python
class WindowMonitor:
    def __init__(self, callback: Callable):
        """Initialize window monitor.
        
        Args:
            callback: Function called when window change detected
        """
        
    def start(self) -> None:
        """Start monitoring."""
        
    def stop(self) -> None:
        """Stop monitoring."""
        
    def get_current_window(self) -> dict:
        """Get current window information.
        
        Returns:
            Dictionary with window information
        """
```

---

## Development Workflow

### Branch Strategy

**Main Branches:**
- `main`: Production-ready code
- `develop`: Integration branch for features

**Feature Branches:**
- `feature/feature-name`: New features
- `bugfix/bug-name`: Bug fixes
- `hotfix/hotfix-name`: Critical fixes

### Development Process

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Develop Feature:**
   - Write code
   - Write tests
   - Update documentation

3. **Test:**
   ```bash
   pytest
   pytest --cov=src
   ```

4. **Commit:**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

5. **Push and Create Pull Request:**
   ```bash
   git push origin feature/new-feature
   ```

### Commit Message Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tool changes

**Examples:**
```
feat(session): Add pause/resume functionality

Add ability to pause and resume documentation sessions.
Implements session state management for pause/resume.

Closes #123
```

```
fix(ocr): Fix OCR text extraction for special characters

Handle special characters correctly in OCR text extraction.
Add character encoding handling.

Fixes #456
```

---

## Testing

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_ai.py              # AI component tests
├── test_audit.py           # Audit component tests
├── test_capture.py          # Capture component tests
├── test_config.py          # Configuration tests
├── test_document.py         # Document generation tests
├── test_e2e.py             # End-to-end tests
├── test_integration.py      # Integration tests
└── test_monitor.py          # Monitoring tests
```

### Writing Tests

**Unit Test Example:**

```python
import pytest
from src.monitor.session_manager import SessionManager
from pathlib import Path

def test_session_manager_start():
    """Test session manager start functionality."""
    session = SessionManager(
        session_id="test_session",
        prompt_profile="sop",
        output_dir=Path("data/test")
    )
    
    session.start()
    assert session.is_active() == True
    assert session.get_step_count() == 0
```

**Integration Test Example:**

```python
import pytest
from src.monitor.session_manager import SessionManager
from src.ai.text_generator import TextGenerator
from pathlib import Path

@pytest.mark.integration
def test_session_with_text_generation():
    """Test session with AI text generation."""
    session = SessionManager(...)
    generator = TextGenerator('sop')
    
    session.start()
    session.add_step({...})
    
    step = session.get_steps()[0]
    description = generator.generate_step_description(step, [])
    
    assert description is not None
    assert len(description) > 0
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_ai.py

# Integration tests only
pytest tests/test_integration.py -m integration

# Unit tests only
pytest -m "not integration"
```

### Test Coverage

**Target Coverage:** 80%+

**Coverage Report:**
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

---

## Code Style and Standards

### Python Style Guide

**Follow PEP 8:**
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Follow naming conventions

**Naming Conventions:**
- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Type Hints

**Always use type hints:**

```python
def process_step(step: dict, context: list[dict]) -> str:
    """Process a step with context."""
    ...
```

**Complex types:**

```python
from typing import List, Dict, Optional, Union

def get_steps() -> List[Dict[str, any]]:
    """Get all steps."""
    ...

def find_step(step_id: int) -> Optional[Dict[str, any]]:
    """Find step by ID."""
    ...
```

### Docstrings

**Google-style docstrings:**

```python
def capture_screenshot(window_handle: int) -> PIL.Image:
    """Capture screenshot of specified window.
    
    Args:
        window_handle: Windows HWND handle of the window to capture
        
    Returns:
        PIL Image object containing the screenshot
        
    Raises:
        WindowNotFoundError: If window handle is invalid
        CaptureError: If screenshot capture fails
        
    Example:
        >>> image = capture_screenshot(12345678)
        >>> image.size
        (1920, 1080)
    """
    ...
```

### Code Formatting

**Use `black` formatter:**

```bash
black src/
```

**Configuration (`pyproject.toml`):**

```toml
[tool.black]
line-length = 100
target-version = ['py310']
```

---

## Contributing

### Contribution Process

1. **Fork Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Write Tests**
5. **Update Documentation**
6. **Submit Pull Request**

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No breaking changes (or documented)

### Code Review

**Review Criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance considerations
- Security implications

---

## Debugging

### Logging

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Usage:**

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Debugging Tools

**Python Debugger:**

```python
import pdb

# Set breakpoint
pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

**VS Code Debugging:**

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Main",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal"
    }
  ]
}
```

---

## Performance Optimization

### Profiling

**cProfile:**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Optimization Strategies

**Screenshot Capture:**
- Optimize image processing
- Use efficient image formats
- Minimize memory allocations

**OCR Processing:**
- Cache OCR results
- Optimize image preprocessing
- Use appropriate language settings

**Document Generation:**
- Batch processing
- Optimize template rendering
- Efficient file I/O

---

## Appendices

### Appendix A: Common Tasks

**Add New Export Format:**

1. Create exporter class in `src/document/`
2. Implement export interface
3. Register in `TemplateEngine`
4. Add tests
5. Update documentation

**Add New Prompt Profile:**

1. Create YAML file in `config/prompt_profiles/`
2. Define system prompt and templates
3. Test with sample session
4. Update documentation

### Appendix B: Resources

**Documentation:**
- [Architecture Guide](architecture.md)
- [Development Guide](development-guide.md)
- [User Manual](../USER_MANUAL.md)

**External:**
- [Python Documentation](https://docs.python.org/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Maintained By:** Development Team

