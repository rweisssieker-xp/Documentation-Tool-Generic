"""
Dashboard API - REST API for ROI dashboard.
Part of Feature: Documentation ROI Dashboard (v2.0)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from src.analytics.metrics_collector import MetricsCollector
from src.analytics.roi_calculator import ROICalculator
from src.analytics.predictive_engine import PredictiveEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DashboardAPI:
    """
    Provides API endpoints for ROI dashboard.
    Can be used by web frontend or other clients.
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        roi_calculator: Optional[ROICalculator] = None
    ):
        """
        Initialize dashboard API.
        
        Args:
            metrics_collector: Optional MetricsCollector instance
            roi_calculator: Optional ROICalculator instance
        """
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.roi_calculator = roi_calculator or ROICalculator(self.metrics_collector)
        self.predictive_engine = PredictiveEngine(self.metrics_collector, self.roi_calculator)
    
    def get_dashboard_data(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get complete dashboard data.
        
        Args:
            days: Optional number of days to analyze
            
        Returns:
            Dashboard data dictionary
        """
        roi = self.roi_calculator.calculate_roi(days)
        time_metrics = self.metrics_collector.get_total_time_saved(days)
        efficiency = self.metrics_collector.get_efficiency_metrics()
        quality_trends = self.metrics_collector.get_quality_trends(days or 30)
        predictions = self.predictive_engine.predict_future_roi(days_ahead=30)
        recommendations = self.predictive_engine.recommend_optimizations()
        
        return {
            'roi': {
                'time_saved_hours': roi.time_saved_hours,
                'cost_saved': roi.cost_saved,
                'efficiency_gain': roi.efficiency_gain,
                'quality_improvement': roi.quality_improvement,
                'roi_percentage': roi.roi_percentage,
                'payback_period_days': roi.payback_period_days
            },
            'time_metrics': time_metrics,
            'efficiency_metrics': efficiency,
            'quality_trends': quality_trends,
            'predictions': predictions,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_dashboard_json(self, output_path: Path, days: Optional[int] = None) -> bool:
        """
        Export dashboard data as JSON.
        
        Args:
            output_path: Output file path
            days: Optional number of days
            
        Returns:
            True if successful
        """
        try:
            data = self.get_dashboard_data(days)
            output_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            return True
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")
            return False

