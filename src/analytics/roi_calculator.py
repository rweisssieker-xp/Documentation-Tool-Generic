"""
ROI Calculator - Calculates ROI for documentation efforts.
Part of Feature: Documentation ROI Dashboard (v2.0)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.analytics.metrics_collector import MetricsCollector


@dataclass
class ROIMetrics:
    """ROI calculation results."""
    time_saved_hours: float
    cost_saved: float  # Based on hourly rate
    efficiency_gain: float  # Percentage
    quality_improvement: float  # Percentage
    roi_percentage: float  # ROI %
    payback_period_days: float  # Days to break even


class ROICalculator:
    """
    Calculates ROI for documentation efforts.
    Compares automated vs. manual documentation costs.
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        hourly_rate: float = 50.0,  # Default hourly rate in EUR/USD
        tool_cost_per_month: float = 0.0  # Tool subscription cost
    ):
        """
        Initialize ROI calculator.
        
        Args:
            metrics_collector: MetricsCollector instance
            hourly_rate: Hourly rate for manual documentation
            tool_cost_per_month: Monthly tool cost
        """
        self.metrics_collector = metrics_collector
        self.hourly_rate = hourly_rate
        self.tool_cost_per_month = tool_cost_per_month
    
    def calculate_roi(
        self,
        days: Optional[int] = None,
        include_quality: bool = True
    ) -> ROIMetrics:
        """
        Calculate ROI for documentation efforts.
        
        Args:
            days: Optional number of days to analyze
            include_quality: Whether to include quality improvements
            
        Returns:
            ROIMetrics
        """
        time_metrics = self.metrics_collector.get_total_time_saved(days)
        quality_trends = self.metrics_collector.get_quality_trends(days or 365)
        
        time_saved_hours = time_metrics['total_time_saved_hours']
        cost_saved = time_saved_hours * self.hourly_rate
        
        # Calculate tool cost
        if days:
            tool_cost = (self.tool_cost_per_month / 30) * days
        else:
            # Estimate based on metrics
            oldest_metric = None
            if self.metrics_collector._metrics:
                timestamps = [m.get('timestamp') for m in self.metrics_collector._metrics]
                oldest = min(timestamps)
                if isinstance(oldest, str):
                    oldest_metric = datetime.fromisoformat(oldest)
                else:
                    oldest_metric = oldest
            
            if oldest_metric:
                days_used = (datetime.now() - oldest_metric).days
                tool_cost = (self.tool_cost_per_month / 30) * days_used
            else:
                tool_cost = 0
        
        # Calculate efficiency gain
        manual_time = time_metrics.get('total_manual_hours', 0)
        efficiency_gain = ((manual_time - time_saved_hours) / manual_time * 100) if manual_time > 0 else 0
        
        # Quality improvement
        quality_improvement = 0
        if include_quality and quality_trends.get('avg_quality', 0) > 0:
            # Assume baseline quality of 70% for manual documentation
            baseline_quality = 70.0
            current_quality = quality_trends['avg_quality']
            quality_improvement = ((current_quality - baseline_quality) / baseline_quality * 100) if baseline_quality > 0 else 0
        
        # ROI calculation
        net_savings = cost_saved - tool_cost
        roi_percentage = (net_savings / tool_cost * 100) if tool_cost > 0 else float('inf')
        
        # Payback period (days to break even)
        if net_savings > 0 and time_metrics.get('session_count', 0) > 0:
            avg_daily_savings = net_savings / (days or 30)
            payback_period = tool_cost / avg_daily_savings if avg_daily_savings > 0 else 0
        else:
            payback_period = 0
        
        return ROIMetrics(
            time_saved_hours=time_saved_hours,
            cost_saved=cost_saved,
            efficiency_gain=efficiency_gain,
            quality_improvement=quality_improvement,
            roi_percentage=roi_percentage,
            payback_period_days=payback_period
        )
    
    def calculate_project_roi(
        self,
        project_name: str,
        days: Optional[int] = None
    ) -> ROIMetrics:
        """
        Calculate ROI for a specific project.
        
        Args:
            project_name: Project name
            days: Optional number of days
            
        Returns:
            ROIMetrics
        """
        # Filter metrics by project (would need project field in metrics)
        # For now, use all metrics
        return self.calculate_roi(days)
    
    def generate_roi_report(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate comprehensive ROI report.
        
        Args:
            days: Optional number of days
            
        Returns:
            Report dictionary
        """
        roi = self.calculate_roi(days)
        time_metrics = self.metrics_collector.get_total_time_saved(days)
        efficiency = self.metrics_collector.get_efficiency_metrics()
        
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
            'calculated_at': datetime.now().isoformat()
        }

