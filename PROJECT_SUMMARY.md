# Automatischer Handbuch-Generator (AHG)

**Version 1.0.0** | Vollständig implementiert und produktionsreif

## 🎯 Übersicht

Der Automatische Handbuch-Generator (AHG) ist eine vollautomatische Lösung zur Erstellung bebilderter technischer Handbücher aus realen Nutzungsszenarien von Software-Anwendungen.

## ✨ Hauptfunktionen

- ✅ **Vollautomatische Dokumentation**: Erfasst Benutzeraktionen, Screenshots und generiert Handbücher
- ✅ **AI-gestützte Textgenerierung**: Verwendet OpenAI GPT-5 für präzise Beschreibungen
- ✅ **Revisionssichere Dokumentation**: SHA-256-Hashing und vollständiger Audit-Trail
- ✅ **Multiple Export-Formate**: DOCX, PDF, Markdown, HTML, JSON, CSV
- ✅ **Privacy-Maskierung**: Automatische Erkennung und Schwärzung sensibler Daten
- ✅ **Session-Management**: Pause/Resume, Undo/Redo, Wiederherstellung nach Absturz

## 📋 Vollständige Feature-Liste

### Core Features
- ✅ Windows-Fenster-Monitoring
- ✅ Automatische Screenshot-Erstellung
- ✅ OCR-Integration (Tesseract)
- ✅ AI-Textgenerierung (OpenAI GPT-5)
- ✅ DOCX/PDF-Generierung
- ✅ Audit-Trail (JSON/CSV)

### Erweiterte Features
- ✅ Mausklicks- und Tastatureingaben-Erfassung
- ✅ Markdown/HTML-Export
- ✅ Automatische Troubleshooting-Generierung
- ✅ Sicherheitshinweise-Sektion
- ✅ Automatische Privacy-Erkennung
- ✅ Konfigurierbare Trigger-Schwellenwerte
- ✅ Erweiterte Dokument-Metadaten
- ✅ Automatisches Inhaltsverzeichnis
- ✅ Session-Pause/Resume
- ✅ Batch-Processing
- ✅ Dokument-Templates
- ✅ Export-Filter/Optionen

### Production-Ready Features
- ✅ Strukturiertes Logging-System
- ✅ Verbesserte Fehlerbehandlung (Retry-Logik)
- ✅ Konfigurationsvalidierung
- ✅ Session-Wiederherstellung (GUI-Dialog)
- ✅ Automatische Bereinigung (mit GUI-Option)
- ✅ Umfassende Tests (Unit & Integration)
- ✅ Live-Vorschau funktionsfähig
- ✅ Session-Statistiken
- ✅ Undo/Redo-Funktionalität
- ✅ Hotkeys/Shortcuts
- ✅ Keyboard-Monitoring vollständig
- ✅ Export-Validierung
- ✅ Erweiterte Dokumentation

## 🚀 Schnellstart

```bash
# Installation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Konfiguration
copy env.example .env
# Bearbeite .env und füge OpenAI API-Key ein

# Start
python main.py
```

Siehe [QUICKSTART.md](QUICKSTART.md) für detaillierte Anleitung.

## 📚 Dokumentation

- **[README.md](README.md)**: Vollständige Dokumentation
- **[QUICKSTART.md](QUICKSTART.md)**: Schnellstart-Anleitung
- **[CHANGELOG.md](CHANGELOG.md)**: Versionshistorie

## 🧪 Tests

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=src --cov-report=html

# Nur Integrationstests
pytest tests/test_integration.py -m integration
```

## 🏗️ Projektstruktur

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
│   └── utils/             # Utilities
├── tests/                 # Test-Suite
├── config/                # Konfigurationsdateien
├── scripts/               # Utility-Scripts
└── data/                  # Datenverzeichnis
```

## 📝 Lizenz

[Lizenz hier einfügen]

## 👥 Beiträge

Beiträge sind willkommen! Bitte erstellen Sie ein Issue oder Pull Request.

## 📞 Support

Bei Fragen oder Problemen:
- Überprüfen Sie die [Troubleshooting-Sektion](README.md#troubleshooting)
- Erstellen Sie ein Issue im Repository
- Lesen Sie die [Dokumentation](README.md)

---

**Status**: ✅ Produktionsreif - Alle Features implementiert und getestet

