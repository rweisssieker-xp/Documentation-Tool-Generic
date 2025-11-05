# Automatic Documentation Generator (AHG) - User Manual

**Version 1.0.0**

## Table of Contents

1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Getting Started](#getting-started)
4. [User Interface Overview](#user-interface-overview)
5. [Features and Functionality](#features-and-functionality)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Features](#advanced-features)
10. [Appendices](#appendices)

---

## Introduction

### What is AHG?

The Automatic Documentation Generator (AHG) is a fully automated tool for creating illustrated technical documentation from real-world software usage scenarios. It monitors user actions, captures screenshots, and uses AI to generate comprehensive step-by-step manuals.

### Key Features

- **Automatic Monitoring**: Tracks all relevant user actions (window switches, mouse clicks, keyboard input)
- **Screenshot Capture**: Automatically captures screenshots at each relevant step
- **OCR Integration**: Extracts text from screenshots for better context analysis
- **AI Text Generation**: Uses OpenAI GPT models for precise, context-aware descriptions
- **Audit-Safe Documentation**: SHA-256 hash for each screenshot, complete audit trail
- **Configurable Prompt Profiles**: Various styles (SOP, Training, Technical)
- **Multiple Export Formats**: DOCX, PDF, Markdown, HTML, JSON/CSV for audit trails

### Use Cases

- Creating standard operating procedures (SOPs)
- Developing training manuals
- Writing technical documentation
- Documenting software workflows
- Compliance documentation

---

## Installation and Setup

### System Requirements

- **Operating System**: Windows 10/11
- **Python**: Version 3.10 or higher
- **Tesseract OCR**: Required for text recognition
  - Download from: https://github.com/UB-Mannheim/tesseract/wiki
- **OpenAI API Key**: Required for AI text generation
  - Obtain from: https://platform.openai.com/api-keys

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd Documentation-Tool-Generic
```

#### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Install Tesseract OCR

1. Download Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
2. Install it to a location on your system (e.g., `C:\Program Files\Tesseract-OCR`)
3. Set the environment variable `TESSERACT_CMD` to point to the executable:
   - Example: `C:\Program Files\Tesseract-OCR\tesseract.exe`
4. Alternatively, set `TESSDATA_PREFIX` to the Tesseract installation directory

#### 5. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o
   ```

3. Configure other optional settings as needed:
   - `OCR_LANGUAGE`: Language for OCR (default: `deu+eng` for German and English)
   - `PRIVACY_MASK_ENABLED`: Enable/disable privacy masking (default: `true`)

#### 6. Verify Installation

Run the application to verify everything is set up correctly:

```bash
python main.py
```

If you see the main window without errors, the installation is successful.

---

## Getting Started

### First Launch

1. **Start the Application**
   ```bash
   python main.py
   ```

2. **Configure Settings**
   - Press **F1** or click **Settings** to open the settings dialog
   - Navigate to the **OpenAI API** tab
   - Enter your OpenAI API key (or verify it's loaded from `.env`)
   - Select your preferred model (default: `gpt-4o`)

3. **Select a Prompt Profile**
   - Go to the **Prompt Profiles** tab in settings
   - Select a profile:
     - **SOP**: Standard Operating Procedure (formal, compliant)
     - **Training**: Training manual (explanatory, didactic)
     - **Technical**: Technical manual (precise, concise)

4. **Configure Export Formats**
   - Go to the **Export Formats** tab
   - Select desired output formats:
     - DOCX (Microsoft Word) - Recommended
     - PDF - Recommended
     - Markdown - For wikis and web portals
     - HTML - For web viewing
     - JSON/CSV - For audit trails

5. **Enter Document Metadata** (Optional)
   - Go to the **Document Metadata** tab
   - Enter:
     - Department
     - Project
     - Contact information
     - Document ID

### Creating Your First Documentation

1. **Prepare Your Environment**
   - Close unnecessary applications
   - Open the application you want to document
   - Ensure the application window is visible

2. **Start a Session**
   - Click **Start Session** (or press **Ctrl+S**)
   - The status indicator will turn green and show "Recording in progress..."
   - You'll see session statistics updating in real-time

3. **Perform Actions**
   - Work through the process you want to document
   - The application automatically captures screenshots when:
     - You switch windows
     - Window content changes significantly
     - Mouse clicks occur
   - Actions are shown in the preview panel

4. **Manage the Session**
   - **Pause** (Ctrl+P): Temporarily stop recording
   - **Undo** (Ctrl+Z): Remove the last captured step
   - **Redo** (Ctrl+Y): Restore a previously undone step
   - Monitor progress in the statistics panel

5. **End the Session**
   - Click **End Session** (or press **Ctrl+Shift+S**)
   - The application will automatically:
     - Generate AI descriptions for each step
     - Create the documentation in selected formats
     - Save files to `data/output/`
     - Create audit trail files

6. **Review the Output**
   - Navigate to `data/output/` directory
   - Open the generated DOCX or PDF file
   - Review and edit as needed

---

## User Interface Overview

### Main Window

The main window consists of several key areas:

#### 1. Menu Bar

- **File Menu**
  - Settings (F1)
  - Exit (Alt+F4)

- **Session Menu**
  - Start Session (Ctrl+S)
  - End Session (Ctrl+Shift+S)
  - Pause/Resume (Ctrl+P)
  - Undo (Ctrl+Z)
  - Redo (Ctrl+Y)

- **Help Menu**
  - Keyboard Shortcuts
  - About

#### 2. Control Buttons

- **Start Session**: Begins recording a new documentation session
- **End Session**: Stops recording and generates documentation
- **Pause**: Temporarily pauses recording
- **Undo**: Removes the last captured step
- **Redo**: Restores a previously undone step
- **Settings**: Opens configuration dialog

#### 3. Status Indicator

Shows current application status:
- **Ready**: Application is ready to start a session
- **Recording in progress...**: Session is active and capturing steps
- **Recording paused**: Session is paused
- **Generating documents...**: Creating final documentation

#### 4. Preview Panel

Displays captured steps in real-time:
- Step number and window title
- Screenshot thumbnails
- Step descriptions (after AI generation)
- Ability to delete individual steps

#### 5. Statistics Panel

Shows session statistics:
- **Steps**: Number of captured steps
- **Duration**: Session duration (formatted as HH:MM:SS)
- **Screenshots**: Number of captured screenshots

#### 6. Info Panel

Displays:
- Current prompt profile
- Session information
- Error messages
- Completion statistics

### Settings Dialog

Accessible via **F1** or the Settings button, organized in tabs:

#### OpenAI API Tab
- API Key configuration
- Model selection (gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo)

#### Prompt Profiles Tab
- List of available profiles
- Current profile selection
- Profile description display

#### Export Formats Tab
- Checkboxes for each export format:
  - DOCX
  - PDF
  - Markdown
  - HTML
  - JSON (Audit Trail)
  - CSV (Audit Trail)

#### Document Metadata Tab
- Department
- Project
- Contact
- Document ID

---

## Features and Functionality

### Automatic Monitoring

The application monitors several types of user actions:

#### Window Monitoring
- Detects window switches
- Tracks window title changes
- Monitors window size changes
- Identifies significant content changes

#### Mouse and Keyboard Monitoring
- Captures mouse clicks
- Tracks keyboard input (optional)
- Records interaction patterns

#### Trigger Configuration

Actions are captured based on configurable thresholds:
- **Poll Interval**: How often to check for changes (default: 1 second)
- **Change Threshold**: Sensitivity for detecting changes (0.0-1.0)
- **Size Change Threshold**: Minimum pixels for size change detection

Configure in `config/trigger_config.yml`:

```yaml
poll_interval: 1.0          # seconds between checks
change_threshold: 0.5       # change sensitivity (0.0-1.0)
size_change_threshold: 10   # pixels threshold for size changes
double_click_delay: 0.5     # seconds for double-click detection
```

### Screenshot Capture

#### Automatic Capture
Screenshots are automatically captured when:
- Window switches occur
- Significant content changes are detected
- Mouse clicks happen
- Configurable triggers are met

#### Privacy Masking

Sensitive data can be automatically masked:
- Configure masks in `config/privacy_mask.yml`
- Define rectangular or circular mask areas
- Automatic detection of personal data (optional)

Example configuration:

```yaml
masks:
  - type: rectangle
    x: 100
    y: 200
    width: 300
    height: 50
  - type: circle
    center_x: 500
    center_y: 300
    radius: 50
```

### OCR Integration

#### Text Extraction
- Extracts text from captured screenshots
- Supports multiple languages (configured via `OCR_LANGUAGE`)
- Improves AI context understanding

#### Language Support
Default: German and English (`deu+eng`)
- Configure in `.env`: `OCR_LANGUAGE=deu+eng`
- Supports all Tesseract-supported languages

### AI Text Generation

#### Prompt Profiles

The application uses YAML-based prompt profiles to generate text in different styles:

**SOP Profile** (`sop.yml`):
- Formal, compliant language
- Imperative sentences
- Technical terminology
- Step-by-step instructions

**Training Profile** (`training.yml`):
- Explanatory, educational style
- Contextual explanations
- Learning-oriented descriptions
- Beginner-friendly language

**Technical Profile** (`technical.yml`):
- Precise, concise descriptions
- Technical terminology
- Brief explanations
- Expert-level documentation

#### Context Awareness

The AI considers:
- Previous steps in the session
- Window titles and context
- Extracted OCR text
- User actions and interactions

### Document Generation

#### Document Structure

Generated documents include:
- **Title Page**: With metadata and document information
- **Table of Contents**: Automatically generated
- **Introduction**: AI-generated based on captured steps
- **Numbered Steps**: Each with:
  - Screenshot
  - AI-generated description
  - Context information
- **Conclusion**: AI-generated summary
- **Troubleshooting Section**: AI-identified common issues (optional)
- **Security Notes**: Safety considerations (optional)

#### Export Formats

**DOCX (Microsoft Word)**
- Full formatting support
- Editable document
- Professional appearance
- Recommended for most use cases

**PDF**
- Read-only format
- Universal compatibility
- Professional appearance
- Suitable for distribution

**Markdown**
- Plain text format
- Wiki-compatible
- Version control friendly
- Suitable for web portals

**HTML**
- Web-ready format
- Styled output
- Interactive elements
- Suitable for web publishing

**JSON/CSV (Audit Trail)**
- Machine-readable format
- Complete audit information
- Compliance tracking
- Data analysis

### Session Management

#### Session Lifecycle

1. **Start**: Begin recording
2. **Active**: Capturing steps
3. **Paused**: Temporarily stopped
4. **Resumed**: Continue recording
5. **End**: Stop and generate documentation

#### Session Recovery

- Automatic session state saving
- Recovery after crashes
- Resume interrupted sessions
- Session validation on recovery

#### Session Statistics

Tracked metrics:
- Duration
- Step count
- Screenshot count
- Windows used
- Processes used
- Average steps per minute

### Undo/Redo Functionality

- **Undo**: Remove last captured step
- **Redo**: Restore previously undone step
- Maintains step numbering
- Updates preview panel
- History management

### Automatic Cleanup

Configure automatic cleanup in `config/cleanup_config.yml`:

```yaml
auto_cleanup_enabled: true
retention_days_screenshots: 30
retention_days_sessions: 90
```

- Deletes old screenshots after retention period
- Removes completed sessions after retention period
- Runs automatically on application startup
- Manual cleanup available

---

## Configuration

### Environment Variables

Configure in `.env` file:

```env
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
OPENAI_MODEL=gpt-4o
OCR_LANGUAGE=deu+eng
PRIVACY_MASK_ENABLED=true
DATA_DIR=./data
SESSION_DIR=./data/sessions
SCREENSHOT_DIR=./data/screenshots
OUTPUT_DIR=./data/output
```

### Prompt Profiles

Create custom prompt profiles in `config/prompt_profiles/`:

```yaml
name: custom_profile
language: en
style: custom
description: Custom documentation style

system_prompt: |
  You are an expert documentation assistant...
  
step_template: |
  Generate a description for step {step_number}...
  
introduction_template: |
  Create an introduction for {total_steps} steps...
  
conclusion_template: |
  Create a conclusion for the documentation...
```

### Trigger Configuration

Modify `config/trigger_config.yml` to adjust capture sensitivity:

```yaml
poll_interval: 1.0          # Check interval in seconds
change_threshold: 0.5       # Sensitivity (0.0-1.0, higher = more sensitive)
size_change_threshold: 10   # Minimum pixels for size change
double_click_delay: 0.5     # Double-click detection delay
```

### Privacy Mask Configuration

Define areas to mask in `config/privacy_mask.yml`:

```yaml
masks:
  - type: rectangle
    x: 100
    y: 200
    width: 300
    height: 50
  - type: circle
    center_x: 500
    center_y: 300
    radius: 50
```

### Cleanup Configuration

Configure automatic cleanup in `config/cleanup_config.yml`:

```yaml
auto_cleanup_enabled: true
retention_days_screenshots: 30
retention_days_sessions: 90
```

### Document Templates

Configure document structure in `config/document_templates/standard.yml`:

```yaml
name: standard
include_title_page: true
include_table_of_contents: true
include_introduction: true
include_conclusion: true
include_troubleshooting: false
include_security_notes: false
```

---

## Best Practices

### Preparation

1. **Close Unnecessary Applications**
   - Reduces false triggers
   - Cleaner screenshots
   - Better performance

2. **Prepare Your Desktop**
   - Clear desktop clutter
   - Close irrelevant windows
   - Ensure application is visible

3. **Review Application State**
   - Start from a known state
   - Use test data if needed
   - Clear cache if necessary

### During Recording

1. **Work Methodically**
   - Perform actions slowly
   - Wait for UI updates
   - Confirm each step

2. **Use Pause Function**
   - Pause when taking breaks
   - Pause to think through steps
   - Prevents unwanted captures

3. **Monitor Preview Panel**
   - Check captured steps regularly
   - Use Undo if needed
   - Verify screenshots are clear

4. **Avoid Rapid Actions**
   - Slow down complex workflows
   - Pause between major steps
   - Ensure each step is captured

### After Recording

1. **Review Statistics**
   - Check step count
   - Verify duration
   - Review screenshot count

2. **Inspect Generated Documents**
   - Open DOCX file
   - Review AI-generated text
   - Edit if necessary

3. **Check Audit Trail**
   - Verify JSON/CSV files
   - Confirm hash integrity
   - Archive for compliance

### Documentation Quality

1. **Clear Steps**
   - One action per step
   - Logical progression
   - Clear visual context

2. **Consistent Naming**
   - Use descriptive window titles
   - Consistent terminology
   - Clear step descriptions

3. **Appropriate Detail Level**
   - Match target audience
   - Include necessary context
   - Avoid over-documentation

---

## Troubleshooting

### Common Issues

#### 1. OpenAI API Errors

**Problem**: "OpenAI API Key not set" or API errors

**Solutions**:
- Verify `OPENAI_API_KEY` is set in `.env` file
- Check API key is valid and active
- Verify OpenAI API credits and limits
- Check internet connection
- Try a different model if rate-limited

#### 2. Tesseract OCR Not Found

**Problem**: OCR functionality not available

**Solutions**:
- Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
- Set `TESSERACT_CMD` environment variable to executable path
- Alternatively, set `TESSDATA_PREFIX` to installation directory
- Restart application after installation
- Verify installation: `tesseract --version`

#### 3. Screenshots Not Captured

**Problem**: No screenshots during session

**Solutions**:
- Ensure application window is visible and not minimized
- Check no other applications overlay the window
- Verify trigger configuration in `config/trigger_config.yml`
- Increase `poll_interval` if needed
- Decrease `change_threshold` for more sensitivity
- Check application has permission to capture screenshots

#### 4. Document Generation Fails

**Problem**: Error when generating documents

**Solutions**:
- Ensure at least one step was captured
- Verify sufficient disk space available
- Check log files in `logs/` for detailed errors
- Verify prompt profile configuration is valid
- Check OpenAI API is accessible
- Ensure output directory is writable

#### 5. Session Recovery Not Working

**Problem**: Cannot recover session after crash

**Solutions**:
- Check session data exists in `data/sessions/`
- Verify session files are not corrupted
- Check log files for error details
- Ensure session was properly saved
- Try manual recovery from session JSON file

#### 6. Privacy Masking Not Working

**Problem**: Sensitive data not masked

**Solutions**:
- Verify `PRIVACY_MASK_ENABLED=true` in `.env`
- Check `config/privacy_mask.yml` exists and is valid
- Verify mask coordinates are correct
- Test with explicit mask configuration
- Check screenshot coordinates match mask areas

#### 7. Poor AI Text Quality

**Problem**: Generated descriptions are inaccurate or unclear

**Solutions**:
- Try a different prompt profile
- Use a more capable model (e.g., gpt-4o instead of gpt-3.5-turbo)
- Improve screenshot quality (ensure text is readable)
- Check OCR is working correctly
- Review and customize prompt templates
- Provide more context in window titles

#### 8. Application Crashes

**Problem**: Application crashes unexpectedly

**Solutions**:
- Check log files in `logs/` for errors
- Verify all dependencies are installed
- Check system resources (memory, disk space)
- Update Python and dependencies
- Report issue with log files attached

### Log Files

The application creates log files in the `logs/` directory:

- **ahg.log**: Main log file with all activities
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation**: Automatic log rotation (configurable)

View logs to diagnose issues:
```bash
# Windows PowerShell
Get-Content logs\ahg.log -Tail 50

# Windows CMD
type logs\ahg.log | more
```

### Performance Issues

#### Slow Screenshot Capture
- Increase `poll_interval` in trigger config
- Reduce screen resolution
- Close unnecessary applications
- Check system resources

#### Slow Document Generation
- Reduce number of steps
- Use faster OpenAI model
- Disable unnecessary export formats
- Check internet connection speed

#### High Memory Usage
- Enable automatic cleanup
- Reduce retention periods
- Regularly clean old sessions
- Close other applications

---

## Advanced Features

### Batch Processing

Process multiple sessions simultaneously:

1. Configure batch settings
2. Queue multiple sessions
3. Track progress per session
4. Generate all documents at once

### Custom Prompt Profiles

Create custom documentation styles:

1. Create YAML file in `config/prompt_profiles/`
2. Define system prompt and templates
3. Configure language and style
4. Select in settings dialog

### Keyboard Shortcuts

Speed up workflow with shortcuts:

- **Ctrl+S**: Start Session
- **Ctrl+Shift+S**: End Session
- **Ctrl+P**: Pause/Resume
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+Shift+Z**: Redo (alternative)
- **F1**: Open Settings
- **ESC**: End Session (when active)
- **Alt+F4**: Exit Application

### Session Recovery

Recover interrupted sessions:

1. Application automatically saves session state
2. On restart, check for recoverable sessions
3. Select session to recover
4. Resume from last saved state

### Export Customization

Customize export formats:

1. Configure in Settings → Export Formats
2. Set default formats
3. Override per session if needed
4. Export to custom locations

### Document Templates

Customize document structure:

1. Edit templates in `config/document_templates/`
2. Configure sections to include
3. Set formatting options
4. Apply to new sessions

### API Integration

For developers, the application provides Python APIs:

```python
from src.monitor.session_manager import SessionManager
from src.ai.text_generator import TextGenerator
from src.document.template_engine import TemplateEngine

# Create and manage sessions programmatically
session = SessionManager(session_id="test", prompt_profile="sop")
session.start()
# ... perform actions ...
session.stop()

# Generate documentation
generator = TextGenerator('sop')
description = generator.generate_step_description(step, previous_steps)

# Export documents
engine = TemplateEngine(session_manager, template_name="standard")
output_path = engine.generate_document(export_formats={'docx': True})
```

---

## Appendices

### Appendix A: File Structure

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
├── data/                  # Data directory
│   ├── sessions/          # Session data
│   ├── screenshots/       # Screenshots
│   └── output/            # Generated documents
├── config/                # Configuration files
│   ├── prompt_profiles/   # Prompt profiles
│   └── document_templates/ # Document templates
├── logs/                  # Log files
├── tests/                 # Test files
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── README.md              # German documentation
└── USER_MANUAL.md         # This file
```

### Appendix B: Supported Formats

#### Export Formats
- **DOCX**: Microsoft Word format (.docx)
- **PDF**: Portable Document Format (.pdf)
- **Markdown**: Markdown format (.md)
- **HTML**: HyperText Markup Language (.html)
- **JSON**: JavaScript Object Notation (.json)
- **CSV**: Comma-Separated Values (.csv)

#### Image Formats
- **PNG**: Screenshot format (default)
- **JPEG**: Alternative format (if configured)

### Appendix C: Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Start Session |
| Ctrl+Shift+S | End Session |
| Ctrl+P | Pause/Resume |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+Shift+Z | Redo (alternative) |
| F1 | Open Settings |
| ESC | End Session (when active) |
| Alt+F4 | Exit Application |

### Appendix D: Configuration Files

#### Required Files
- `.env`: Environment variables (API keys, paths)
- `config/prompt_profiles/*.yml`: Prompt profiles

#### Optional Files
- `config/trigger_config.yml`: Trigger configuration
- `config/privacy_mask.yml`: Privacy mask configuration
- `config/cleanup_config.yml`: Cleanup configuration
- `config/document_templates/*.yml`: Document templates

### Appendix E: Logging

Log levels:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (critical issues)
- **CRITICAL**: Critical errors (application may stop)

Log location: `logs/ahg.log`

### Appendix F: System Requirements

#### Minimum Requirements
- Windows 10 (64-bit)
- Python 3.10
- 4 GB RAM
- 1 GB free disk space
- Internet connection (for OpenAI API)

#### Recommended Requirements
- Windows 11 (64-bit)
- Python 3.11 or higher
- 8 GB RAM
- 5 GB free disk space
- Stable internet connection
- SSD storage

### Appendix G: Support and Resources

#### Getting Help
- Check log files for error details
- Review troubleshooting section
- Consult README.md (German)
- Check GitHub issues
- Contact support (if available)

#### Useful Links
- Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- OpenAI API: https://platform.openai.com/docs
- Python Documentation: https://docs.python.org/

---

## Version History

### Version 1.0.0
- Complete implementation of all planned features
- Comprehensive test suite
- Extended documentation
- Production-ready error handling
- Session recovery & cleanup
- Multiple export formats
- Privacy masking
- Audit trail support

---

## License

[License information to be added]

---

## Acknowledgments

- Built with Python and Tkinter
- Uses OpenAI GPT models for text generation
- Tesseract OCR for text recognition
- Various open-source libraries (see requirements.txt)

---

**End of User Manual**

For technical documentation and developer information, please refer to the README.md file and source code documentation.

