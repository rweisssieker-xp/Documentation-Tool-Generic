#!/usr/bin/env python3
"""
ROI Analysis Example
Demonstrates ROI calculation and predictive analytics.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics import MetricsCollector, ROICalculator, PredictiveEngine, DashboardAPI
from src.analytics.metrics_collector import DocumentationMetrics


def main():
    print("=" * 60)
    print("Documentation ROI Dashboard - Analysis Example")
    print("=" * 60)
    
    # Initialize components
    collector = MetricsCollector()
    calculator = ROICalculator(collector, hourly_rate=50.0, tool_cost_per_month=0.0)
    predictive = PredictiveEngine(collector, calculator)
    dashboard = DashboardAPI(collector, calculator)
    
    # Simulate some metrics
    print("\n1. Recording Session Metrics...")
    for i in range(5):
        metrics = DocumentationMetrics(
            timestamp=datetime.now() - timedelta(days=i),
            session_id=f"session-{i+1}",
            steps_count=10 + i,
            screenshots_count=5 + i,
            duration_seconds=300.0 + i * 60,
            manual_time_estimate=600.0 + i * 120,
            ai_time_saved=300.0 + i * 60,
            quality_score=80.0 + i * 2,
            completeness_score=85.0 + i * 2
        )
        collector.record_session_metrics(metrics)
    
    print(f"   [OK] {len(collector._metrics)} sessions recorded")
    
    # Calculate ROI
    print("\n2. Calculating ROI...")
    roi = calculator.calculate_roi(days=30)
    
    print(f"   Time Saved:     {roi.time_saved_hours:.1f} hours")
    print(f"   Cost Saved:     {roi.cost_saved:.2f} EUR")
    print(f"   Efficiency:     {roi.efficiency_gain:.1f}%")
    print(f"   Quality Gain:   {roi.quality_improvement:.1f}%")
    print(f"   ROI:            {roi.roi_percentage:.1f}%")
    
    # Efficiency metrics
    print("\n3. Efficiency Metrics:")
    efficiency = collector.get_efficiency_metrics()
    print(f"   Total Sessions:      {efficiency['total_sessions']}")
    print(f"   Total Steps:         {efficiency['total_steps']}")
    print(f"   Avg Steps/Session:   {efficiency['avg_steps_per_session']:.1f}")
    print(f"   Avg Duration:        {efficiency['avg_duration_per_session']:.1f}s")
    
    # Quality trends
    print("\n4. Quality Trends:")
    quality = collector.get_quality_trends(days=30)
    print(f"   Avg Quality:         {quality['avg_quality']:.1f}%")
    print(f"   Avg Completeness:    {quality['avg_completeness']:.1f}%")
    
    # Predictions
    print("\n5. Predictive Analytics:")
    prediction = predictive.predict_future_roi(days_ahead=30)
    print(f"   Predicted Sessions:     {prediction['predicted_sessions']:.0f}")
    print(f"   Predicted Time Saved:   {prediction['predicted_time_saved_hours']:.1f} hours")
    print(f"   Predicted Cost Saved:   {prediction['predicted_cost_saved']:.2f} EUR")
    print(f"   Trend:                  {prediction['trend']}")
    
    # Recommendations
    print("\n6. Recommendations:")
    recommendations = predictive.recommend_optimizations()
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("   No specific recommendations")
    
    # Export dashboard
    print("\n7. Exporting Dashboard...")
    output_path = Path("data/output/roi_dashboard.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if dashboard.export_dashboard_json(output_path):
        print(f"   [OK] Dashboard exported: {output_path}")
    
    print("\n" + "=" * 60)
    print("[OK] ROI analysis completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

