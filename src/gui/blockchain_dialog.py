"""
Blockchain Dialog - GUI für Blockchain Audit Trail
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path

from src.blockchain import BlockchainAuditTrail, BlockchainType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BlockchainDialog:
    """Dialog for Blockchain Audit Trail"""
    
    def __init__(self, parent):
        """
        Initialize Blockchain Dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self.blockchain = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Blockchain Audit Trail")
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
        
        # Store Hash Tab
        store_frame = ttk.Frame(notebook)
        notebook.add(store_frame, text="Store Hash")
        self._create_store_tab(store_frame)
        
        # Verify Tab
        verify_frame = ttk.Frame(notebook)
        notebook.add(verify_frame, text="Verify")
        self._create_verify_tab(verify_frame)
    
    def _create_config_tab(self, parent):
        """Create configuration tab"""
        # Blockchain Type
        chain_frame = ttk.LabelFrame(parent, text="Blockchain Selection")
        chain_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.blockchain_type_var = tk.StringVar(value="polygon")
        ttk.Radiobutton(chain_frame, text="Ethereum", variable=self.blockchain_type_var, value="ethereum").pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(chain_frame, text="Polygon", variable=self.blockchain_type_var, value="polygon").pack(anchor=tk.W, padx=5)
        
        # Private Key (optional)
        key_frame = ttk.Frame(parent)
        key_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(key_frame, text="Private Key (optional):").pack(side=tk.LEFT)
        self.private_key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.private_key_var, width=40, show="*").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Initialize Button
        ttk.Button(parent, text="Initialize Blockchain", command=self._initialize_blockchain).pack(pady=10)
        
        # Status
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text.insert(tk.END, "Blockchain Status\n")
        self.status_text.insert(tk.END, "=" * 50 + "\n")
        self.status_text.insert(tk.END, "Status: Not Initialized\n")
    
    def _create_store_tab(self, parent):
        """Create store hash tab"""
        # Document selection
        doc_frame = ttk.Frame(parent)
        doc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(doc_frame, text="Document:").pack(side=tk.LEFT)
        self.document_path_var = tk.StringVar()
        ttk.Entry(doc_frame, textvariable=self.document_path_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(doc_frame, text="Browse", command=self._browse_document).pack(side=tk.LEFT, padx=5)
        
        # Store Button
        ttk.Button(parent, text="Store Hash on Blockchain", command=self._store_hash).pack(pady=10)
        
        # Result
        result_frame = ttk.LabelFrame(parent, text="Transaction Hash")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tx_hash_text = scrolledtext.ScrolledText(result_frame, height=5, wrap=tk.WORD)
        self.tx_hash_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_verify_tab(self, parent):
        """Create verify tab"""
        # Transaction Hash
        tx_frame = ttk.Frame(parent)
        tx_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(tx_frame, text="Transaction Hash:").pack(side=tk.LEFT)
        self.tx_hash_var = tk.StringVar()
        ttk.Entry(tx_frame, textvariable=self.tx_hash_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Document
        doc_frame = ttk.Frame(parent)
        doc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(doc_frame, text="Document:").pack(side=tk.LEFT)
        self.verify_doc_path_var = tk.StringVar()
        ttk.Entry(doc_frame, textvariable=self.verify_doc_path_var, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(doc_frame, text="Browse", command=self._browse_verify_document).pack(side=tk.LEFT, padx=5)
        
        # Verify Button
        ttk.Button(parent, text="Verify Document", command=self._verify_document).pack(pady=10)
        
        # Result
        result_frame = ttk.LabelFrame(parent, text="Verification Result")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.verify_result_text = scrolledtext.ScrolledText(result_frame, height=10, wrap=tk.WORD)
        self.verify_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _initialize_blockchain(self):
        """Initialize blockchain"""
        try:
            chain_type_str = self.blockchain_type_var.get()
            chain_type = BlockchainType.ETHEREUM if chain_type_str == "ethereum" else BlockchainType.POLYGON
            private_key = self.private_key_var.get() if self.private_key_var.get() else None
            
            self.blockchain = BlockchainAuditTrail(
                blockchain_type=chain_type,
                private_key=private_key,
            )
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "Blockchain Status\n")
            self.status_text.insert(tk.END, "=" * 50 + "\n")
            self.status_text.insert(tk.END, f"Status: Initialized\n")
            self.status_text.insert(tk.END, f"Blockchain: {chain_type_str.title()}\n")
            self.status_text.insert(tk.END, f"Private Key: {'Set' if private_key else 'Not Set'}\n")
            
            messagebox.showinfo("Success", "Blockchain initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing blockchain: {e}")
            messagebox.showerror("Error", f"Failed to initialize blockchain: {e}")
    
    def _browse_document(self):
        """Browse for document"""
        file_path = filedialog.askopenfilename(title="Select Document")
        if file_path:
            self.document_path_var.set(file_path)
    
    def _browse_verify_document(self):
        """Browse for verify document"""
        file_path = filedialog.askopenfilename(title="Select Document")
        if file_path:
            self.verify_doc_path_var.set(file_path)
    
    def _store_hash(self):
        """Store document hash on blockchain"""
        if not self.blockchain:
            messagebox.showwarning("Warning", "Please initialize blockchain first")
            return
        
        doc_path = self.document_path_var.get()
        if not doc_path:
            messagebox.showwarning("Warning", "Please select a document")
            return
        
        try:
            # Read document and create hash
            with open(doc_path, 'rb') as f:
                content = f.read()
            
            doc_hash = self.blockchain.create_document_hash(content)
            tx_hash = self.blockchain.store_hash(doc_hash)
            
            self.tx_hash_text.delete(1.0, tk.END)
            self.tx_hash_text.insert(tk.END, f"Document Hash: {doc_hash}\n")
            self.tx_hash_text.insert(tk.END, f"Transaction Hash: {tx_hash}\n")
            
            messagebox.showinfo("Success", f"Hash stored on blockchain!\nTransaction: {tx_hash}")
        except Exception as e:
            logger.error(f"Error storing hash: {e}")
            messagebox.showerror("Error", f"Failed to store hash: {e}")
    
    def _verify_document(self):
        """Verify document against blockchain"""
        if not self.blockchain:
            messagebox.showwarning("Warning", "Please initialize blockchain first")
            return
        
        tx_hash = self.tx_hash_var.get()
        doc_path = self.verify_doc_path_var.get()
        
        if not tx_hash or not doc_path:
            messagebox.showwarning("Warning", "Please provide transaction hash and document")
            return
        
        try:
            # Read document and create hash
            with open(doc_path, 'rb') as f:
                content = f.read()
            
            doc_hash = self.blockchain.create_document_hash(content)
            is_valid = self.blockchain.verify_hash(doc_hash, tx_hash)
            
            self.verify_result_text.delete(1.0, tk.END)
            self.verify_result_text.insert(tk.END, f"Document Hash: {doc_hash}\n")
            self.verify_result_text.insert(tk.END, f"Transaction Hash: {tx_hash}\n")
            self.verify_result_text.insert(tk.END, f"\nVerification: {'VALID' if is_valid else 'INVALID'}\n")
            
            if is_valid:
                messagebox.showinfo("Success", "Document verified successfully!")
            else:
                messagebox.showwarning("Warning", "Document verification failed!")
        except Exception as e:
            logger.error(f"Error verifying document: {e}")
            messagebox.showerror("Error", f"Failed to verify document: {e}")

