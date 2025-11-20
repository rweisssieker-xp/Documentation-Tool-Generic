# Quickstart-Guide für AHG

Dieses Dokument führt Sie schnell durch die ersten Schritte mit dem Automatischen Handbuch-Generator.

## Schnellstart (5 Minuten)

### 1. Installation (2 Minuten)

```bash
# Repository klonen
git clone <repository-url>
cd Documentation-Tool-Generic

# Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Konfiguration (1 Minute)

```bash
# .env-Datei erstellen
copy env.example .env

# .env bearbeiten und OpenAI API-Key eintragen
notepad .env
```

Fügen Sie Ihren OpenAI API-Key ein:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Validierung (1 Minute)

```bash
# Prüfe ob alles korrekt installiert ist
python -m src.utils.startup_validator
```

### 4. Erste Session (1 Minute)

```bash
# Anwendung starten
python main.py
```

**In der GUI:**
1. Klicken Sie auf "Einstellungen" (F1)
2. Wählen Sie ein Prompt-Profil (z.B. "sop")
3. Stellen Sie sicher, dass der API-Key gesetzt ist
4. Klicken Sie auf "Session starten" (Ctrl+S)
5. Führen Sie einige Aktionen in einer anderen Anwendung aus
6. Klicken Sie auf "Session beenden" (Ctrl+Shift+S)
7. Das Handbuch wird automatisch generiert!

## Beispiel-Workflow

### Szenario: Dokumentation einer Web-Anwendung

1. **Vorbereitung:**
   - Öffnen Sie die zu dokumentierende Web-Anwendung im Browser
   - Schließen Sie unnötige Fenster
   - Starten Sie AHG

2. **Session starten:**
   - Klicken Sie auf "Session starten" oder drücken Sie `Ctrl+S`
   - AHG beginnt automatisch Screenshots zu erfassen

3. **Dokumentation durchführen:**
   - Führen Sie die Schritte durch, die dokumentiert werden sollen
   - AHG erfasst automatisch Screenshots bei jedem Fensterwechsel
   - Nutzen Sie die Live-Vorschau um zu sehen, was erfasst wird
   - Nutzen Sie `Ctrl+P` für Pause, falls nötig

4. **Schritte bearbeiten:**
   - Wählen Sie einen Schritt in der Liste aus
   - Klicken Sie "Löschen" um unerwünschte Schritte zu entfernen
   - Nutzen Sie `Ctrl+Z` für Undo und `Ctrl+Y` für Redo

5. **Session beenden:**
   - Klicken Sie auf "Session beenden" oder drücken Sie `Ctrl+Shift+S`
   - AHG generiert automatisch das Handbuch
   - Das fertige Dokument finden Sie in `data/output/`

## Tipps & Tricks

### Keyboard Shortcuts

- `Ctrl+S` - Session starten
- `Ctrl+Shift+S` - Session beenden
- `Ctrl+P` - Pause/Fortsetzen
- `Ctrl+Z` - Rückgängig
- `Ctrl+Y` - Wiederholen
- `F1` - Einstellungen
- `ESC` - Session beenden (wenn aktiv)

### Menü-Funktionen

**Datei-Menü:**
- Einstellungen: Konfiguration der Anwendung (F1)
- Beenden: Anwendung schließen (Alt+F4)

**Session-Menü:**
- Session starten: Neue Aufzeichnung beginnen (Ctrl+S)
- Session beenden: Aufzeichnung beenden und Dokument generieren (Ctrl+Shift+S)
- Pause/Fortsetzen: Aufzeichnung pausieren/fortsetzen (Ctrl+P)
- Rückgängig: Letzten Schritt rückgängig machen (Ctrl+Z)
- Wiederholen: Letzten Undo wiederholen (Ctrl+Y)
- Session wiederherstellen: Abgebrochene Sessions wieder herstellen

**Export-Menü:**
- Multi-Sprach-Export: Dokumentation in mehreren Sprachen exportieren
- Cloud-Upload: Dokumente in Cloud-Speicher hochladen
- Quick-Reference: Kurze Referenz-Leitfäden generieren
- Video-Export: Video-Walkthroughs aus Screenshots erstellen
- Platform-Export: Für spezifische Plattformen exportieren
- Export-Filter: Schritte vor dem Export filtern

**Tools-Menü:**
- Bereinigung ausführen: Manuelle Bereinigung alter Dateien
- Batch-Verarbeitung: Mehrere Sessions gleichzeitig verarbeiten
- Statistiken: Session-Statistiken anzeigen
- Schritt-Konsolidierung: Ähnliche Schritte zusammenführen
- Session-Vergleich: Zwei Sessions vergleichen
- Test-Checkliste generieren: Test-Checklisten aus Schritten generieren
- Qualitätsprüfung: Dokumentationsqualität prüfen

**Automatisierung-Menü:**
- App erkunden: Anwendung automatisch erkunden und dokumentieren

**Hilfe-Menü:**
- Tastenkürzel: Zeigt alle verfügbaren Shortcuts
- Über: Informationen zur Anwendung

### Best Practices

1. **Vorbereitung ist wichtig:**
   - Bereiten Sie einen sauberen Desktop vor
   - Schließen Sie unnötige Anwendungen
   - Stellen Sie sicher, dass die zu dokumentierende Anwendung sichtbar ist

2. **Während der Aufzeichnung:**
   - Arbeiten Sie langsam und methodisch
   - Nutzen Sie die Pause-Funktion für Pausen
   - Überprüfen Sie regelmäßig die Live-Vorschau
   - Nutzen Sie Undo/Redo bei Fehlern

3. **Nach der Aufzeichnung:**
   - Überprüfen Sie die Session-Statistiken
   - Prüfen Sie die generierten Dokumente
   - Exportieren Sie den Audit-Trail für Compliance

## Häufige Probleme

### Problem: OpenAI API-Fehler
**Lösung:** Überprüfen Sie den API-Key in `.env` oder als Umgebungsvariable

### Problem: Keine Screenshots
**Lösung:** 
- Stellen Sie sicher, dass die zu dokumentierende Anwendung im Vordergrund ist
- Prüfen Sie die Trigger-Konfiguration in `config/trigger_config.yml`

### Problem: OCR funktioniert nicht
**Lösung:** 
- Installieren Sie Tesseract OCR
- Setzen Sie `TESSERACT_CMD` als Umgebungsvariable

## Nächste Schritte

- Lesen Sie die vollständige Dokumentation im [USER_MANUAL.md](USER_MANUAL.md)
- Lesen Sie die technische Dokumentation im [README.md](README.md)
- Konfigurieren Sie eigene Prompt-Profile in `config/prompt_profiles/`
- Erstellen Sie eigene Dokument-Templates in `config/document_templates/`
- Passen Sie die Privacy-Mask an in `config/privacy_mask.yml`
- Erweitern Sie die Funktionalität mit den erweiterten Export-Optionen
- Nutzen Sie die Automatisierungs-Features für effiziente Dokumentation

## Support

Bei Fragen oder Problemen:
- Überprüfen Sie die Log-Dateien in `logs/ahg.log`
- Erstellen Sie ein Issue im Repository
- Lesen Sie den Troubleshooting-Abschnitt im README

