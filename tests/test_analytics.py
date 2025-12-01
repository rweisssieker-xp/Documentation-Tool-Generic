"""
Tests for Analytics/ROI Dashboard Module
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.analytics.metrics_collector import MetricsCollector, DocumentationMetrics
from src.analytics.roi_calculator import ROICalculator, ROIMetrics
from src.analytics.predictive_engine import PredictiveEngine
from src.analytics.dashboard_api import DashboardAPI
from datetime import datetime


class TestMetricsCollector:
    """Tests for MetricsCollector class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_metrics_collector_initialization(self, temp_storage):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector(storage_dir=temp_storage)
        assert collector.storage_dir == temp_storage
    
    def test_record_session_metrics(self, temp_storage):
        """Test recording session metrics."""
        collector = MetricsCollector(storage_dir=temp_storage)
        
        metrics = DocumentationMetrics(
            timestamp=datetime.now(),
            session_id="test-123",
            steps_count=10,
            screenshots_count=5,
            duration_seconds=300.0,
            manual_time_estimate=600.0,
            ai_time_saved=300.0,
            quality_score=85.0,
            completeness_score=90.0
        )
        
        collector.record_session_metrics(metrics)
        assert len(collector._metrics) == 1
    
    def test_get_total_time_saved(self, temp_storage):
        """Test getting total time saved."""
        collector = MetricsCollector(storage_dir=temp_storage)
        
        metrics = DocumentationMetrics(
            timestamp=datetime.now(),
            session_id="test-123",
            steps_count=10,
            screenshots_count=5,
            duration_seconds=300.0,
            manual_time_estimate=600.0,
            ai_time_saved=300.0,
            quality_score=85.0,
            completeness_score=90.0
        )
        
        collector.record_session_metrics(metrics)
        result = collector.get_total_time_saved()
        
        assert result['total_time_saved_hours'] > 0
        assert result['session_count'] == 1
    
    def test_get_efficiency_metrics(self, temp_storage):
        """Test getting efficiency metrics."""
        collector = MetricsCollector(storage_dir=temp_storage)
        
        metrics = DocumentationMetrics(
            timestamp=datetime.now(),
            session_id="test-123",
            steps_count=10,
            screenshots_count=5,
            duration_seconds=300.0,
            manual_time_estimate=600.0,
            ai_time_saved=300.0,
            quality_score=85.0,
            completeness_score=90.0
        )
        
        collector.record_session_metrics(metrics)
        efficiency = collector.get_efficiency_metrics()
        
        assert efficiency['total_sessions'] == 1
        assert efficiency['total_steps'] == 10


class TestROICalculator:
    """Tests for ROICalculator class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_roi_calculator_initialization(self, temp_storage):
        """Test ROICalculator initialization."""
        collector = MetricsCollector(storage_dir=temp_storage)
        calculator = ROICalculator(collector, hourly_rate=50.0)
        
        assert calculator.hourly_rate == 50.0
        assert calculator.metrics_collector == collector
    
    def test_calculate_roi(self, temp_storage):
        """Test ROI calculation."""
        collector = MetricsCollector(storage_dir=temp_storage)
        calculator = ROICalculator(collector, hourly_rate=50.0)
        
        # Add some metrics
        metrics = DocumentationMetrics(
            timestamp=datetime.now(),
            session_id="test-123",
            steps_count=10,
            screenshots_count=5,
            duration_seconds=300.0,
            manual_time_estimate=600.0,
            ai_time_saved=300.0,
            quality_score=85.0,
            completeness_score=90.0
        )
        collector.record_session_metrics(metrics)
        
        roi = calculator.calculate_roi()
        
        assert isinstance(roi, ROIMetrics)
        assert roi.time_saved_hours >= 0
        assert roi.cost_saved >= 0


class TestPredictiveEngine:
    """Tests for PredictiveEngine class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_predictive_engine_initialization(self, temp_storage):
        """Test PredictiveEngine initialization."""
        collector = MetricsCollector(storage_dir=temp_storage)
        calculator = ROICalculator(collector)
        engine = PredictiveEngine(collector, calculator)
        
        assert engine.metrics_collector == collector
        assert engine.roi_calculator == calculator
    
    def test_predict_future_roi(self, temp_storage):
        """Test future ROI prediction."""
        collector = MetricsCollector(storage_dir=temp_storage)
        calculator = ROICalculator(collector)
        engine = PredictiveEngine(collector, calculator)
        
        prediction = engine.predict_future_roi(days_ahead=30)
        
        assert 'predicted_time_saved_hours' in prediction
        assert 'predicted_cost_saved' in prediction
        assert 'trend' in prediction


class TestDashboardAPI:
    """Tests for DashboardAPI class."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_dashboard_api_initialization(self, temp_storage):
        """Test DashboardAPI initialization."""
        api = DashboardAPI()
        assert api is not None
    
    def test_get_dashboard_data(self, temp_storage):
        """Test getting dashboard data."""
        api = DashboardAPI()
        data = api.get_dashboard_data()
        
        assert 'roi' in data
        assert 'time_metrics' in data
        assert 'efficiency_metrics' in data
        assert 'predictions' in data
    
    def test_export_dashboard_json(self, temp_storage):
        """Test exporting dashboard as JSON."""
        api = DashboardAPI()
        output_path = temp_storage / "dashboard.json"
        
        result = api.export_dashboard_json(output_path)
        assert result == True
        assert output_path.exists()

