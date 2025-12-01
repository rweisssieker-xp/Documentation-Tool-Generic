"""
ROI Dashboard - GUI for Documentation ROI metrics.
Part of Feature: Documentation ROI Dashboard (v2.0)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from src.analytics import MetricsCollector, ROICalculator, DashboardAPI
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ROIDashboard:
    """Dashboard for displaying ROI metrics."""
    
    def __init__(self, parent):
        """
        Initialize ROI dashboard.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Documentation ROI Dashboard")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self.metrics_collector = MetricsCollector()
        self.roi_calculator = ROICalculator(self.metrics_collector)
        self.dashboard_api = DashboardAPI(self.metrics_collector, self.roi_calculator)
        
        self._create_widgets()
        self._refresh_data()
    
    def _create_widgets(self):
        """Create dashboard widgets."""
        # Header
        header_frame = ttk.Frame(self.dialog)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="📊 Documentation ROI Dashboard", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Aktualisieren", command=self._refresh_data).pack(side=tk.RIGHT, padx=5)
        
        # Time period selector
        period_frame = ttk.Frame(self.dialog)
        period_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(period_frame, text="Zeitraum:").pack(side=tk.LEFT, padx=5)
        self.period_var = tk.IntVar(value=30)
        ttk.Radiobutton(period_frame, text="7 Tage", variable=self.period_var, value=7, command=self._refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="30 Tage", variable=self.period_var, value=30, command=self._refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="90 Tage", variable=self.period_var, value=90, command=self._refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="Alle", variable=self.period_var, value=0, command=self._refresh_data).pack(side=tk.LEFT, padx=5)
        
        # Main content notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ROI Overview tab
        roi_frame = ttk.Frame(notebook)
        notebook.add(roi_frame, text="ROI Übersicht")
        self.roi_text = tk.Text(roi_frame, wrap=tk.WORD, font=("Courier", 10))
        self.roi_text.pack(fill=tk.BOTH, expand=True)
        
        # Efficiency tab
        efficiency_frame = ttk.Frame(notebook)
        notebook.add(efficiency_frame, text="Effizienz")
        self.efficiency_text = tk.Text(efficiency_frame, wrap=tk.WORD, font=("Courier", 10))
        self.efficiency_text.pack(fill=tk.BOTH, expand=True)
        
        # Predictions tab
        predictions_frame = ttk.Frame(notebook)
        notebook.add(predictions_frame, text="Vorhersagen")
        self.predictions_text = tk.Text(predictions_frame, wrap=tk.WORD, font=("Courier", 10))
        self.predictions_text.pack(fill=tk.BOTH, expand=True)
        
        # Recommendations tab
        rec_frame = ttk.Frame(notebook)
        notebook.add(rec_frame, text="Empfehlungen")
        self.rec_text = tk.Text(rec_frame, wrap=tk.WORD, font=("Courier", 10))
        self.rec_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Exportieren...", command=self._export_dashboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Schließen", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _refresh_data(self):
        """Refresh dashboard data."""
        try:
            days = self.period_var.get() if self.period_var.get() > 0 else None
            data = self.dashboard_api.get_dashboard_data(days)
            
            # Display ROI
            self._display_roi(data['roi'])
            
            # Display efficiency
            self._display_efficiency(data['efficiency_metrics'], data['time_metrics'])
            
            # Display predictions
            self._display_predictions(data['predictions'])
            
            # Display recommendations
            self._display_recommendations(data['recommendations'])
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Aktualisieren:\n{e}")
    
    def _display_roi(self, roi_data: Dict[str, Any]):
        """Display ROI metrics."""
        self.roi_text.delete(1.0, tk.END)
        
        self.roi_text.insert(tk.END, "=" * 60 + "\n")
        self.roi_text.insert(tk.END, "ROI METRICS\n")
        self.roi_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.roi_text.insert(tk.END, f"Zeit gespart:     {roi_data['time_saved_hours']:.1f} Stunden\n")
        self.roi_text.insert(tk.END, f"Kosten gespart:   {roi_data['cost_saved']:.2f} EUR\n")
        self.roi_text.insert(tk.END, f"Effizienz-Gewinn: {roi_data['efficiency_gain']:.1f}%\n")
        self.roi_text.insert(tk.END, f"Qualitäts-Verbesserung: {roi_data['quality_improvement']:.1f}%\n")
        self.roi_text.insert(tk.END, f"ROI:              {roi_data['roi_percentage']:.1f}%\n")
        
        if roi_data['payback_period_days'] > 0:
            self.roi_text.insert(tk.END, f"Amortisationszeit: {roi_data['payback_period_days']:.1f} Tage\n")
        else:
            self.roi_text.insert(tk.END, "Amortisationszeit: Bereits amortisiert\n")
    
    def _display_efficiency(self, efficiency: Dict[str, Any], time_metrics: Dict[str, Any]):
        """Display efficiency metrics."""
        self.efficiency_text.delete(1.0, tk.END)
        
        self.efficiency_text.insert(tk.END, "=" * 60 + "\n")
        self.efficiency_text.insert(tk.END, "EFFIZIENZ METRICS\n")
        self.efficiency_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.efficiency_text.insert(tk.END, f"Gesamt Sessions:        {efficiency['total_sessions']}\n")
        self.efficiency_text.insert(tk.END, f"Gesamt Steps:           {efficiency['total_steps']}\n")
        self.efficiency_text.insert(tk.END, f"Gesamt Screenshots:     {efficiency['total_screenshots']}\n")
        self.efficiency_text.insert(tk.END, f"Durchschnitt Steps/Session: {efficiency['avg_steps_per_session']:.1f}\n")
        self.efficiency_text.insert(tk.END, f"Durchschnitt Dauer/Session: {efficiency['avg_duration_per_session']:.1f} Sekunden\n")
        self.efficiency_text.insert(tk.END, f"\nZeit gespart pro Session: {time_metrics.get('avg_time_saved_per_session', 0):.2f} Stunden\n")
    
    def _display_predictions(self, predictions: Dict[str, Any]):
        """Display predictions."""
        self.predictions_text.delete(1.0, tk.END)
        
        self.predictions_text.insert(tk.END, "=" * 60 + "\n")
        self.predictions_text.insert(tk.END, f"VORHERSAGE FÜR NÄCHSTE {predictions['days_ahead']} TAGE\n")
        self.predictions_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.predictions_text.insert(tk.END, f"Erwartete Sessions:     {predictions['predicted_sessions']:.0f}\n")
        self.predictions_text.insert(tk.END, f"Erwartete Zeit gespart: {predictions['predicted_time_saved_hours']:.1f} Stunden\n")
        self.predictions_text.insert(tk.END, f"Erwartete Kosten gespart: {predictions['predicted_cost_saved']:.2f} EUR\n")
        self.predictions_text.insert(tk.END, f"Trend:                  {predictions['trend']}\n")
        self.predictions_text.insert(tk.END, f"Täglicher Durchschnitt: {predictions['current_daily_average']:.2f} Stunden\n")
    
    def _display_recommendations(self, recommendations: List[str]):
        """Display recommendations."""
        self.rec_text.delete(1.0, tk.END)
        
        self.rec_text.insert(tk.END, "=" * 60 + "\n")
        self.rec_text.insert(tk.END, "OPTIMIERUNGS-EMPFEHLUNGEN\n")
        self.rec_text.insert(tk.END, "=" * 60 + "\n\n")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                self.rec_text.insert(tk.END, f"{i}. {rec}\n\n")
        else:
            self.rec_text.insert(tk.END, "Keine spezifischen Empfehlungen.\n")
            self.rec_text.insert(tk.END, "Die Dokumentation läuft effizient!\n")
    
    def _export_dashboard(self):
        """Export dashboard data."""
        from tkinter import filedialog
        
        path = filedialog.asksaveasfilename(
            title="Dashboard exportieren",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        
        if path:
            try:
                days = self.period_var.get() if self.period_var.get() > 0 else None
                if self.dashboard_api.export_dashboard_json(Path(path), days):
                    messagebox.showinfo("Erfolg", f"Dashboard exportiert: {path}")
            except Exception as e:
                logger.error(f"Error exporting dashboard: {e}")
                messagebox.showerror("Fehler", f"Fehler beim Export:\n{e}")

