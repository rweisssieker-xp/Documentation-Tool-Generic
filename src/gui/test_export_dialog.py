"""
Test Export Dialog - GUI for exporting automated tests.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestExportDialog(tk.Toplevel):
    """
    Dialog for exporting documentation as automated tests.
    """
    
    FRAMEWORKS = {
        "Selenium (Python)": ("selenium", "python"),
        "Selenium (Java)": ("selenium", "java"),
        "Playwright (Python)": ("playwright", "python"),
        "Playwright (TypeScript)": ("playwright", "typescript"),
        "Gherkin/BDD (Deutsch)": ("gherkin", "de"),
        "Gherkin/BDD (English)": ("gherkin", "en")
    }
    
    def __init__(self, parent: tk.Widget, session_data: dict):
        """
        Initialize test export dialog.
        
        Args:
            parent: Parent widget
            session_data: Session data to export
        """
        super().__init__(parent)
        
        self.session_data = session_data
        
        self.title("🧪 Test Export")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text="Automatisierte Tests generieren",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W)
        
        session_name = self.session_data.get("name", "Unbekannte Session")
        step_count = len(self.session_data.get("steps", []))
        
        ttk.Label(
            header_frame,
            text=f"Session: {session_name} ({step_count} Schritte)",
            foreground="gray"
        ).pack(anchor=tk.W)
        
        # Framework selection
        framework_frame = ttk.LabelFrame(self, text="Test-Framework")
        framework_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self._framework_var = tk.StringVar(value="Playwright (Python)")
        
        for name in self.FRAMEWORKS.keys():
            ttk.Radiobutton(
                framework_frame,
                text=name,
                variable=self._framework_var,
                value=name
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(self, text="Optionen")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self._include_comments = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Kommentare einschließen",
            variable=self._include_comments
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self._include_waits = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Automatische Waits einfügen",
            variable=self._include_waits
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self._generate_edge_cases = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Edge Cases generieren",
            variable=self._generate_edge_cases
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Output path
        output_frame = ttk.LabelFrame(self, text="Ausgabe")
        output_frame.pack(fill=tk.X, padx=20, pady=10)
        
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(path_frame, text="Speicherort:").pack(side=tk.LEFT)
        
        self._output_path = tk.StringVar()
        self._path_entry = ttk.Entry(path_frame, textvariable=self._output_path, width=40)
        self._path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            path_frame,
            text="📁",
            command=self._browse_output,
            width=3
        ).pack(side=tk.LEFT)
        
        # Preview
        preview_frame = ttk.LabelFrame(self, text="Vorschau")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._preview_text = tk.Text(preview_frame, height=10, wrap=tk.NONE)
        self._preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars for preview
        h_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self._preview_text.xview)
        h_scroll.pack(fill=tk.X)
        self._preview_text.configure(xscrollcommand=h_scroll.set)
        
        # Update preview button
        ttk.Button(
            preview_frame,
            text="🔄 Vorschau aktualisieren",
            command=self._update_preview
        ).pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(
            button_frame,
            text="❌ Abbrechen",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        self._export_btn = ttk.Button(
            button_frame,
            text="✅ Exportieren",
            command=self._export
        )
        self._export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Initial preview
        self._update_preview()
    
    def _browse_output(self):
        """Browse for output location."""
        framework = self._framework_var.get()
        framework_type, _ = self.FRAMEWORKS.get(framework, ("", ""))
        
        if framework_type == "gherkin":
            ext = ".feature"
            filetypes = [("Gherkin Feature", "*.feature")]
        elif "typescript" in framework.lower():
            ext = ".spec.ts"
            filetypes = [("TypeScript", "*.ts")]
        elif "java" in framework.lower():
            ext = ".java"
            filetypes = [("Java", "*.java")]
        else:
            ext = ".py"
            filetypes = [("Python", "*.py")]
        
        session_name = self.session_data.get("name", "test").replace(" ", "_").lower()
        default_name = f"test_{session_name}{ext}"
        
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=filetypes,
            initialfile=default_name
        )
        
        if path:
            self._output_path.set(path)
    
    def _update_preview(self):
        """Update code preview."""
        self._preview_text.delete(1.0, tk.END)
        
        try:
            code = self._generate_code()
            self._preview_text.insert(tk.END, code[:5000])  # Limit preview size
            
            if len(code) > 5000:
                self._preview_text.insert(tk.END, "\n\n... (gekürzt)")
        
        except Exception as e:
            self._preview_text.insert(tk.END, f"Fehler bei Code-Generierung:\n{e}")
    
    def _generate_code(self) -> str:
        """Generate test code."""
        framework = self._framework_var.get()
        framework_type, language = self.FRAMEWORKS.get(framework, ("playwright", "python"))
        
        try:
            if framework_type == "selenium":
                from src.testgen import SeleniumExporter
                exporter = SeleniumExporter(language=language)
                return exporter._generate_python(self.session_data, None) if language == "python" else exporter._generate_java(self.session_data, None)
            
            elif framework_type == "playwright":
                from src.testgen import PlaywrightExporter
                exporter = PlaywrightExporter(language=language)
                return exporter._generate_python(self.session_data, None) if language == "python" else exporter._generate_typescript(self.session_data, None)
            
            elif framework_type == "gherkin":
                from src.testgen import GherkinExporter
                exporter = GherkinExporter(language=language)
                # Create temp output to get content
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.feature', delete=False) as f:
                    return exporter.export_session(self.session_data, f.name)
        
        except ImportError as e:
            return f"# Modul nicht gefunden: {e}\n# Bitte installieren Sie die erforderlichen Abhängigkeiten."
        except Exception as e:
            return f"# Fehler: {e}"
    
    def _export(self):
        """Export test code."""
        output_path = self._output_path.get().strip()
        
        if not output_path:
            messagebox.showwarning("Hinweis", "Bitte Speicherort auswählen")
            return
        
        self._export_btn.configure(state=tk.DISABLED)
        
        threading.Thread(
            target=self._run_export,
            args=(output_path,),
            daemon=True
        ).start()
    
    def _run_export(self, output_path: str):
        """Run export in background."""
        try:
            code = self._generate_code()
            
            Path(output_path).write_text(code, encoding='utf-8')
            
            self.after(0, lambda: messagebox.showinfo(
                "Erfolg",
                f"Tests erfolgreich exportiert:\n{output_path}"
            ))
            self.after(0, self.destroy)
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.after(0, lambda: messagebox.showerror(
                "Fehler",
                f"Export fehlgeschlagen:\n{e}"
            ))
        
        finally:
            self.after(0, lambda: self._export_btn.configure(state=tk.NORMAL))

