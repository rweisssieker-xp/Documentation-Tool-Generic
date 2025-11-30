"""
Example: Automated Test Case Generator
Demonstrates how to generate automated tests from documentation.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main example demonstrating test generation."""
    
    print("=" * 60)
    print("🧪 Automated Test Case Generator Example")
    print("=" * 60)
    
    try:
        from src.testgen import TestGenerator, TestFramework
        from src.testgen import SeleniumExporter, PlaywrightExporter, GherkinExporter
        
        print("\n✅ Test-Module geladen")
        
        # Sample session data
        session_data = {
            "session_id": "login_test_001",
            "name": "User Login Workflow",
            "description": "Test der Login-Funktionalität",
            "application": "WebApp",
            "steps": [
                {
                    "id": "step_1",
                    "description": "Öffne die Login-Seite",
                    "window_title": "Login - MyApp",
                    "action_type": "navigate",
                    "selector": "https://app.example.com/login"
                },
                {
                    "id": "step_2",
                    "description": "Klicke auf das Benutzername-Feld",
                    "action_type": "click",
                    "selector": "#username"
                },
                {
                    "id": "step_3",
                    "description": "Gib den Benutzernamen ein",
                    "action_type": "input",
                    "selector": "#username",
                    "input_value": "testuser"
                },
                {
                    "id": "step_4",
                    "description": "Gib das Passwort ein",
                    "action_type": "input",
                    "selector": "#password",
                    "input_value": "testpass123"
                },
                {
                    "id": "step_5",
                    "description": "Klicke auf Login-Button",
                    "action_type": "click",
                    "selector": "#login-btn"
                },
                {
                    "id": "step_6",
                    "description": "Warte auf Dashboard",
                    "action_type": "wait",
                    "selector": "#dashboard",
                    "expected_result": "Dashboard wird angezeigt"
                }
            ]
        }
        
        print(f"\n📋 Session: {session_data['name']}")
        print(f"   Schritte: {len(session_data['steps'])}")
        
        # Initialize Test Generator
        print("\n📦 Initialisiere TestGenerator...")
        generator = TestGenerator()
        
        # Generate test cases
        print("\n🔧 Generiere Testfälle...")
        test_cases = generator.generate_test_cases(session_data)
        print(f"   ✅ {len(test_cases)} Testfälle generiert")
        
        for tc in test_cases:
            print(f"      - {tc.name} ({len(tc.steps)} Schritte)")
        
        # Export to different frameworks
        print("\n📤 Export zu verschiedenen Frameworks:")
        
        # 1. Selenium Python
        print("\n   1️⃣ Selenium (Python):")
        selenium_code = generator.export_test(test_cases[0], TestFramework.SELENIUM)
        print(f"      Generiert: {len(selenium_code)} Zeichen")
        print("      Vorschau:")
        for line in selenium_code.split('\n')[:10]:
            print(f"         {line}")
        print("         ...")
        
        # 2. Playwright Python
        print("\n   2️⃣ Playwright (Python):")
        playwright_code = generator.export_test(test_cases[0], TestFramework.PLAYWRIGHT)
        print(f"      Generiert: {len(playwright_code)} Zeichen")
        print("      Vorschau:")
        for line in playwright_code.split('\n')[:10]:
            print(f"         {line}")
        print("         ...")
        
        # 3. Gherkin/BDD
        print("\n   3️⃣ Gherkin/BDD:")
        gherkin_code = generator.export_test(test_cases[0], TestFramework.GHERKIN)
        print(f"      Generiert: {len(gherkin_code)} Zeichen")
        print("      Vorschau:")
        for line in gherkin_code.split('\n')[:15]:
            print(f"         {line}")
        
        # Using specific exporters
        print("\n\n🔧 Spezialisierte Exporter:")
        
        # German Gherkin
        print("\n   Gherkin (Deutsch):")
        gherkin_de = GherkinExporter(language="de")
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.feature', delete=False) as f:
            content = gherkin_de.export_session(session_data, f.name)
            print(f"      Feature-Datei: {f.name}")
        
        for line in content.split('\n')[:12]:
            print(f"         {line}")
        
        # Selenium Java
        print("\n   Selenium (Java):")
        selenium_java = SeleniumExporter(language="java")
        java_code = selenium_java._generate_java(session_data, "TestLogin")
        print(f"      Generiert: {len(java_code)} Zeichen")
        
        # Playwright TypeScript
        print("\n   Playwright (TypeScript):")
        playwright_ts = PlaywrightExporter(language="typescript")
        ts_code = playwright_ts._generate_typescript(session_data, "login workflow")
        print(f"      Generiert: {len(ts_code)} Zeichen")
        
        print("\n\n✅ Test Generation Beispiel abgeschlossen!")
        print("\nNächste Schritte:")
        print("1. Generierte Tests in Ihr Test-Framework integrieren")
        print("2. Selektoren anpassen für Ihre Anwendung")
        print("3. Assertions hinzufügen für Validierung")
        
    except ImportError as e:
        print(f"\n❌ Modul nicht gefunden: {e}")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

