#!/usr/bin/env python3
"""
Collaboration Demo
Demonstrates real-time collaboration features.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collaboration import CRDTEngine, PresenceManager, CommentSystem
from src.collaboration.crdt_engine import CRDTOperation
from src.collaboration.presence_manager import PresenceType
from src.collaboration.comment_system import Comment, CommentStatus
from datetime import datetime


def main():
    print("=" * 60)
    print("Real-Time Collaboration Hub - Demo")
    print("=" * 60)
    
    # CRDT Engine
    print("\n1. CRDT Engine:")
    crdt = CRDTEngine()
    
    op1 = CRDTOperation(
        id="op-1",
        type="insert",
        position=0,
        content="Hello",
        timestamp=datetime.now(),
        user_id="user-1",
        vector_clock={"user-1": 1}
    )
    
    op2 = CRDTOperation(
        id="op-2",
        type="insert",
        position=5,
        content=" World",
        timestamp=datetime.now(),
        user_id="user-2",
        vector_clock={"user-2": 1}
    )
    
    crdt.apply_operation(op1)
    crdt.apply_operation(op2)
    
    state = crdt.get_state()
    print(f"   Document State: '{state}'")
    print(f"   Operations: {len(crdt.operations)}")
    
    # Presence Manager
    print("\n2. Presence Manager:")
    presence = PresenceManager()
    
    from src.collaboration.presence_manager import UserPresence
    user1 = UserPresence(
        user_id="user-1",
        user_name="Alice",
        presence_type=PresenceType.CURSOR,
        position=(100, 200)
    )
    
    user2 = UserPresence(
        user_id="user-2",
        user_name="Bob",
        presence_type=PresenceType.SELECTION,
        selection=(10, 20)
    )
    
    presence.update_presence(user1)
    presence.update_presence(user2)
    
    all_presences = presence.get_all_presences()
    print(f"   Active Users: {len(all_presences)}")
    for p in all_presences:
        print(f"     - {p.user_name} ({p.presence_type.value})")
    
    # Comment System
    print("\n3. Comment System:")
    comments = CommentSystem()
    
    comment1 = Comment(
        id="comment-1",
        author="Alice",
        content="This section needs clarification",
        position=(5, 10),
        status=CommentStatus.OPEN,
        created_at=datetime.now()
    )
    
    comment2 = Comment(
        id="comment-2",
        author="Bob",
        content="Good point!",
        position=(5, 10),
        status=CommentStatus.OPEN,
        created_at=datetime.now()
    )
    comment2.replies = [comment1]
    
    comments.add_comment(comment1)
    comments.add_comment(comment2)
    
    all_comments = comments.get_comments()
    print(f"   Total Comments: {len(all_comments)}")
    for c in all_comments:
        print(f"     - [{c.status.value}] {c.author}: {c.content[:30]}...")
    
    print("\n" + "=" * 60)
    print("[OK] Collaboration demo completed!")
    print("=" * 60)
    print("\nNote: To start collaboration server, run:")
    print("  python cli/innovation_cli.py collaboration start-server")


if __name__ == "__main__":
    main()

