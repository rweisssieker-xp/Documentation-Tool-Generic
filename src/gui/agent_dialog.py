"""
Autonomous Agent Dialog - GUI for Autonomous Documentation Agent
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any
import threading

from src.agent import AutonomousAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentDialog:
    """Dialog for autonomous agent control."""
    
    def __init__(self, parent):
        """
        Initialize agent dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Autonomous Documentation Agent")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self.agent = AutonomousAgent()
        self.is_running = False
        self.agent_thread = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Goal input
        goal_frame = ttk.LabelFrame(self.dialog, text="Task Definition")
        goal_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(goal_frame, text="Goal:").pack(anchor=tk.W, padx=5, pady=5)
        self.goal_text = scrolledtext.ScrolledText(goal_frame, width=70, height=4)
        self.goal_text.pack(fill=tk.X, padx=5, pady=5)
        self.goal_text.insert(1.0, "Dokumentiere den Benutzer-Registrierungsprozess")
        
        # Control buttons
        control_frame = ttk.Frame(goal_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Agent", command=self._start_agent)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Agent", command=self._stop_agent, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Max Steps:").pack(side=tk.LEFT, padx=10)
        self.max_steps_var = tk.IntVar(value=20)
        ttk.Spinbox(control_frame, from_=5, to=100, textvariable=self.max_steps_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = ttk.LabelFrame(self.dialog, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Bereit")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10)).pack(padx=5, pady=5)
        
        # Notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Execution log
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Execution Log")
        self._create_log_tab(log_frame)
        
        # Tools tab
        tools_frame = ttk.Frame(notebook)
        notebook.add(tools_frame, text="Tools")
        self._create_tools_tab(tools_frame)
        
        # Questions tab
        questions_frame = ttk.Frame(notebook)
        notebook.add(questions_frame, text="Questions")
        self._create_questions_tab(questions_frame)
    
    def _create_log_tab(self, parent):
        """Create execution log tab."""
        self.log_text = scrolledtext.ScrolledText(parent, width=80, height=25, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Log löschen", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportieren...", command=self._export_log).pack(side=tk.LEFT, padx=5)
    
    def _create_tools_tab(self, parent):
        """Create tools tab."""
        ttk.Label(parent, text="Verfügbare Tools:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        tools_list = scrolledtext.ScrolledText(parent, width=80, height=20, font=("Courier", 9))
        tools_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tools_text = """Verfügbare Tools:

1. click - Klickt auf eine Position (x, y)
   Parameter: x, y (Koordinaten)

2. type - Gibt Text ein
   Parameter: text (zu tippender Text)

3. navigate - Navigiert zu einer URL
   Parameter: url (Ziel-URL)

4. screenshot - Macht einen Screenshot
   Parameter: path (Speicherpfad)

5. verify - Verifiziert ein Element
   Parameter: element (Element-Selektor)

Der Agent verwendet diese Tools automatisch basierend auf dem Goal.
"""
        tools_list.insert(1.0, tools_text)
        tools_list.config(state=tk.DISABLED)
    
    def _create_questions_tab(self, parent):
        """Create questions tab."""
        ttk.Label(parent, text="Agent-Fragen:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        self.questions_text = scrolledtext.ScrolledText(parent, width=80, height=20)
        self.questions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Answer input
        answer_frame = ttk.Frame(parent)
        answer_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(answer_frame, text="Antwort:").pack(side=tk.LEFT, padx=5)
        self.answer_var = tk.StringVar()
        ttk.Entry(answer_frame, textvariable=self.answer_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(answer_frame, text="Senden", command=self._send_answer).pack(side=tk.LEFT, padx=5)
    
    def _start_agent(self):
        """Start autonomous agent."""
        if self.is_running:
            messagebox.showwarning("Warnung", "Agent läuft bereits")
            return
        
        goal = self.goal_text.get(1.0, tk.END).strip()
        if not goal:
            messagebox.showwarning("Warnung", "Bitte geben Sie ein Goal ein")
            return
        
        if not self.agent.client:
            messagebox.showwarning("Warnung", "OpenAI API Key nicht gesetzt. Agent benötigt AI.")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Läuft...")
        
        max_steps = self.max_steps_var.get()
        
        def run_agent():
            try:
                self._log("Agent gestartet...")
                self._log(f"Goal: {goal}")
                self._log(f"Max Steps: {max_steps}")
                self._log("-" * 60)
                
                steps = self.agent.execute_task(goal, max_steps=max_steps)
                
                self._log("-" * 60)
                self._log(f"Agent abgeschlossen. {len(steps)} Steps ausgeführt.")
                
                for i, step in enumerate(steps, 1):
                    self._log(f"\nStep {i}:")
                    self._log(f"  Action: {step.get('action', 'N/A')}")
                    self._log(f"  Result: {step.get('result', 'N/A')}")
                    self._log(f"  Success: {step.get('success', False)}")
                
            except Exception as e:
                logger.error(f"Agent error: {e}")
                self._log(f"FEHLER: {e}")
            finally:
                self.is_running = False
                self.dialog.after(0, self._agent_finished)
        
        self.agent_thread = threading.Thread(target=run_agent, daemon=True)
        self.agent_thread.start()
    
    def _stop_agent(self):
        """Stop autonomous agent."""
        self.is_running = False
        self.status_var.set("Gestoppt")
        self._log("Agent gestoppt durch Benutzer")
        self._agent_finished()
    
    def _agent_finished(self):
        """Called when agent finishes."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Bereit")
    
    def _log(self, message: str):
        """Add log message."""
        self.dialog.after(0, lambda: self.log_text.insert(tk.END, message + "\n"))
        self.dialog.after(0, lambda: self.log_text.see(tk.END))
    
    def _clear_log(self):
        """Clear log."""
        self.log_text.delete(1.0, tk.END)
    
    def _export_log(self):
        """Export log."""
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Erfolg", f"Log exportiert: {path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{e}")
    
    def _send_answer(self):
        """Send answer to agent question."""
        answer = self.answer_var.get().strip()
        if not answer:
            messagebox.showwarning("Warnung", "Bitte geben Sie eine Antwort ein")
            return
        
        self.questions_text.insert(tk.END, f"\nAntwort: {answer}\n")
        self.answer_var.set("")
        # Would send to agent in production

