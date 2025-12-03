"""
Plugin System Dialog - GUI für Plugin-System & Marketplace
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from pathlib import Path

from src.plugins import PluginManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PluginDialog:
    """Dialog for Plugin System management"""
    
    def __init__(self, parent):
        """
        Initialize Plugin Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.plugin_manager = PluginManager()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Plugin System & Marketplace")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        self._create_widgets()
        self._refresh_plugin_list()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Installed Plugins Tab
        installed_frame = ttk.Frame(notebook)
        notebook.add(installed_frame, text="Installed Plugins")
        self._create_installed_tab(installed_frame)
        
        # Marketplace Tab
        marketplace_frame = ttk.Frame(notebook)
        notebook.add(marketplace_frame, text="Marketplace")
        self._create_marketplace_tab(marketplace_frame)
    
    def _create_installed_tab(self, parent):
        """Create installed plugins tab"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Load Plugin", command=self._load_plugin).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Unload Plugin", command=self._unload_plugin).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_plugin_list).pack(side=tk.LEFT, padx=2)
        
        # Plugin list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for plugins
        columns = ("ID", "Name", "Version", "Author", "Status")
        self.plugin_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.plugin_tree.heading(col, text=col)
            self.plugin_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Plugin details
        details_frame = ttk.LabelFrame(parent, text="Plugin Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.details_text = tk.Text(details_frame, height=8, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.plugin_tree.bind("<<TreeviewSelect>>", self._on_plugin_select)
    
    def _create_marketplace_tab(self, parent):
        """Create marketplace tab"""
        # Search
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self._search_plugins).pack(side=tk.LEFT, padx=5)
        
        # Marketplace list
        marketplace_list_frame = ttk.Frame(parent)
        marketplace_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.marketplace_text = tk.Text(marketplace_list_frame, wrap=tk.WORD)
        self.marketplace_text.pack(fill=tk.BOTH, expand=True)
        
        self.marketplace_text.insert(tk.END, "Plugin Marketplace\n")
        self.marketplace_text.insert(tk.END, "=" * 50 + "\n\n")
        self.marketplace_text.insert(tk.END, "Marketplace functionality coming soon!\n")
        self.marketplace_text.insert(tk.END, "You can load plugins from local files using 'Load Plugin'.\n")
    
    def _load_plugin(self):
        """Load plugin from file"""
        file_path = filedialog.askopenfilename(
            title="Select Plugin File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                success = self.plugin_manager.load_plugin(file_path)
                if success:
                    messagebox.showinfo("Success", "Plugin loaded successfully")
                    self._refresh_plugin_list()
                else:
                    messagebox.showerror("Error", "Failed to load plugin")
            except Exception as e:
                logger.error(f"Error loading plugin: {e}")
                messagebox.showerror("Error", f"Error loading plugin: {e}")
    
    def _unload_plugin(self):
        """Unload selected plugin"""
        selection = self.plugin_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to unload")
            return
        
        item = self.plugin_tree.item(selection[0])
        plugin_id = item['values'][0]
        
        try:
            success = self.plugin_manager.unload_plugin(plugin_id)
            if success:
                messagebox.showinfo("Success", "Plugin unloaded successfully")
                self._refresh_plugin_list()
            else:
                messagebox.showerror("Error", "Failed to unload plugin")
        except Exception as e:
            logger.error(f"Error unloading plugin: {e}")
            messagebox.showerror("Error", f"Error unloading plugin: {e}")
    
    def _refresh_plugin_list(self):
        """Refresh plugin list"""
        # Clear existing items
        for item in self.plugin_tree.get_children():
            self.plugin_tree.delete(item)
        
        # Load plugins
        self.plugin_manager.load_all_plugins()
        plugins = self.plugin_manager.list_plugins()
        
        for plugin in plugins:
            metadata = plugin.get('metadata', {})
            self.plugin_tree.insert(
                "",
                tk.END,
                values=(
                    plugin.get('id', 'unknown'),
                    metadata.get('name', 'Unknown'),
                    metadata.get('version', '1.0.0'),
                    metadata.get('author', 'Unknown'),
                    'Loaded' if plugin.get('loaded') else 'Not Loaded',
                )
            )
    
    def _on_plugin_select(self, event):
        """Handle plugin selection"""
        selection = self.plugin_tree.selection()
        if not selection:
            return
        
        item = self.plugin_tree.item(selection[0])
        plugin_id = item['values'][0]
        
        plugin = self.plugin_manager.get_plugin(plugin_id)
        metadata = self.plugin_manager.plugin_metadata.get(plugin_id, {})
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, f"Plugin ID: {plugin_id}\n")
        self.details_text.insert(tk.END, f"Name: {metadata.get('name', 'Unknown')}\n")
        self.details_text.insert(tk.END, f"Version: {metadata.get('version', '1.0.0')}\n")
        self.details_text.insert(tk.END, f"Author: {metadata.get('author', 'Unknown')}\n")
        self.details_text.insert(tk.END, f"\nDescription:\n{metadata.get('description', 'No description')}\n")
    
    def _search_plugins(self):
        """Search plugins in marketplace"""
        query = self.search_var.get()
        if not query:
            return
        
        # Placeholder - would search marketplace
        self.marketplace_text.insert(tk.END, f"\nSearching for: {query}...\n")
        self.marketplace_text.insert(tk.END, "Marketplace search coming soon!\n")






