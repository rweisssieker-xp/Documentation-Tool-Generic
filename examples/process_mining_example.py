"""
Example: Process Mining Engine
Demonstrates how to discover and analyze processes from documentation sessions.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main example demonstrating process mining."""
    
    print("=" * 60)
    print("🔍 Process Mining Engine Example")
    print("=" * 60)
    
    try:
        from src.processmining import ProcessMiner, PatternDetector, VariantAnalyzer, BPMNExporter, ProcessGraph
        
        print("\n✅ Process Mining Module geladen")
        
        # Sample sessions representing different workflow variants
        sessions = [
            {
                "session_id": "sess_001",
                "name": "Standard Login",
                "steps": [
                    {"action_type": "open", "description": "App öffnen"},
                    {"action_type": "input", "description": "Username eingeben"},
                    {"action_type": "input", "description": "Password eingeben"},
                    {"action_type": "click", "description": "Login klicken"},
                    {"action_type": "wait", "description": "Warten auf Dashboard"}
                ]
            },
            {
                "session_id": "sess_002",
                "name": "Standard Login (Variante)",
                "steps": [
                    {"action_type": "open", "description": "App öffnen"},
                    {"action_type": "input", "description": "Username eingeben"},
                    {"action_type": "input", "description": "Password eingeben"},
                    {"action_type": "click", "description": "Login klicken"},
                    {"action_type": "wait", "description": "Warten auf Dashboard"}
                ]
            },
            {
                "session_id": "sess_003",
                "name": "Login mit Remember Me",
                "steps": [
                    {"action_type": "open", "description": "App öffnen"},
                    {"action_type": "input", "description": "Username eingeben"},
                    {"action_type": "input", "description": "Password eingeben"},
                    {"action_type": "click", "description": "Remember Me aktivieren"},
                    {"action_type": "click", "description": "Login klicken"},
                    {"action_type": "wait", "description": "Warten auf Dashboard"}
                ]
            },
            {
                "session_id": "sess_004",
                "name": "Login mit Fehler",
                "steps": [
                    {"action_type": "open", "description": "App öffnen"},
                    {"action_type": "input", "description": "Username eingeben"},
                    {"action_type": "input", "description": "Password eingeben"},
                    {"action_type": "click", "description": "Login klicken"},
                    {"action_type": "wait", "description": "Fehlermeldung"},
                    {"action_type": "input", "description": "Password erneut eingeben"},
                    {"action_type": "click", "description": "Login klicken"},
                    {"action_type": "wait", "description": "Warten auf Dashboard"}
                ]
            },
            {
                "session_id": "sess_005",
                "name": "Quick Login",
                "steps": [
                    {"action_type": "open", "description": "App öffnen"},
                    {"action_type": "click", "description": "Gespeicherten Login verwenden"},
                    {"action_type": "wait", "description": "Warten auf Dashboard"}
                ]
            }
        ]
        
        print(f"\n📋 {len(sessions)} Sessions zur Analyse")
        
        # Initialize Process Miner
        print("\n📦 Initialisiere ProcessMiner...")
        miner = ProcessMiner()
        
        # Add sessions
        print("\n📥 Füge Sessions hinzu...")
        for session in sessions:
            case = miner.add_session(session)
            print(f"   ✅ {session['name']} ({len(case.activities)} Aktivitäten)")
        
        # Discover process
        print("\n🔍 Entdecke Prozessmodell...")
        model = miner.discover_process("Login Process")
        
        print(f"\n📊 Prozessmodell: {model.name}")
        print(f"   Aktivitäten: {len(model.activities)}")
        print(f"   Start-Aktivitäten: {model.start_activities}")
        print(f"   End-Aktivitäten: {model.end_activities}")
        print(f"   Varianten: {len(model.variants)}")
        
        # Show transitions
        print("\n   Übergänge:")
        for from_act, to_acts in model.transitions.items():
            print(f"      {from_act} → {', '.join(to_acts)}")
        
        # Get statistics
        print("\n📈 Statistik:")
        stats = miner.get_statistics()
        print(f"   Cases: {stats['total_cases']}")
        print(f"   Aktivitäten gesamt: {stats['total_activities']}")
        print(f"   Durchschnitt: {stats['avg_activities_per_case']:.1f} pro Case")
        print(f"   Unique Aktivitäten: {stats['unique_activities']}")
        
        # Pattern Detection
        print("\n🔎 Muster-Erkennung...")
        detector = PatternDetector(min_support=0.3)
        
        # Extract traces
        traces = [
            [act.name for act in case.activities]
            for case in miner._cases
        ]
        
        patterns = detector.detect_patterns(traces)
        
        print(f"   Gefundene Muster: {len(patterns)}")
        for pattern in patterns[:5]:
            seq = " → ".join(pattern.sequence)
            print(f"      {pattern.pattern_type}: {seq} (Support: {pattern.support:.0%})")
        
        # Variant Analysis
        print("\n📊 Varianten-Analyse...")
        analyzer = VariantAnalyzer()
        
        variants = analyzer.analyze_variants(traces)
        
        print(f"   Varianten: {len(variants)}")
        for var in variants[:3]:
            trace = " → ".join(var.trace[:4])
            if len(var.trace) > 4:
                trace += " ..."
            hp = "⭐ Happy Path" if var.is_happy_path else ""
            print(f"      {trace} ({var.percentage:.0f}%) {hp}")
        
        # Export to different formats
        print("\n📤 Export:")
        
        # Mermaid
        exporter = BPMNExporter()
        mermaid = exporter.export_to_mermaid(model)
        print("\n   Mermaid Diagramm:")
        for line in mermaid.split('\n')[:10]:
            print(f"      {line}")
        if len(mermaid.split('\n')) > 10:
            print("      ...")
        
        # Process Graph
        print("\n   DOT (Graphviz):")
        graph = ProcessGraph.from_process_model(model)
        dot = graph.to_dot()
        for line in dot.split('\n')[:8]:
            print(f"      {line}")
        print("      ...")
        
        # Graph metrics
        print("\n   Graph-Metriken:")
        metrics = graph.calculate_metrics()
        print(f"      Knoten: {metrics['nodes']}")
        print(f"      Kanten: {metrics['edges']}")
        print(f"      Dichte: {metrics['density']:.2f}")
        print(f"      Verbunden: {metrics['is_connected']}")
        
        print("\n\n✅ Process Mining Beispiel abgeschlossen!")
        print("\nNächste Schritte:")
        print("1. BPMN-Export für Camunda/Signavio")
        print("2. Varianten-Vergleich für Optimierung")
        print("3. Konformitäts-Prüfung gegen Soll-Prozess")
        
    except ImportError as e:
        print(f"\n❌ Modul nicht gefunden: {e}")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

