# Automatischer Handbuch-Generator (AHG)

Vollautomatische Erstellung bebilderter technischer Handbücher aus realen Nutzungsszenarien von Software-Anwendungen.

## Features

- **Automatische Beobachtung**: Überwacht alle relevanten Benutzeraktionen (Fensterwechsel, Mausklicks, Tastatureingaben)
- **Screenshot-Erstellung**: Automatische Screenshots bei jedem relevanten Schritt
- **OCR-Integration**: Texterkennung aus Screenshots für bessere Kontextanalyse
- **AI-Textgenerierung**: Verwendet OpenAI GPT-5 für präzise, kontextbezogene Beschreibungen
- **Revisionssichere Dokumentation**: SHA-256-Hash für jeden Screenshot, vollständiger Audit-Trail
- **Konfigurierbare Prompt-Profile**: Verschiedene Stile (SOP, Schulung, technisch)
- **Mehrere Ausgabeformate**: DOCX, PDF, Markdown, HTML, JSON/CSV für Audit-Trail
- **Erweiterte Export-Optionen**: Multi-Sprach-Export, Cloud-Upload, Quick-Reference, Video-Export, Platform-Export
- **Automatisierungs-Features**: Automatische App-Erkundung und Dokumentation

### 🚀 Innovation Features

#### v1.1 Features
- **Voice-First Documentation**: Hands-free Dokumentation per Sprachsteuerung mit OpenAI Whisper
- **Multi-Modal Knowledge Base**: Semantische Suche mit RAG (Retrieval-Augmented Generation)
- **Predictive Documentation**: KI-gestützte Vorhersage nächster Dokumentationsschritte
- **Smart Context Capture**: Erweitertes Monitoring von Clipboard, Tabs und Anwendungskontext
- **Automated Test Generation**: Export dokumentierter Workflows als Selenium/Playwright/Gherkin Tests
- **Interactive Tutorial Generator**: Konvertierung von Dokumentation in SCORM-kompatible interaktive Tutorials
- **Process Mining Engine**: Analyse und BPMN-Export von Benutzer-Sessions

#### v2.0 Features (NEU!)
- **GitOps Documentation Pipeline**: Documentation-as-Code mit Git-Integration, AI Commits, PR Automation
- **Accessibility Compliance Engine**: WCAG 2.2 Prüfung, Auto-Remediation, Compliance-Reports
- **Documentation ROI Dashboard**: Metriken, ROI-Berechnung, Predictive Analytics
- **Intelligent Translation Hub**: Kontextbewusste Übersetzung, Glossar, Translation Memory
- **Video Tutorial Synthesizer**: Automatische Video-Generierung mit AI-Narration und Untertiteln
- **Real-Time Collaboration Hub**: Echtzeit-Synchronisation mit CRDT, Presence-Tracking, Comments
- **Autonomous Documentation Agent**: Vollautonome KI für selbstständige Dokumentation

## Schnellstart

Für eine schnelle Einführung siehe [QUICKSTART.md](QUICKSTART.md)

## Installation

### Voraussetzungen

- Python 3.10 oder höher
- Windows 10/11
- Tesseract OCR ([Download](https://github.com/UB-Mannheim/tesseract/wiki))

### Setup

1. Repository klonen:
```bash
git clone <repository-url>
cd Documentation-Tool-Generic
```

2. Virtual Environment erstellen (empfohlen):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Dependencies installieren:
```bash
pip install -r requirements.txt
```

4. Tesseract OCR installieren und Pfad setzen:
   - Installiere Tesseract von https://github.com/UB-Mannheim/tesseract/wiki
   - Setze die Umgebungsvariable `TESSDATA_PREFIX` auf den Installationspfad

5. Environment-Variablen konfigurieren:
```bash
copy .env.example .env
# Bearbeite .env und füge deinen OpenAI API-Key ein
```

## Verwendung

1. Starte die Anwendung:
```bash
python main.py
```

2. Konfiguriere die Einstellungen:
   - Wähle ein Prompt-Profil (SOP, Schulung, technisch)
   - Stelle sicher, dass der OpenAI API-Key gesetzt ist

3. Starte eine Session:
   - Klicke auf "Session starten"
   - Führe die gewünschten Aktionen in der zu dokumentierenden Software aus
   - Die Anwendung erfasst automatisch Screenshots bei jedem Fensterwechsel oder Maske-Änderung

4. Stoppe die Session:
   - Klicke auf "Session beenden"
   - Die Anwendung generiert automatisch das Handbuch

5. Export:
   - Das fertige Dokument wird im `data/output/` Verzeichnis gespeichert
   - Zusätzlich wird ein Audit-Trail als JSON/CSV erstellt

## Projektstruktur

```
Documentation-Tool-Generic/
├── src/                    # Quellcode
│   ├── gui/               # GUI-Komponenten
│   ├── monitor/           # Windows-Monitoring
│   ├── capture/           # Screenshot & OCR
│   ├── ai/                # OpenAI-Integration
│   ├── document/          # Dokumentgenerierung
│   ├── audit/             # Audit-Trail
│   ├── config/            # Konfiguration
│   │
│   │  --- Innovation Features (v1.1 & v2.0) ---
│   │   ├── voice/           # Voice-First Documentation
│   │   ├── knowledge/       # Knowledge Base / RAG
│   │   ├── prediction/      # Predictive Assistant
│   │   ├── context/         # Smart Context Capture
│   │   ├── testgen/         # Test Case Generator
│   │   ├── tutorial/        # Tutorial Generator
│   │   ├── processmining/   # Process Mining Engine
│   │   ├── gitops/          # GitOps Pipeline (v2.0)
│   │   ├── accessibility/   # Accessibility Engine (v2.0)
│   │   ├── analytics/       # ROI Dashboard (v2.0)
│   │   ├── translation/     # Translation Hub (v2.0)
│   │   ├── video/           # Video Synthesizer (v2.0)
│   │   ├── collaboration/   # Collaboration Hub (v2.0)
│   │   └── agent/           # Autonomous Agent (v2.0)
│   ├── voice/             # Voice-First Documentation
│   ├── knowledge/         # Knowledge Base + RAG
│   ├── prediction/        # Predictive Assistant
│   ├── context/           # Smart Context Capture
│   ├── testgen/           # Test Case Generator
│   ├── tutorial/          # Tutorial Generator
│   └── processmining/     # Process Mining Engine
│
├── data/                  # Datenverzeichnis
│   ├── sessions/          # Session-Daten
│   ├── screenshots/       # Screenshots
│   ├── output/            # Generierte Dokumente
│   ├── knowledge_base/    # Knowledge Base Speicher
│   ├── embeddings/        # Vector Embeddings
│   ├── voice_recordings/  # Sprachaufnahmen
│   ├── tutorials/         # Generierte Tutorials
│   ├── generated_tests/   # Generierte Testfälle
│   └── process_models/    # BPMN Prozessmodelle
│
├── config/                # Konfiguration
│   ├── prompt_profiles/   # Prompt-Profile
│   └── innovation_config.yaml  # Innovation Features Config
│
├── cli/                   # Command-Line Interface
│   └── innovation_cli.py  # CLI für Innovation Features
│
└── examples/              # Beispiele
    └── demo_all_features.py  # Full Demo
```

## Prompt-Profile

Die Anwendung verwendet YAML-basierte Prompt-Profile für verschiedene Dokumentationsstile:

- `sop.yml`: Standardarbeitsanweisung (formal, normgerecht)
- `training.yml`: Schulungshandbuch (erklärend, didaktisch)
- `technical.yml`: Technisches Handbuch (präzise, knapp)

## Erweiterte Features

### Tastenkürzel (Hotkeys)

- **Ctrl+S**: Session starten
- **Ctrl+Shift+S**: Session beenden
- **Ctrl+P**: Pause/Resume
- **Ctrl+Z**: Rückgängig (Undo)
- **Ctrl+Y** oder **Ctrl+Shift+Z**: Wiederholen (Redo)
- **F1**: Einstellungen öffnen
- **ESC**: Session beenden (wenn aktiv)

### Session-Management

- **Pause/Resume**: Unterbrechen und Fortsetzen von Aufzeichnungen
- **Undo/Redo**: Rückgängig machen und Wiederholen von Schritten
- **Session-Statistiken**: Live-Anzeige von Dauer, Schritten, Screenshots
- **Session-Wiederherstellung**: Automatische Wiederherstellung nach Absturz
  - Dialog zur Auswahl wiederherstellbarer Sessions (Menü: Session → Session wiederherstellen)
  - Automatisches Speichern des Session-Zustands
  - Validierung vor Wiederherstellung

### Export-Formate

- **DOCX**: Microsoft Word-Dokument (Standard)
- **PDF**: Portable Document Format
- **Markdown**: Für Wikis und Web-Portale
- **HTML**: Für Web-Ansicht mit Styling
- **JSON**: Audit-Trail im JSON-Format
- **CSV**: Audit-Trail im CSV-Format
### Tools & Utilities

- **Manuelle Bereinigung**: Tools → Bereinigung ausführen (Menü)
  - Löscht alte Screenshots und Sessions nach konfigurierbaren Retention-Richtlinien
  - Zeigt Statistiken über gelöschte Dateien
- **Batch-Verarbeitung**: Tools → Batch-Verarbeitung (Menü)
  - Verarbeitet mehrere Sessions gleichzeitig
  - Generiert Dokumente für mehrere Sessions in einem Durchgang
- **Statistiken-Dashboard**: Tools → Statistiken (Menü)
  - Zeigt umfassende Session-Statistiken
  - Qualitäts-Metriken und Performance-Daten
- **Schritt-Konsolidierung**: Tools → Schritt-Konsolidierung (Menü)
  - Führt ähnliche oder redundante Schritte zusammen
  - AI-gestützte Ähnlichkeitserkennung
- **Session-Vergleich**: Tools → Session-Vergleich (Menü)
  - Vergleicht zwei Sessions nebeneinander
  - Identifiziert Unterschiede und Änderungen
- **Test-Checkliste**: Tools → Test-Checkliste generieren (Menü)
  - Generiert Test-Checklisten aus dokumentierten Schritten
  - Exportierbar als DOCX, PDF oder Markdown
- **Qualitätsprüfung**: Tools → Qualitätsprüfung (Menü)
  - Prüft Dokumentationsqualität und Vollständigkeit
  - Zeigt detaillierte Qualitätsberichte
- **Session-Wiederherstellung**: Session → Session wiederherstellen (Menü)
  - Dialog zur Auswahl wiederherstellbarer Sessions
  - Validierung vor Wiederherstellung
  - Möglichkeit, Sessions zu löschen
- **Startup-Validierung**: Automatische Prüfung beim Start
  - Python-Version, Dependencies, Config-Dateien
  - Environment-Variablen, externe Tools
  - Manuelle Validierung: `python scripts/validate_startup.py`

### Export-Features

- **Multi-Sprach-Export**: Export → Multi-Sprach-Export (Menü)
  - Exportiert Dokumentation in mehreren Sprachen
  - Automatische Übersetzung mit AI
- **Cloud-Upload**: Export → Cloud-Upload (Menü)
  - Lädt Dokumente in Cloud-Speicher hoch
  - Unterstützt Google Drive, OneDrive, Dropbox
- **Quick-Reference**: Export → Quick-Reference (Menü)
  - Generiert kompakte Referenz-Leitfäden
  - Ideal für Quick-Start-Guides und Cheat Sheets
- **Video-Export**: Export → Video-Export (Menü)
  - Erstellt Video-Walkthroughs aus Screenshots
  - Konfigurierbare Timing und Übergänge
- **Platform-Export**: Export → Platform-Export (Menü)
  - Exportiert für spezifische Plattformen
  - Unterstützt Confluence, Jira, SharePoint, WordPress
- **Export-Filter**: Export → Export-Filter (Menü)
  - Filtert Schritte vor dem Export
  - Erlaubt selektive Dokumentation

### Automatisierung

- **App-Erkundung**: Automatisierung → App erkunden (Menü)
  - Automatische Erkundung und Dokumentation von Anwendungen
  - UI-Element-Erkennung
  - Intelligente Navigation

### 🚀 Innovation Features (v1.1)

#### Voice-First Documentation
Dokumentieren Sie freihändig per Sprachsteuerung:
- **Aktivierung**: Tools → Voice-First Panel (`Ctrl+Alt+V`)
- **Sprachen**: Deutsch und Englisch
- **Sprachbefehle**: "Nächster Schritt", "Screenshot", "Pause", etc.
- **AI-Backend**: OpenAI Whisper für hochpräzise Spracherkennung

#### Multi-Modal Knowledge Base
Zentralisierte Wissensbasis mit semantischer Suche:
- **Aktivierung**: Tools → Knowledge Base (`Ctrl+Alt+K`)
- **Suche**: Keyword + semantische Hybrid-Suche
- **RAG**: KI-gestützte Antworten basierend auf Ihrer Dokumentation
- **Backend**: ChromaDB für Vektor-Embeddings

#### Predictive Documentation
KI-Assistent für optimierte Dokumentation:
- Vorhersage des nächsten wahrscheinlichen Schritts
- Lücken-Analyse für vollständige Dokumentation
- Auto-Completion für Schrittbeschreibungen
- Workflow-Pattern-Learning

#### Smart Context Capture
Erweitertes Kontext-Monitoring:
- Clipboard-Überwachung (Kopierte Texte/Bilder)
- Browser-Tab-Tracking (Chrome, Firefox, Edge)
- Intent-Analyse mittels GPT-4o
- Context Cloud für zentrale Speicherung

#### Test Case Generator
Export dokumentierter Workflows als ausführbare Tests:
- **Aktivierung**: Export → Test Case Export (`Ctrl+Alt+T`)
- **Frameworks**: Selenium, Playwright, Gherkin/BDD
- **Sprachen**: Python, TypeScript
- **Features**: Smart Selector Generation, Fallback-Strategien

#### Tutorial Generator
Konvertierung von Dokumentation in interaktive Tutorials:
- **Aktivierung**: Export → Tutorial Export (`Ctrl+Alt+U`)
- **Format**: HTML5 interaktiv mit Navigation
- **SCORM**: 2004 4th Edition für LMS-Integration
- **Quizzes**: Automatisch generierte Verständnisfragen

#### Process Mining Engine
Analyse und Visualisierung von Benutzer-Prozessen:
- **Aktivierung**: Tools → Process Mining (`Ctrl+Alt+M`)
- **Discovery**: Automatische Prozess-Erkennung aus Sessions
- **Patterns**: Erkennung wiederkehrender Muster
- **Varianten**: Analyse verschiedener Prozess-Varianten
- **Export**: BPMN 2.0 XML, Mermaid Flowcharts

### Datenschutz & Compliance

- **Automatische Privacy-Maskierung**: Erkennung und Schwärzung sensibler Daten
- **SHA-256-Hashing**: Revisionssichere Dokumentation
- **Vollständiger Audit-Trail**: JSON/CSV-Export aller Aktivitäten
- **Konfigurierbare Masken**: Manuelle Definition von Schwärzungsbereichen

## Troubleshooting

### Häufige Probleme

#### 1. OpenAI API-Fehler
**Problem**: "OpenAI API-Key nicht gesetzt" oder API-Fehler

**Lösung**:
- Überprüfe, ob die Umgebungsvariable `OPENAI_API_KEY` gesetzt ist
- Stelle sicher, dass der API-Key gültig ist
- Prüfe deine OpenAI API-Credits und Limits

#### 2. Tesseract OCR nicht gefunden
**Problem**: OCR-Funktionalität nicht verfügbar

**Lösung**:
- Installiere Tesseract OCR von https://github.com/UB-Mannheim/tesseract/wiki
- Setze die Umgebungsvariable `TESSERACT_CMD` auf den Installationspfad
- Alternativ: Setze `TESSDATA_PREFIX` auf das Tesseract-Verzeichnis

#### 3. Screenshots werden nicht erstellt
**Problem**: Keine Screenshots während der Session

**Lösung**:
- Überprüfe, ob die zu dokumentierende Anwendung im Vordergrund ist
- Stelle sicher, dass keine anderen Anwendungen das Fenster überdecken
- Prüfe die Trigger-Konfiguration in `config/trigger_config.yml`
- Erhöhe ggf. die `poll_interval` und `change_threshold` Werte

#### 4. Dokumentgenerierung schlägt fehl
**Problem**: Fehler beim Generieren des Dokuments

**Lösung**:
- Überprüfe, ob mindestens ein Schritt erfasst wurde
- Stelle sicher, dass genügend Speicherplatz vorhanden ist
- Prüfe die Log-Dateien in `logs/` für detaillierte Fehlermeldungen
- Überprüfe die Prompt-Profil-Konfiguration

#### 5. Session wird nicht wiederhergestellt
**Problem**: Wiederherstellung nach Absturz funktioniert nicht

**Lösung**:
- Überprüfe, ob Session-Daten in `data/sessions/` vorhanden sind
- Stelle sicher, dass die Session-Dateien nicht beschädigt sind
- Prüfe die Log-Dateien für Fehlerdetails

### Log-Dateien

Die Anwendung erstellt Log-Dateien im `logs/` Verzeichnis:
- `ahg.log`: Haupt-Log-Datei mit allen Aktivitäten
- Log-Level: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Entwickler-Dokumentation

### Projektstruktur

```
src/
├── gui/                    # GUI-Komponenten
│   ├── main_window.py     # Hauptfenster
│   ├── settings_dialog.py  # Einstellungsdialog
│   └── preview_panel.py    # Live-Vorschau
├── monitor/               # Windows-Monitoring
│   ├── window_monitor.py  # Fenster-Tracking
│   ├── action_detector.py # Änderungs-Erkennung
│   ├── session_manager.py # Session-Verwaltung
│   └── mouse_keyboard_monitor.py # Input-Monitoring
├── capture/               # Screenshot & OCR
│   ├── screenshot.py      # Screenshot-Erstellung
│   ├── ocr_engine.py      # OCR-Integration
│   └── privacy_mask.py    # Privacy-Maskierung
├── ai/                    # AI-Integration
│   ├── openai_client.py   # OpenAI API-Client
│   ├── prompt_templates.py # Prompt-Templates
│   └── text_generator.py  # Textgenerierung
├── document/              # Dokumentgenerierung
│   ├── docx_builder.py    # DOCX-Generierung
│   ├── pdf_exporter.py    # PDF-Export
│   ├── markdown_exporter.py # Markdown-Export
│   ├── html_exporter.py   # HTML-Export
│   └── template_engine.py # Template-Engine
├── audit/                 # Audit & Compliance
│   ├── audit_logger.py    # Audit-Logging
│   └── compliance.py      # Compliance-Funktionen
├── config/                # Konfiguration
│   ├── config_manager.py  # Config-Manager
│   ├── config_validator.py # Config-Validierung
│   └── trigger_config.py  # Trigger-Konfiguration
└── utils/                 # Utilities
    ├── logger.py          # Logging-System
    └── cleanup_manager.py # Cleanup-Manager
```

### API-Dokumentation

#### SessionManager

```python
from src.monitor.session_manager import SessionManager

# Erstelle Session
session = SessionManager(
    session_id="unique_session_id",
    prompt_profile="sop",
    output_dir=Path("data/sessions")
)

# Starte Session
session.start()

# Pausiere Session
session.pause()

# Setze Session fort
session.resume()

# Stoppe Session
session.stop()

# Hole Schritte
steps = session.get_steps()

# Hole Statistiken
stats = session.get_session_statistics()

# Undo/Redo
session.undo()
session.redo()
```

#### TextGenerator

```python
from src.ai.text_generator import TextGenerator

# Erstelle Generator
generator = TextGenerator('sop')

# Generiere Schritt-Beschreibung
description = generator.generate_step_description(step, previous_steps)

# Generiere Einleitung
introduction = generator.generate_introduction(steps)

# Generiere Fazit
conclusion = generator.generate_conclusion(steps)
```

#### TemplateEngine

```python
from src.document.template_engine import TemplateEngine

# Erstelle Engine
engine = TemplateEngine(
    session_manager,
    output_dir=Path("data/output"),
    template_name="standard"
)

# Generiere Dokument
output_path = engine.generate_document(
    include_introduction=True,
    include_conclusion=True,
    export_formats={
        'docx': True,
        'pdf': True,
        'markdown': False,
        'html': False
    }
)
```

### Innovation CLI

Das Command-Line Interface bietet Zugriff auf alle Innovation Features:

```bash
# Hilfe anzeigen
python cli/innovation_cli.py --help

# Knowledge Base durchsuchen
python cli/innovation_cli.py kb search "Benutzer anlegen"

# Dokument zur Knowledge Base hinzufügen
python cli/innovation_cli.py kb add -f manual.md -t "Benutzerhandbuch" --type manual

# Tests aus Session generieren
python cli/innovation_cli.py test generate -s session.json -f playwright -o test_login.py

# Tutorial aus Session erstellen
python cli/innovation_cli.py tutorial generate -s session.json -o tutorial.html --with-quiz

# Process Mining auf Sessions ausführen
python cli/innovation_cli.py pm analyze -d data/sessions -o process.bpmn -f bpmn

# RAG-Abfrage stellen
python cli/innovation_cli.py rag query "Wie erstelle ich einen Benutzer?"
```

### Tests ausführen

```bash
# Alle Tests ausführen
pytest

# Mit Coverage-Report
pytest --cov=src --cov-report=html

# Nur Unit-Tests
pytest tests/test_*.py -m "not integration"

# Nur Integrationstests
pytest tests/test_integration.py -m integration
```

### Konfiguration erweitern

#### Neues Prompt-Profil erstellen

1. Erstelle Datei `config/prompt_profiles/mein_profil.yml`:

```yaml
language: de
style: custom
system_prompt: "Du bist ein Dokumentationsassistent..."
step_template: "Schritt {step_number}: {window_title}"
introduction_template: "Einleitung für {step_count} Schritte"
conclusion_template: "Fazit für {step_count} Schritte"
```

2. Profil wird automatisch erkannt und in der GUI angezeigt

#### Trigger-Konfiguration anpassen

Bearbeite `config/trigger_config.yml`:

```yaml
poll_interval: 1.0          # Sekunden zwischen Polling
change_threshold: 0.5       # Änderungsschwelle (0.0-1.0)
size_change_threshold: 10   # Pixel-Schwelle für Größenänderung
double_click_delay: 0.5     # Sekunden für Doppelklick-Erkennung
```

#### Privacy-Mask konfigurieren

Bearbeite `config/privacy_mask.yml`:

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

### Erweiterungen entwickeln

#### Neues Export-Format hinzufügen

1. Erstelle neue Klasse in `src/document/`:

```python
class CustomExporter:
    def export(self, steps, output_path, **kwargs):
        # Implementierung
        pass
```

2. Integriere in `TemplateEngine.generate_document()`

#### Neues Monitoring-Feature

1. Erweitere `WindowMonitor` oder erstelle neues Modul
2. Integriere in `SessionManager`
3. Füge Callback für Events hinzu

## Benutzerhandbuch

### Erste Schritte

1. **Installation**: Folge den Installationsanweisungen oben
2. **Konfiguration**: Öffne Einstellungen (F1) und konfiguriere:
   - OpenAI API-Key
   - Prompt-Profil auswählen
   - Export-Formate wählen
   - Dokument-Metadaten eingeben

3. **Erste Session**:
   - Klicke auf "Session starten"
   - Führe die zu dokumentierenden Aktionen aus
   - Die Anwendung erfasst automatisch Screenshots
   - Klicke auf "Session beenden"
   - Das Handbuch wird automatisch generiert

### Best Practices

1. **Vorbereitung**:
   - Schließe unnötige Anwendungen
   - Stelle sicher, dass die zu dokumentierende Anwendung sichtbar ist
   - Bereite einen sauberen Desktop vor

2. **Während der Aufzeichnung**:
   - Arbeite langsam und methodisch
   - Nutze die Pause-Funktion für Pausen
   - Überprüfe die Live-Vorschau regelmäßig
   - Nutze Undo/Redo bei Fehlern

3. **Nach der Aufzeichnung**:
   - Überprüfe die Session-Statistiken
   - Prüfe die generierten Dokumente
   - Exportiere Audit-Trail für Compliance

### Konfiguration

#### Dokument-Metadaten

In den Einstellungen können konfiguriert werden:
- Abteilung
- Projekt
- Kontakt
- Dokument-ID

Diese werden automatisch in das Deckblatt eingefügt.

#### Cleanup-Einstellungen

Erstelle `config/cleanup_config.yml`:

```yaml
auto_cleanup_enabled: true
retention_days_screenshots: 30
retention_days_sessions: 90
```

Alte Dateien werden automatisch beim Start bereinigt.

## Lizenz

[Lizenz hier einfügen]

## Support

Bei Fragen oder Problemen erstelle bitte ein Issue im Repository.

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für vollständige Versionshistorie.

### Version 1.1.0 - Innovation Features

- 🚀 **Voice-First Documentation**: Whisper-Integration für Sprachdokumentation
- 🚀 **Multi-Modal Knowledge Base**: RAG mit ChromaDB und GPT-4o
- 🚀 **Predictive Documentation**: AI-gestützte Step-Vorhersage und Lücken-Analyse
- 🚀 **Smart Context Capture**: Clipboard, Tab-Tracking, Intent-Analyse
- 🚀 **Automated Test Generator**: Selenium, Playwright, Gherkin Export
- 🚀 **Tutorial Generator**: Interaktive Tutorials mit SCORM-Support
- 🚀 **Process Mining Engine**: Prozess-Discovery mit BPMN-Export
- ✅ CLI für alle Innovation Features
- ✅ Vollständige Test-Suite für alle neuen Module
- ✅ GUI-Integration (Menüs, Dialoge, Hotkeys)
- ✅ Konfiguration via `innovation_config.yaml`
- ✅ Umfassende Beispiele und Demo-Skript

### Version 1.0.0

- ✅ Vollständige Implementierung aller geplanten Features
- ✅ Umfassende Test-Suite (Unit & Integration)
- ✅ Erweiterte Dokumentation (README, Quickstart, API-Docs)
- ✅ Production-ready Error Handling & Logging
- ✅ Session Recovery & Cleanup-Management
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Startup-Validierung
- ✅ GUI mit Menüleiste und Dialogen
- ✅ Alle erweiterten Features implementiert
