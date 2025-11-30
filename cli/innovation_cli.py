#!/usr/bin/env python3
"""
Innovation Features CLI
Command-line interface for AHG innovation features.
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def cmd_knowledge_search(args):
    """Search the knowledge base."""
    from src.knowledge import KnowledgeBase
    
    kb = KnowledgeBase(storage_dir=args.storage or "data/knowledge_base")
    
    results = kb.search(
        query=args.query,
        doc_type=args.type,
        limit=args.limit,
        semantic=not args.keyword_only
    )
    
    if not results:
        print("Keine Ergebnisse gefunden.")
        return
    
    print(f"\n🔍 {len(results)} Ergebnisse für: '{args.query}'\n")
    
    for i, result in enumerate(results, 1):
        doc = result.document
        print(f"{i}. {doc.title}")
        print(f"   Typ: {doc.doc_type} | Score: {result.score:.2f}")
        if result.highlights:
            print(f"   ... {result.highlights[0][:100]}...")
        print()


def cmd_knowledge_add(args):
    """Add document to knowledge base."""
    from src.knowledge import KnowledgeBase
    
    kb = KnowledgeBase(storage_dir=args.storage or "data/knowledge_base")
    
    # Read content from file or stdin
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
        title = args.title or Path(args.file).stem
    else:
        content = sys.stdin.read()
        title = args.title or "Untitled"
    
    doc = kb.add_document(
        title=title,
        content=content,
        doc_type=args.type or "manual",
        tags=args.tags.split(",") if args.tags else []
    )
    
    print(f"✅ Dokument hinzugefügt: {doc.id}")
    print(f"   Titel: {doc.title}")
    print(f"   Typ: {doc.doc_type}")


def cmd_knowledge_stats(args):
    """Show knowledge base statistics."""
    from src.knowledge import KnowledgeBase
    
    kb = KnowledgeBase(storage_dir=args.storage or "data/knowledge_base")
    stats = kb.get_statistics()
    
    print("\n📊 Knowledge Base Statistik")
    print("=" * 40)
    print(f"Gesamte Dokumente: {stats['total_documents']}")
    print(f"Sessions: {stats['total_sessions']}")
    print(f"Unique Tags: {stats['unique_tags']}")
    
    if stats.get('documents_by_type'):
        print("\nDokumente nach Typ:")
        for doc_type, count in stats['documents_by_type'].items():
            print(f"  {doc_type}: {count}")


def cmd_generate_tests(args):
    """Generate tests from session file."""
    from src.testgen import TestGenerator, TestFramework
    from src.testgen import SeleniumExporter, PlaywrightExporter, GherkinExporter
    
    # Load session data
    session_data = json.loads(Path(args.session).read_text(encoding='utf-8'))
    
    # Determine framework
    framework_map = {
        "selenium": TestFramework.SELENIUM,
        "playwright": TestFramework.PLAYWRIGHT,
        "gherkin": TestFramework.GHERKIN
    }
    framework = framework_map.get(args.framework, TestFramework.PLAYWRIGHT)
    
    # Generate
    generator = TestGenerator(default_framework=framework)
    test_cases = generator.generate_test_cases(session_data, framework)
    
    print(f"✅ {len(test_cases)} Testfälle generiert")
    
    # Export
    if args.output:
        for i, tc in enumerate(test_cases):
            output_path = args.output if len(test_cases) == 1 else f"{args.output}_{i+1}"
            code = generator.export_test(tc, framework, output_path)
            print(f"   → {output_path}")
    else:
        # Print to stdout
        code = generator.export_test(test_cases[0], framework)
        print("\n" + code)


def cmd_generate_tutorial(args):
    """Generate tutorial from session file."""
    from src.tutorial import TutorialGenerator
    
    # Load session data
    session_data = json.loads(Path(args.session).read_text(encoding='utf-8'))
    
    # Generate
    generator = TutorialGenerator(include_quizzes=args.with_quiz)
    tutorial = generator.generate_tutorial(session_data, title=args.title)
    
    print(f"✅ Tutorial generiert: {tutorial.title}")
    print(f"   Schritte: {len(tutorial.steps)}")
    print(f"   Geschätzte Dauer: {tutorial.estimated_duration // 60} Min.")
    
    # Export
    if args.output:
        html = generator.export_html(tutorial, args.output, include_navigation=True)
        print(f"   → {args.output}")
    else:
        html = generator._generate_html(tutorial, True)
        print("\n" + html[:2000] + "\n...")


def cmd_process_mining(args):
    """Run process mining on session files."""
    from src.processmining import ProcessMiner, PatternDetector, VariantAnalyzer, BPMNExporter
    
    # Load sessions
    sessions = []
    for session_file in Path(args.sessions).glob("*.json"):
        try:
            session_data = json.loads(session_file.read_text(encoding='utf-8'))
            if session_data.get("steps"):
                sessions.append(session_data)
        except Exception as e:
            print(f"⚠️  Konnte {session_file} nicht laden: {e}")
    
    if not sessions:
        print("❌ Keine Sessions gefunden")
        return
    
    print(f"📊 Analysiere {len(sessions)} Sessions...")
    
    # Mine processes
    miner = ProcessMiner()
    for session in sessions:
        miner.add_session(session)
    
    model = miner.discover_process("Discovered Process")
    stats = miner.get_statistics()
    
    print(f"\n✅ Prozess entdeckt: {model.name}")
    print(f"   Aktivitäten: {len(model.activities)}")
    print(f"   Varianten: {len(model.variants)}")
    print(f"   Cases: {stats['total_cases']}")
    
    # Export
    if args.output:
        exporter = BPMNExporter()
        
        if args.format == "bpmn":
            exporter.export(model, args.output)
        elif args.format == "mermaid":
            mermaid = exporter.export_to_mermaid(model)
            Path(args.output).write_text(mermaid, encoding='utf-8')
        
        print(f"   → {args.output}")
    else:
        # Print Mermaid to stdout
        exporter = BPMNExporter()
        print("\n" + exporter.export_to_mermaid(model))


def cmd_rag_query(args):
    """Query knowledge base with RAG."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY nicht gesetzt")
        return
    
    from src.knowledge import KnowledgeBase, EmbeddingEngine, SemanticSearch, RAGEngine
    
    storage = args.storage or "data/knowledge_base"
    
    # Initialize
    kb = KnowledgeBase(storage_dir=storage)
    embedding = EmbeddingEngine(storage_dir=storage + "/embeddings")
    search = SemanticSearch(kb, embedding)
    rag = RAGEngine(search, language=args.lang or "de")
    
    # Query
    print(f"\n❓ Frage: {args.question}\n")
    
    response = rag.query(args.question)
    
    print(f"💡 Antwort:\n{response.answer}\n")
    print(f"📊 Konfidenz: {response.confidence:.0%}")
    
    if response.sources:
        print("\n📚 Quellen:")
        for source in response.sources:
            print(f"   - {source.get('title', 'Unbekannt')}")


def main():
    parser = argparse.ArgumentParser(
        description="AHG Innovation Features CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Wissenssuche
  python cli/innovation_cli.py kb search "Benutzer anlegen"
  
  # Dokument hinzufügen
  python cli/innovation_cli.py kb add -f manual.md -t "Benutzerhandbuch" --type manual
  
  # Tests generieren
  python cli/innovation_cli.py test generate -s session.json -f playwright -o test_login.py
  
  # Tutorial erstellen
  python cli/innovation_cli.py tutorial generate -s session.json -o tutorial.html --with-quiz
  
  # Process Mining
  python cli/innovation_cli.py pm analyze -d data/sessions -o process.bpmn -f bpmn
  
  # RAG-Abfrage
  python cli/innovation_cli.py rag query "Wie erstelle ich einen Benutzer?"
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")
    
    # Knowledge Base commands
    kb_parser = subparsers.add_parser("kb", help="Knowledge Base Befehle")
    kb_sub = kb_parser.add_subparsers(dest="kb_command")
    
    # kb search
    kb_search = kb_sub.add_parser("search", help="Suche in der Wissensbasis")
    kb_search.add_argument("query", help="Suchbegriff")
    kb_search.add_argument("--storage", "-s", help="Speicherort der KB")
    kb_search.add_argument("--type", "-t", help="Dokumenttyp filtern")
    kb_search.add_argument("--limit", "-l", type=int, default=10, help="Max. Ergebnisse")
    kb_search.add_argument("--keyword-only", "-k", action="store_true", help="Nur Keyword-Suche")
    kb_search.set_defaults(func=cmd_knowledge_search)
    
    # kb add
    kb_add = kb_sub.add_parser("add", help="Dokument hinzufügen")
    kb_add.add_argument("--file", "-f", help="Datei mit Inhalt")
    kb_add.add_argument("--title", "-t", help="Titel des Dokuments")
    kb_add.add_argument("--type", help="Dokumenttyp")
    kb_add.add_argument("--tags", help="Tags (kommasepariert)")
    kb_add.add_argument("--storage", "-s", help="Speicherort der KB")
    kb_add.set_defaults(func=cmd_knowledge_add)
    
    # kb stats
    kb_stats = kb_sub.add_parser("stats", help="Statistiken anzeigen")
    kb_stats.add_argument("--storage", "-s", help="Speicherort der KB")
    kb_stats.set_defaults(func=cmd_knowledge_stats)
    
    # Test generation commands
    test_parser = subparsers.add_parser("test", help="Test-Generierung")
    test_sub = test_parser.add_subparsers(dest="test_command")
    
    # test generate
    test_gen = test_sub.add_parser("generate", help="Tests aus Session generieren")
    test_gen.add_argument("--session", "-s", required=True, help="Session JSON-Datei")
    test_gen.add_argument("--framework", "-f", default="playwright", 
                         choices=["selenium", "playwright", "gherkin"], help="Test-Framework")
    test_gen.add_argument("--output", "-o", help="Ausgabedatei")
    test_gen.set_defaults(func=cmd_generate_tests)
    
    # Tutorial commands
    tut_parser = subparsers.add_parser("tutorial", help="Tutorial-Generierung")
    tut_sub = tut_parser.add_subparsers(dest="tut_command")
    
    # tutorial generate
    tut_gen = tut_sub.add_parser("generate", help="Tutorial aus Session generieren")
    tut_gen.add_argument("--session", "-s", required=True, help="Session JSON-Datei")
    tut_gen.add_argument("--output", "-o", help="Ausgabe HTML-Datei")
    tut_gen.add_argument("--title", "-t", help="Tutorial-Titel")
    tut_gen.add_argument("--with-quiz", action="store_true", help="Mit Quiz-Fragen")
    tut_gen.set_defaults(func=cmd_generate_tutorial)
    
    # Process Mining commands
    pm_parser = subparsers.add_parser("pm", help="Process Mining")
    pm_sub = pm_parser.add_subparsers(dest="pm_command")
    
    # pm analyze
    pm_analyze = pm_sub.add_parser("analyze", help="Sessions analysieren")
    pm_analyze.add_argument("--sessions", "-d", required=True, help="Verzeichnis mit Session-Dateien")
    pm_analyze.add_argument("--output", "-o", help="Ausgabedatei")
    pm_analyze.add_argument("--format", "-f", default="mermaid", 
                           choices=["bpmn", "mermaid"], help="Ausgabeformat")
    pm_analyze.set_defaults(func=cmd_process_mining)
    
    # RAG commands
    rag_parser = subparsers.add_parser("rag", help="RAG Q&A")
    rag_sub = rag_parser.add_subparsers(dest="rag_command")
    
    # rag query
    rag_query = rag_sub.add_parser("query", help="Frage stellen")
    rag_query.add_argument("question", help="Die Frage")
    rag_query.add_argument("--storage", "-s", help="KB Speicherort")
    rag_query.add_argument("--lang", "-l", default="de", help="Sprache (de/en)")
    rag_query.set_defaults(func=cmd_rag_query)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

