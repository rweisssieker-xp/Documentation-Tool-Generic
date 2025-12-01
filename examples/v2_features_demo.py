#!/usr/bin/env python3
"""Demo für alle v2.0 Features"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def demo_accessibility():
    """Demo Accessibility Engine"""
    print("=" * 60)
    print("Accessibility Compliance Engine")
    print("=" * 60)
    
    from src.accessibility import WCAGAuditor, WCAGLevel
    
    auditor = WCAGAuditor(level=WCAGLevel.AA)
    html = '<img src="test.png"><h1>Title</h1><h3>Subtitle</h3>'
    result = auditor.audit_html(html)
    
    print(f"[OK] WCAG {result.level.value} Audit")
    print(f"   Score: {result.score:.1f}%")
    print(f"   Violations: {len(result.violations)}")
    for v in result.violations[:3]:
        print(f"   - {v.rule_id}: {v.description}")

def demo_roi():
    """Demo ROI Dashboard"""
    print("\n" + "=" * 60)
    print("ROI Dashboard")
    print("=" * 60)
    
    from src.analytics import MetricsCollector, ROICalculator
    
    collector = MetricsCollector()
    calculator = ROICalculator(collector, hourly_rate=50.0)
    
    roi = calculator.calculate_roi(days=30)
    print(f"[OK] ROI Berechnung")
    print(f"   Zeit gespart: {roi.time_saved_hours:.1f} Stunden")
    print(f"   Kosten gespart: {roi.cost_saved:.2f} EUR")
    print(f"   ROI: {roi.roi_percentage:.1f}%")

def demo_translation():
    """Demo Translation Hub"""
    print("\n" + "=" * 60)
    print("Intelligent Translation Hub")
    print("=" * 60)
    
    from src.translation import TranslationHub
    
    hub = TranslationHub("demo_project")
    hub.add_glossary_term("Benutzer", "en", "User")
    
    translated = hub.translate_document("Erstelle einen neuen Benutzer", "de", "en")
    print(f"[OK] Übersetzung")
    print(f"   DE: Erstelle einen neuen Benutzer")
    print(f"   EN: {translated}")

def demo_video():
    """Demo Video Synthesizer"""
    print("\n" + "=" * 60)
    print("Video Tutorial Synthesizer")
    print("=" * 60)
    
    from src.video import VideoSynthesizer, VideoConfig
    
    config = VideoConfig(frame_rate=30, language="de")
    synthesizer = VideoSynthesizer(config)
    
    print("[OK] Video Synthesizer initialisiert")
    print(f"   Frame Rate: {config.frame_rate} fps")
    print(f"   Sprache: {config.language}")

def demo_collaboration():
    """Demo Collaboration Hub"""
    print("\n" + "=" * 60)
    print("Real-Time Collaboration Hub")
    print("=" * 60)
    
    from src.collaboration import CRDTEngine, PresenceManager
    
    crdt = CRDTEngine()
    presence = PresenceManager()
    
    print("[OK] Collaboration Engine initialisiert")
    print(f"   CRDT Operations: {len(crdt.operations)}")
    print(f"   Active Users: {len(presence.presences)}")

def demo_agent():
    """Demo Autonomous Agent"""
    print("\n" + "=" * 60)
    print("Autonomous Documentation Agent")
    print("=" * 60)
    
    from src.agent import AutonomousAgent
    
    agent = AutonomousAgent()
    print("[OK] Autonomous Agent initialisiert")
    print(f"   Tools verfügbar: {agent.tool_executor.available}")
    print(f"   AI verfügbar: {agent.client is not None}")

if __name__ == "__main__":
    print("\nInnovation Features v2.0 - Demo\n")
    
    demo_accessibility()
    demo_roi()
    demo_translation()
    demo_video()
    demo_collaboration()
    demo_agent()
    
    print("\n" + "=" * 60)
    print("[OK] Alle v2.0 Features demonstriert!")
    print("=" * 60)

