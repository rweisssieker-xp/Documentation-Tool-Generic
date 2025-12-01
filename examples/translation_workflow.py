#!/usr/bin/env python3
"""
Translation Workflow Example
Demonstrates complete translation workflow with glossary and review.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.translation import TranslationHub
from src.translation.review_workflow import ReviewStatus


def main():
    print("=" * 60)
    print("Intelligent Translation Hub - Complete Workflow")
    print("=" * 60)
    
    # Initialize hub
    hub = TranslationHub(project_name="demo_project")
    
    # Step 1: Build glossary
    print("\n1. Building Glossary...")
    hub.add_glossary_term("Benutzer", "en", "User", context="UI Element")
    hub.add_glossary_term("Passwort", "en", "Password", context="Security")
    hub.add_glossary_term("Anmelden", "en", "Sign In", context="Action")
    print("   [OK] 3 terms added to glossary")
    
    # Step 2: Translate document
    print("\n2. Translating Document...")
    source_text = """
    Um einen neuen Benutzer anzulegen, klicken Sie auf "Benutzer" 
    im Hauptmenü. Geben Sie dann ein Passwort ein und klicken Sie 
    auf "Anmelden".
    """
    
    translated = hub.translate_document(source_text, "de", "en")
    print(f"   Source (DE): {source_text.strip()[:50]}...")
    print(f"   Target (EN): {translated.strip()[:50]}...")
    
    # Step 3: Save to translation memory
    print("\n3. Saving to Translation Memory...")
    hub.translation_memory.add_translation(
        source_text.strip(),
        translated.strip(),
        "de",
        "en"
    )
    print("   [OK] Translation saved")
    
    # Step 4: Submit for review
    print("\n4. Submitting for Review...")
    import uuid
    review_id = str(uuid.uuid4())[:8]
    hub.review_workflow.submit_for_review(review_id, source_text.strip(), translated.strip())
    print(f"   [OK] Submitted: {review_id}")
    
    # Step 5: Review
    print("\n5. Reviewing Translation...")
    hub.review_workflow.review_translation(review_id, "Reviewer", ReviewStatus.APPROVED)
    print("   [OK] Translation approved")
    
    # Step 6: Statistics
    print("\n6. Statistics:")
    stats = hub.get_translation_statistics()
    print(f"   Translation Memory Units: {stats['translation_memory']['total_units']}")
    print(f"   Glossary Terms: {stats['glossary_terms']}")
    
    print("\n" + "=" * 60)
    print("[OK] Translation workflow completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

