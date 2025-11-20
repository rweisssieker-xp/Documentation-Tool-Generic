# Epic Technical Specification: Core Documentation Generation

Date: 2025-11-20
Author: BMad
Epic ID: 1
Status: Draft

---

## Overview

Epic 1: Core Documentation Generation enables users to automatically generate complete documentation from their software usage. This epic provides the foundational capabilities for capturing screenshots, extracting text via OCR, generating AI-powered descriptions, and exporting documentation in multiple formats (DOCX, PDF, Markdown, HTML, LaTeX).

This epic addresses Functional Requirements FR1 (Screenshot Capture), FR2 (OCR Text Extraction), FR3 (AI Text Generation), FR4 (Multi-Format Document Export), and FR10 (Prompt Profile Selection) from the PRD. It establishes the core workflow that transforms user interactions into professional documentation without manual writing.

The epic is organized into four sequential stories that build upon each other: automatic screenshot capture, OCR text extraction, AI-powered text generation, and multi-format document export. Each story implements a critical component of the documentation generation pipeline.

---

## Objectives and Scope

### In-Scope

- **Automatic Screenshot Capture (Story 1.1):**
  - Window change detection and monitoring
  - Screenshot capture using mss/pywinctl
  - Screenshot storage with unique identifiers
  - Screenshot metadata recording (timestamp, window title)

- **OCR Text Extraction (Story 1.2):**
  - Tesseract OCR integration for text extraction
  - Image preprocessing for OCR accuracy
  - OCR text storage with screenshot metadata
  - Graceful error handling for OCR failures

- **AI-Powered Text Generation (Story 1.3):**
  - OpenAI API integration for text generation
  - Prompt template management (SOP, training, technical profiles)
  - Contextually appropriate description generation
  - API error handling with retry logic

- **Multi-Format Document Export (Story 1.4):**
  - DOCX export (primary format)
  - PDF export (via docx2pdf)
  - Markdown export
  - HTML export with styling
  - LaTeX export
  - Consistent formatting across all formats

### Out-of-Scope

- Session management (covered in Epic 2)
- Privacy masking (covered in Epic 3)
- Batch processing (covered in Epic 5)
- Advanced export features like multi-language, cloud upload (covered in Epic 4)
- Live preview (covered in Epic 9)
- Configuration management (covered in Epic 8)

---

## System Architecture Alignment

This epic aligns with the **Layered Architecture Pattern** defined in the Architecture document:

- **Capture Layer (`src/capture/`):** Implements screenshot capture (Story 1.1) and OCR processing (Story 1.2)
- **AI Integration Layer (`src/ai/`):** Implements AI text generation (Story 1.3)
- **Document Generation Layer (`src/document/`):** Implements multi-format export (Story 1.4)
- **Monitor Layer (`src/monitor/`):** Provides window monitoring for screenshot triggers (Story 1.1)

**Architectural Decisions Applied:**
- Screenshot Capture: Uses mss + pywinctl (ADR-003) for cross-platform support
- OCR Engine: Uses Tesseract (pytesseract) (ADR-005) for text extraction
- AI Integration: Uses OpenAI API (GPT-5) (ADR-004) for text generation
- Document Generation: Uses python-docx (ADR-006) for DOCX, docx2pdf for PDF
- Error Handling: Exception-based with retry logic (ADR-008)
- Logging: Structured logging via logger.py (ADR-009)

**Constraints:**
- Must follow Layered Architecture boundaries (no direct GUI access from capture layer)
- Must use existing technology stack decisions
- Must maintain consistency with existing codebase patterns

---

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| **ScreenshotCapture** (`src/capture/screenshot.py`) | Captures screenshots on window changes | Window change events, session_id | Screenshot files, metadata | Capture Layer |
| **WindowMonitor** (`src/monitor/window_monitor.py`) | Monitors active window changes | System events | Window change notifications | Monitor Layer |
| **OCREngine** (`src/capture/ocr_engine.py`) | Extracts text from screenshots | Screenshot images | OCR text, confidence scores | Capture Layer |
| **TextGenerator** (`src/ai/text_generator.py`) | Generates AI descriptions | Screenshots, OCR text, prompt profile | AI-generated descriptions | AI Layer |
| **OpenAIClient** (`src/ai/openai_client.py`) | Handles OpenAI API communication | API requests | API responses | AI Layer |
| **PromptTemplates** (`src/ai/prompt_templates.py`) | Manages prompt templates | Profile name | Prompt template content | AI Layer |
| **DOCXBuilder** (`src/document/docx_builder.py`) | Builds DOCX documents | Session data, screenshots | DOCX file | Document Layer |
| **PDFExporter** (`src/document/pdf_exporter.py`) | Exports PDF documents | DOCX file | PDF file | Document Layer |
| **MarkdownExporter** (`src/document/markdown_exporter.py`) | Exports Markdown documents | Session data, screenshots | Markdown file | Document Layer |
| **HTMLExporter** (`src/document/html_exporter.py`) | Exports HTML documents | Session data, screenshots | HTML file | Document Layer |
| **LaTeXExporter** (`src/document/latex_exporter.py`) | Exports LaTeX documents | Session data, screenshots | LaTeX file | Document Layer |

### Data Models and Contracts

**Session Step Model:**
```python
{
    "step_number": int,
    "timestamp": str,  # ISO 8601 format
    "screenshot_path": str,
    "screenshot_id": str,  # UUID
    "ocr_text": str,
    "ai_description": str,
    "window_title": str,
    "actions": [str]  # List of user actions
}
```

**Screenshot Metadata Model:**
```python
{
    "screenshot_id": str,  # UUID
    "session_id": str,  # UUID
    "step_number": int,
    "file_path": str,
    "timestamp": str,  # ISO 8601 format
    "window_title": str,
    "dimensions": {
        "width": int,
        "height": int
    }
}
```

**OCR Result Model:**
```python
{
    "screenshot_id": str,
    "ocr_text": str,
    "confidence": float,  # 0.0 to 1.0
    "preprocessing_applied": [str],
    "processing_time_ms": int
}
```

**AI Generation Request Model:**
```python
{
    "screenshot_path": str,
    "ocr_text": str,
    "prompt_profile": str,  # "sop", "training", "technical"
    "context": {
        "previous_steps": [dict],
        "window_title": str
    }
}
```

**Document Export Model:**
```python
{
    "session_id": str,
    "format": str,  # "docx", "pdf", "markdown", "html", "latex"
    "output_path": str,
    "screenshots_included": [str],
    "export_timestamp": str
}
```

### APIs and Interfaces

**ScreenshotCapture API:**
```python
class ScreenshotCapture:
    def capture_screenshot(window_handle: Optional[int] = None) -> ScreenshotMetadata
    def save_screenshot(image: Image, session_id: str, step_number: int) -> str
    def get_screenshot_path(session_id: str, screenshot_id: str) -> str
```

**OCREngine API:**
```python
class OCREngine:
    def extract_text(image_path: str) -> OCRResult
    def preprocess_image(image: Image) -> Image
    def postprocess_text(text: str) -> str
```

**TextGenerator API:**
```python
class TextGenerator:
    def generate_description(request: AIGenerationRequest) -> str
    def apply_prompt_template(profile_name: str, context: dict) -> str
```

**Document Exporters API (Common Interface):**
```python
class DocumentExporter(ABC):
    @abstractmethod
    def export(session_data: dict, output_path: str) -> str
    @abstractmethod
    def validate_format() -> bool
```

**Error Codes:**
- `SCREENSHOT_CAPTURE_FAILED`: Screenshot capture error
- `OCR_PROCESSING_FAILED`: OCR processing error
- `AI_GENERATION_FAILED`: AI text generation error
- `EXPORT_FAILED`: Document export error
- `INVALID_FORMAT`: Unsupported export format

### Workflows and Sequencing

**Core Documentation Generation Workflow:**

1. **Screenshot Capture (Story 1.1):**
   - WindowMonitor detects window change
   - WindowMonitor notifies SessionManager
   - SessionManager triggers ScreenshotCapture
   - ScreenshotCapture captures screenshot using mss/pywinctl
   - Screenshot saved to `data/screenshots/{session_id}/{screenshot_id}.png`
   - Screenshot metadata stored in session step

2. **OCR Processing (Story 1.2):**
   - SessionManager triggers OCR processing after screenshot capture
   - OCREngine preprocesses screenshot image
   - OCREngine calls Tesseract OCR
   - OCR text extracted and stored with screenshot metadata
   - OCR errors handled gracefully

3. **AI Text Generation (Story 1.3):**
   - SessionManager triggers AI generation after OCR completion
   - TextGenerator loads prompt template based on selected profile
   - TextGenerator calls OpenAI API with screenshot and OCR context
   - AI-generated description stored in session step
   - API errors handled with retry logic

4. **Document Export (Story 1.4):**
   - User selects export format
   - Appropriate exporter (DOCXBuilder, PDFExporter, etc.) selected
   - Exporter processes session data and screenshots
   - Document generated with consistent formatting
   - Document saved to `data/output/{session_id}_{format}.{ext}`

**Sequence Diagram (Text Format):**
```
User → SessionManager: Start Session
SessionManager → WindowMonitor: Begin Monitoring
WindowMonitor → SessionManager: Window Change Detected
SessionManager → ScreenshotCapture: Capture Screenshot
ScreenshotCapture → FileSystem: Save Screenshot
ScreenshotCapture → SessionManager: Screenshot Metadata
SessionManager → OCREngine: Process Screenshot
OCREngine → Tesseract: Extract Text
OCREngine → SessionManager: OCR Text
SessionManager → TextGenerator: Generate Description
TextGenerator → OpenAI API: Request Text Generation
OpenAI API → TextGenerator: Generated Text
TextGenerator → SessionManager: AI Description
SessionManager → FileSystem: Save Session Step
User → SessionManager: Export Document
SessionManager → DocumentExporter: Export Session
DocumentExporter → FileSystem: Save Document
```

---

## Non-Functional Requirements

### Performance

**Screenshot Capture:**
- Capture screenshots within 100ms of window change detection (PRD Performance Requirement)
- Process screenshots without blocking UI thread
- Handle multiple rapid window changes efficiently

**OCR Processing:**
- Complete OCR processing within 2 seconds per screenshot (PRD Performance Requirement)
- Process OCR asynchronously to avoid UI blocking
- Cache OCR results when possible to improve performance

**AI Text Generation:**
- Complete AI text generation within 5 seconds per step (PRD Performance Requirement)
- Implement retry logic with exponential backoff for API failures
- Respect OpenAI API rate limits (requests per minute)

**Document Generation:**
- Generate DOCX documents within 10 seconds for typical sessions (50 steps) (PRD Performance Requirement)
- Handle large sessions (200+ steps) efficiently
- Optimize memory usage during document generation

**Performance Targets:**
- Screenshot capture: <100ms
- OCR processing: <2s per screenshot
- AI generation: <5s per step
- Document export: <10s for 50 steps, <30s for 200+ steps

### Security

**API Key Security:**
- OpenAI API keys stored in environment variables (`.env` file)
- API keys never logged or exposed in error messages
- Secure API communication via HTTPS only

**Data Protection:**
- Screenshots stored securely in `data/screenshots/` directory
- Session data stored securely in `data/sessions/` directory
- No sensitive data transmitted except to OpenAI API

**Error Handling:**
- API errors handled gracefully without exposing sensitive information
- User-friendly error messages that don't reveal system internals

### Reliability/Availability

**Error Recovery:**
- Screenshot capture failures don't crash the application
- OCR failures handled gracefully with user notification
- AI API failures handled with retry logic (max 3 retries)
- Export failures handled gracefully with error reporting

**Data Integrity:**
- Screenshot files validated before storage
- Session data validated before saving
- Export files validated before completion

**Availability:**
- Application remains responsive during all operations
- Long-running operations (OCR, AI generation) don't block UI
- Progress indicators provided for user feedback

### Observability

**Logging:**
- All screenshot captures logged with metadata (timestamp, window title)
- OCR processing logged with results and timing
- AI generation requests logged (without sensitive data)
- Export operations logged with format and timing
- Errors logged with full context for debugging

**Metrics:**
- Screenshot capture count and timing
- OCR processing count, success rate, and timing
- AI generation count, success rate, and timing
- Export operation count and timing

**Log Levels:**
- DEBUG: Detailed operation information
- INFO: Normal operation events
- WARNING: Recoverable errors
- ERROR: Operation failures
- CRITICAL: System failures

---

## Dependencies and Integrations

### External Dependencies

**Screenshot Libraries:**
- `mss>=9.0.1` - Cross-platform screenshot capture
- `pywinctl>=0.0.44` - Window management and capture
- `pyautogui>=0.9.54` - GUI automation support
- `Pillow>=10.0.0` - Image processing

**OCR Library:**
- `pytesseract>=0.3.10` - Tesseract OCR Python wrapper
- Tesseract OCR binary (system installation required)

**AI Integration:**
- `openai>=1.12.0` - OpenAI API client library

**Document Generation:**
- `python-docx>=1.1.0` - DOCX document generation
- `docx2pdf>=0.1.8` - PDF conversion from DOCX

**Configuration:**
- `PyYAML>=6.0.1` - YAML configuration parsing
- `python-dotenv>=1.0.0` - Environment variable management

### Internal Dependencies

**Monitor Layer:**
- `src/monitor/window_monitor.py` - Window change detection
- `src/monitor/session_manager.py` - Session lifecycle management

**Configuration Layer:**
- `src/config/config_manager.py` - Configuration management
- `config/prompt_profiles/` - Prompt template files

**Utilities:**
- `src/utils/logger.py` - Logging system

### Integration Points

**OpenAI API:**
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Authentication: Bearer token (API key from environment)
- Rate Limits: Per OpenAI API documentation
- Error Handling: Retry with exponential backoff

**Tesseract OCR:**
- Local binary integration via pytesseract
- Command-line interface
- Language data files required

**File System:**
- Screenshot storage: `data/screenshots/{session_id}/`
- Session storage: `data/sessions/{session_id}.json`
- Output storage: `data/output/`

---

## Acceptance Criteria (Authoritative)

1. **Screenshot Capture (Story 1.1):**
   - Given a documentation session is active, when the active window changes, then a screenshot is automatically captured
   - Screenshot is stored with unique identifier (UUID format)
   - Screenshot is associated with current session step
   - Screenshot metadata (timestamp, window title) is recorded
   - Screenshot capture completes within 100ms of window change detection

2. **OCR Text Extraction (Story 1.2):**
   - Given a screenshot has been captured, when OCR processing is triggered, then text is extracted using Tesseract OCR
   - Extracted text is stored with screenshot metadata
   - OCR errors are handled gracefully with user-friendly messages
   - Image preprocessing is applied to improve OCR accuracy
   - OCR processing completes within 2 seconds per screenshot

3. **AI Text Generation (Story 1.3):**
   - Given a screenshot and OCR text are available, when AI text generation is triggered, then a descriptive text is generated using OpenAI API
   - Prompt template matches selected profile (SOP, training, technical)
   - Generated text is contextually appropriate
   - API errors are handled with retry logic (max 3 retries)
   - Rate limits are respected
   - AI generation completes within 5 seconds per step

4. **Multi-Format Document Export (Story 1.4):**
   - Given a documentation session is complete, when user selects export format (DOCX, PDF, Markdown, HTML, LaTeX), then documentation is exported in selected format
   - Formatting is consistent across all formats
   - Screenshots are properly embedded/referenced
   - Exported document is saved to `data/output/`
   - Export errors are handled gracefully
   - Document export completes within 10 seconds for 50 steps

---

## Traceability Mapping

| AC | Spec Section | Component/API | Test Idea |
|----|--------------|---------------|-----------|
| AC1.1 | Screenshot Capture | ScreenshotCapture.capture_screenshot() | Unit test: Verify screenshot captured on window change |
| AC1.1 | Screenshot Capture | WindowMonitor.detect_change() | Integration test: Window change triggers screenshot |
| AC1.2 | Screenshot Storage | ScreenshotCapture.save_screenshot() | Unit test: Verify screenshot saved with UUID |
| AC1.3 | Screenshot Metadata | ScreenshotCapture.get_metadata() | Unit test: Verify metadata includes timestamp and window title |
| AC2.1 | OCR Processing | OCREngine.extract_text() | Unit test: Verify OCR text extraction from image |
| AC2.2 | OCR Storage | OCREngine.store_result() | Integration test: Verify OCR text stored with metadata |
| AC2.3 | OCR Error Handling | OCREngine.handle_error() | Unit test: Verify graceful error handling |
| AC2.4 | OCR Preprocessing | OCREngine.preprocess_image() | Unit test: Verify image preprocessing improves accuracy |
| AC3.1 | AI Generation | TextGenerator.generate_description() | Unit test: Verify AI text generation |
| AC3.2 | Prompt Templates | PromptTemplates.load_template() | Unit test: Verify correct template loaded for profile |
| AC3.3 | AI Context | TextGenerator.apply_context() | Integration test: Verify contextually appropriate text |
| AC3.4 | API Retry Logic | OpenAIClient.retry_request() | Unit test: Verify retry logic on API failures |
| AC4.1 | Document Export | DocumentExporter.export() | Integration test: Verify export in all formats |
| AC4.2 | Format Consistency | DocumentExporter.apply_formatting() | Unit test: Verify consistent formatting |
| AC4.3 | Screenshot Embedding | DocumentExporter.embed_screenshots() | Integration test: Verify screenshots embedded correctly |
| AC4.4 | Export Storage | DocumentExporter.save_document() | Unit test: Verify document saved to output directory |

---

## Risks, Assumptions, Open Questions

### Risks

**Risk 1: OCR Accuracy**
- **Description:** Tesseract OCR may not accurately extract text from all screenshots
- **Mitigation:** Implement image preprocessing (contrast, scaling, noise reduction)
- **Impact:** Medium - May require manual text correction
- **Status:** Mitigated through preprocessing

**Risk 2: OpenAI API Costs**
- **Description:** API costs can accumulate with heavy usage
- **Mitigation:** Monitor API usage, optimize prompts, implement caching where possible
- **Impact:** Medium - Cost management required
- **Status:** Monitoring required

**Risk 3: Performance Under Load**
- **Description:** Large sessions (200+ steps) may impact performance
- **Mitigation:** Optimize memory usage, implement efficient processing, batch operations
- **Impact:** Low - Performance targets defined
- **Status:** Addressed in design

### Assumptions

**Assumption 1: Tesseract OCR Installation**
- Tesseract OCR binary is installed and accessible via system PATH
- Language data files are available for text extraction

**Assumption 2: OpenAI API Access**
- User has valid OpenAI API key
- Internet connection available for API calls
- API rate limits are acceptable for usage patterns

**Assumption 3: Screenshot Quality**
- Screenshots contain readable text
- Applications have standard Windows GUI
- Window titles are meaningful and descriptive

### Open Questions

**Question 1: OCR Language Support**
- Should we support multiple languages for OCR?
- **Answer:** Initially support English, expand based on user needs

**Question 2: AI Prompt Optimization**
- Should we implement prompt caching or optimization?
- **Answer:** Implement basic caching, optimize prompts based on feedback

**Question 3: Export Format Priority**
- Which export format should be prioritized for initial release?
- **Answer:** DOCX is primary format, others follow based on user feedback

---

## Test Strategy Summary

### Test Levels

**Unit Tests:**
- ScreenshotCapture class methods
- OCREngine class methods
- TextGenerator class methods
- DocumentExporter implementations
- Error handling and retry logic

**Integration Tests:**
- Screenshot capture → OCR processing flow
- OCR processing → AI generation flow
- AI generation → Document export flow
- Window monitoring → Screenshot capture integration

**End-to-End Tests:**
- Complete documentation generation workflow
- Multi-format export validation
- Error recovery scenarios

### Test Frameworks

- **Unit Testing:** pytest with pytest-mock
- **Integration Testing:** pytest with fixtures
- **Coverage:** pytest-cov for code coverage

### Test Coverage

- **Target Coverage:** 80% code coverage
- **Critical Paths:** 100% coverage (screenshot capture, OCR, AI generation, export)
- **Error Handling:** All error paths tested

### Edge Cases

- Rapid window changes (multiple screenshots in quick succession)
- OCR failures (unreadable screenshots)
- API failures (network errors, rate limits)
- Large sessions (200+ steps)
- Invalid export formats
- Missing dependencies (Tesseract, OpenAI API key)

---

