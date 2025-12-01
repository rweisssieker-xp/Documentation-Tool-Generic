# Blockchain Audit Trail - User Guide

**Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Target Audience:** Compliance Officers, Auditors, Enterprise Administrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Supported Blockchains](#supported-blockchains)
4. [Storing Document Hashes](#storing-document-hashes)
5. [Verifying Documents](#verifying-documents)
6. [Batch Operations](#batch-operations)
7. [Merkle Trees](#merkle-trees)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Blockchain Audit Trail?

The Blockchain Audit Trail provides immutable verification for documentation through blockchain technology. Each document version is stored on the blockchain, enabling:

- **Immutable Records**: Documents cannot be altered without detection
- **Compliance**: Meet regulatory requirements for audit trails
- **Verification**: Verify document integrity at any time
- **Multi-Party Trust**: Multiple parties can verify documents independently
- **Legal Proof**: Provide legal proof of document existence and integrity

### How It Works

1. **Hash Creation**: Document content is hashed using SHA-256
2. **Blockchain Storage**: Hash is stored on blockchain (Ethereum/Polygon)
3. **Verification**: Document can be verified by comparing current hash with stored hash
4. **Immutable Proof**: Blockchain provides cryptographic proof of document state

---

## Getting Started

### Prerequisites

- Python 3.10+
- Web3 library: `pip install web3 eth-account`
- Blockchain account (optional, for private key signing)
- Network connection (for blockchain access)

### Installation

```bash
pip install web3 eth-account
```

### Configuration

#### Using GUI

1. Open AHG application
2. Navigate to: **🚀 Innovation** → **🔗 Blockchain Audit...**
3. Select blockchain (Ethereum/Polygon)
4. Enter private key (optional)
5. Click **Initialize Blockchain**

#### Using CLI

```bash
# Initialize Polygon (recommended, lower fees)
python cli/innovation_cli.py blockchain init --chain polygon

# Initialize Ethereum
python cli/innovation_cli.py blockchain init --chain ethereum
```

#### Using Python

```python
from src.blockchain import BlockchainAuditTrail, BlockchainType

# Initialize Polygon
blockchain = BlockchainAuditTrail(
    blockchain_type=BlockchainType.POLYGON,
    private_key=None  # Optional, for signing transactions
)
```

---

## Supported Blockchains

### Polygon

**Recommended for most use cases**

- **Advantages**: Lower transaction fees, faster confirmation
- **Network**: Polygon Mainnet
- **RPC URL**: `https://polygon-rpc.com`
- **Use Case**: High-volume document verification

### Ethereum

**For maximum security and decentralization**

- **Advantages**: Most secure, widely recognized
- **Network**: Ethereum Mainnet
- **RPC URL**: `https://eth.llamarpc.com`
- **Use Case**: Critical compliance requirements

### Private Blockchain (Planned)

For enterprise deployments requiring complete control.

---

## Storing Document Hashes

### Basic Usage

#### Using GUI

1. Open Blockchain Audit dialog
2. Navigate to **Store Hash** tab
3. Select document file
4. Click **Store Hash on Blockchain**
5. Copy transaction hash for verification

#### Using CLI

```bash
python cli/innovation_cli.py blockchain store --file document.pdf
```

Output:

```
Document Hash: 9a5736fd6959125e...
Transaction Hash: 0x1234abcd...
```

#### Using Python

```python
from src.blockchain import BlockchainAuditTrail, BlockchainType
from pathlib import Path

blockchain = BlockchainAuditTrail(blockchain_type=BlockchainType.POLYGON)

# Read document
doc_path = Path("document.pdf")
with open(doc_path, 'rb') as f:
    content = f.read()

# Create hash
doc_hash = blockchain.create_document_hash(content)

# Store on blockchain
tx_hash = blockchain.store_hash(doc_hash, metadata={
    "filename": "document.pdf",
    "version": "1.0"
})

print(f"Document hash: {doc_hash}")
print(f"Transaction hash: {tx_hash}")
```

### Metadata

You can include metadata with the hash:

```python
tx_hash = blockchain.store_hash(
    doc_hash,
    metadata={
        "document_id": "DOC-001",
        "author": "John Doe",
        "version": "1.0",
        "created_at": "2025-12-01T12:00:00Z"
    }
)
```

---

## Verifying Documents

### Basic Verification

#### Using GUI

1. Open Blockchain Audit dialog
2. Navigate to **Verify** tab
3. Enter transaction hash
4. Select document file
5. Click **Verify Document**

#### Using CLI

```bash
python cli/innovation_cli.py blockchain verify \
  --file document.pdf \
  --tx 0x1234abcd...
```

#### Using Python

```python
from src.blockchain import BlockchainAuditTrail, BlockchainType
from pathlib import Path

blockchain = BlockchainAuditTrail(blockchain_type=BlockchainType.POLYGON)

# Read document
doc_path = Path("document.pdf")
with open(doc_path, 'rb') as f:
    content = f.read()

# Create current hash
current_hash = blockchain.create_document_hash(content)

# Verify against blockchain
tx_hash = "0x1234abcd..."  # From storage
is_valid = blockchain.verify_hash(current_hash, tx_hash)

if is_valid:
    print("Document is valid - no changes detected")
else:
    print("Document is invalid - changes detected!")
```

---

## Batch Operations

### Batch Storage with Merkle Tree

For multiple documents, use Merkle Tree for efficient batch storage:

```python
from src.blockchain import BlockchainAuditTrail, BlockchainType
from pathlib import Path

blockchain = BlockchainAuditTrail(blockchain_type=BlockchainType.POLYGON)

# Create hashes for multiple documents
documents = [
    "document1.pdf",
    "document2.pdf",
    "document3.pdf"
]

hashes = []
for doc_path in documents:
    with open(doc_path, 'rb') as f:
        content = f.read()
    doc_hash = blockchain.create_document_hash(content)
    hashes.append(doc_hash)

# Batch store using Merkle Tree
tx_hash = blockchain.batch_store(hashes)
print(f"Merkle root stored: {tx_hash}")
```

### Merkle Tree Benefits

- **Efficiency**: Single transaction for multiple documents
- **Cost Savings**: Lower transaction fees
- **Verification**: Individual documents can still be verified
- **Scalability**: Handle hundreds of documents efficiently

---

## Merkle Trees

### How Merkle Trees Work

A Merkle Tree creates a single root hash from multiple document hashes:

```
        Root Hash
       /         \
   Hash1+2      Hash3+4
   /    \       /    \
Hash1  Hash2  Hash3  Hash4
```

### Creating Merkle Tree

```python
from src.blockchain.hashing.merkle_tree import MerkleTree

tree = MerkleTree()
hashes = ["hash1", "hash2", "hash3", "hash4"]
root = tree.create_tree(hashes)
print(f"Merkle root: {root}")
```

### Verifying with Merkle Proof

```python
from src.blockchain.hashing.merkle_tree import MerkleTree

tree = MerkleTree()
merkle_root = "root_hash_from_blockchain"
document_hash = "hash1"
proof = ["hash2", "hash3+4"]  # Sibling hashes

is_valid = tree.verify_proof(document_hash, merkle_root, proof)
```

---

## Best Practices

### Document Management

1. **Version Control**: Store hash for each document version
2. **Metadata**: Include meaningful metadata for traceability
3. **Batch Storage**: Use Merkle Trees for multiple documents
4. **Regular Verification**: Periodically verify document integrity

### Security

1. **Private Keys**: Never share private keys
2. **Hash Storage**: Only store hashes, not document content
3. **Verification**: Always verify before trusting documents
4. **Backup**: Keep transaction hashes in secure storage

### Cost Optimization

1. **Use Polygon**: Lower fees than Ethereum
2. **Batch Operations**: Use Merkle Trees for multiple documents
3. **Metadata Size**: Keep metadata minimal to reduce gas costs
4. **Timing**: Consider gas prices when storing

---

## Troubleshooting

### Connection Errors

**Problem**: Cannot connect to blockchain

**Solution**:
- Check internet connection
- Verify RPC URL is accessible
- Try alternative RPC endpoint

### Transaction Failures

**Problem**: Transaction fails

**Solution**:
- Check account balance (for gas fees)
- Verify private key is correct
- Ensure sufficient gas limit

### Verification Failures

**Problem**: Document verification fails

**Solution**:
- Verify document hasn't been modified
- Check transaction hash is correct
- Ensure using same blockchain network

---

## Use Cases

### Compliance Documentation

Store audit trails for regulatory compliance:

```python
# Store compliance document
tx_hash = blockchain.store_hash(
    doc_hash,
    metadata={
        "type": "compliance",
        "regulation": "GDPR",
        "audit_date": "2025-12-01"
    }
)
```

### Legal Documentation

Provide legal proof of document existence:

```python
# Store legal document with timestamp
tx_hash = blockchain.store_hash(
    doc_hash,
    metadata={
        "type": "legal",
        "document_type": "contract",
        "parties": ["Party A", "Party B"]
    }
)
```

### Version Control

Track document versions:

```python
# Store each version
for version in range(1, 5):
    doc_hash = blockchain.create_document_hash(document_content)
    tx_hash = blockchain.store_hash(
        doc_hash,
        metadata={"version": version}
    )
```

---

## Additional Resources

- [Blockchain Basics](./BLOCKCHAIN_BASICS.md)
- [Smart Contract Integration](./SMART_CONTRACTS.md)
- [Cost Estimation](./BLOCKCHAIN_COSTS.md)
- [Enterprise Deployment](./ENTERPRISE_BLOCKCHAIN.md)

---

**Document Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Maintained By:** Technical Writing Team


