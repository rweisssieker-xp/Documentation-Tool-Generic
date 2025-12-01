# Changelog

Alle bemerkenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [1.1.0] - 2025-11-30 - Innovation Features Release

### 🚀 Neue Features

#### Voice-First Documentation (`src/voice/`)
- OpenAI Whisper Integration für Sprach-zu-Text
- Sprachbefehle in Deutsch und Englisch
- Freihändige Dokumentation während der Arbeit
- Voice-Annotationen für Dokumentationsschritte

#### Multi-Modal Knowledge Base (`src/knowledge/`)
- Zentrale Wissensbasis mit Dokument-Management
- ChromaDB Vector Store für Embeddings
- Semantische & Hybrid-Suche
- RAG (Retrieval-Augmented Generation) mit GPT-4o

#### Predictive Documentation Assistant (`src/prediction/`)
- KI-gestützte Vorhersage nächster Dokumentationsschritte
- Lücken-Analyse für vollständige Dokumentation
- Auto-Completion für Beschreibungen
- Workflow-Pattern-Learning

#### Smart Context Capture (`src/context/`)
- Erweiterte Kontext-Erfassung
- Clipboard-Monitoring
- Browser-Tab-Tracking (Chrome, Firefox, Edge, Brave)
- Intent-Analyse mittels AI
- Context Cloud Visualisierung

#### Automated Test Case Generator (`src/testgen/`)
- Export dokumentierter Workflows als ausführbare Tests
- Selenium WebDriver (Python/Java)
- Playwright (Python/TypeScript)
- Gherkin/BDD Features (DE/EN)
- Smart Selector Engine

#### Interactive Tutorial Generator (`src/tutorial/`)
- Konvertierung von Dokumentation in interaktive Tutorials
- Quiz-Generator für Verständnisfragen
- SCORM 2004 4th Edition Export für LMS-Systeme
- Adaptive Learning Path Optimierung

#### Process Mining Engine (`src/processmining/`)
- Automatische Prozess-Discovery aus Sessions
- Pattern- und Varianten-Erkennung
- BPMN 2.0 XML Export
- Mermaid Flowchart Export
- Graphviz DOT Export

### 🖥️ GUI-Erweiterungen
- Voice-First Panel (`Ctrl+Alt+V`)
- Knowledge Base Dialog (`Ctrl+Alt+K`)
- Process Mining Dialog (`Ctrl+Alt+M`)
- Test Export Dialog (`Ctrl+Alt+T`)
- Tutorial Export Dialog (`Ctrl+Alt+U`)

### 🔧 CLI (Command-Line Interface)
- `innovation_cli.py` mit Unterbefehlen:
  - `kb search/add/stats` - Knowledge Base
  - `test generate` - Test-Generierung
  - `tutorial generate` - Tutorial-Erstellung
  - `pm analyze` - Process Mining
  - `rag query` - RAG Q&A

### 📦 Neue Dependencies
- sounddevice, soundfile, webrtcvad (Voice)
- chromadb, sentence-transformers, tiktoken (RAG)
- selenium, playwright, behave, gherkin-official (Tests)
- pm4py, networkx, graphviz (Process Mining)
- lxml, jinja2, scikit-learn, pyperclip

### 📄 Dokumentation
- `docs/innovation-backlog-v1.1.md` - Feature-Dokumentation
- `config/innovation_config.yaml` - Konfiguration
- `examples/demo_all_features.py` - Vollständige Demo
- Aktualisiertes README mit neuen Features

### 🧪 Tests
- 102 Tests insgesamt (99 passed, 3 skipped)
- Vollständige Test-Coverage für alle neuen Module
- Integration in bestehende Test-Suite

---

## [1.0.0] - 2025-11-05

### Hinzugefügt
- Vollständige Implementierung aller geplanten Features
- GUI mit Menüleiste (Datei, Session, Tools, Hilfe)
- Session-Management mit Start/Stop/Pause/Resume
- Undo/Redo-Funktionalität für Schritte
- Live-Vorschau mit Screenshot-Anzeige
- Session-Statistiken (Dauer, Schritte, Screenshots)
- Session-Wiederherstellung nach Absturz (GUI-Dialog)
- Automatische Bereinigung alter Dateien (mit GUI-Option)
- Startup-Validierung
- Umfassende Test-Suite (Unit & Integration)
- CI/CD Pipeline (GitHub Actions)
- Quickstart-Guide
- Erweiterte Dokumentation (README, API-Docs)

### Features
- Windows-Fenster-Monitoring mit pywin32
- Automatische Screenshot-Erstellung bei Fensterwechsel
- OCR-Integration mit Tesseract
- AI-Textgenerierung mit OpenAI GPT-5
- Privacy-Maskierung (automatisch & manuell)
- Multiple Export-Formate (DOCX, PDF, Markdown, HTML, JSON, CSV)
- Revisionssichere Dokumentation (SHA-256, Audit-Trail)
- Konfigurierbare Prompt-Profile (SOP, Training, Technical)
- Dokument-Templates
- Batch-Processing für mehrere Sessions
- Tastenkürzel für alle wichtigen Aktionen
- Keyboard-Monitoring mit Privacy-Filter

### Technisch
- Strukturiertes Logging-System
- Retry-Logik für API-Calls
- Konfigurationsvalidierung
- Graceful Error Handling
- Thread-sichere Implementierung
- Session-State-Management

### Dokumentation
- Vollständiges README mit Troubleshooting
- Quickstart-Guide
- API-Dokumentation
- Entwickler-Dokumentation
- Benutzerhandbuch

### Tests
- Unit-Tests für alle kritischen Module
- Integrationstests für vollständige Workflows
- Mock-Objekte für externe Dependencies
- Test-Coverage-Reporting

### Sicherheit & Compliance
- SHA-256-Hashing für Screenshots
- Vollständiger Audit-Trail
- Privacy-Maskierung für sensible Daten
- Konfigurierbare Datenschutz-Richtlinien

