# Project Overview

## Project Information

- **Name:** Automatischer Handbuch-Generator (AHG) / Documentation-Tool-Generic
- **Type:** Desktop Application (Monolith)
- **Primary Language:** Python 3.10+
- **Architecture Pattern:** Layered Architecture with GUI, Business Logic, and Data Layers
- **Repository Structure:** Monolith

## Executive Summary

The Automatischer Handbuch-Generator (AHG) is a fully automated solution for creating illustrated technical manuals from real-world software usage scenarios. It monitors user interactions (window changes, mouse clicks, keyboard input), automatically captures screenshots, performs OCR, and uses AI (OpenAI GPT) to generate comprehensive documentation in multiple formats (DOCX, PDF, Markdown, HTML, LaTeX).

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Language** | Python | 3.10+ | Core application language |
| **GUI Framework** | Tkinter | Built-in | Cross-platform GUI toolkit |
| **Screenshot** | mss, pyautogui, pywinctl | Latest | Cross-platform window capture |
| **OCR** | Tesseract (pytesseract) | Latest | Text extraction from images |
| **AI Integration** | OpenAI API | GPT-5 | Text generation for documentation |
| **Document Generation** | python-docx, docx2pdf | Latest | DOCX/PDF export |
| **Windows Integration** | pywin32, pywinauto | Latest | Windows-specific monitoring |
| **Configuration** | PyYAML, python-dotenv | Latest | YAML config and env vars |
| **Testing** | pytest, pytest-cov | Latest | Unit and integration testing |

## Architecture Type

**Layered Desktop Application:**
- **Presentation Layer:** Tkinter GUI (`src/gui/`)
- **Business Logic Layer:** Core modules (`src/monitor/`, `src/capture/`, `src/ai/`, `src/document/`)
- **Data Layer:** File system storage (`data/`), configuration (`config/`)

## Key Features

1. **Automatic Monitoring:** Tracks user actions (window changes, mouse clicks, keyboard input)
2. **Screenshot Capture:** Automatic screenshots at relevant steps
3. **OCR Integration:** Text recognition from screenshots
4. **AI Text Generation:** Uses OpenAI GPT for precise, context-aware descriptions
5. **Multiple Export Formats:** DOCX, PDF, Markdown, HTML, LaTeX, JSON, CSV
6. **Session Management:** Pause/Resume, Undo/Redo, crash recovery
7. **Privacy Masking:** Automatic detection and masking of sensitive data
8. **Audit Trail:** SHA-256 hashing and complete audit logging

## Entry Points

- **Main Entry:** `main.py` → Starts GUI application
- **GUI Entry:** `src/gui/main_window.py` → MainWindow class

## Project Structure

```
Documentation-Tool-Generic/
├── src/                    # Source code
│   ├── gui/               # GUI components (Tkinter)
│   ├── monitor/           # Windows monitoring
│   ├── capture/           # Screenshot & OCR
│   ├── ai/                # OpenAI integration
│   ├── document/          # Document generation
│   ├── audit/             # Audit trail
│   ├── automation/        # Automated exploration
│   ├── config/            # Configuration management
│   └── utils/             # Utilities
├── config/                # Configuration files
├── data/                  # Data directory
│   ├── sessions/          # Session data
│   ├── screenshots/       # Screenshots
│   └── output/            # Generated documents
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Getting Started

1. **Prerequisites:**
   - Python 3.10+
   - Windows 10/11
   - Tesseract OCR

2. **Installation:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration:**
   - Copy `env.example` to `.env`
   - Add OpenAI API key

4. **Run:**
   ```bash
   python main.py
   ```

