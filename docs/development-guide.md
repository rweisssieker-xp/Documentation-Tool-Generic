# Development Guide

## Prerequisites

### Required Software

- **Python:** 3.10 or higher
- **Tesseract OCR:** [Download](https://github.com/UB-Mannheim/tesseract/wiki)
- **Git:** For version control
- **IDE:** VS Code, PyCharm, or similar

### Python Dependencies

All dependencies are listed in `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Documentation-Tool-Generic
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
copy env.example .env
# Edit .env and add your OpenAI API key
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model name (default: gpt-5)
- `TESSDATA_PREFIX`: Path to Tesseract data directory (optional)

### 5. Install Tesseract OCR

1. Download Tesseract from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location or set `TESSDATA_PREFIX` environment variable
3. Verify installation: `tesseract --version`

## Local Development

### Running the Application

```bash
python main.py
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
```

### Running Startup Validation

```bash
python scripts/validate_startup.py
```

## Build Process

### Development Build

No build required for development - run directly with Python.

### Production Build

For creating standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## Project Structure

See [Source Tree Analysis](./source-tree-analysis.md) for detailed structure.

## Code Style

- **Formatting:** Follow PEP 8
- **Type Hints:** Use type hints for function parameters and returns
- **Docstrings:** Use Google-style docstrings
- **Imports:** Organize imports (standard library, third-party, local)

Example:

```python
from typing import Optional, Dict, List
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


def process_screenshot(
    screenshot_path: Path,
    options: Optional[Dict] = None
) -> Dict[str, str]:
    """
    Process a screenshot and extract text.
    
    Args:
        screenshot_path: Path to screenshot file
        options: Optional processing options
        
    Returns:
        Dictionary with extracted text and metadata
    """
    # Implementation
    pass
```

## Common Development Tasks

### Adding a New Export Format

1. Create exporter class in `src/document/`
2. Implement export interface
3. Add export dialog in `src/gui/`
4. Register in MainWindow
5. Add tests

### Adding a New Monitoring Feature

1. Create monitor class in `src/monitor/`
2. Integrate with SessionManager
3. Add configuration options
4. Add tests

### Adding a New AI Feature

1. Extend OpenAI client or create new client
2. Add prompt templates
3. Integrate with TextGenerator
4. Add tests

## Testing

### Test Structure

- **Unit Tests:** Test individual components in isolation
- **Integration Tests:** Test component interactions
- **E2E Tests:** Test full workflows

### Writing Tests

```python
import pytest
from src.monitor.session_manager import SessionManager

def test_session_creation():
    """Test session creation."""
    session = SessionManager(
        session_id="test-123",
        prompt_profile="technical"
    )
    assert session.session_id == "test-123"
    assert session.prompt_profile == "technical"
```

### Test Fixtures

Common fixtures in `tests/conftest.py`:
- Mock OpenAI client
- Test session data
- Temporary directories

## Debugging

### Logging

The application uses structured logging:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Information message")
logger.error("Error message", exc_info=True)
```

Log files are stored in `logs/ahg.log`.

### Debug Mode

Enable debug logging by setting log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Configuration

### Configuration Files

- **Trigger Config:** `config/trigger_config.yml` - Action detection thresholds
- **Privacy Mask:** `config/privacy_mask.yml` - Privacy masking rules
- **Cleanup Config:** `config/cleanup_config.yml` - File cleanup settings
- **Prompt Profiles:** `config/prompt_profiles/` - AI prompt templates

### Adding Configuration

1. Create YAML file in `config/`
2. Add config loader in `src/config/config_manager.py`
3. Add validation in `src/config/config_validator.py`
4. Use in application code

## Git Workflow

### Branching Strategy

- **main:** Production-ready code
- **develop:** Development branch
- **feature/:** Feature branches
- **fix/:** Bug fix branches

### Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

## Troubleshooting

### Common Issues

**Issue:** Tesseract not found
- **Solution:** Install Tesseract and set `TESSDATA_PREFIX`

**Issue:** OpenAI API errors
- **Solution:** Check API key in `.env` file

**Issue:** Screenshot capture fails
- **Solution:** Check Windows permissions and pywin32 installation

**Issue:** GUI not responding
- **Solution:** Check for blocking operations, use threading

## Performance Optimization

### Screenshot Optimization

- Use efficient image formats
- Compress images before storage
- Batch screenshot operations

### AI API Optimization

- Cache API responses where possible
- Batch API calls
- Use appropriate model sizes

### Memory Management

- Clean up large objects after use
- Use generators for large datasets
- Monitor memory usage

## Deployment Checklist

- [ ] Update version in `main.py`
- [ ] Update `CHANGELOG.md`
- [ ] Run all tests
- [ ] Update documentation
- [ ] Create release tag
- [ ] Build executable (if needed)
- [ ] Test on clean environment

