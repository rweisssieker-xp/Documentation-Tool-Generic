# Documentation-Tool-Generic - Project Documentation Index

## Project Overview

- **Type:** Desktop Application (Monolith)
- **Primary Language:** Python 3.10+
- **Architecture:** Layered Architecture with GUI, Business Logic, and Data Layers
- **Repository Structure:** Monolith

## Quick Reference

- **Tech Stack:** Python 3.10+, Tkinter, OpenAI API, Tesseract OCR
- **Entry Point:** `main.py`
- **Architecture Pattern:** Layered Desktop Application
- **Main Framework:** Tkinter for GUI

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md) - Executive summary and project information
- [Architecture](./architecture.md) - Complete architecture documentation
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and critical folders
- [Development Guide](./development-guide.md) - Setup, build, and development instructions
- [PRD](./prd.md) - Product Requirements Document

### Documentation Standards and Manuals

- [Documentation Standards](./DOCUMENTATION_STANDARDS.md) - Comprehensive documentation standards and guidelines
- [Administrator Manual](./ADMINISTRATOR_MANUAL.md) - System administration, deployment, and maintenance guide
- [Developer Manual](./DEVELOPER_MANUAL.md) - Architecture, API reference, and development guidelines
- [Technical Writer Guide](./TECHNICAL_WRITER_GUIDE.md) - Guide for creating documentation with this tool

### Innovation Features v3.0 Documentation

- [API Gateway User Guide](./API_GATEWAY_USER_GUIDE.md) - Complete REST/GraphQL API documentation
- [Plugin System Developer Guide](./PLUGIN_SYSTEM_DEVELOPER_GUIDE.md) - Plugin development and marketplace guide
- [Edge AI User Guide](./EDGE_AI_USER_GUIDE.md) - On-device AI processing guide
- [Blockchain Audit Trail Guide](./BLOCKCHAIN_AUDIT_TRAIL_GUIDE.md) - Immutable document verification
- [Predictive Maintenance Guide](./PREDICTIVE_MAINTENANCE_GUIDE.md) - AI-powered documentation maintenance
- [Multi-Modal Capture Guide](./MULTIMODAL_CAPTURE_GUIDE.md) - Video, audio, and sensor data capture
- [AR Documentation Guide](./AR_DOCUMENTATION_GUIDE.md) - Mixed Reality overlay documentation
- [v3.0 Features Quick Reference](./V3_FEATURES_QUICK_REFERENCE.md) - Quick reference for all v3.0 features

### Supporting Documentation

- [Workflow Status](./bmm-workflow-status.yaml) - BMM workflow tracking

## Existing Documentation

- [README.md](../README.md) - Main project documentation
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [USER_MANUAL.md](../USER_MANUAL.md) - User manual
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Project summary
- [CHANGELOG.md](../CHANGELOG.md) - Change log

## Getting Started

### For Developers

1. **Setup Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure:**
   - Copy `env.example` to `.env`
   - Add OpenAI API key

3. **Run:**
   ```bash
   python main.py
   ```

4. **Test:**
   ```bash
   pytest
   ```

### For AI-Assisted Development

When creating a brownfield PRD or planning new features:

1. **Reference Architecture:** Use `docs/architecture.md` for system design context
2. **Reference Source Tree:** Use `docs/source-tree-analysis.md` for code structure
3. **Reference Development Guide:** Use `docs/development-guide.md` for setup and conventions

## Project Structure Summary

```
Documentation-Tool-Generic/
├── src/                    # Source code
│   ├── gui/               # GUI Layer (Tkinter)
│   ├── monitor/           # Monitoring Layer
│   ├── capture/           # Capture Layer
│   ├── ai/                # AI Integration Layer
│   ├── document/          # Document Generation Layer
│   ├── automation/        # Automation Layer
│   ├── audit/             # Audit Layer
│   ├── config/            # Configuration Layer
│   └── utils/             # Utilities Layer
├── config/                # Configuration files
├── data/                  # Data directory
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Key Modules

### GUI Layer (`src/gui/`)
- **MainWindow:** Main application window
- **PreviewPanel:** Live preview
- **Various Dialogs:** Export, settings, recovery dialogs

### Monitoring Layer (`src/monitor/`)
- **SessionManager:** Session lifecycle management
- **WindowMonitor:** Window change detection
- **ActionDetector:** User action detection

### Capture Layer (`src/capture/`)
- **ScreenshotCapture:** Screenshot capture
- **OCREngine:** OCR text extraction
- **PrivacyMask:** Privacy data masking

### AI Integration Layer (`src/ai/`)
- **OpenAIClient:** OpenAI API client
- **TextGenerator:** AI text generation
- **StepConsolidator:** Step consolidation

### Document Generation Layer (`src/document/`)
- **DOCXBuilder:** DOCX document builder
- **PDFExporter:** PDF export
- **TemplateEngine:** Template processing

## Technology Stack

- **Language:** Python 3.10+
- **GUI:** Tkinter
- **Screenshot:** mss, pyautogui, pywinctl
- **OCR:** Tesseract (pytesseract)
- **AI:** OpenAI API (GPT-5)
- **Documents:** python-docx, docx2pdf
- **Windows:** pywin32, pywinauto
- **Config:** PyYAML, python-dotenv
- **Testing:** pytest, pytest-cov

## Next Steps

For brownfield PRD creation:
1. Review `docs/architecture.md` for system design
2. Review `docs/source-tree-analysis.md` for code structure
3. Use this index as context for AI-assisted planning

---

**Last Updated:** 2025-11-20  
**Documentation Version:** 1.0.0  
**Generated by:** BMad Method - document-project workflow

