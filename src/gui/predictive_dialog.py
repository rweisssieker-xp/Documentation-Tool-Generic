"""
Predictive Maintenance Dialog - GUI für Predictive Documentation Maintenance
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional

from src.predictive import PredictiveMaintenanceEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictiveDialog:
    """Dialog for Predictive Documentation Maintenance"""
    
    def __init__(self, parent):
        """
        Initialize Predictive Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.engine = PredictiveMaintenanceEngine()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Predictive Documentation Maintenance")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Session Selection
        session_frame = ttk.Frame(self.dialog)
        session_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(session_frame, text="Session ID:").pack(side=tk.LEFT, padx=5)
        self.session_id_var = tk.StringVar()
        ttk.Entry(session_frame, textvariable=self.session_id_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(session_frame, text="Analyze", command=self._analyze_session).pack(side=tk.LEFT, padx=5)
        
        # Issues List
        issues_frame = ttk.LabelFrame(self.dialog, text="Detected Issues")
        issues_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for issues
        columns = ("Priority", "Type", "Description", "Confidence")
        self.issues_tree = ttk.Treeview(issues_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.issues_tree.heading(col, text=col)
            self.issues_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(issues_frame, orient=tk.VERTICAL, command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=scrollbar.set)
        
        self.issues_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Issue Details
        details_frame = ttk.LabelFrame(self.dialog, text="Issue Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.issues_tree.bind("<<TreeviewSelect>>", self._on_issue_select)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Send Alerts", command=self._send_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Report", command=self._export_report).pack(side=tk.LEFT, padx=5)
    
    def _analyze_session(self):
        """Analyze session for outdated documentation"""
        session_id = self.session_id_var.get()
        if not session_id:
            messagebox.showwarning("Warning", "Please enter a session ID")
            return
        
        try:
            issues = self.engine.analyze_documentation(session_id)
            
            # Clear existing items
            for item in self.issues_tree.get_children():
                self.issues_tree.delete(item)
            
            # Add issues
            for issue in issues:
                self.issues_tree.insert(
                    "",
                    tk.END,
                    values=(
                        f"{issue.get('priority', 0):.1f}",
                        issue.get('type', 'unknown'),
                        issue.get('description', 'No description')[:50],
                        f"{issue.get('confidence', 0):.0%}",
                    ),
                    tags=(issue.get('id', ''),)
                )
            
            messagebox.showinfo("Success", f"Analysis complete. Found {len(issues)} issues.")
        except Exception as e:
            logger.error(f"Error analyzing session: {e}")
            messagebox.showerror("Error", f"Failed to analyze session: {e}")
    
    def _on_issue_select(self, event):
        """Handle issue selection"""
        selection = self.issues_tree.selection()
        if not selection:
            return
        
        # Get issue details (placeholder)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Issue Details\n")
        self.details_text.insert(tk.END, "=" * 50 + "\n")
        self.details_text.insert(tk.END, "Detailed information about the selected issue...\n")
    
    def _send_alerts(self):
        """Send alerts for high-priority issues"""
        items = self.issues_tree.get_children()
        issues = []
        
        for item in items:
            values = self.issues_tree.item(item)['values']
            issues.append({
                'priority': float(values[0]),
                'type': values[1],
                'description': values[2],
            })
        
        if issues:
            self.engine.send_alerts(issues)
            messagebox.showinfo("Success", "Alerts sent successfully")
        else:
            messagebox.showwarning("Warning", "No issues to send alerts for")
    
    def _export_report(self):
        """Export analysis report"""
        messagebox.showinfo("Info", "Export functionality coming soon!")




