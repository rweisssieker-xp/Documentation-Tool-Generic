"""
Tests for Smart Context Capture Module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestContextCollector:
    """Tests for ContextCollector class."""
    
    def test_context_collector_initialization(self):
        """Test ContextCollector initialization."""
        from src.context.context_collector import ContextCollector
        
        collector = ContextCollector()
        assert collector.history_size == 10
    
    def test_collect_context(self):
        """Test collecting context."""
        from src.context.context_collector import ContextCollector
        
        collector = ContextCollector()
        
        context = collector.collect_context(
            step_id="step_001",
            window_title="Test Window"
        )
        
        assert context.step_id == "step_001"
        assert context.window_context["title"] == "Test Window"
    
    def test_record_action(self):
        """Test recording action history."""
        from src.context.context_collector import ContextCollector
        
        collector = ContextCollector(history_size=3)
        
        collector.record_action("action1")
        collector.record_action("action2")
        collector.record_action("action3")
        collector.record_action("action4")
        
        # Should only keep last 3
        assert len(collector._action_history) == 3
        assert collector._action_history[0] == "action2"
    
    def test_get_context_summary(self):
        """Test getting context summary."""
        from src.context.context_collector import ContextCollector
        
        collector = ContextCollector()
        
        collector.collect_context("step_1", window_title="My Window")
        
        summary = collector.get_context_summary("step_1")
        
        assert "window" in summary
        assert summary["window"] == "My Window"


class TestClipboardMonitor:
    """Tests for ClipboardMonitor class."""
    
    @patch('src.context.clipboard_monitor.PYPERCLIP_AVAILABLE', True)
    @patch('src.context.clipboard_monitor.pyperclip')
    def test_clipboard_monitor_initialization(self, mock_pyperclip):
        """Test ClipboardMonitor initialization."""
        from src.context.clipboard_monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor(history_size=10)
        assert monitor.history_size == 10
        assert monitor.is_monitoring() == False
    
    @patch('src.context.clipboard_monitor.PYPERCLIP_AVAILABLE', True)
    @patch('src.context.clipboard_monitor.pyperclip')
    def test_get_current(self, mock_pyperclip):
        """Test getting current clipboard content."""
        from src.context.clipboard_monitor import ClipboardMonitor
        
        mock_pyperclip.paste.return_value = "Test clipboard content"
        
        monitor = ClipboardMonitor()
        content = monitor.get_current()
        
        assert content == "Test clipboard content"
    
    @patch('src.context.clipboard_monitor.PYPERCLIP_AVAILABLE', True)
    @patch('src.context.clipboard_monitor.pyperclip')
    def test_get_history(self, mock_pyperclip):
        """Test getting clipboard history."""
        from src.context.clipboard_monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor()
        
        history = monitor.get_history()
        assert isinstance(history, list)
    
    @patch('src.context.clipboard_monitor.PYPERCLIP_AVAILABLE', False)
    def test_get_current_unavailable(self):
        """Test when pyperclip is unavailable."""
        from src.context.clipboard_monitor import ClipboardMonitor
        
        monitor = ClipboardMonitor()
        content = monitor.get_current()
        
        assert content is None


class TestTabTracker:
    """Tests for TabTracker class."""
    
    def test_tab_tracker_initialization(self):
        """Test TabTracker initialization."""
        from src.context.tab_tracker import TabTracker
        
        tracker = TabTracker()
        assert tracker is not None
    
    def test_get_active_tabs(self):
        """Test getting active tabs."""
        from src.context.tab_tracker import TabTracker
        
        tracker = TabTracker()
        
        tabs = tracker.get_active_tabs()
        assert isinstance(tabs, list)
    
    def test_supported_browsers(self):
        """Test supported browser list."""
        from src.context.tab_tracker import TabTracker
        
        tracker = TabTracker()
        
        assert "chrome.exe" in tracker.SUPPORTED_BROWSERS
        assert "firefox.exe" in tracker.SUPPORTED_BROWSERS
        assert "msedge.exe" in tracker.SUPPORTED_BROWSERS


class TestIntentAnalyzer:
    """Tests for IntentAnalyzer class."""
    
    def test_intent_analyzer_initialization(self):
        """Test IntentAnalyzer initialization."""
        from src.context.intent_analyzer import IntentAnalyzer
        
        analyzer = IntentAnalyzer(use_ai=False)
        assert analyzer.use_ai == False
    
    def test_analyze_data_entry_intent(self):
        """Test analyzing data entry intent."""
        from src.context.intent_analyzer import IntentAnalyzer, IntentCategory
        
        analyzer = IntentAnalyzer(use_ai=False)
        
        context = {
            "window": {"title": "Form Input"},
            "history": ["enter username", "type password"]
        }
        
        intent = analyzer.analyze(context)
        
        assert intent.category == IntentCategory.DATA_ENTRY
    
    def test_analyze_navigation_intent(self):
        """Test analyzing navigation intent."""
        from src.context.intent_analyzer import IntentAnalyzer, IntentCategory
        
        analyzer = IntentAnalyzer(use_ai=False)
        
        context = {
            "window": {"title": "Menu"},
            "history": ["click menu", "open settings"]
        }
        
        intent = analyzer.analyze(context)
        
        assert intent.category == IntentCategory.NAVIGATION


class TestContextCloud:
    """Tests for ContextCloud class."""
    
    def test_context_cloud_initialization(self):
        """Test ContextCloud initialization."""
        from src.context.context_cloud import ContextCloud
        
        cloud = ContextCloud(step_id="step_1", timestamp=datetime.now())
        
        assert cloud.step_id == "step_1"
        assert len(cloud.nodes) == 0
    
    def test_add_node(self):
        """Test adding node to cloud."""
        from src.context.context_cloud import ContextCloud
        
        cloud = ContextCloud(step_id="step_1", timestamp=datetime.now())
        
        node = cloud.add_node(
            node_id="node_1",
            node_type="window",
            label="Test Window",
            weight=1.0
        )
        
        assert node.id == "node_1"
        assert "node_1" in cloud.nodes
    
    def test_connect_nodes(self):
        """Test connecting nodes."""
        from src.context.context_cloud import ContextCloud
        
        cloud = ContextCloud(step_id="step_1", timestamp=datetime.now())
        
        cloud.add_node("node_1", "window", "Window 1")
        cloud.add_node("node_2", "action", "Action 1")
        
        result = cloud.connect("node_1", "node_2")
        
        assert result == True
        assert "node_2" in cloud.nodes["node_1"].connections
    
    def test_to_mermaid(self):
        """Test Mermaid diagram generation."""
        from src.context.context_cloud import ContextCloud
        
        cloud = ContextCloud(step_id="step_1", timestamp=datetime.now())
        
        cloud.add_node("window", "window", "Main Window")
        cloud.add_node("action", "action", "Click Button")
        cloud.connect("window", "action")
        
        mermaid = cloud.to_mermaid()
        
        assert "graph LR" in mermaid
        assert "window" in mermaid
    
    def test_context_cloud_builder(self):
        """Test ContextCloudBuilder."""
        from src.context.context_cloud import ContextCloudBuilder
        
        builder = ContextCloudBuilder()
        
        context_data = {
            "window": {"title": "Test Window", "process": "test.exe"},
            "history": ["action1", "action2"],
            "clipboard": "Test content"
        }
        
        cloud = builder.build_from_context("step_1", context_data)
        
        assert cloud.step_id == "step_1"
        assert len(cloud.nodes) > 0

