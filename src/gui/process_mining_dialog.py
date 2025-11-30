"""
Process Mining Dialog - GUI for process mining features.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProcessMiningDialog(tk.Toplevel):
    """
    Dialog for process mining and analysis.
    """
    
    def __init__(self, parent: tk.Widget, sessions: list):
        """
        Initialize process mining dialog.
        
        Args:
            parent: Parent widget
            sessions: List of session data to analyze
        """
        super().__init__(parent)
        
        self.sessions = sessions
        self._miner = None
        self._model = None
        
        self.title("🔍 Process Mining")
        self.geometry("900x700")
        self.minsize(700, 500)
        
        self._setup_ui()
        self._initialize_miner()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text="Process Mining & Analyse",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text=f"{len(self.sessions)} Sessions zur Analyse",
            foreground="gray"
        ).pack(anchor=tk.W)
        
        # Main content with tabs
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 1: Process Discovery
        discovery_frame = ttk.Frame(self._notebook)
        self._notebook.add(discovery_frame, text="Prozess-Entdeckung")
        
        self._setup_discovery_tab(discovery_frame)
        
        # Tab 2: Variants
        variants_frame = ttk.Frame(self._notebook)
        self._notebook.add(variants_frame, text="Varianten")
        
        self._setup_variants_tab(variants_frame)
        
        # Tab 3: Patterns
        patterns_frame = ttk.Frame(self._notebook)
        self._notebook.add(patterns_frame, text="Muster")
        
        self._setup_patterns_tab(patterns_frame)
        
        # Tab 4: Export
        export_frame = ttk.Frame(self._notebook)
        self._notebook.add(export_frame, text="Export")
        
        self._setup_export_tab(export_frame)
        
        # Status bar
        self._status_var = tk.StringVar(value="Bereit")
        ttk.Label(self, textvariable=self._status_var).pack(side=tk.BOTTOM, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(
            button_frame,
            text="🔄 Analyse starten",
            command=self._run_analysis
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="❌ Schließen",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def _setup_discovery_tab(self, parent: ttk.Frame):
        """Set up process discovery tab."""
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistik")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._stats_text = tk.Text(stats_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self._stats_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Process model visualization
        model_frame = ttk.LabelFrame(parent, text="Prozessmodell (Mermaid)")
        model_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._model_text = tk.Text(model_frame, wrap=tk.NONE)
        self._model_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(model_frame, orient=tk.HORIZONTAL, command=self._model_text.xview)
        h_scroll.pack(fill=tk.X)
        self._model_text.configure(xscrollcommand=h_scroll.set)
    
    def _setup_variants_tab(self, parent: ttk.Frame):
        """Set up variants tab."""
        # Variants list
        self._variants_tree = ttk.Treeview(
            parent,
            columns=("trace", "frequency", "percentage"),
            show="headings",
            selectmode="browse"
        )
        self._variants_tree.heading("trace", text="Ablauf")
        self._variants_tree.heading("frequency", text="Häufigkeit")
        self._variants_tree.heading("percentage", text="Anteil")
        
        self._variants_tree.column("trace", width=400)
        self._variants_tree.column("frequency", width=100)
        self._variants_tree.column("percentage", width=100)
        
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self._variants_tree.yview)
        self._variants_tree.configure(yscrollcommand=v_scroll.set)
        
        self._variants_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def _setup_patterns_tab(self, parent: ttk.Frame):
        """Set up patterns tab."""
        # Patterns list
        self._patterns_tree = ttk.Treeview(
            parent,
            columns=("pattern", "type", "support", "occurrences"),
            show="headings",
            selectmode="browse"
        )
        self._patterns_tree.heading("pattern", text="Muster")
        self._patterns_tree.heading("type", text="Typ")
        self._patterns_tree.heading("support", text="Support")
        self._patterns_tree.heading("occurrences", text="Vorkommen")
        
        self._patterns_tree.column("pattern", width=300)
        self._patterns_tree.column("type", width=100)
        self._patterns_tree.column("support", width=100)
        self._patterns_tree.column("occurrences", width=100)
        
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self._patterns_tree.yview)
        self._patterns_tree.configure(yscrollcommand=v_scroll.set)
        
        self._patterns_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def _setup_export_tab(self, parent: ttk.Frame):
        """Set up export tab."""
        # Export options
        options_frame = ttk.LabelFrame(parent, text="Export-Optionen")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._export_format = tk.StringVar(value="bpmn")
        
        formats = [
            ("BPMN 2.0 XML", "bpmn"),
            ("Mermaid Diagramm", "mermaid"),
            ("DOT (Graphviz)", "dot"),
            ("JSON", "json")
        ]
        
        for text, value in formats:
            ttk.Radiobutton(
                options_frame,
                text=text,
                variable=self._export_format,
                value=value
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Export button
        ttk.Button(
            parent,
            text="📤 Exportieren",
            command=self._export_model
        ).pack(pady=10)
        
        # Preview
        preview_frame = ttk.LabelFrame(parent, text="Export-Vorschau")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._export_preview = tk.Text(preview_frame, wrap=tk.NONE)
        self._export_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _initialize_miner(self):
        """Initialize process miner."""
        try:
            from src.processmining import ProcessMiner
            
            self._miner = ProcessMiner()
            
            # Add sessions
            for session in self.sessions:
                self._miner.add_session(session)
            
            self._status_var.set(f"Miner initialisiert: {len(self.sessions)} Sessions")
        
        except ImportError as e:
            logger.error(f"Process mining module not available: {e}")
            self._status_var.set("Process Mining nicht verfügbar")
            messagebox.showerror("Fehler", "Process Mining Modul nicht verfügbar")
    
    def _run_analysis(self):
        """Run process mining analysis."""
        if not self._miner:
            messagebox.showerror("Fehler", "Miner nicht initialisiert")
            return
        
        self._status_var.set("Analyse läuft...")
        
        threading.Thread(target=self._perform_analysis, daemon=True).start()
    
    def _perform_analysis(self):
        """Perform analysis in background."""
        try:
            # Discover process
            self._model = self._miner.discover_process("Discovered Process")
            
            # Get statistics
            stats = self._miner.get_statistics()
            
            # Update UI
            self.after(0, lambda: self._display_statistics(stats))
            self.after(0, self._display_model)
            self.after(0, self._display_variants)
            self.after(0, self._detect_patterns)
            
            self.after(0, lambda: self._status_var.set("Analyse abgeschlossen"))
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.after(0, lambda: messagebox.showerror("Fehler", f"Analyse fehlgeschlagen:\n{e}"))
            self.after(0, lambda: self._status_var.set("Fehler bei Analyse"))
    
    def _display_statistics(self, stats: dict):
        """Display statistics."""
        self._stats_text.configure(state=tk.NORMAL)
        self._stats_text.delete(1.0, tk.END)
        
        text = f"📊 PROCESS MINING STATISTIK\n"
        text += f"{'=' * 40}\n"
        text += f"Sessions analysiert: {stats.get('total_cases', 0)}\n"
        text += f"Aktivitäten gesamt: {stats.get('total_activities', 0)}\n"
        text += f"Durchschn. Aktivitäten/Session: {stats.get('avg_activities_per_case', 0):.1f}\n"
        text += f"Einzigartige Aktivitäten: {stats.get('unique_activities', 0)}\n"
        text += f"Varianten: {stats.get('variants_count', 0)}\n"
        
        self._stats_text.insert(tk.END, text)
        self._stats_text.configure(state=tk.DISABLED)
    
    def _display_model(self):
        """Display process model."""
        if not self._model:
            return
        
        try:
            from src.processmining import BPMNExporter
            
            exporter = BPMNExporter()
            mermaid = exporter.export_to_mermaid(self._model)
            
            self._model_text.delete(1.0, tk.END)
            self._model_text.insert(tk.END, mermaid)
        
        except Exception as e:
            self._model_text.insert(tk.END, f"Fehler bei Diagramm-Generierung: {e}")
    
    def _display_variants(self):
        """Display process variants."""
        if not self._model:
            return
        
        # Clear existing
        for item in self._variants_tree.get_children():
            self._variants_tree.delete(item)
        
        # Add variants
        for i, variant in enumerate(self._model.variants[:20]):  # Limit to top 20
            trace_str = " → ".join(variant[:5])
            if len(variant) > 5:
                trace_str += f" ... (+{len(variant)-5})"
            
            # Calculate frequency (simplified)
            freq = len(self.sessions) - i
            percentage = f"{(freq / len(self.sessions) * 100):.1f}%"
            
            self._variants_tree.insert(
                "",
                tk.END,
                values=(trace_str, freq, percentage)
            )
    
    def _detect_patterns(self):
        """Detect and display patterns."""
        try:
            from src.processmining import PatternDetector
            
            detector = PatternDetector(min_support=0.2)
            
            # Extract traces
            traces = [self._model.variants[0]] if self._model.variants else []
            traces.extend(self._model.variants[1:5])
            
            patterns = detector.detect_patterns(traces)
            
            # Clear existing
            for item in self._patterns_tree.get_children():
                self._patterns_tree.delete(item)
            
            # Add patterns
            for pattern in patterns[:20]:
                sequence = " → ".join(pattern.sequence)
                
                self._patterns_tree.insert(
                    "",
                    tk.END,
                    values=(sequence, pattern.pattern_type, f"{pattern.support:.0%}", pattern.occurrences)
                )
        
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
    
    def _export_model(self):
        """Export process model."""
        if not self._model:
            messagebox.showwarning("Hinweis", "Zuerst Analyse durchführen")
            return
        
        format_type = self._export_format.get()
        
        # Get file extension
        extensions = {
            "bpmn": (".bpmn", [("BPMN", "*.bpmn")]),
            "mermaid": (".md", [("Markdown", "*.md")]),
            "dot": (".dot", [("DOT", "*.dot")]),
            "json": (".json", [("JSON", "*.json")])
        }
        
        ext, filetypes = extensions.get(format_type, (".txt", [("Text", "*.txt")]))
        
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=filetypes,
            initialfile=f"process_model{ext}"
        )
        
        if not path:
            return
        
        try:
            from src.processmining import BPMNExporter, ProcessGraph
            
            if format_type == "bpmn":
                exporter = BPMNExporter()
                exporter.export(self._model, path)
            
            elif format_type == "mermaid":
                exporter = BPMNExporter()
                content = exporter.export_to_mermaid(self._model)
                Path(path).write_text(content, encoding='utf-8')
            
            elif format_type == "dot":
                graph = ProcessGraph.from_process_model(self._model)
                content = graph.to_dot()
                Path(path).write_text(content, encoding='utf-8')
            
            elif format_type == "json":
                import json
                content = json.dumps({
                    "id": self._model.id,
                    "name": self._model.name,
                    "activities": self._model.activities,
                    "transitions": self._model.transitions,
                    "variants": self._model.variants[:10]
                }, indent=2, ensure_ascii=False)
                Path(path).write_text(content, encoding='utf-8')
            
            messagebox.showinfo("Erfolg", f"Exportiert nach:\n{path}")
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{e}")

