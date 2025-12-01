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


def cmd_gitops_init(args):
    """Initialize Git repository for documentation."""
    from src.gitops import GitManager, GitConfig
    from pathlib import Path
    
    config = GitConfig(
        repo_path=Path(args.repo_path),
        remote_url=args.remote_url or None,
        branch=args.branch,
        author_name=args.author_name,
        author_email=args.author_email
    )
    
    manager = GitManager(config)
    print(f"✅ Git Repository initialisiert: {args.repo_path}")
    
    status = manager.status()
    print(f"   Branch: {status.get('current_branch', 'N/A')}")


def cmd_gitops_sync(args):
    """Sync documentation to Git."""
    from src.gitops import GitManager, GitConfig, RepositorySync, SyncConfig
    from pathlib import Path
    
    git_config = GitConfig(repo_path=Path(args.repo_path))
    git_manager = GitManager(git_config)
    
    sync_config = SyncConfig(auto_sync=True)
    sync = RepositorySync(git_manager, sync_config)
    
    # Get files to sync
    if args.files:
        files = args.files.split(",")
    else:
        # Auto-detect changed files
        status = git_manager.status()
        files = status.get("modified_files", []) + status.get("untracked_files", [])
    
    if not files:
        print("⚠️  Keine Dateien zum Synchronisieren gefunden")
        return
    
    result = sync.sync_to_git(files, commit_message=args.message)
    
    if result:
        print(f"✅ {len(files)} Dateien synchronisiert")
        if args.push:
            if git_manager.push():
                print("✅ Zu Remote gepusht")
    else:
        print("❌ Synchronisation fehlgeschlagen")


def cmd_gitops_status(args):
    """Show Git repository status."""
    from src.gitops import GitManager, GitConfig
    from pathlib import Path
    
    git_config = GitConfig(repo_path=Path(args.repo_path))
    git_manager = GitManager(git_config)
    
    status = git_manager.status()
    sync_status = None
    
    if args.sync:
        from src.gitops import RepositorySync
        sync = RepositorySync(git_manager)
        sync_status = sync.get_sync_status()
    
    print("\n📊 Git Repository Status")
    print("=" * 40)
    print(f"Branch: {status.get('current_branch', 'N/A')}")
    print(f"Last Commit: {status.get('last_commit', 'Keine Commits')}")
    print(f"Modified: {len(status.get('modified_files', []))}")
    print(f"Untracked: {len(status.get('untracked_files', []))}")
    print(f"Is Dirty: {status.get('is_dirty', False)}")
    
    if sync_status:
        print("\n📡 Sync Status")
        print("=" * 40)
        print(f"Last Sync: {sync_status.get('last_sync', 'Nie')}")
        print(f"Last Pull: {sync_status.get('last_pull', 'Nie')}")
        print(f"Last Push: {sync_status.get('last_push', 'Nie')}")
        print(f"Pending Changes: {sync_status.get('pending_changes', 0)}")


def cmd_translation_translate(args):
    """Translate text or file."""
    from src.translation import TranslationHub
    
    hub = TranslationHub(project_name=args.project)
    
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
    elif args.text:
        content = args.text
    else:
        print("Fehler: --file oder --text erforderlich")
        return
    
    translated = hub.translate_document(content, args.source, args.target)
    print(f"\nÜbersetzung ({args.source} -> {args.target}):")
    print("=" * 60)
    print(translated)
    print("=" * 60)


def cmd_translation_glossary_add(args):
    """Add glossary term."""
    from src.translation import TranslationHub
    
    hub = TranslationHub(project_name=args.project)
    hub.add_glossary_term(args.term, args.language, args.value)
    print(f"Begriff hinzugefügt: {args.term} -> {args.value} ({args.language})")


def cmd_translation_memory(args):
    """Search translation memory."""
    from src.translation import TranslationMemory
    
    tm = TranslationMemory()
    
    if args.search:
        matches = tm.find_fuzzy_match(args.search, args.source, args.target)
        print(f"\n{len(matches)} Treffer für '{args.search}':\n")
        for unit, similarity in matches[:10]:
            print(f"  [{similarity:.0%}] {unit.source_text[:50]}...")
            print(f"       -> {unit.target_text[:50]}...")
            print()
    else:
        stats = tm.get_statistics()
        print(f"\nTranslation Memory Statistiken:")
        print(f"  Total Units: {stats['total_units']}")
        print(f"  Total Usage: {stats['total_usage']}")
        print(f"  Avg Quality: {stats['avg_quality']:.2f}")


def cmd_collaboration_start(args):
    """Start collaboration server."""
    from src.collaboration import RealtimeServer
    
    server = RealtimeServer(port=args.port)
    
    if not server.app:
        print("Fehler: FastAPI nicht verfügbar. Installieren Sie: pip install fastapi uvicorn")
        return
    
    print(f"Server startet auf Port {args.port}...")
    print(f"WebSocket Endpoint: ws://localhost:{args.port}/ws")
    print("Drücken Sie Ctrl+C zum Beenden")
    
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=args.port)


def cmd_agent_execute(args):
    """Execute autonomous agent task."""
    from src.agent import AutonomousAgent
    
    agent = AutonomousAgent()
    
    if not agent.client:
        print("Fehler: OPENAI_API_KEY nicht gesetzt")
        return
    
    print(f"Agent startet...")
    print(f"Goal: {args.goal}")
    print(f"Max Steps: {args.max_steps}")
    print("-" * 60)
    
    steps = agent.execute_task(args.goal, max_steps=args.max_steps)
    
    print("-" * 60)
    print(f"Agent abgeschlossen. {len(steps)} Steps ausgeführt.\n")
    
    for i, step in enumerate(steps, 1):
        print(f"Step {i}: {step.get('action', 'N/A')}")
        print(f"  Result: {step.get('result', 'N/A')}")
        print(f"  Success: {step.get('success', False)}")
        print()


def cmd_agent_status(args):
    """Show agent status."""
    from src.agent import AutonomousAgent
    
    agent = AutonomousAgent()
    
    print("\nAgent Status:")
    print(f"  Tools verfügbar: {agent.tool_executor.available}")
    print(f"  AI verfügbar: {agent.client is not None}")
    print(f"  Model: {agent.model}")


def cmd_video_generate(args):
    """Generate video tutorial."""
    from src.video import VideoSynthesizer, VideoConfig
    from pathlib import Path
    import json
    
    config = VideoConfig(
        frame_rate=args.fps,
        language=args.language
    )
    synthesizer = VideoSynthesizer(config)
    
    session_data = {}
    screenshot_paths = []
    
    if args.session:
        session_file = Path(args.session)
        if session_file.exists():
            session_data = json.loads(session_file.read_text(encoding='utf-8'))
            # Extract screenshot paths
            steps = session_data.get('steps', [])
            screenshot_paths = [Path(s.get('screenshot_path', '')) for s in steps if s.get('screenshot_path')]
    
    output_path = Path(args.output)
    
    print(f"Video-Generierung startet...")
    print(f"  Output: {output_path}")
    print(f"  FPS: {args.fps}")
    print(f"  Sprache: {args.language}")
    
    success = synthesizer.generate_video(session_data, screenshot_paths, output_path)
    
    if success:
        print(f"\nVideo erfolgreich generiert: {output_path}")
    else:
        print("\nVideo-Generierung fehlgeschlagen")


def cmd_roi_calculate(args):
    """Calculate ROI."""
    from src.analytics import MetricsCollector, ROICalculator
    
    collector = MetricsCollector()
    calculator = ROICalculator(collector, hourly_rate=args.hourly_rate)
    
    roi = calculator.calculate_roi(days=args.days)
    
    print("\nROI Berechnung:")
    print("=" * 60)
    print(f"Zeit gespart:     {roi.time_saved_hours:.1f} Stunden")
    print(f"Kosten gespart:   {roi.cost_saved:.2f} EUR")
    print(f"Effizienz-Gewinn: {roi.efficiency_gain:.1f}%")
    print(f"ROI:              {roi.roi_percentage:.1f}%")
    if roi.payback_period_days > 0:
        print(f"Amortisationszeit: {roi.payback_period_days:.1f} Tage")
    print("=" * 60)


def cmd_roi_export(args):
    """Export ROI dashboard."""
    from src.analytics import DashboardAPI
    from pathlib import Path
    
    api = DashboardAPI()
    output_path = Path(args.output)
    
    if args.format == "json":
        success = api.export_dashboard_json(output_path, days=args.days)
    else:
        print("HTML Export noch nicht implementiert")
        return
    
    if success:
        print(f"ROI Dashboard exportiert: {output_path}")
    else:
        print("Export fehlgeschlagen")


def cmd_a11y_audit(args):
    """Audit accessibility."""
    from src.accessibility import WCAGAuditor, WCAGLevel
    from pathlib import Path
    
    level_map = {"A": WCAGLevel.A, "AA": WCAGLevel.AA, "AAA": WCAGLevel.AAA}
    auditor = WCAGAuditor(level=level_map.get(args.level, WCAGLevel.AA))
    
    file_path = Path(args.file)
    result = auditor.audit_file(file_path)
    
    print(f"\nWCAG {args.level} Audit für {args.file}:")
    print("=" * 60)
    print(f"Score: {result.score:.1f}%")
    print(f"Violations: {len(result.violations)}")
    print(f"Passes: {result.passes}")
    print("\nViolations:")
    for v in result.violations[:10]:
        print(f"  [{v.impact.upper()}] {v.rule_id}: {v.description}")


def cmd_a11y_fix(args):
    """Fix accessibility issues."""
    from src.accessibility import WCAGAuditor, WCAGLevel, AutoRemediation
    from pathlib import Path
    
    file_path = Path(args.file)
    
    auditor = WCAGAuditor(level=WCAGLevel.AA)
    result = auditor.audit_file(file_path)
    
    if not result.violations:
        print("Keine Violations gefunden")
        return
    
    remediation = AutoRemediation()
    html_content = file_path.read_text(encoding='utf-8')
    
    fixed_html = remediation.remediate_html(html_content, result.violations)
    
    backup_path = file_path.with_suffix('.html.backup')
    file_path.rename(backup_path)
    file_path.write_text(fixed_html, encoding='utf-8')
    
    print(f"Datei korrigiert: {file_path}")
    print(f"Backup: {backup_path}")


def cmd_a11y_report(args):
    """Generate accessibility report."""
    from src.accessibility import WCAGAuditor, WCAGLevel, StructureValidator, ComplianceReportGenerator
    from pathlib import Path
    
    file_path = Path(args.file)
    
    auditor = WCAGAuditor(level=WCAGLevel.AA)
    audit_result = auditor.audit_file(file_path)
    
    validator = StructureValidator()
    html_content = file_path.read_text(encoding='utf-8')
    structure_issues = validator.validate(html_content)
    
    generator = ComplianceReportGenerator()
    report = generator.generate_report(audit_result, structure_issues, str(file_path))
    
    output_path = Path(args.output) if args.output else file_path.with_suffix(f'.{args.format}')
    
    if args.format == "json":
        generator.export_json(report, output_path)
    else:
        generator.export_html(report, output_path)
    
    print(f"Report generiert: {output_path}")
    print(f"Compliant: {report.compliant}")
    print(f"Score: {report.score:.1f}%")


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
  
  # GitOps
  python cli/innovation_cli.py gitops init -p ./docs --remote-url https://github.com/user/repo.git
  python cli/innovation_cli.py gitops sync -p ./docs --push
  python cli/innovation_cli.py gitops status -p ./docs
  
  # Translation
  python cli/innovation_cli.py translation translate --text "Hallo Welt" -s de -t en
  python cli/innovation_cli.py translation glossary add -t "Benutzer" -l en -v "User"
  
  # Collaboration
  python cli/innovation_cli.py collaboration start-server --port 8765
  
  # Agent
  python cli/innovation_cli.py agent execute --goal "Dokumentiere Login-Prozess"
  
  # Video
  python cli/innovation_cli.py video generate -s session.json -o tutorial.mp4
  
  # ROI
  python cli/innovation_cli.py roi calculate --days 30
  python cli/innovation_cli.py roi export -o dashboard.json
  
  # Accessibility
  python cli/innovation_cli.py a11y audit -f doc.html
  python cli/innovation_cli.py a11y fix -f doc.html --auto
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
    
    # GitOps commands
    gitops_parser = subparsers.add_parser("gitops", help="GitOps Documentation Pipeline")
    gitops_sub = gitops_parser.add_subparsers(dest="gitops_command")
    
    # gitops init
    gitops_init = gitops_sub.add_parser("init", help="Git Repository initialisieren")
    gitops_init.add_argument("--repo-path", "-p", required=True, help="Repository-Pfad")
    gitops_init.add_argument("--remote-url", "-r", help="Remote URL")
    gitops_init.add_argument("--branch", "-b", default="main", help="Branch")
    gitops_init.add_argument("--author-name", default="AHG Documentation Tool", help="Autor Name")
    gitops_init.add_argument("--author-email", default="ahg@example.com", help="Autor E-Mail")
    gitops_init.set_defaults(func=cmd_gitops_init)
    
    # gitops sync
    gitops_sync = gitops_sub.add_parser("sync", help="Zu Git synchronisieren")
    gitops_sync.add_argument("--repo-path", "-p", required=True, help="Repository-Pfad")
    gitops_sync.add_argument("--files", "-f", help="Dateien (kommasepariert)")
    gitops_sync.add_argument("--message", "-m", help="Commit-Message")
    gitops_sync.add_argument("--push", action="store_true", help="Nach Commit pushen")
    gitops_sync.set_defaults(func=cmd_gitops_sync)
    
    # gitops status
    gitops_status = gitops_sub.add_parser("status", help="Repository-Status anzeigen")
    gitops_status.add_argument("--repo-path", "-p", required=True, help="Repository-Pfad")
    gitops_status.add_argument("--sync", "-s", action="store_true", help="Sync-Status anzeigen")
    gitops_status.set_defaults(func=cmd_gitops_status)
    
    # Translation commands
    translation_parser = subparsers.add_parser("translation", help="Intelligent Translation Hub")
    trans_sub = translation_parser.add_subparsers(dest="translation_command")
    
    # translation translate
    trans_translate = trans_sub.add_parser("translate", help="Text übersetzen")
    trans_translate.add_argument("--file", "-f", help="Datei zum Übersetzen")
    trans_translate.add_argument("--source", "-s", default="de", help="Quellsprache")
    trans_translate.add_argument("--target", "-t", default="en", help="Zielsprache")
    trans_translate.add_argument("--text", help="Text direkt (statt Datei)")
    trans_translate.add_argument("--project", "-p", default="default", help="Projektname")
    trans_translate.set_defaults(func=cmd_translation_translate)
    
    # translation glossary
    trans_glossary = trans_sub.add_parser("glossary", help="Glossar-Verwaltung")
    trans_glossary_sub = trans_glossary.add_subparsers(dest="glossary_command")
    
    trans_glossary_add = trans_glossary_sub.add_parser("add", help="Begriff hinzufügen")
    trans_glossary_add.add_argument("--term", "-t", required=True, help="Quellbegriff")
    trans_glossary_add.add_argument("--language", "-l", required=True, help="Zielsprache")
    trans_glossary_add.add_argument("--value", "-v", required=True, help="Übersetzung")
    trans_glossary_add.add_argument("--project", "-p", default="default", help="Projektname")
    trans_glossary_add.set_defaults(func=cmd_translation_glossary_add)
    
    # translation memory
    trans_memory = trans_sub.add_parser("memory", help="Translation Memory")
    trans_memory.add_argument("search", nargs="?", help="Suchbegriff")
    trans_memory.add_argument("--source", "-s", default="de", help="Quellsprache")
    trans_memory.add_argument("--target", "-t", default="en", help="Zielsprache")
    trans_memory.set_defaults(func=cmd_translation_memory)
    
    # Collaboration commands
    collab_parser = subparsers.add_parser("collaboration", help="Real-Time Collaboration")
    collab_sub = collab_parser.add_subparsers(dest="collaboration_command")
    
    collab_start = collab_sub.add_parser("start-server", help="Server starten")
    collab_start.add_argument("--port", "-p", type=int, default=8765, help="Port")
    collab_start.set_defaults(func=cmd_collaboration_start)
    
    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Autonomous Documentation Agent")
    agent_sub = agent_parser.add_subparsers(dest="agent_command")
    
    agent_execute = agent_sub.add_parser("execute", help="Task ausführen")
    agent_execute.add_argument("--goal", "-g", required=True, help="Task-Goal")
    agent_execute.add_argument("--max-steps", "-m", type=int, default=20, help="Maximale Steps")
    agent_execute.set_defaults(func=cmd_agent_execute)
    
    agent_status = agent_sub.add_parser("status", help="Agent-Status")
    agent_status.set_defaults(func=cmd_agent_status)
    
    # Video commands
    video_parser = subparsers.add_parser("video", help="Video Tutorial Synthesizer")
    video_sub = video_parser.add_subparsers(dest="video_command")
    
    video_generate = video_sub.add_parser("generate", help="Video generieren")
    video_generate.add_argument("--session", "-s", help="Session-Datei")
    video_generate.add_argument("--output", "-o", required=True, help="Ausgabedatei")
    video_generate.add_argument("--fps", type=int, default=30, help="Frame Rate")
    video_generate.add_argument("--language", "-l", default="de", help="Sprache")
    video_generate.set_defaults(func=cmd_video_generate)
    
    # ROI commands
    roi_parser = subparsers.add_parser("roi", help="ROI Dashboard")
    roi_sub = roi_parser.add_subparsers(dest="roi_command")
    
    roi_calculate = roi_sub.add_parser("calculate", help="ROI berechnen")
    roi_calculate.add_argument("--days", "-d", type=int, help="Anzahl Tage")
    roi_calculate.add_argument("--hourly-rate", type=float, default=50.0, help="Stundensatz")
    roi_calculate.set_defaults(func=cmd_roi_calculate)
    
    roi_export = roi_sub.add_parser("export", help="ROI exportieren")
    roi_export.add_argument("--format", "-f", default="json", choices=["json", "html"], help="Format")
    roi_export.add_argument("--output", "-o", required=True, help="Ausgabedatei")
    roi_export.add_argument("--days", "-d", type=int, help="Anzahl Tage")
    roi_export.set_defaults(func=cmd_roi_export)
    
    # Accessibility commands
    a11y_parser = subparsers.add_parser("a11y", help="Accessibility Compliance")
    a11y_sub = a11y_parser.add_subparsers(dest="a11y_command")
    
    a11y_audit = a11y_sub.add_parser("audit", help="WCAG Audit durchführen")
    a11y_audit.add_argument("--file", "-f", required=True, help="HTML-Datei")
    a11y_audit.add_argument("--level", "-l", default="AA", choices=["A", "AA", "AAA"], help="WCAG Level")
    a11y_audit.set_defaults(func=cmd_a11y_audit)
    
    a11y_fix = a11y_sub.add_parser("fix", help="Automatisch korrigieren")
    a11y_fix.add_argument("--file", "-f", required=True, help="HTML-Datei")
    a11y_fix.add_argument("--auto", action="store_true", help="Automatisch korrigieren")
    a11y_fix.set_defaults(func=cmd_a11y_fix)
    
    a11y_report = a11y_sub.add_parser("report", help="Report generieren")
    a11y_report.add_argument("--file", "-f", required=True, help="HTML-Datei")
    a11y_report.add_argument("--format", choices=["json", "html"], default="html", help="Format")
    a11y_report.add_argument("--output", "-o", help="Ausgabedatei")
    a11y_report.set_defaults(func=cmd_a11y_report)
    
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

