"""
Demo für alle v3.0 Innovation Features
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("AHG Innovation Features v3.0 - Demo")
print("=" * 60)
print()

# 1. API-First Gateway
print("[1] API-First Gateway")
print("-" * 60)
try:
    from src.api import APIGateway
    gateway = APIGateway()
    print("[OK] API Gateway initialized")
    print(f"     Title: {gateway.title}")
    print(f"     Version: {gateway.version}")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# 2. Plugin-System
print("[2] Plugin-System & Marketplace")
print("-" * 60)
try:
    from src.plugins import PluginManager
    manager = PluginManager()
    print("[OK] Plugin Manager initialized")
    plugins = manager.list_plugins()
    print(f"     Loaded plugins: {len(plugins)}")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# 3. Edge AI Engine
print("[3] Edge AI Engine")
print("-" * 60)
try:
    from src.edge_ai import EdgeAIEngine, ModelType
    engine = EdgeAIEngine(model_type=ModelType.LLAMA)
    print("[OK] Edge AI Engine initialized")
    print(f"     Available: {engine.is_available()}")
except Exception as e:
    print(f"[WARN] {e} (Edge AI requires local models)")

print()

# 4. AR Documentation Overlay
print("[4] AR Documentation Overlay")
print("-" * 60)
try:
    from src.ar import AROverlayEngine, ARPlatform
    ar_engine = AROverlayEngine(platform=ARPlatform.VISION_PRO)
    print("[OK] AR Overlay Engine initialized")
except Exception as e:
    print(f"[WARN] {e} (AR requires hardware)")

print()

# 5. Blockchain Audit Trail
print("[5] Blockchain Audit Trail")
print("-" * 60)
try:
    from src.blockchain import BlockchainAuditTrail, BlockchainType
    blockchain = BlockchainAuditTrail(blockchain_type=BlockchainType.POLYGON)
    print("[OK] Blockchain Audit Trail initialized")
    
    # Test hash creation
    test_content = b"Test document content"
    doc_hash = blockchain.create_document_hash(test_content)
    print(f"     Document hash: {doc_hash[:16]}...")
except Exception as e:
    print(f"[WARN] {e} (Blockchain requires network connection)")

print()

# 6. Predictive Documentation Maintenance
print("[6] Predictive Documentation Maintenance")
print("-" * 60)
try:
    from src.predictive import PredictiveMaintenanceEngine
    maintenance = PredictiveMaintenanceEngine()
    print("[OK] Predictive Maintenance Engine initialized")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# 7. Multi-Modal Capture Engine
print("[7] Multi-Modal Capture Engine")
print("-" * 60)
try:
    from src.multimodal import MultiModalCaptureEngine
    capture = MultiModalCaptureEngine()
    print("[OK] Multi-Modal Capture Engine initialized")
    print(f"     Recording: {capture.is_recording()}")
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 60)
print("Demo abgeschlossen!")
print("=" * 60)

