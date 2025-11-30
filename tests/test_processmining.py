"""
Tests for Process Mining Engine Module
"""

import pytest
from unittest.mock import Mock, patch


class TestProcessMiner:
    """Tests for ProcessMiner class."""
    
    def test_process_miner_initialization(self):
        """Test ProcessMiner initialization."""
        from src.processmining.process_miner import ProcessMiner
        
        miner = ProcessMiner(min_support=0.1)
        assert miner.min_support == 0.1
        assert len(miner._cases) == 0
    
    def test_add_session(self):
        """Test adding a session as process case."""
        from src.processmining.process_miner import ProcessMiner
        
        miner = ProcessMiner()
        
        session_data = {
            "session_id": "sess_001",
            "steps": [
                {"action_type": "open"},
                {"action_type": "click"},
                {"action_type": "save"}
            ]
        }
        
        case = miner.add_session(session_data)
        
        assert case.case_id == "sess_001"
        assert len(case.activities) == 3
        assert len(miner._cases) == 1
    
    def test_discover_process(self):
        """Test process discovery."""
        from src.processmining.process_miner import ProcessMiner
        
        miner = ProcessMiner()
        
        # Add multiple sessions
        for i in range(3):
            session_data = {
                "session_id": f"sess_{i}",
                "steps": [
                    {"action_type": "open"},
                    {"action_type": "edit"},
                    {"action_type": "save"}
                ]
            }
            miner.add_session(session_data)
        
        model = miner.discover_process("Test Process")
        
        assert model.name == "Test Process"
        assert len(model.activities) == 3
        assert "open" in model.start_activities
        assert "save" in model.end_activities
    
    def test_get_statistics(self):
        """Test getting mining statistics."""
        from src.processmining.process_miner import ProcessMiner
        
        miner = ProcessMiner()
        
        miner.add_session({
            "session_id": "sess_1",
            "steps": [{"action_type": "action"}]
        })
        
        stats = miner.get_statistics()
        
        assert stats["total_cases"] == 1
        assert stats["total_activities"] == 1


class TestPatternDetector:
    """Tests for PatternDetector class."""
    
    def test_pattern_detector_initialization(self):
        """Test PatternDetector initialization."""
        from src.processmining.pattern_detector import PatternDetector
        
        detector = PatternDetector(min_support=0.1, min_confidence=0.5)
        
        assert detector.min_support == 0.1
        assert detector.min_confidence == 0.5
    
    def test_detect_sequential_patterns(self):
        """Test detecting sequential patterns."""
        from src.processmining.pattern_detector import PatternDetector
        
        detector = PatternDetector(min_support=0.3)
        
        traces = [
            ["A", "B", "C"],
            ["A", "B", "C"],
            ["A", "B", "D"],
            ["X", "Y", "Z"]
        ]
        
        patterns = detector.detect_patterns(traces)
        
        # A->B should be detected as a pattern
        assert any(p.sequence == ["A", "B"] for p in patterns)
    
    def test_find_common_subsequences(self):
        """Test finding common subsequences."""
        from src.processmining.pattern_detector import PatternDetector
        
        detector = PatternDetector(min_support=0.5)
        
        traces = [
            ["A", "B", "C", "D"],
            ["A", "B", "X", "D"],
            ["A", "B", "C", "D"]
        ]
        
        common = detector.find_common_subsequences(traces, min_length=2)
        
        # A->B should be common
        assert any(seq == ["A", "B"] for seq, _ in common)


class TestVariantAnalyzer:
    """Tests for VariantAnalyzer class."""
    
    def test_variant_analyzer_initialization(self):
        """Test VariantAnalyzer initialization."""
        from src.processmining.variant_analyzer import VariantAnalyzer
        
        analyzer = VariantAnalyzer()
        assert analyzer is not None
    
    def test_analyze_variants(self):
        """Test analyzing process variants."""
        from src.processmining.variant_analyzer import VariantAnalyzer
        
        analyzer = VariantAnalyzer()
        
        traces = [
            ["A", "B", "C"],
            ["A", "B", "C"],
            ["A", "X", "C"],
            ["A", "B", "C"]
        ]
        
        variants = analyzer.analyze_variants(traces)
        
        # Should find 2 variants
        assert len(variants) == 2
        
        # Most common should be happy path
        happy_path = [v for v in variants if v.is_happy_path]
        assert len(happy_path) == 1
        assert happy_path[0].trace == ["A", "B", "C"]
    
    def test_compare_variants(self):
        """Test comparing two variants."""
        from src.processmining.variant_analyzer import VariantAnalyzer, ProcessVariant
        
        analyzer = VariantAnalyzer()
        
        variant1 = ProcessVariant(
            id="v1",
            trace=["A", "B", "C"],
            frequency=5,
            percentage=50.0,
            avg_duration=100.0,
            is_happy_path=True,
            deviations=[]
        )
        
        variant2 = ProcessVariant(
            id="v2",
            trace=["A", "X", "C"],
            frequency=3,
            percentage=30.0,
            avg_duration=120.0,
            is_happy_path=False,
            deviations=["Different middle step"]
        )
        
        comparison = analyzer.compare_variants(variant1, variant2)
        
        assert "similarity" in comparison
        assert "common_activities" in comparison
        assert "A" in comparison["common_activities"]
        assert "C" in comparison["common_activities"]
    
    def test_identify_anomalies(self):
        """Test identifying anomalous variants."""
        from src.processmining.variant_analyzer import VariantAnalyzer, ProcessVariant
        
        analyzer = VariantAnalyzer()
        
        variants = [
            ProcessVariant(id="v1", trace=["A", "B"], frequency=90, percentage=90.0, 
                          avg_duration=100, is_happy_path=True, deviations=[]),
            ProcessVariant(id="v2", trace=["A", "X"], frequency=2, percentage=2.0,
                          avg_duration=200, is_happy_path=False, deviations=["Deviation"])
        ]
        
        anomalies = analyzer.identify_anomalies(variants, threshold_percentage=5.0)
        
        assert len(anomalies) == 1
        assert anomalies[0].id == "v2"


class TestBPMNExporter:
    """Tests for BPMNExporter class."""
    
    def test_bpmn_exporter_initialization(self):
        """Test BPMNExporter initialization."""
        from src.processmining.bpmn_exporter import BPMNExporter
        
        exporter = BPMNExporter()
        assert exporter is not None
    
    def test_export_to_mermaid(self):
        """Test Mermaid diagram export."""
        from src.processmining.bpmn_exporter import BPMNExporter
        from src.processmining.process_miner import ProcessModel
        
        exporter = BPMNExporter()
        
        model = ProcessModel(
            id="proc_001",
            name="Test Process",
            activities=["Open", "Edit", "Save"],
            transitions={"Open": ["Edit"], "Edit": ["Save"]},
            start_activities=["Open"],
            end_activities=["Save"],
            frequency={"Open": 10, "Edit": 10, "Save": 10},
            variants=[["Open", "Edit", "Save"]]
        )
        
        mermaid = exporter.export_to_mermaid(model)
        
        assert "graph LR" in mermaid
        assert "Start" in mermaid
        assert "End" in mermaid
        assert "Open" in mermaid


class TestProcessGraph:
    """Tests for ProcessGraph class."""
    
    def test_process_graph_initialization(self):
        """Test ProcessGraph initialization."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph(name="Test Graph")
        
        assert graph.name == "Test Graph"
        assert len(graph.nodes) == 0
    
    def test_add_node(self):
        """Test adding node to graph."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph()
        
        node = graph.add_node("node_1", "Activity 1", "activity", frequency=5)
        
        assert node.id == "node_1"
        assert "node_1" in graph.nodes
    
    def test_add_edge(self):
        """Test adding edge to graph."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph()
        
        graph.add_node("n1", "Node 1", "activity")
        graph.add_node("n2", "Node 2", "activity")
        
        edge = graph.add_edge("n1", "n2", frequency=10)
        
        assert edge is not None
        assert edge.source == "n1"
        assert edge.target == "n2"
    
    def test_get_successors(self):
        """Test getting successor nodes."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph()
        
        graph.add_node("n1", "Node 1", "activity")
        graph.add_node("n2", "Node 2", "activity")
        graph.add_node("n3", "Node 3", "activity")
        
        graph.add_edge("n1", "n2")
        graph.add_edge("n1", "n3")
        
        successors = graph.get_successors("n1")
        
        assert len(successors) == 2
        assert "n2" in successors
        assert "n3" in successors
    
    def test_find_paths(self):
        """Test finding paths between nodes."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph()
        
        graph.add_node("start", "Start", "start")
        graph.add_node("middle", "Middle", "activity")
        graph.add_node("end", "End", "end")
        
        graph.add_edge("start", "middle")
        graph.add_edge("middle", "end")
        
        paths = graph.find_paths("start", "end")
        
        assert len(paths) == 1
        assert paths[0] == ["start", "middle", "end"]
    
    def test_to_dot(self):
        """Test DOT format export."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph(name="Test")
        
        graph.add_node("n1", "Start", "start")
        graph.add_node("n2", "Activity", "activity")
        graph.add_edge("n1", "n2")
        
        dot = graph.to_dot()
        
        assert 'digraph "Test"' in dot
        assert "n1" in dot
        assert "n2" in dot
    
    def test_calculate_metrics(self):
        """Test calculating graph metrics."""
        from src.processmining.process_graph import ProcessGraph
        
        graph = ProcessGraph()
        
        graph.add_node("n1", "Node 1", "activity")
        graph.add_node("n2", "Node 2", "activity")
        graph.add_edge("n1", "n2")
        
        metrics = graph.calculate_metrics()
        
        assert metrics["nodes"] == 2
        assert metrics["edges"] == 1
        assert "density" in metrics

