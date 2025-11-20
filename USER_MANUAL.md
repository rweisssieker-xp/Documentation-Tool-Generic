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
   OPENAI_MODEL=gpt-5
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
   - Select your preferred model (default: `gpt-5`)

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
  - Session Recovery... (restore interrupted sessions)

- **Export Menu**
  - Multi-Language Export... (export documentation in multiple languages)
  - Cloud Upload... (upload documents to cloud storage)
  - Quick Reference... (generate quick reference guide)
  - Video Export... (create video walkthrough from screenshots)
  - Platform Export... (export for specific platforms)
  - Export Filter... (filter steps before export)

- **Tools Menu**
  - Cleanup... (manual cleanup of old files)
  - Batch Processing... (process multiple sessions)
  - Statistics... (view session statistics dashboard)
  - Step Consolidation... (merge similar steps)
  - Session Comparison... (compare two sessions)
  - Test Checklist Generator... (generate test checklist from steps)
  - Quality Check... (check documentation quality)
  - Export Filter... (filter steps before export)

- **Automation Menu**
  - App Exploration... (automatically explore and document an application)

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
- Ability to reorder steps (drag and drop)

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
- Model selection (gpt-5, gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo)

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

The application employs a sophisticated multi-layered monitoring system that tracks user interactions and system state changes in real-time. Understanding how this works helps optimize capture quality and performance.

#### Window Monitoring - Detailed Process

The window monitoring system uses Windows API calls (`pywin32`) to continuously track the active foreground window. Here's how it works:

**1. Polling Mechanism**
- The system polls the foreground window at configurable intervals (default: 1 second)
- Uses `win32gui.GetForegroundWindow()` to obtain the current window handle (HWND)
- Runs in a separate background thread to avoid blocking the main application

**2. Window Information Extraction**
For each detected window, the system extracts:
- **Window Handle (HWND)**: Unique Windows identifier for the window
- **Window Title**: The text displayed in the window's title bar
- **Class Name**: Windows class name (e.g., "Notepad", "Chrome_WidgetWin_1")
- **Process Information**: 
  - Process ID (PID)
  - Process name (executable name)
  - Full executable path
- **Position and Size**: 
  - Left, top, right, bottom coordinates
  - Width and height in pixels
- **Timestamp**: Precise capture time

**3. Change Detection Algorithm**
The system determines if a capture should occur based on multiple criteria:

**Window Switch Detection**:
- Compares current window handle with previous window handle
- Detects when user switches between different applications
- Captures immediately on window switch

**Title Change Detection**:
- Monitors window title text for changes
- Useful for applications that change titles (e.g., "Untitled - Notepad" → "Document.txt - Notepad")
- Triggers capture when title changes within the same window

**Size Change Detection**:
- Compares current window dimensions with previous dimensions
- Only triggers if change exceeds threshold (default: 10 pixels)
- Helps capture when windows are resized or maximized/minimized

**Content Change Detection**:
- Uses time-based heuristics to detect content changes
- Monitors for extended periods of activity in the same window
- Can detect when form fields change or dialogs appear

**4. Window State Tracking**
The system maintains a state dictionary tracking:
- Last known window information
- Timestamp of last capture
- Window key (combination of process name and class name)
- Previous position and size

**Example Window Information Dictionary**:
```python
{
    'hwnd': 12345678,
    'title': 'Document.txt - Notepad',
    'class_name': 'Notepad',
    'pid': 7890,
    'process_name': 'notepad.exe',
    'executable_path': 'C:\\Windows\\System32\\notepad.exe',
    'position': {
        'left': 100,
        'top': 100,
        'right': 800,
        'bottom': 600,
        'width': 700,
        'height': 500
    },
    'timestamp': 1699123456.789
}
```

#### Mouse and Keyboard Monitoring

**Mouse Click Detection**:
- Captures mouse click events through Windows hooks
- Records click coordinates relative to the active window
- Distinguishes between left, right, and middle mouse button clicks
- Supports double-click detection with configurable delay

**Keyboard Input Monitoring**:
- Optional feature for capturing keyboard input
- Can be enabled/disabled for privacy reasons
- Filters sensitive inputs (passwords, etc.) automatically
- Records typed text for context in documentation

**Interaction Pattern Recording**:
- Tracks sequences of mouse and keyboard events
- Identifies common interaction patterns (e.g., click → type → click)
- Helps AI understand workflow context

#### Trigger Configuration - Detailed Settings

Actions are captured based on configurable thresholds that control sensitivity and performance:

**Poll Interval** (`poll_interval`):
- **Default**: 1.0 seconds
- **Range**: 0.1 to 10.0 seconds
- **Effect**: How frequently the system checks for changes
- **Lower values**: More responsive, higher CPU usage
- **Higher values**: Less CPU usage, may miss rapid changes
- **Recommendation**: 
  - Fast workflows: 0.5 seconds
  - Normal use: 1.0 seconds
  - Slow workflows: 2.0 seconds

**Change Threshold** (`change_threshold`):
- **Default**: 0.5
- **Range**: 0.0 to 1.0
- **Effect**: Sensitivity for detecting content changes
- **Lower values**: Less sensitive, fewer captures
- **Higher values**: More sensitive, more captures
- **Note**: This is a time-based threshold (in seconds) for detecting changes

**Size Change Threshold** (`size_change_threshold`):
- **Default**: 10 pixels
- **Range**: 1 to 100 pixels
- **Effect**: Minimum pixel change required to trigger capture
- **Lower values**: Captures small size changes
- **Higher values**: Only captures significant size changes
- **Use case**: Prevents captures from minor window adjustments

**Double-Click Delay** (`double_click_delay`):
- **Default**: 0.5 seconds
- **Range**: 0.1 to 2.0 seconds
- **Effect**: Maximum time between clicks to be considered double-click
- **Note**: Windows default is typically 0.5 seconds

**Complete Configuration Example**:
```yaml
# config/trigger_config.yml

# Polling Configuration
poll_interval: 1.0          # Check every 1 second

# Change Detection
change_threshold: 0.5       # Consider changes after 0.5 seconds
size_change_threshold: 10    # Minimum 10 pixels for size change

# Mouse Interaction
double_click_delay: 0.5     # 500ms for double-click detection

# Advanced Options (if supported)
min_capture_interval: 2.0    # Minimum seconds between captures
max_captures_per_minute: 30  # Rate limiting
```

**Tuning Guide**:
- **Too many captures**: Increase `poll_interval` and `change_threshold`, increase `size_change_threshold`
- **Too few captures**: Decrease `poll_interval` and `change_threshold`, decrease `size_change_threshold`
- **Performance issues**: Increase `poll_interval`, enable rate limiting
- **Missed rapid changes**: Decrease `poll_interval` and `min_capture_interval`

### Screenshot Capture - Detailed Process

#### Automatic Capture Mechanism

Screenshots are automatically captured through a multi-stage process:

**1. Capture Trigger**
Screenshots are triggered when:
- **Window switches occur**: User switches to a different application window
- **Title changes**: Window title changes (e.g., file save changes title)
- **Size changes**: Window is resized beyond threshold
- **Content changes**: Significant content change detected (time-based)
- **Mouse clicks**: User clicks in the active window (optional)
- **Manual trigger**: User manually requests capture (future feature)

**2. Screenshot Capture Process**

**Step 1: Window Identification**
- System identifies the active window using `win32gui.GetForegroundWindow()`
- Validates window is visible and not minimized
- Checks window dimensions (must be > 0 pixels)

**Step 2: Window Capture**
- Uses `mss` library for efficient screen capture
- Captures only the active window, not entire screen
- Maintains original resolution and color depth
- Handles multi-monitor setups automatically

**Step 3: Image Processing**
- Converts captured image to PIL Image object
- Applies privacy masks if configured
- Optimizes image quality (no compression artifacts)
- Saves in PNG format for lossless quality

**Step 4: File Management**
- Generates unique filename: `step_0001.png`, `step_0002.png`, etc.
- Stores in session-specific directory: `data/screenshots/{session_id}/`
- Creates directory structure automatically
- Maintains file associations in session data

**Example Screenshot File Structure**:
```
data/screenshots/
└── 20231215_143022/          # Session ID directory
    ├── step_0001.png         # First screenshot
    ├── step_0002.png         # Second screenshot
    ├── step_0003.png         # Third screenshot
    └── ...
```

**3. Screenshot Metadata**

Each screenshot includes metadata:
```python
{
    'step_number': 1,
    'timestamp': '2023-12-15T14:30:22.123456',
    'window_title': 'Document.txt - Notepad',
    'window_class': 'Notepad',
    'process_name': 'notepad.exe',
    'position': {
        'left': 100,
        'top': 100,
        'right': 800,
        'bottom': 600,
        'width': 700,
        'height': 500
    },
    'screenshot_path': 'data/screenshots/20231215_143022/step_0001.png',
    'file_size_bytes': 245678,
    'resolution': {'width': 700, 'height': 500}
}
```

**4. Error Handling**

The capture system includes robust error handling:
- **Window not accessible**: Retries up to 2 times with 100ms delay
- **Permission denied**: Logs warning, continues with next window
- **Disk full**: Raises error, allows user to free space
- **Invalid window handle**: Skips capture, logs warning

**5. Performance Considerations**

- **Capture time**: Typically 50-200ms per screenshot
- **File size**: Average 100-500 KB per PNG screenshot
- **Storage**: ~1-5 MB per session (10-20 screenshots)
- **CPU usage**: Minimal impact (~1-2% during capture)

#### Privacy Masking - Detailed Configuration

The privacy masking system protects sensitive data through multiple mechanisms:

**1. Static Mask Configuration**

Define fixed mask areas in `config/privacy_mask.yml`:

```yaml
# Rectangular masks for fixed UI elements
masks:
  - type: rectangle
    x: 100          # Left coordinate (pixels from left edge)
    y: 200          # Top coordinate (pixels from top edge)
    width: 300      # Width in pixels
    height: 50      # Height in pixels
    description: "Username field"
    
  # Circular masks for icons or circular elements
  - type: circle
    center_x: 500   # Center X coordinate
    center_y: 300   # Center Y coordinate
    radius: 50      # Radius in pixels
    description: "Profile picture"
    
  # Multiple masks can be defined
  - type: rectangle
    x: 100
    y: 250
    width: 300
    height: 30
    description: "Password field"
```

**2. Automatic Detection**

The system can automatically detect sensitive data:
- **Email addresses**: Pattern matching for email format
- **Phone numbers**: International phone number patterns
- **Credit card numbers**: Luhn algorithm validation
- **Social security numbers**: Pattern matching
- **Personal names**: OCR-based detection (experimental)

**3. Mask Application Process**

**Step 1: OCR Text Extraction**
- Extracts text from screenshot using Tesseract OCR
- Identifies text regions and coordinates

**Step 2: Pattern Matching**
- Searches for sensitive data patterns in OCR text
- Identifies bounding boxes for detected sensitive data

**Step 3: Mask Rendering**
- Applies black rectangles over identified areas
- Blurs sensitive regions (alternative to black boxes)
- Maintains screenshot dimensions and quality

**4. Mask Configuration Options**

```yaml
# config/privacy_mask.yml

# Enable/disable automatic detection
auto_detection_enabled: true

# Detection patterns
detection_patterns:
  - email: true
  - phone: true
  - credit_card: false
  - ssn: true
  - ip_address: false

# Mask rendering style
mask_style: black_rectangle  # Options: black_rectangle, blur, pixelate

# Blur intensity (if using blur style)
blur_intensity: 15

# Static masks (always applied)
masks:
  - type: rectangle
    x: 100
    y: 200
    width: 300
    height: 50
```

**5. Verification**

After masking, verify effectiveness:
- Check masked screenshots in `data/screenshots/` directory
- Ensure sensitive data is completely obscured
- Adjust mask coordinates if needed
- Test with sample data before production use

### OCR Integration - Detailed Process

#### Text Extraction Workflow

**1. OCR Engine Initialization**

The OCR engine uses Tesseract OCR:
- Initializes with specified language(s)
- Loads language data files (tessdata)
- Configures OCR parameters (PSM, OEM modes)
- Validates installation and availability

**2. Text Extraction Process**

**Step 1: Image Preprocessing** (optional)
- Converts color image to grayscale
- Enhances contrast for better recognition
- Resizes if necessary (maintains aspect ratio)
- Applies noise reduction filters

**Step 2: OCR Processing**
- Processes image with Tesseract OCR engine
- Extracts text with bounding box coordinates
- Identifies text regions and lines
- Handles multiple languages simultaneously

**Step 3: Text Post-Processing**
- Cleans extracted text (removes artifacts)
- Formats text structure (paragraphs, lines)
- Extracts confidence scores per word
- Maps text to screen coordinates

**3. OCR Output Format**

```python
{
    'raw_text': 'Username: admin\nPassword: ********\nLogin',
    'words': [
        {
            'text': 'Username:',
            'confidence': 95.5,
            'bbox': {'x': 100, 'y': 200, 'width': 80, 'height': 20}
        },
        {
            'text': 'admin',
            'confidence': 98.2,
            'bbox': {'x': 190, 'y': 200, 'width': 50, 'height': 20}
        },
        # ... more words
    ],
    'language': 'deu+eng',
    'processing_time': 0.5  # seconds
}
```

**4. Language Support**

**Supported Languages**:
The system supports all Tesseract-supported languages. Common ones include:
- **German**: `deu`
- **English**: `eng`
- **French**: `fra`
- **Spanish**: `spa`
- **Multiple languages**: `deu+eng` (processes both)

**Configuration**:
```env
# Single language
OCR_LANGUAGE=eng

# Multiple languages (recommended)
OCR_LANGUAGE=deu+eng

# Three languages
OCR_LANGUAGE=deu+eng+fra
```

**Language Code Reference**:
- Use ISO 639-2 language codes
- Separate multiple languages with `+`
- Order matters: First language is primary
- All language data files must be installed

**5. OCR Performance**

**Speed**:
- Small images (< 500x500px): 0.1-0.3 seconds
- Medium images (500-1500px): 0.3-1.0 seconds
- Large images (> 1500px): 1.0-3.0 seconds

**Accuracy**:
- High-quality screenshots: 95-99% accuracy
- Low-quality screenshots: 70-85% accuracy
- Depends on: font size, contrast, language, image quality

**Optimization Tips**:
- Use high-resolution screenshots
- Ensure good contrast
- Avoid small fonts (< 10pt)
- Use appropriate language setting
- Enable image preprocessing if needed

**6. OCR Integration with AI**

The extracted OCR text is used to enhance AI-generated descriptions:
- Provides context about on-screen elements
- Helps identify UI components and labels
- Improves description accuracy
- Enables automatic field identification

**Example Flow**:
1. Screenshot captured → OCR extracts text
2. OCR text → Privacy mask identifies sensitive data
3. Masked screenshot + OCR text → AI generates description
4. Description includes references to UI elements found in OCR text

### AI Text Generation - Detailed Process

#### OpenAI API Integration

The application uses OpenAI's GPT models to generate high-quality, context-aware descriptions. The integration includes:

**1. API Client Architecture**

**Connection Management**:
- Loads API key from `.env` file or environment variables
- Validates API key format before making requests
- Handles authentication automatically
- Supports multiple OpenAI models

**Model Selection**:
- **gpt-5** (recommended): Latest flagship model, best quality, supports vision API
- **gpt-4o**: High quality, supports vision API
- **gpt-4-turbo**: High quality, faster than gpt-4
- **gpt-4**: High quality, reliable
- **gpt-3.5-turbo**: Fast, cost-effective for simple tasks

**Error Handling**:
- Retry logic with exponential backoff (up to 3 retries)
- Handles rate limiting automatically
- Manages API errors gracefully
- Logs all API interactions for debugging

**2. Request Structure**

**System Prompt**:
- Defines the AI's role and behavior
- Sets tone and style guidelines
- Specifies output format requirements
- Loaded from prompt profile YAML file

**User Prompt**:
- Contains step-specific information
- Includes OCR text from screenshot
- Provides context from previous steps
- Formatted according to prompt template

**Example API Request**:
```python
{
    "model": "gpt-5",
    "messages": [
        {
            "role": "system",
            "content": "You are an expert documentation assistant..."
        },
        {
            "role": "user",
            "content": "Generate a description for step 1:\nWindow: Login Dialog\nOCR Text: Username: [____]\nPassword: [____]\n[Login Button]"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500
}
```

**3. Response Processing**

**Text Extraction**:
- Extracts generated text from API response
- Handles streaming responses if enabled
- Validates response format
- Cleans and formats output text

**Error Recovery**:
- Falls back to template-based descriptions if API fails
- Uses window title as fallback description
- Logs errors for debugging
- Continues processing remaining steps

#### Prompt Profiles - Detailed Configuration

The application uses YAML-based prompt profiles to generate text in different styles. Each profile defines:

**Profile Structure**:
```yaml
name: sop                    # Profile identifier
language: de                 # Target language (de, en, etc.)
style: sop                   # Style identifier
description: "Standard Operating Procedure (formal, compliant)"

system_prompt: |
  You are an expert documentation assistant...
  
step_template: |
  Generate a description for step {step_number}...
  
introduction_template: |
  Create an introduction for {total_steps} steps...
  
conclusion_template: |
  Create a conclusion for the documentation...
```

**SOP Profile** (`sop.yml`):
- **Language**: Formal, compliant, professional
- **Sentence Structure**: Imperative sentences ("Click the button", "Enter the value")
- **Terminology**: Technical, precise terminology
- **Format**: Step-by-step instructions with expected outcomes
- **Use Case**: Standard operating procedures, compliance documentation

**Example SOP Output**:
> "Step 1: Login Dialog
> 
> Click in the 'Username' field and enter your username. Click in the 'Password' field and enter your password. Click the 'Login' button to proceed. The system will authenticate your credentials and display the main application window."

**Training Profile** (`training.yml`):
- **Language**: Explanatory, educational, friendly
- **Sentence Structure**: Descriptive sentences with context
- **Terminology**: Beginner-friendly, explains technical terms
- **Format**: Explanatory paragraphs with learning objectives
- **Use Case**: Training manuals, user guides, onboarding materials

**Example Training Output**:
> "Step 1: Login Dialog
> 
> You will see the login dialog, which is the first screen you encounter when starting the application. This dialog contains two text fields: one for your username and one for your password. The username field is located at the top, and the password field is below it. Both fields are empty when you first see them. At the bottom of the dialog, you'll find the 'Login' button. To log in, simply click in the username field, type your username, then click in the password field and type your password. Finally, click the 'Login' button to access the application."

**Technical Profile** (`technical.yml`):
- **Language**: Precise, concise, technical
- **Sentence Structure**: Short, direct statements
- **Terminology**: Technical terminology without explanation
- **Format**: Brief technical descriptions
- **Use Case**: Technical documentation, API documentation, developer guides

**Example Technical Output**:
> "Step 1: Login Dialog
> 
> Access login dialog. Enter credentials in username and password fields. Click Login button to authenticate. System validates credentials and redirects to main interface."

**4. Template Variables**

Prompt templates support variables that are replaced at runtime:

**Available Variables**:
- `{step_number}`: Current step number (1, 2, 3, ...)
- `{window_title}`: Window title text
- `{ocr_text}`: Extracted OCR text (truncated to 2000 chars)
- `{context}`: Context from previous steps (last 3 steps)
- `{total_steps}`: Total number of steps in session
- `{window_titles}`: List of all window titles
- `{metadata}`: Additional metadata dictionary

**Example Template**:
```yaml
step_template: |
  Generate a description for step {step_number}:
  
  Window Title: {window_title}
  OCR Text: {ocr_text}
  
  Previous Steps:
  {context}
  
  Create a concise step description (2-3 sentences).
```

**5. Context Awareness - Detailed Process**

The AI considers multiple sources of context when generating descriptions:

**Previous Steps Context**:
- Last 3 steps are included in context (configurable)
- Each previous step includes:
  - Step number
  - Window title
  - Generated description (if available)
- Provides workflow continuity
- Helps AI understand progression

**Example Context Format**:
```
Previous Steps:
- Step 1: Login Dialog: Click in the username field and enter your username...
- Step 2: Main Window: The main application window displays after successful login...
- Step 3: Settings Menu: Navigate to Settings menu by clicking the gear icon...
```

**Window Title Context**:
- Window title often contains useful information
- File names, application names, dialog types
- Helps AI understand screen purpose
- Example: "Document.txt - Notepad" indicates text editor with open file

**OCR Text Context**:
- Extracted text provides UI element information
- Identifies buttons, labels, fields
- Shows current state of interface
- Limited to 2000 characters to avoid token limits

**Metadata Context**:
- Additional information from window monitoring
- Process name, executable path
- Window position and size
- Timestamp information

**6. Generation Process Flow**

**Step 1: Step Collection**
- Session manager collects all captured steps
- Steps are ordered chronologically
- Each step has screenshot and metadata

**Step 2: Sequential Processing**
- Steps are processed one at a time
- Previous steps are included in context
- OCR text is extracted for each screenshot
- Prompt is formatted with all available data

**Step 3: API Call**
- Formatted prompt sent to OpenAI API
- System prompt defines AI behavior
- User prompt contains step-specific data
- Response is awaited (typically 2-10 seconds)

**Step 4: Result Processing**
- Generated text is extracted from response
- Text is cleaned and formatted
- Step description is updated
- Process continues to next step

**Step 5: Batch Generation** (Alternative)
- All steps can be processed in batch
- More efficient for large sessions
- Requires careful context management
- Faster overall processing time

**7. Performance Considerations**

**Generation Time**:
- Per step: 2-10 seconds (depends on API response time)
- For 20 steps: 40-200 seconds total
- Can be parallelized for faster processing

**Token Usage**:
- Each step: ~200-500 tokens
- Entire session: ~5000-15000 tokens (20 steps)
- Costs: ~$0.01-0.10 per session (gpt-5 pricing, varies by model)

**Optimization Tips**:
- Use gpt-3.5-turbo for faster, cheaper generation
- Limit OCR text length (already limited to 2000 chars)
- Reduce context window (only last 3 steps)
- Batch process multiple steps
- Cache descriptions for repeated steps

### Document Generation - Detailed Process

#### Document Structure - Complete Overview

Generated documents follow a structured format designed for professional documentation:

**1. Title Page**

The title page includes:
- **Document Title**: Main title (from session metadata or prompt profile)
- **Subtitle**: Optional subtitle (e.g., "User Manual", "Training Guide")
- **Metadata Section**:
  - Author name (from system username or configuration)
  - Creation date (formatted as DD.MM.YYYY)
  - Version number (default: 1.0)
  - Department (if configured)
  - Project name (if configured)
  - Contact information (if configured)
  - Document ID (if configured)
- **Formatting**: Centered text, professional typography
- **Page Break**: Automatic page break after title page

**2. Table of Contents**

- **Automatic Generation**: Generated from document headings
- **Hierarchical Structure**: 
  - Level 1: Introduction, Conclusion, Troubleshooting
  - Level 2: Individual steps (Step 1, Step 2, etc.)
- **Page Numbers**: References to page numbers (if supported)
- **Formatting**: Indented according to heading level
- **Update**: Automatically updated after document generation

**3. Introduction**

- **AI-Generated**: Created using introduction template from prompt profile
- **Content Includes**:
  - Purpose of the documentation
  - Scope and applicability
  - Overview of the process
  - Prerequisites (if mentioned)
  - Expected outcomes
- **Length**: Typically 100-200 words
- **Format**: Paragraph format, justified alignment

**4. Numbered Steps**

Each step includes:

**Step Header**:
- Step number (e.g., "Step 1:")
- Window title (e.g., "Login Dialog")
- Formatted as Heading 2 style

**Screenshot**:
- Full-resolution screenshot embedded in document
- Width: 6 inches (maintains aspect ratio)
- Centered alignment
- Caption below: "Figure X: [Window Title]"
- Caption formatting: Italic, 9pt font, centered

**Description**:
- AI-generated text description
- Paragraph format, justified alignment
- References to UI elements identified in OCR text
- Context-aware descriptions

**Metadata** (optional):
- Timestamp (formatted)
- Process name
- Window class name

**5. Conclusion**

- **AI-Generated**: Created using conclusion template
- **Content Includes**:
  - Summary of completed process
  - Key points reminder
  - Next steps or related procedures
  - References to related documentation
- **Length**: Typically 50-100 words
- **Format**: Paragraph format, justified alignment

**6. Troubleshooting Section** (Optional)

- **AI-Generated**: Identifies common issues and solutions
- **Format**: 
  - Problem statements
  - Solution descriptions
  - 3-5 common issues typically included
- **Based On**: Analysis of captured steps and common workflow issues

**7. Security Notes** (Optional)

- **AI-Generated**: Safety and security considerations
- **Content Includes**:
  - General security aspects
  - Process-specific risks
  - Preventive measures
  - Best practices
- **Length**: Typically 100-150 words

#### Document Generation Process

**Step 1: Preparation**

Before generation begins:
- All steps are collected from session manager
- Screenshots are verified (exist and are accessible)
- AI descriptions are generated (if not already done)
- Document metadata is prepared
- Export formats are determined

**Step 2: Document Creation**

**DOCX Creation**:
1. Create new Document object
2. Configure page margins (1 inch all sides)
3. Set document properties (title, author, etc.)
4. Add title page
5. Add table of contents placeholder
6. Add introduction (if enabled)
7. Add each step sequentially:
   - Add step heading
   - Embed screenshot
   - Add screenshot caption
   - Add description paragraph
8. Add conclusion (if enabled)
9. Add troubleshooting (if enabled)
10. Add security notes (if enabled)
11. Update table of contents
12. Save document

**Step 3: Export Conversion**

**PDF Export**:
- Converts DOCX to PDF using `docx2pdf` or `reportlab`
- Maintains formatting and layout
- Embeds fonts if necessary
- Sets metadata (title, author, etc.)

**Markdown Export**:
- Converts DOCX structure to Markdown syntax
- Preserves headings (#, ##, ###)
- Embeds images as relative paths
- Maintains text formatting (bold, italic)
- Creates compatible structure for wikis

**HTML Export**:
- Converts DOCX to HTML with CSS styling
- Embeds images as base64 or relative paths
- Applies professional CSS stylesheet
- Creates self-contained HTML file
- Includes responsive design elements

**Step 4: File Management**

**Output Directory Structure**:
```
data/output/
└── 20231215_143022/              # Session ID directory
    ├── manual_20231215_143022.docx
    ├── manual_20231215_143022.pdf
    ├── manual_20231215_143022.md
    ├── manual_20231215_143022.html
    ├── audit_trail_20231215_143022.json
    └── audit_trail_20231215_143022.csv
```

**Naming Convention**:
- Format: `{prefix}_{session_id}.{extension}`
- Prefix: `manual` for documents, `audit_trail` for audit files
- Session ID: `YYYYMMDD_HHMMSS` format
- Extensions: `.docx`, `.pdf`, `.md`, `.html`, `.json`, `.csv`

**Step 5: Validation**

After generation:
- Verify all files were created successfully
- Check file sizes (should be > 0 bytes)
- Validate document structure
- Test opening documents in respective applications
- Log generation statistics

#### Export Formats - Detailed Specifications

**DOCX (Microsoft Word)**

**Format**: Open XML format (.docx)
**Library**: `python-docx`
**Features**:
- Full formatting support (headings, paragraphs, images)
- Editable text content
- Professional styling
- Compatible with Microsoft Word, LibreOffice, Google Docs
- Supports tables, lists, hyperlinks
- Embeddable images (PNG format)

**Technical Details**:
- Page size: Letter (8.5" x 11") or A4 (210mm x 297mm)
- Margins: 1 inch (2.54 cm) all sides
- Font: Calibri (default), 11pt body text
- Headings: Calibri, bold, various sizes
- Image width: 6 inches (maintains aspect ratio)
- Line spacing: Single (1.0)

**Limitations**:
- Maximum file size: ~50 MB (practical limit)
- Maximum pages: Limited by memory
- Complex formatting: May require manual adjustment

**PDF**

**Format**: Portable Document Format (.pdf)
**Library**: `docx2pdf` (Windows) or `reportlab`
**Features**:
- Read-only format (cannot be edited)
- Universal compatibility (all platforms)
- Professional appearance
- Print-ready format
- File size optimization

**Technical Details**:
- Page size: Letter or A4 (matches DOCX)
- Resolution: 300 DPI (for print quality)
- Compression: Automatic image compression
- Font embedding: Embed fonts for consistency
- Security: Can be password-protected (optional)

**Limitations**:
- No editing capability
- Requires conversion tool installation
- Larger file size than DOCX (compressed images)

**Markdown**

**Format**: Markdown text format (.md)
**Library**: Custom converter
**Features**:
- Plain text format (human-readable)
- Wiki-compatible syntax
- Version control friendly (Git, SVN)
- Easy to edit manually
- Lightweight file size

**Syntax Examples**:
```markdown
# Document Title

## Introduction

This is the introduction text.

## Step 1: Login Dialog

![Figure 1: Login Dialog](screenshots/step_0001.png)

Click in the username field and enter your username...
```

**Limitations**:
- Basic formatting only
- No advanced styling
- Images stored as relative paths
- Requires Markdown viewer for rendering

**HTML**

**Format**: HyperText Markup Language (.html)
**Library**: Custom HTML generator with CSS
**Features**:
- Web-ready format
- Professional CSS styling
- Responsive design
- Embeddable images (base64 or paths)
- Interactive elements (if needed)

**CSS Features**:
- Professional typography
- Color scheme (configurable)
- Print stylesheet
- Responsive layout
- Cross-browser compatibility

**Limitations**:
- Requires web browser to view
- External dependencies (CSS, images)
- Security considerations (if embedded scripts)

**JSON/CSV (Audit Trail)**

**Format**: JSON (.json) and CSV (.csv)
**Purpose**: Machine-readable audit information
**Features**:
- Complete audit trail
- SHA-256 hash verification
- Timestamp information
- Metadata tracking
- Compliance support

**JSON Structure**:
```json
{
    "session_id": "20231215_143022",
    "session_start": "2023-12-15T14:30:22",
    "session_end": "2023-12-15T14:45:10",
    "username": "john.doe",
    "systemname": "DESKTOP-ABC123",
    "steps": [
        {
            "step_number": 1,
            "timestamp": "2023-12-15T14:30:25",
            "window_title": "Login Dialog",
            "screenshot_path": "data/screenshots/20231215_143022/step_0001.png",
            "screenshot_hash": "a1b2c3d4e5f6...",
            "metadata": {...}
        }
    ]
}
```

**CSV Structure**:
```csv
step_number,timestamp,window_title,screenshot_path,screenshot_hash
1,2023-12-15T14:30:25,Login Dialog,data/screenshots/...,a1b2c3d4...
2,2023-12-15T14:30:30,Main Window,data/screenshots/...,b2c3d4e5...
```

**Use Cases**:
- Compliance auditing
- Data analysis
- Process tracking
- Quality assurance
- Legal documentation

### Session Management - Detailed Process

#### Session Lifecycle - Complete Workflow

**1. Session Initialization**

When a new session is started:

**Session ID Generation**:
- Format: `YYYYMMDD_HHMMSS` (e.g., `20231215_143022`)
- Unique identifier for the session
- Used for file naming and directory structure

**Directory Creation**:
- Creates session-specific directories:
  - `data/sessions/{session_id}/` - Session data
  - `data/screenshots/{session_id}/` - Screenshots
- Creates directories if they don't exist
- Sets up file structure automatically

**Session State Initialization**:
- Initializes empty step list
- Sets start timestamp
- Loads prompt profile
- Configures monitoring components
- Prepares audit logger

**Example Session Data Structure**:
```python
{
    'session_id': '20231215_143022',
    'start_time': '2023-12-15T14:30:22.123456',
    'end_time': None,
    'prompt_profile': 'sop',
    'steps': [],
    'status': 'active',
    'metadata': {
        'username': 'john.doe',
        'systemname': 'DESKTOP-ABC123'
    }
}
```

**2. Active Recording Phase**

**Monitoring Loop**:
- Window monitor continuously checks for changes
- Action detector analyzes window state
- Screenshot capture triggered on changes
- Steps are added to session data
- Preview panel updates in real-time

**Step Capture Process**:
1. Window change detected
2. Window information extracted
3. Screenshot captured
4. OCR text extracted (if available)
5. Privacy mask applied (if enabled)
6. Step data structure created
7. Step added to session
8. Audit log entry created
9. UI updated

**3. Pause/Resume Functionality**

**Pausing a Session**:
- Stops monitoring loop temporarily
- Preserves all captured steps
- Maintains session state
- UI shows "Paused" status
- Can resume at any time

**Resuming a Session**:
- Restarts monitoring loop
- Continues from last captured step
- Maintains step numbering
- Preserves session history
- UI shows "Recording" status

**4. Undo/Redo Mechanism**

**Undo Functionality**:
- Removes last captured step
- Maintains step numbering
- Updates preview panel
- Preserves history for redo
- Can undo multiple steps sequentially

**Redo Functionality**:
- Restores previously undone step
- Maintains step numbering
- Updates preview panel
- Removes from redo history
- Can redo multiple steps sequentially

**History Management**:
- Maintains undo/redo stack
- Limited to recent operations (configurable)
- Preserves step data for restoration
- Updates UI buttons state

**5. Session Completion**

**Ending a Session**:
1. Stop monitoring loop
2. Set end timestamp
3. Calculate session statistics
4. Save session data to disk
5. Generate AI descriptions (if not done)
6. Generate documents in selected formats
7. Create audit trail files
8. Update UI with completion status

**Session Data Persistence**:
- Saves session data as JSON file
- Location: `data/sessions/{session_id}/session_data.json`
- Includes all steps, metadata, timestamps
- Can be loaded for recovery or review

**6. Session Recovery**

**Automatic Recovery**:
- Application checks for incomplete sessions on startup
- Identifies sessions without end timestamp
- Offers recovery option in UI
- Validates session data integrity
- Restores session state

**Recovery Process**:
1. Load session data from JSON file
2. Verify screenshot files exist
3. Restore step list
4. Reinitialize monitoring components
5. Offer to resume or generate documents

**Manual Recovery**:
- Access session data files directly
- Load session JSON file
- Review captured steps
- Generate documents if needed
- Export data if necessary

#### Session Statistics - Detailed Metrics

The system tracks comprehensive statistics:

**Basic Metrics**:
- **Duration**: Total session time (HH:MM:SS format)
- **Step Count**: Number of captured steps
- **Screenshot Count**: Number of screenshots captured
- **Start Time**: Session start timestamp
- **End Time**: Session end timestamp

**Advanced Metrics**:
- **Windows Used**: Number of unique windows captured
- **Processes Used**: Number of unique processes captured
- **Average Steps per Minute**: Calculated from duration and step count
- **Average Time per Step**: Calculated from duration and step count
- **Total Screenshot Size**: Sum of all screenshot file sizes

**Example Statistics Output**:
```python
{
    'duration': 900,  # seconds
    'duration_formatted': '00:15:00',
    'step_count': 12,
    'screenshot_count': 12,
    'windows_used': 3,
    'processes_used': 2,
    'average_steps_per_minute': 0.8,
    'average_time_per_step': 75.0,  # seconds
    'total_screenshot_size_bytes': 2456789,
    'start_time': '2023-12-15T14:30:22',
    'end_time': '2023-12-15T14:45:22'
}
```

#### Session Data Structure

**Complete Session Data Format**:
```json
{
    "session_id": "20231215_143022",
    "prompt_profile": "sop",
    "start_time": "2023-12-15T14:30:22.123456",
    "end_time": "2023-12-15T14:45:22.654321",
    "status": "completed",
    "metadata": {
        "username": "john.doe",
        "systemname": "DESKTOP-ABC123",
        "department": "IT",
        "project": "Documentation Project"
    },
    "steps": [
        {
            "step_number": 1,
            "timestamp": "2023-12-15T14:30:25.123456",
            "window_title": "Login Dialog",
            "window_class": "LoginDialog",
            "process_name": "app.exe",
            "executable_path": "C:\\Program Files\\App\\app.exe",
            "position": {
                "left": 100,
                "top": 100,
                "right": 800,
                "bottom": 600,
                "width": 700,
                "height": 500
            },
            "screenshot_path": "data/screenshots/20231215_143022/step_0001.png",
            "description": "Click in the username field and enter your username...",
            "metadata": {}
        }
    ],
    "statistics": {
        "duration": 900,
        "step_count": 12,
        "screenshot_count": 12,
        "windows_used": 3,
        "processes_used": 2
    }
}
```

### Complete Workflow Examples

#### Example 1: Creating a Simple Login Procedure

**Scenario**: Document a login process for a web application

**Step-by-Step Process**:

**1. Preparation** (5 minutes):
- Open the application
- Ensure login page is visible
- Close unnecessary applications
- Configure prompt profile: "SOP"
- Verify API key is set

**2. Start Session** (30 seconds):
- Click "Start Session" button
- Verify status shows "Recording"
- Confirm statistics panel shows "Steps: 0"

**3. Perform Actions** (2 minutes):
- **Action 1**: Click in username field
  - System captures: Window title "Login Page"
  - Screenshot captured automatically
  - Step 1 created
  
- **Action 2**: Type username
  - System captures: Window title unchanged
  - Screenshot captured (content change detected)
  - Step 2 created
  
- **Action 3**: Click in password field
  - System captures: Window title unchanged
  - Screenshot captured
  - Step 3 created
  
- **Action 4**: Type password
  - System captures: Window title unchanged
  - Screenshot captured
  - Step 4 created
  
- **Action 5**: Click login button
  - System captures: Window title changes to "Dashboard"
  - Screenshot captured
  - Step 5 created

**4. Review Steps** (1 minute):
- Check preview panel: 5 steps captured
- Verify screenshots are clear
- Use Undo if needed (e.g., remove accidental step)

**5. End Session** (2 minutes):
- Click "End Session" button
- System generates AI descriptions:
  - Step 1: "Click in the username field..."
  - Step 2: "Enter your username..."
  - Step 3: "Click in the password field..."
  - Step 4: "Enter your password..."
  - Step 5: "Click the Login button..."
- Documents generated (DOCX, PDF)
- Audit trail created

**6. Review Output** (5 minutes):
- Open DOCX file
- Review AI-generated descriptions
- Edit if necessary
- Save final document

**Total Time**: ~15 minutes
**Result**: Professional login procedure documentation

#### Example 2: Complex Multi-Step Workflow

**Scenario**: Document a complete data entry process with multiple windows

**Preparation**:
- Prepare test data
- Open all required applications
- Configure privacy masks for sensitive fields
- Select "Training" prompt profile

**Workflow Steps**:
1. Login (3 steps)
2. Navigate to data entry form (2 steps)
3. Fill form fields (10 steps)
4. Validate data (2 steps)
5. Submit form (1 step)
6. Review confirmation (1 step)

**Management During Recording**:
- Use Pause when reviewing data
- Use Undo if mistakes made
- Monitor preview panel regularly
- Check statistics periodically

**Result**: Comprehensive training manual with 19 steps

#### Example 3: Batch Processing Multiple Sessions

**Scenario**: Document multiple related procedures

**Process**:
1. Document Session 1: Login procedure
2. Document Session 2: User profile setup
3. Document Session 3: Password reset
4. Generate all documents at once
5. Combine into single manual

**Time Savings**: 
- Individual: 3 × 15 minutes = 45 minutes
- Batch: ~30 minutes (parallel processing)

### Undo/Redo Functionality - Detailed Usage

**Use Cases for Undo**:
- **Accidental capture**: Removed unwanted step
- **Wrong sequence**: Correct step order
- **Duplicate steps**: Remove redundant captures
- **Test steps**: Remove testing actions

**Use Cases for Redo**:
- **Accidental undo**: Restore removed step
- **Change of mind**: Restore previous state
- **Correction**: Fix undo mistakes

**Limitations**:
- Limited undo/redo history (configurable, default: 50 steps)
- Cannot undo after session end
- Cannot undo after document generation
- History lost on application restart

### Step Reordering

Change the order of captured steps:

1. In the preview panel, select a step
2. Drag and drop to new position
3. Steps are automatically renumbered
4. Changes are saved immediately

**Use Cases**:
- Correct step sequence
- Reorganize workflow steps
- Group related steps together

**Best Practices**:
- Review steps before ending session
- Use Undo immediately after mistakes
- Don't rely on Undo for major corrections
- Consider restarting session for major issues

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
OPENAI_MODEL=gpt-5
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
- Use a more capable model (e.g., gpt-5 or gpt-4o instead of gpt-3.5-turbo)
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

1. Open **Tools → Batch Processing...**
2. Select multiple sessions from the list
3. Choose export formats for batch processing
4. Start batch processing
5. Track progress per session in real-time
6. All documents are generated automatically

**Use Cases**:
- Process multiple related documentation sessions
- Generate documentation for entire workflows
- Bulk export of existing sessions

### Step Consolidation

Merge similar or redundant steps:

1. Open **Tools → Step Consolidation...**
2. Select steps to consolidate
3. Configure consolidation settings (similarity threshold)
4. Review consolidated steps
5. Apply changes to session

**Features**:
- AI-powered step similarity detection
- Automatic merging of duplicate steps
- Manual review and approval
- Preserves step order and context

### Session Comparison

Compare two sessions to identify differences:

1. Open **Tools → Session Comparison...**
2. Select two sessions to compare
3. View side-by-side comparison
4. Identify added, removed, or modified steps
5. Export comparison report

**Use Cases**:
- Track changes between documentation versions
- Identify workflow variations
- Compare test scenarios

### Test Checklist Generator

Generate test checklists from documented steps:

1. Open **Tools → Test Checklist Generator...**
2. Select session with steps
3. Configure checklist options
4. Generate checklist with checkboxes
5. Export as DOCX, PDF, or Markdown

**Features**:
- Automatic test case generation
- Customizable checklist format
- Multiple export formats
- Step-by-step validation items

### Quality Check

Assess documentation quality and completeness:

1. Open **Tools → Quality Check...**
2. Review quality metrics:
   - Screenshot quality
   - Step completeness
   - Description clarity
   - Consistency checks
3. View detailed quality report
4. Address quality issues

**Quality Metrics**:
- Screenshot resolution and clarity
- Step description completeness
- Consistency of terminology
- Coverage of workflow steps
- Metadata completeness

### Multi-Language Export

Export documentation in multiple languages:

1. Open **Export → Multi-Language Export...**
2. Select source session
3. Choose target languages
4. Configure translation settings
5. Generate translated documents

**Supported Features**:
- Automatic translation using AI
- Language-specific formatting
- Cultural adaptation
- Terminology consistency

### Cloud Upload

Upload generated documents to cloud storage:

1. Open **Export → Cloud Upload...**
2. Select files to upload (DOCX, PDF, Markdown, HTML)
3. Choose cloud provider (configured in settings)
4. Configure upload options
5. Upload files

**Supported Platforms**:
- Google Drive
- Microsoft OneDrive
- Dropbox
- Custom cloud storage (configurable)

### Quick Reference Export

Generate concise quick reference guides:

1. Open **Export → Quick Reference...**
2. Select session with steps
3. Configure reference format:
   - Compact layout
   - Key steps only
   - Visual highlights
4. Generate quick reference document

**Use Cases**:
- One-page workflow summaries
- Quick-start guides
- Reference cards
- Cheat sheets

### Video Export

Create video walkthroughs from screenshots:

1. Open **Export → Video Export...**
2. Select session with steps
3. Configure video settings:
   - Frame duration per step
   - Transitions
   - Resolution
   - Audio narration (optional)
4. Generate video file

**Features**:
- Automatic video creation from screenshots
- Customizable timing
- Smooth transitions
- Multiple video formats (MP4, AVI)

### Platform Export

Export documentation for specific platforms:

1. Open **Export → Platform Export...**
2. Select target platform:
   - Confluence
   - Jira
   - SharePoint
   - WordPress
   - Custom platform
3. Configure platform-specific settings
4. Generate formatted export

**Platform-Specific Features**:
- Platform-compatible formatting
- Metadata mapping
- Image optimization
- Link generation

### Automated App Exploration

Automatically explore and document an application:

1. Open **Automation → App Exploration...**
2. Select target application
3. Configure exploration settings:
   - Exploration depth
   - UI element discovery
   - Navigation strategy
4. Start automated exploration
5. Review generated documentation

**Features**:
- Automatic UI element discovery
- Intelligent navigation
- Step-by-step documentation
- Screenshot capture at each step

### Statistics Dashboard

View comprehensive session statistics:

1. Open **Tools → Statistics...**
2. Review metrics:
   - Session duration
   - Step count
   - Screenshot statistics
   - Quality metrics
   - Window usage patterns
   - Process statistics
3. View graphs and charts
4. Export statistics report

**Statistics Include**:
- Basic metrics (duration, steps, screenshots)
- Advanced metrics (windows used, processes used)
- Quality metrics (screenshot quality, description completeness)
- Performance metrics (capture times, processing times)

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

