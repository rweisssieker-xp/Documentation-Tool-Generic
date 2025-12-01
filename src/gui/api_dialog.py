"""
API Gateway Dialog - GUI für API-First Gateway
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
import threading

from src.api import APIGateway
from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIDialog:
    """Dialog for API Gateway configuration and management"""
    
    def __init__(self, parent):
        """
        Initialize API Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.gateway = None
        self.server_thread = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API-First Gateway")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self._create_config_tab(config_frame)
        
        # Status Tab
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Status")
        self._create_status_tab(status_frame)
        
        # API Docs Tab
        docs_frame = ttk.Frame(notebook)
        notebook.add(docs_frame, text="API Documentation")
        self._create_docs_tab(docs_frame)
    
    def _create_config_tab(self, parent):
        """Create configuration tab"""
        # Title
        title_label = ttk.Label(parent, text="API Gateway Configuration", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Port
        port_frame = ttk.Frame(parent)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8000")
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=10)
        port_entry.pack(side=tk.LEFT, padx=5)
        
        # Enable CORS
        self.cors_var = tk.BooleanVar(value=True)
        cors_check = ttk.Checkbutton(parent, text="Enable CORS", variable=self.cors_var)
        cors_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Enable Auth
        self.auth_var = tk.BooleanVar(value=True)
        auth_check = ttk.Checkbutton(parent, text="Enable Authentication", variable=self.auth_var)
        auth_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Enable Rate Limit
        self.rate_limit_var = tk.BooleanVar(value=True)
        rate_limit_check = ttk.Checkbutton(parent, text="Enable Rate Limiting", variable=self.rate_limit_var)
        rate_limit_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Server", command=self._start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Server", command=self._stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def _create_status_tab(self, parent):
        """Create status tab"""
        # Status text
        self.status_text = scrolledtext.ScrolledText(parent, height=20, width=70)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text.insert(tk.END, "API Gateway Status\n")
        self.status_text.insert(tk.END, "=" * 50 + "\n")
        self.status_text.insert(tk.END, "Status: Stopped\n")
        self.status_text.insert(tk.END, "Port: -\n")
        self.status_text.insert(tk.END, "Endpoints: -\n")
    
    def _create_docs_tab(self, parent):
        """Create API documentation tab"""
        # Docs text
        self.docs_text = scrolledtext.ScrolledText(parent, height=20, width=70)
        self.docs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.docs_text.insert(tk.END, "API Documentation\n")
        self.docs_text.insert(tk.END, "=" * 50 + "\n\n")
        self.docs_text.insert(tk.END, "REST API Endpoints:\n")
        self.docs_text.insert(tk.END, "- GET /api/v1/sessions - List sessions\n")
        self.docs_text.insert(tk.END, "- POST /api/v1/sessions - Create session\n")
        self.docs_text.insert(tk.END, "- GET /api/v1/documents - List documents\n")
        self.docs_text.insert(tk.END, "- POST /api/v1/documents/generate - Generate document\n")
        self.docs_text.insert(tk.END, "- GET /api/v1/knowledge/search - Search knowledge base\n")
        self.docs_text.insert(tk.END, "\nGraphQL Endpoint:\n")
        self.docs_text.insert(tk.END, "- POST /graphql - GraphQL queries\n")
        self.docs_text.insert(tk.END, "\nWebSocket:\n")
        self.docs_text.insert(tk.END, "- WS /ws - Real-time updates\n")
    
    def _start_server(self):
        """Start API server"""
        try:
            port = int(self.port_var.get())
            
            self.gateway = APIGateway(
                enable_cors=self.cors_var.get(),
                enable_auth=self.auth_var.get(),
                enable_rate_limit=self.rate_limit_var.get(),
            )
            
            # Start server in thread
            self.server_thread = threading.Thread(
                target=self.gateway.run,
                kwargs={"host": "0.0.0.0", "port": port},
                daemon=True
            )
            self.server_thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"API Gateway Status\n")
            self.status_text.insert(tk.END, "=" * 50 + "\n")
            self.status_text.insert(tk.END, f"Status: Running\n")
            self.status_text.insert(tk.END, f"Port: {port}\n")
            self.status_text.insert(tk.END, f"URL: http://localhost:{port}\n")
            self.status_text.insert(tk.END, f"OpenAPI: http://localhost:{port}/openapi.json\n")
            
            messagebox.showinfo("Success", f"API Gateway started on port {port}")
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def _stop_server(self):
        """Stop API server"""
        # Note: uvicorn doesn't have a clean stop method in this implementation
        # In production, you'd use a proper server manager
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.status_text.insert(tk.END, "\nServer stopped\n")
        messagebox.showinfo("Info", "Server stop requested (restart application to fully stop)")

