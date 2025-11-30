"""
Example: Multi-Modal Knowledge Base
Demonstrates how to use the knowledge base for semantic search and Q&A.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main example demonstrating knowledge base usage."""
    
    print("=" * 60)
    print("🧠 Multi-Modal Knowledge Base Example")
    print("=" * 60)
    
    try:
        from src.knowledge import KnowledgeBase
        
        # Create temporary storage
        import tempfile
        storage_dir = tempfile.mkdtemp(prefix="kb_example_")
        
        print(f"\n📁 Speicherort: {storage_dir}")
        
        # Initialize Knowledge Base
        print("\n📦 Initialisiere Knowledge Base...")
        kb = KnowledgeBase(storage_dir=storage_dir)
        print("   ✅ Knowledge Base bereit")
        
        # Add documents
        print("\n📄 Füge Dokumente hinzu...")
        
        doc1 = kb.add_document(
            title="Benutzer anlegen",
            content="""
            So legen Sie einen neuen Benutzer an:
            1. Öffnen Sie die Benutzerverwaltung
            2. Klicken Sie auf 'Neu'
            3. Geben Sie Name und E-Mail ein
            4. Wählen Sie die Berechtigungsgruppe
            5. Klicken Sie auf 'Speichern'
            """,
            doc_type="manual",
            tags=["benutzer", "verwaltung", "anleitung"]
        )
        print(f"   ✅ Dokument 1: {doc1.title}")
        
        doc2 = kb.add_document(
            title="Passwort zurücksetzen",
            content="""
            Um ein Passwort zurückzusetzen:
            1. Gehen Sie zu 'Benutzer bearbeiten'
            2. Klicken Sie auf 'Passwort zurücksetzen'
            3. Das System sendet eine E-Mail mit neuem Passwort
            """,
            doc_type="manual",
            tags=["passwort", "sicherheit", "benutzer"]
        )
        print(f"   ✅ Dokument 2: {doc2.title}")
        
        doc3 = kb.add_document(
            title="Report erstellen",
            content="""
            Zum Erstellen eines Reports:
            1. Wählen Sie 'Reports' im Menü
            2. Klicken Sie auf 'Neuer Report'
            3. Wählen Sie den Berichtstyp
            4. Definieren Sie den Zeitraum
            5. Klicken Sie auf 'Generieren'
            6. Exportieren Sie als PDF oder Excel
            """,
            doc_type="manual",
            tags=["report", "export", "analyse"]
        )
        print(f"   ✅ Dokument 3: {doc3.title}")
        
        # Add a session
        print("\n📋 Füge Session hinzu...")
        
        session_data = {
            "session_id": "sess_001",
            "name": "Login-Workflow",
            "application": "TestApp",
            "steps": [
                {"id": "s1", "title": "App öffnen", "description": "Starten Sie die Anwendung"},
                {"id": "s2", "title": "Login eingeben", "description": "Geben Sie Benutzername und Passwort ein"},
                {"id": "s3", "title": "Anmelden", "description": "Klicken Sie auf Anmelden"}
            ]
        }
        
        docs = kb.add_session(session_data, include_steps=True)
        print(f"   ✅ Session hinzugefügt: {len(docs)} Dokumente")
        
        # Search
        print("\n🔍 Suche...")
        
        queries = [
            "Wie lege ich einen Benutzer an?",
            "Passwort vergessen",
            "Report exportieren"
        ]
        
        for query in queries:
            print(f"\n   Suche: '{query}'")
            results = kb.search(query, limit=3, semantic=False)
            
            for i, result in enumerate(results):
                print(f"      {i+1}. {result.document.title} (Score: {result.score:.2f})")
        
        # Statistics
        print("\n📊 Statistik:")
        stats = kb.get_statistics()
        print(f"   Dokumente: {stats['total_documents']}")
        print(f"   Sessions: {stats['total_sessions']}")
        print(f"   Tags: {stats['unique_tags']}")
        
        # Check for OpenAI for RAG demo
        if os.getenv("OPENAI_API_KEY"):
            print("\n🤖 RAG-Demo (erfordert API-Key)...")
            
            try:
                from src.knowledge import EmbeddingEngine, SemanticSearch, RAGEngine
                
                # Initialize embedding engine
                embedding = EmbeddingEngine(storage_dir=storage_dir + "/embeddings")
                
                # Recreate KB with embeddings
                kb_with_embeddings = KnowledgeBase(
                    storage_dir=storage_dir + "/kb2",
                    embedding_engine=embedding
                )
                
                # Add documents
                for doc in [doc1, doc2, doc3]:
                    kb_with_embeddings.add_document(
                        title=doc.title,
                        content=doc.content,
                        doc_type=doc.doc_type,
                        tags=doc.tags
                    )
                
                # Create semantic search
                search = SemanticSearch(kb_with_embeddings, embedding)
                
                # Create RAG engine
                rag = RAGEngine(search, language="de")
                
                # Ask question
                question = "Wie erstelle ich einen neuen Benutzer?"
                print(f"\n   Frage: {question}")
                
                response = rag.query(question)
                print(f"\n   Antwort: {response.answer[:200]}...")
                print(f"   Konfidenz: {response.confidence:.0%}")
                
            except Exception as e:
                print(f"   ⚠️  RAG-Demo fehlgeschlagen: {e}")
        else:
            print("\n💡 Für RAG-Demo: OPENAI_API_KEY setzen")
        
        print("\n✅ Knowledge Base Beispiel abgeschlossen!")
        
        # Cleanup
        import shutil
        shutil.rmtree(storage_dir, ignore_errors=True)
        
    except ImportError as e:
        print(f"\n❌ Modul nicht gefunden: {e}")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

