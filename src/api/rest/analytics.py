"""
Analytics REST API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.analytics import MetricsCollector, ROICalculator, PredictiveEngine, DashboardAPI
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsAPI:
    """Analytics API"""
    
    def __init__(self):
        self.router = APIRouter()
        self.metrics_collector = MetricsCollector()
        self.roi_calculator = ROICalculator(self.metrics_collector)
        self.predictive_engine = PredictiveEngine(self.metrics_collector)
        self.dashboard_api = DashboardAPI()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes"""
        @self.router.get("/metrics")
        async def get_metrics(days: Optional[int] = Query(None)):
            """Get metrics"""
            try:
                metrics = self.metrics_collector.collect_metrics(days=days)
                return metrics
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/roi")
        async def calculate_roi(days: Optional[int] = Query(None), hourly_rate: float = Query(50.0)):
            """Calculate ROI"""
            try:
                self.roi_calculator.hourly_rate = hourly_rate
                roi = self.roi_calculator.calculate_roi(days=days)
                return {
                    "time_saved_hours": roi.time_saved_hours,
                    "cost_saved": roi.cost_saved,
                    "efficiency_gain": roi.efficiency_gain,
                    "roi_percentage": roi.roi_percentage,
                    "payback_period_days": roi.payback_period_days,
                }
            except Exception as e:
                logger.error(f"Error calculating ROI: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/predictions")
        async def get_predictions():
            """Get predictions"""
            try:
                predictions = self.predictive_engine.generate_predictions()
                return {"predictions": predictions}
            except Exception as e:
                logger.error(f"Error getting predictions: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/dashboard")
        async def get_dashboard(days: Optional[int] = Query(None)):
            """Get dashboard data"""
            try:
                dashboard_data = self.dashboard_api.get_dashboard_data(days=days)
                return dashboard_data
            except Exception as e:
                logger.error(f"Error getting dashboard: {e}")
                raise HTTPException(status_code=500, detail=str(e))

