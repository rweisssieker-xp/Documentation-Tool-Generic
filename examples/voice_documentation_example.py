"""
Example: Voice-First Documentation
Demonstrates how to use voice capture and transcription during documentation.
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main example demonstrating voice-first documentation."""
    
    print("=" * 60)
    print("🎤 Voice-First Documentation Example")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY nicht gesetzt!")
        print("   Bitte setzen Sie die Umgebungsvariable:")
        print("   export OPENAI_API_KEY='your-key-here'")
        return
    
    try:
        from src.voice import VoiceCapture, WhisperClient, VoiceCommandProcessor, VoiceAnnotator
        
        print("\n✅ Voice-Module geladen")
        
        # Initialize components
        print("\n📦 Initialisiere Komponenten...")
        
        # Voice Capture
        capture = VoiceCapture(sample_rate=16000, chunk_duration=5.0)
        print("   ✅ VoiceCapture bereit")
        
        # Whisper Client
        whisper = WhisperClient(language="de")
        print("   ✅ WhisperClient bereit")
        
        # Command Processor
        commands = VoiceCommandProcessor(primary_language="de")
        print("   ✅ VoiceCommandProcessor bereit")
        
        # Voice Annotator
        annotator = VoiceAnnotator(session_id="example_session")
        annotator.set_current_step("step_1")
        print("   ✅ VoiceAnnotator bereit")
        
        # Show available commands
        print("\n📋 Verfügbare Sprachbefehle:")
        print(commands.get_help_text("de"))
        
        # Example: Parse commands
        print("\n🔍 Beispiel: Sprachbefehle parsen")
        
        test_commands = [
            "starte die aufnahme",
            "notiz: Das ist ein wichtiger Punkt",
            "wichtig: Hier könnte ein Fehler auftreten",
            "stoppe die aufnahme"
        ]
        
        for text in test_commands:
            cmd = commands.parse_command(text)
            if cmd:
                print(f"   '{text}'")
                print(f"   → Typ: {cmd.type.value}, Aktion: {cmd.action}")
                if cmd.parameters:
                    print(f"   → Parameter: {cmd.parameters}")
                print()
        
        # Example: Add annotations
        print("📝 Beispiel: Annotationen hinzufügen")
        
        annotator.add_annotation(
            text="Dies ist der erste Schritt der Dokumentation",
            annotation_type="narration",
            duration=3.5
        )
        
        annotator.add_annotation(
            text="Wichtig: Beachten Sie die Reihenfolge",
            annotation_type="note"
        )
        
        annotations = annotator.get_annotations_for_step("step_1")
        print(f"   ✅ {len(annotations)} Annotationen hinzugefügt")
        
        # Export
        print("\n📤 Beispiel: Export")
        
        json_export = annotator.export_annotations(format="json")
        print(f"   JSON Export: {len(json_export)} Zeichen")
        
        md_export = annotator.export_annotations(format="markdown")
        print(f"   Markdown Export: {len(md_export)} Zeichen")
        
        print("\n✅ Voice-First Documentation Beispiel abgeschlossen!")
        print("\nNächste Schritte:")
        print("1. Verwenden Sie VoiceCapture.start_recording() für Echtzeit-Aufnahme")
        print("2. Verwenden Sie WhisperClient.transcribe_file() für Transkription")
        print("3. Integrieren Sie VoiceAnnotator in Ihre Dokumentations-Session")
        
    except ImportError as e:
        print(f"\n❌ Modul nicht gefunden: {e}")
        print("   Bitte installieren Sie: pip install sounddevice openai")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")


if __name__ == "__main__":
    main()

