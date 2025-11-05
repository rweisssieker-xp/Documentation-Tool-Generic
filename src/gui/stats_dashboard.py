"""
Metriken-Dashboard: Zeigt Dokumentations-Qualitäts-Metriken und Statistiken
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from src.document.quality_checker import QualityChecker
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StatisticsDashboard:
    """Dashboard für Dokumentations-Metriken und Statistiken"""
    
    def __init__(self, parent):
        """
        Initialisiert das Statistics Dashboard
        
        Args:
            parent: Parent-Window
        """
        self.parent = parent
        self.quality_checker = QualityChecker()
        
        # Erstelle Dashboard-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Statistiken & Qualitäts-Metriken")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt die UI-Komponenten"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook für Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Qualitäts-Metriken
        quality_frame = ttk.Frame(notebook, padding="10")
        notebook.add(quality_frame, text="Qualitäts-Metriken")
        self._setup_quality_tab(quality_frame)
        
        # Tab 2: Session-Statistiken
        stats_frame = ttk.Frame(notebook, padding="10")
        notebook.add(stats_frame, text="Session-Statistiken")
        self._setup_stats_tab(stats_frame)
        
        # Tab 3: Export-Statistiken
        export_frame = ttk.Frame(notebook, padding="10")
        notebook.add(export_frame, text="Export-Statistiken")
        self._setup_export_tab(export_frame)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Aktualisieren",
            command=self._refresh_stats
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Schließen",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _setup_quality_tab(self, parent):
        """Erstellt Qualitäts-Metriken-Tab"""
        # Score-Anzeige
        score_frame = ttk.LabelFrame(parent, text="Gesamt-Qualitäts-Score", padding="10")
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.quality_score_var = tk.StringVar(value="Nicht berechnet")
        ttk.Label(
            score_frame,
            textvariable=self.quality_score_var,
            font=("Arial", 16, "bold")
        ).pack()
        
        # Qualitäts-Details
        details_frame = ttk.LabelFrame(parent, text="Qualitäts-Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(details_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.quality_text = tk.Text(
            details_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set
        )
        self.quality_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.quality_text.yview)
    
    def _setup_stats_tab(self, parent):
        """Erstellt Session-Statistiken-Tab"""
        # Lade Session-Statistiken
        stats = self._load_session_statistics()
        
        # Statistiken-Anzeige
        stats_text = tk.Text(parent, wrap=tk.WORD, state=tk.DISABLED)
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        stats_text.config(state=tk.NORMAL)
        stats_text.insert(1.0, self._format_statistics(stats))
        stats_text.config(state=tk.DISABLED)
    
    def _setup_export_tab(self, parent):
        """Erstellt Export-Statistiken-Tab"""
        # Lade Export-Statistiken
        export_stats = self._load_export_statistics()
        
        # Statistiken-Anzeige
        export_text = tk.Text(parent, wrap=tk.WORD, state=tk.DISABLED)
        export_text.pack(fill=tk.BOTH, expand=True)
        
        export_text.config(state=tk.NORMAL)
        export_text.insert(1.0, self._format_export_statistics(export_stats))
        export_text.config(state=tk.DISABLED)
    
    def _refresh_stats(self):
        """Aktualisiert Statistiken"""
        # Aktualisiere Qualitäts-Metriken
        # (würde normalerweise aktuelle Session-Schritte verwenden)
        self.quality_text.config(state=tk.NORMAL)
        self.quality_text.delete(1.0, tk.END)
        self.quality_text.insert(1.0, "Statistiken werden aktualisiert...")
        self.quality_text.config(state=tk.DISABLED)
        
        # TODO: Lade aktuelle Session-Schritte und berechne Qualität
    
    def _load_session_statistics(self) -> Dict:
        """Lädt Session-Statistiken"""
        stats = {
            'total_sessions': 0,
            'total_steps': 0,
            'total_duration': 0,
            'average_steps_per_session': 0,
            'sessions_by_date': {}
        }
        
        try:
            sessions_dir = Path("data") / "sessions"
            if not sessions_dir.exists():
                return stats
            
            import json
            
            for session_dir in sessions_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                
                session_data_file = session_dir / "session_data.json"
                if not session_data_file.exists():
                    continue
                
                try:
                    with open(session_data_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    stats['total_sessions'] += 1
                    steps = session_data.get('steps', [])
                    stats['total_steps'] += len(steps)
                    
                    # Dauer
                    start_time = session_data.get('start_time')
                    end_time = session_data.get('end_time')
                    if start_time and end_time:
                        try:
                            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            duration = (end - start).total_seconds()
                            stats['total_duration'] += duration
                        except:
                            pass
                    
                    # Nach Datum gruppieren
                    if start_time:
                        try:
                            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            date_key = start.strftime('%Y-%m-%d')
                            stats['sessions_by_date'][date_key] = stats['sessions_by_date'].get(date_key, 0) + 1
                        except:
                            pass
                
                except Exception as e:
                    logger.warning(f"Fehler beim Laden der Session {session_dir.name}: {e}")
                    continue
            
            if stats['total_sessions'] > 0:
                stats['average_steps_per_session'] = stats['total_steps'] / stats['total_sessions']
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Session-Statistiken: {e}", exc_info=True)
        
        return stats
    
    def _load_export_statistics(self) -> Dict:
        """Lädt Export-Statistiken"""
        stats = {
            'total_exports': 0,
            'exports_by_format': {},
            'exports_by_date': {}
        }
        
        try:
            output_dir = Path("data") / "output"
            if not output_dir.exists():
                return stats
            
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in ['.docx', '.pdf', '.md', '.html', '.json', '.csv']:
                        stats['total_exports'] += 1
                        stats['exports_by_format'][ext] = stats['exports_by_format'].get(ext, 0) + 1
                        
                        # Nach Datum
                        try:
                            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            date_key = mtime.strftime('%Y-%m-%d')
                            stats['exports_by_date'][date_key] = stats['exports_by_date'].get(date_key, 0) + 1
                        except:
                            pass
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Export-Statistiken: {e}", exc_info=True)
        
        return stats
    
    def _format_statistics(self, stats: Dict) -> str:
        """Formatiert Statistiken für Anzeige"""
        lines = [
            "=" * 60,
            "SESSION-STATISTIKEN",
            "=" * 60,
            "",
            f"Gesamt-Sessions: {stats['total_sessions']}",
            f"Gesamt-Schritte: {stats['total_steps']}",
            f"Durchschnittliche Schritte pro Session: {stats['average_steps_per_session']:.1f}",
            "",
            f"Gesamt-Dauer: {self._format_duration(stats['total_duration'])}",
            "",
            "Sessions nach Datum:",
        ]
        
        for date, count in sorted(stats['sessions_by_date'].items(), reverse=True)[:10]:
            lines.append(f"  {date}: {count} Session(s)")
        
        return "\n".join(lines)
    
    def _format_export_statistics(self, stats: Dict) -> str:
        """Formatiert Export-Statistiken"""
        lines = [
            "=" * 60,
            "EXPORT-STATISTIKEN",
            "=" * 60,
            "",
            f"Gesamt-Exports: {stats['total_exports']}",
            "",
            "Exports nach Format:",
        ]
        
        format_names = {
            '.docx': 'DOCX',
            '.pdf': 'PDF',
            '.md': 'Markdown',
            '.html': 'HTML',
            '.json': 'JSON',
            '.csv': 'CSV'
        }
        
        for ext, count in sorted(stats['exports_by_format'].items(), key=lambda x: x[1], reverse=True):
            format_name = format_names.get(ext, ext)
            lines.append(f"  {format_name}: {count}")
        
        lines.append("")
        lines.append("Exports nach Datum:")
        for date, count in sorted(stats['exports_by_date'].items(), reverse=True)[:10]:
            lines.append(f"  {date}: {count} Export(s)")
        
        return "\n".join(lines)
    
    def _format_duration(self, seconds: float) -> str:
        """Formatiert Dauer"""
        if not seconds:
            return "0s"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def update_quality_metrics(self, steps: List[Dict]):
        """
        Aktualisiert Qualitäts-Metriken
        
        Args:
            steps: Liste von Schritten
        """
        try:
            metrics = self.quality_checker.check_quality(steps)
            
            # Update Score
            score = metrics['overall_score']
            self.quality_score_var.set(f"{score:.1%}")
            
            # Update Details
            report = self.quality_checker.get_quality_report(steps)
            
            self.quality_text.config(state=tk.NORMAL)
            self.quality_text.delete(1.0, tk.END)
            self.quality_text.insert(1.0, report)
            self.quality_text.config(state=tk.DISABLED)
        
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Qualitäts-Metriken: {e}", exc_info=True)

