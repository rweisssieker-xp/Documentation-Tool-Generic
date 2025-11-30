"""
Tutorial Export Dialog - GUI for exporting interactive tutorials.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TutorialExportDialog(tk.Toplevel):
    """
    Dialog for exporting documentation as interactive tutorials.
    """
    
    EXPORT_FORMATS = [
        ("HTML interaktiv", "html"),
        ("SCORM 2004 (LMS)", "scorm"),
        ("Markdown", "markdown")
    ]
    
    DIFFICULTY_LEVELS = [
        "Anfänger",
        "Fortgeschritten",
        "Experte"
    ]
    
    def __init__(self, parent: tk.Widget, session_data: dict):
        """
        Initialize tutorial export dialog.
        
        Args:
            parent: Parent widget
            session_data: Session data to export
        """
        super().__init__(parent)
        
        self.session_data = session_data
        
        self.title("📚 Tutorial Export")
        self.geometry("600x550")
        self.minsize(500, 450)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text="Interaktives Tutorial erstellen",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W)
        
        session_name = self.session_data.get("name", "Unbekannte Session")
        step_count = len(self.session_data.get("steps", []))
        
        ttk.Label(
            header_frame,
            text=f"Session: {session_name} ({step_count} Schritte)",
            foreground="gray"
        ).pack(anchor=tk.W)
        
        # Tutorial info
        info_frame = ttk.LabelFrame(self, text="Tutorial-Informationen")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title_frame = ttk.Frame(info_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="Titel:", width=15).pack(side=tk.LEFT)
        self._title_var = tk.StringVar(value=session_name)
        ttk.Entry(title_frame, textvariable=self._title_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Description
        desc_frame = ttk.Frame(info_frame)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(desc_frame, text="Beschreibung:", width=15).pack(side=tk.LEFT)
        self._desc_var = tk.StringVar(value=self.session_data.get("description", ""))
        ttk.Entry(desc_frame, textvariable=self._desc_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Difficulty
        diff_frame = ttk.Frame(info_frame)
        diff_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(diff_frame, text="Schwierigkeit:", width=15).pack(side=tk.LEFT)
        self._difficulty_var = tk.StringVar(value="Anfänger")
        ttk.Combobox(
            diff_frame,
            textvariable=self._difficulty_var,
            values=self.DIFFICULTY_LEVELS,
            state="readonly",
            width=20
        ).pack(side=tk.LEFT)
        
        # Export format
        format_frame = ttk.LabelFrame(self, text="Export-Format")
        format_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self._format_var = tk.StringVar(value="html")
        
        for display_name, value in self.EXPORT_FORMATS:
            ttk.Radiobutton(
                format_frame,
                text=display_name,
                variable=self._format_var,
                value=value
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(self, text="Optionen")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self._include_quizzes = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Quiz-Fragen generieren",
            variable=self._include_quizzes
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self._include_navigation = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Navigation einschließen",
            variable=self._include_navigation
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self._include_progress = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Fortschrittsanzeige",
            variable=self._include_progress
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self._include_screenshots = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Screenshots einbetten",
            variable=self._include_screenshots
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
        
        # Preview info
        preview_frame = ttk.LabelFrame(self, text="Tutorial-Vorschau")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._preview_text = tk.Text(preview_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self._preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._update_preview()
        
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
        
        ttk.Button(
            button_frame,
            text="👁️ Vorschau",
            command=self._preview
        ).pack(side=tk.RIGHT, padx=5)
    
    def _browse_output(self):
        """Browse for output location."""
        format_type = self._format_var.get()
        
        if format_type == "scorm":
            ext = ".zip"
            filetypes = [("SCORM Package", "*.zip")]
        elif format_type == "markdown":
            ext = ".md"
            filetypes = [("Markdown", "*.md")]
        else:
            ext = ".html"
            filetypes = [("HTML", "*.html")]
        
        tutorial_name = self._title_var.get().replace(" ", "_").lower()
        default_name = f"tutorial_{tutorial_name}{ext}"
        
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=filetypes,
            initialfile=default_name
        )
        
        if path:
            self._output_path.set(path)
    
    def _update_preview(self):
        """Update preview information."""
        self._preview_text.configure(state=tk.NORMAL)
        self._preview_text.delete(1.0, tk.END)
        
        steps = self.session_data.get("steps", [])
        
        preview = f"📚 Tutorial: {self._title_var.get()}\n"
        preview += f"📊 Schwierigkeit: {self._difficulty_var.get()}\n"
        preview += f"📝 Schritte: {len(steps)}\n"
        preview += f"⏱️ Geschätzte Dauer: {len(steps) * 2} Minuten\n\n"
        preview += "Schritte:\n"
        
        for i, step in enumerate(steps[:5]):
            title = step.get("title", step.get("description", f"Schritt {i+1}"))[:40]
            preview += f"  {i+1}. {title}\n"
        
        if len(steps) > 5:
            preview += f"  ... und {len(steps) - 5} weitere"
        
        self._preview_text.insert(tk.END, preview)
        self._preview_text.configure(state=tk.DISABLED)
    
    def _preview(self):
        """Preview tutorial in browser."""
        try:
            import tempfile
            import webbrowser
            
            html = self._generate_html()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html)
                temp_path = f.name
            
            webbrowser.open(f"file://{temp_path}")
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Vorschau fehlgeschlagen:\n{e}")
    
    def _generate_html(self) -> str:
        """Generate HTML tutorial."""
        try:
            from src.tutorial import TutorialGenerator
            
            generator = TutorialGenerator(include_quizzes=self._include_quizzes.get())
            
            # Override session data with dialog values
            session = self.session_data.copy()
            session["name"] = self._title_var.get()
            session["description"] = self._desc_var.get()
            
            tutorial = generator.generate_tutorial(session, title=self._title_var.get())
            
            return generator._generate_html(tutorial, self._include_navigation.get())
        
        except ImportError:
            return "<html><body><h1>Tutorial-Modul nicht verfügbar</h1></body></html>"
    
    def _export(self):
        """Export tutorial."""
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
            format_type = self._format_var.get()
            
            if format_type == "html":
                html = self._generate_html()
                Path(output_path).write_text(html, encoding='utf-8')
            
            elif format_type == "scorm":
                from src.tutorial import TutorialGenerator, SCORMExporter
                
                generator = TutorialGenerator(include_quizzes=self._include_quizzes.get())
                tutorial = generator.generate_tutorial(self.session_data, title=self._title_var.get())
                html = generator._generate_html(tutorial, self._include_navigation.get())
                
                exporter = SCORMExporter()
                exporter.export(tutorial, output_path, html)
            
            elif format_type == "markdown":
                md = self._generate_markdown()
                Path(output_path).write_text(md, encoding='utf-8')
            
            self.after(0, lambda: messagebox.showinfo(
                "Erfolg",
                f"Tutorial erfolgreich exportiert:\n{output_path}"
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
    
    def _generate_markdown(self) -> str:
        """Generate Markdown tutorial."""
        steps = self.session_data.get("steps", [])
        
        md = f"# {self._title_var.get()}\n\n"
        md += f"{self._desc_var.get()}\n\n"
        md += f"**Schwierigkeit:** {self._difficulty_var.get()}\n"
        md += f"**Geschätzte Dauer:** {len(steps) * 2} Minuten\n\n"
        md += "---\n\n"
        
        for i, step in enumerate(steps):
            title = step.get("title", f"Schritt {i+1}")
            desc = step.get("description", "")
            
            md += f"## Schritt {i+1}: {title}\n\n"
            md += f"{desc}\n\n"
            
            if step.get("screenshot"):
                md += f"![Screenshot](screenshots/{step['screenshot']})\n\n"
        
        md += "---\n\n*Automatisch generiert mit AHG Tutorial Generator*\n"
        
        return md

