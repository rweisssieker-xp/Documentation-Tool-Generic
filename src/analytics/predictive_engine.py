"""
Predictive Engine - AI-powered ROI predictions.
Part of Feature: Documentation ROI Dashboard (v2.0)
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.analytics.metrics_collector import MetricsCollector
from src.analytics.roi_calculator import ROICalculator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictiveEngine:
    """
    Predicts future ROI and efficiency gains using AI.
    Analyzes trends and forecasts outcomes.
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        roi_calculator: ROICalculator
    ):
        """
        Initialize predictive engine.
        
        Args:
            metrics_collector: MetricsCollector instance
            roi_calculator: ROICalculator instance
        """
        self.metrics_collector = metrics_collector
        self.roi_calculator = roi_calculator
        
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = None
                logger.warning("OPENAI_API_KEY not set, predictions will be basic")
        else:
            self.client = None
    
    def predict_future_roi(
        self,
        days_ahead: int = 30,
        current_trend_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict ROI for future period.
        
        Args:
            days_ahead: Number of days to predict ahead
            current_trend_days: Days to analyze for trend
            
        Returns:
            Prediction dictionary
        """
        # Get current metrics
        current_roi = self.roi_calculator.calculate_roi(days=current_trend_days)
        time_metrics = self.metrics_collector.get_total_time_saved(days=current_trend_days)
        efficiency = self.metrics_collector.get_efficiency_metrics()
        
        # Calculate trend
        if time_metrics.get('session_count', 0) > 0:
            avg_daily_sessions = time_metrics['session_count'] / current_trend_days
            avg_daily_time_saved = time_metrics['total_time_saved_hours'] / current_trend_days
        else:
            avg_daily_sessions = 0
            avg_daily_time_saved = 0
        
        # Simple linear projection
        predicted_sessions = avg_daily_sessions * days_ahead
        predicted_time_saved = avg_daily_time_saved * days_ahead
        predicted_cost_saved = predicted_time_saved * self.roi_calculator.hourly_rate
        
        # AI-enhanced prediction if available
        if self.client:
            try:
                ai_prediction = self._ai_predict_roi(
                    current_roi,
                    time_metrics,
                    days_ahead
                )
                if ai_prediction:
                    predicted_time_saved = ai_prediction.get('time_saved', predicted_time_saved)
                    predicted_cost_saved = ai_prediction.get('cost_saved', predicted_cost_saved)
            except Exception as e:
                logger.warning(f"AI prediction failed, using linear projection: {e}")
        
        return {
            'days_ahead': days_ahead,
            'predicted_sessions': predicted_sessions,
            'predicted_time_saved_hours': predicted_time_saved,
            'predicted_cost_saved': predicted_cost_saved,
            'current_daily_average': avg_daily_time_saved,
            'trend': 'increasing' if avg_daily_time_saved > 0 else 'stable'
        }
    
    def _ai_predict_roi(
        self,
        current_roi: Any,
        time_metrics: Dict[str, Any],
        days_ahead: int
    ) -> Optional[Dict[str, Any]]:
        """Use AI to predict ROI."""
        try:
            prompt = f"""Based on these documentation metrics, predict ROI for the next {days_ahead} days:

Current Metrics:
- Time saved: {time_metrics.get('total_time_saved_hours', 0):.1f} hours
- Sessions: {time_metrics.get('session_count', 0)}
- Avg time saved per session: {time_metrics.get('avg_time_saved_per_session', 0):.2f} hours
- Current ROI: {current_roi.roi_percentage:.1f}%

Predict:
1. Expected time saved in next {days_ahead} days
2. Expected cost savings
3. Trend (increasing/stable/decreasing)

Return JSON with: time_saved, cost_saved, trend"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst specializing in ROI predictions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in AI prediction: {e}")
            return None
    
    def recommend_optimizations(self) -> List[str]:
        """
        Recommend optimizations based on metrics.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        efficiency = self.metrics_collector.get_efficiency_metrics()
        quality_trends = self.metrics_collector.get_quality_trends(30)
        
        # Check efficiency
        if efficiency.get('avg_steps_per_session', 0) < 5:
            recommendations.append("Consider documenting more comprehensive workflows (currently averaging <5 steps per session)")
        
        # Check quality
        avg_quality = quality_trends.get('avg_quality', 0)
        if avg_quality < 80:
            recommendations.append(f"Quality score is {avg_quality:.1f}%. Review documentation for completeness and clarity.")
        
        # Check usage
        if efficiency.get('total_sessions', 0) < 10:
            recommendations.append("Low session count. Consider training team on documentation best practices.")
        
        return recommendations

