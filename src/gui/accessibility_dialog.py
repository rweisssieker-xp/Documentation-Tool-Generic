"""
Accessibility Compliance Dialog
GUI for WCAG compliance checking and remediation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Dict, Any

from src.accessibility import WCAGAuditor, WCAGLevel, StructureValidator, AutoRemediation, ComplianceReportGenerator
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AccessibilityDialog:
    """Dialog for accessibility compliance checking."""
    
    def __init__(self, parent, file_path: Optional[Path] = None):
        """
        Initialize accessibility dialog.
        
        Args:
            parent: Parent window
            file_path: Optional file to check
        """
        self.parent = parent
        self.file_path = file_path
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Accessibility Compliance Check")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        
        if file_path:
            self._check_file(file_path)
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Top frame for file selection
        top_frame = ttk.Frame(self.dialog)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Datei:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.file_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(top_frame, text="Durchsuchen...", command=self._browse_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Prüfen", command=self._check_current_file).pack(side=tk.LEFT, padx=5)
        
        # Level selection
        level_frame = ttk.Frame(self.dialog)
        level_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(level_frame, text="WCAG Level:").pack(side=tk.LEFT, padx=5)
        self.level_var = tk.StringVar(value="AA")
        ttk.Radiobutton(level_frame, text="A", variable=self.level_var, value="A").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(level_frame, text="AA", variable=self.level_var, value="AA").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(level_frame, text="AAA", variable=self.level_var, value="AAA").pack(side=tk.LEFT, padx=5)
        
        # Results notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Violations tab
        violations_frame = ttk.Frame(notebook)
        notebook.add(violations_frame, text="Violations")
        self.violations_text = tk.Text(violations_frame, wrap=tk.WORD)
        self.violations_text.pack(fill=tk.BOTH, expand=True)
        
        # Structure Issues tab
        structure_frame = ttk.Frame(notebook)
        notebook.add(structure_frame, text="Structure")
        self.structure_text = tk.Text(structure_frame, wrap=tk.WORD)
        self.structure_text.pack(fill=tk.BOTH, expand=True)
        
        # Recommendations tab
        rec_frame = ttk.Frame(notebook)
        notebook.add(rec_frame, text="Recommendations")
        self.rec_text = tk.Text(rec_frame, wrap=tk.WORD)
        self.rec_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Auto-Fix", command=self._auto_fix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Report exportieren...", command=self._export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Schließen", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.audit_result = None
        self.structure_issues = []
    
    def _browse_file(self):
        """Browse for file to check."""
        path = filedialog.askopenfilename(
            title="HTML-Datei wählen",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if path:
            self.file_var.set(path)
            self._check_file(Path(path))
    
    def _check_current_file(self):
        """Check currently selected file."""
        path = self.file_var.get()
        if path:
            self._check_file(Path(path))
        else:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Datei aus")
    
    def _check_file(self, file_path: Path):
        """Check file for accessibility."""
        if not file_path.exists():
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {file_path}")
            return
        
        try:
            # Set level
            level_map = {"A": WCAGLevel.A, "AA": WCAGLevel.AA, "AAA": WCAGLevel.AAA}
            level = level_map.get(self.level_var.get(), WCAGLevel.AA)
            
            # Audit
            auditor = WCAGAuditor(level=level)
            self.audit_result = auditor.audit_file(file_path)
            
            # Structure validation
            validator = StructureValidator()
            html_content = file_path.read_text(encoding='utf-8')
            self.structure_issues = validator.validate(html_content)
            
            # Display results
            self._display_results()
            
        except Exception as e:
            logger.error(f"Error checking file: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Prüfen:\n{e}")
    
    def _display_results(self):
        """Display audit results."""
        # Violations
        self.violations_text.delete(1.0, tk.END)
        if self.audit_result:
            self.violations_text.insert(tk.END, f"Score: {self.audit_result.score:.1f}%\n")
            self.violations_text.insert(tk.END, f"Violations: {len(self.audit_result.violations)}\n\n")
            
            for v in self.audit_result.violations:
                self.violations_text.insert(tk.END, f"[{v.impact.upper()}] {v.rule_id}\n")
                self.violations_text.insert(tk.END, f"  {v.description}\n")
                if v.help_url:
                    self.violations_text.insert(tk.END, f"  {v.help_url}\n")
                self.violations_text.insert(tk.END, "\n")
        
        # Structure issues
        self.structure_text.delete(1.0, tk.END)
        if self.structure_issues:
            self.structure_text.insert(tk.END, f"Issues: {len(self.structure_issues)}\n\n")
            for issue in self.structure_issues:
                self.structure_text.insert(tk.END, f"[{issue.severity.upper()}] {issue.issue_type.value}\n")
                self.structure_text.insert(tk.END, f"  {issue.description}\n")
                if issue.suggestion:
                    self.structure_text.insert(tk.END, f"  Suggestion: {issue.suggestion}\n")
                self.structure_text.insert(tk.END, "\n")
        else:
            self.structure_text.insert(tk.END, "Keine Structure-Issues gefunden!")
        
        # Recommendations
        self.rec_text.delete(1.0, tk.END)
        if self.audit_result:
            generator = ComplianceReportGenerator()
            report = generator.generate_report(self.audit_result, self.structure_issues)
            
            for rec in report.recommendations:
                self.rec_text.insert(tk.END, f"• {rec}\n")
    
    def _auto_fix(self):
        """Auto-fix accessibility issues."""
        if not self.audit_result:
            messagebox.showwarning("Warnung", "Bitte führen Sie zuerst eine Prüfung durch")
            return
        
        file_path = Path(self.file_var.get())
        if not file_path.exists():
            messagebox.showerror("Fehler", "Datei nicht gefunden")
            return
        
        try:
            remediation = AutoRemediation()
            html_content = file_path.read_text(encoding='utf-8')
            
            fixed_html = remediation.remediate_html(
                html_content,
                self.audit_result.violations
            )
            
            # Save fixed version
            backup_path = file_path.with_suffix('.html.backup')
            file_path.rename(backup_path)
            file_path.write_text(fixed_html, encoding='utf-8')
            
            messagebox.showinfo("Erfolg", f"Datei wurde automatisch korrigiert!\nBackup: {backup_path.name}")
            self._check_file(file_path)  # Re-check
            
        except Exception as e:
            logger.error(f"Error auto-fixing: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Auto-Fix:\n{e}")
    
    def _export_report(self):
        """Export compliance report."""
        if not self.audit_result:
            messagebox.showwarning("Warnung", "Bitte führen Sie zuerst eine Prüfung durch")
            return
        
        path = filedialog.asksaveasfilename(
            title="Report speichern",
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("JSON", "*.json")]
        )
        
        if path:
            try:
                generator = ComplianceReportGenerator()
                report = generator.generate_report(self.audit_result, self.structure_issues, self.file_var.get())
                
                output_path = Path(path)
                if output_path.suffix == ".json":
                    generator.export_json(report, output_path)
                else:
                    generator.export_html(report, output_path)
                
                messagebox.showinfo("Erfolg", f"Report exportiert: {path}")
            except Exception as e:
                logger.error(f"Error exporting report: {e}")
                messagebox.showerror("Fehler", f"Fehler beim Export:\n{e}")

