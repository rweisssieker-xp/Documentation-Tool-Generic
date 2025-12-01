# Edge AI Engine - User Guide

**Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Target Audience:** Privacy-Conscious Users, Enterprise Administrators, Developers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Supported Models](#supported-models)
4. [Configuration](#configuration)
5. [Text Generation](#text-generation)
6. [Speech-to-Text](#speech-to-text)
7. [Embeddings](#embeddings)
8. [Model Management](#model-management)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Edge AI?

Edge AI Engine enables on-device AI processing without cloud dependency. All AI operations run locally on your machine, ensuring:

- **Privacy**: No data leaves your device
- **GDPR Compliance**: Perfect for regulated industries
- **Cost Savings**: No API costs
- **Offline Operation**: Works without internet connection
- **Custom Models**: Use your own trained models

### Supported AI Capabilities

- **Text Generation**: Local LLMs (Llama, Mistral, Phi-3)
- **Speech-to-Text**: Local Whisper models
- **Embeddings**: Local sentence transformers
- **Vision**: Local CLIP models (planned)

---

## Getting Started

### Prerequisites

#### Hardware Requirements

- **CPU**: Modern multi-core processor recommended
- **GPU**: Optional but recommended for faster inference
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 10GB+ for models

#### Software Requirements

- Python 3.10+
- CUDA (optional, for GPU acceleration)
- Model files (download separately)

### Installation

#### Install Dependencies

```bash
pip install llama-cpp-python transformers openai-whisper sentence-transformers torch
```

#### GPU Support (Optional)

For GPU acceleration:

```bash
# CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA-enabled llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

### Download Models

#### Llama Models

Download from Hugging Face or official sources:

```bash
# Example: Llama 3 8B
# Download to: data/models/llama-3-8b.gguf
```

#### Mistral Models

```bash
# Example: Mistral 7B
# Download to: data/models/mistral-7b-instruct-v0.2.gguf
```

#### Whisper Models

Whisper models are downloaded automatically on first use, or download manually:

```bash
# Models: tiny, base, small, medium, large
# Stored in: ~/.cache/whisper/
```

---

## Supported Models

### Text Generation Models

#### Llama 3

- **Model Sizes**: 8B, 70B
- **Format**: GGUF
- **Use Case**: General text generation
- **Performance**: Fast inference, good quality

#### Mistral 7B

- **Model Size**: 7B
- **Format**: GGUF or Transformers
- **Use Case**: Instruction following, chat
- **Performance**: Excellent quality, moderate speed

#### Phi-3 (Planned)

- **Model Sizes**: 3.8B, 7B, 14B
- **Format**: GGUF
- **Use Case**: Lightweight, efficient
- **Performance**: Fast, good for edge devices

### Speech-to-Text Models

#### OpenAI Whisper

- **Model Sizes**: tiny, base, small, medium, large
- **Languages**: 99+ languages
- **Use Case**: Audio transcription
- **Performance**: Large model provides best accuracy

### Embedding Models

#### Sentence Transformers

- **Models**: all-MiniLM-L6-v2, all-mpnet-base-v2
- **Use Case**: Semantic search, similarity
- **Performance**: Fast, good quality embeddings

---

## Configuration

### Using GUI

1. Open AHG application
2. Navigate to: **🚀 Innovation** → **⚡ Edge AI Engine...**
3. Select model type (Llama/Mistral)
4. Specify model path (optional, uses default if not specified)
5. Enable/disable GPU acceleration
6. Click **Initialize Engine**

### Using CLI

```bash
# Initialize with Llama
python cli/innovation_cli.py edgeai init --model llama --path data/models/llama-3-8b.gguf

# Initialize with Mistral
python cli/innovation_cli.py edgeai init --model mistral --path data/models/mistral-7b.gguf
```

### Using Python

```python
from src.edge_ai import EdgeAIEngine, ModelType

# Initialize with Llama
engine = EdgeAIEngine(
    model_type=ModelType.LLAMA,
    model_path="data/models/llama-3-8b.gguf",
    use_gpu=True
)

# Check availability
if engine.is_available():
    print("Edge AI Engine ready")
```

---

## Text Generation

### Basic Usage

#### Using CLI

```bash
python cli/innovation_cli.py edgeai generate \
  --prompt "Explain how to create documentation" \
  --tokens 200
```

#### Using Python

```python
from src.edge_ai import EdgeAIEngine, ModelType

engine = EdgeAIEngine(model_type=ModelType.LLAMA)
generated = engine.generate_text(
    prompt="Write a step-by-step guide for:",
    max_tokens=500
)
print(generated)
```

### Advanced Options

```python
# Custom temperature and top_p
# (Requires model-specific implementation)
generated = engine.generate_text(
    prompt="Your prompt here",
    max_tokens=500,
    temperature=0.7,
    top_p=0.9
)
```

---

## Speech-to-Text

### Basic Usage

#### Using Python

```python
from src.edge_ai import LocalWhisper

whisper = LocalWhisper(model_size="base", use_gpu=True)
transcription = whisper.transcribe(
    audio_file="recording.wav",
    language="de"
)
print(transcription)
```

### Supported Languages

Whisper supports 99+ languages. Common codes:

- `de` - German
- `en` - English
- `fr` - French
- `es` - Spanish
- `it` - Italian
- `pt` - Portuguese

### Audio Format

Supported formats:
- WAV (recommended)
- MP3
- M4A
- FLAC

---

## Embeddings

### Basic Usage

```python
from src.edge_ai import LocalEmbeddings

embeddings = LocalEmbeddings(model_name="all-MiniLM-L6-v2")
vector = embeddings.embed("This is a sample text")
print(f"Embedding dimension: {len(vector)}")
```

### Batch Processing

```python
texts = [
    "First document",
    "Second document",
    "Third document"
]
vectors = embeddings.embed_batch(texts)
```

---

## Model Management

### Model Manager

```python
from src.edge_ai import ModelManager

manager = ModelManager()

# Register model
manager.register_model(
    model_id="my_llama",
    model_path="data/models/llama-3-8b.gguf",
    model_type="llama",
    metadata={
        "size": "8B",
        "format": "GGUF"
    }
)

# List models
models = manager.list_models()
for model in models:
    print(f"{model['type']}: {model['path']}")
```

---

## Performance Optimization

### GPU Acceleration

Enable GPU for faster inference:

```python
engine = EdgeAIEngine(
    model_type=ModelType.LLAMA,
    use_gpu=True  # Enable GPU
)
```

### Model Quantization

Use quantized models for better performance:

- **Q4_K_M**: Good balance of quality and speed
- **Q5_K_M**: Better quality, slightly slower
- **Q8_0**: Best quality, slower

### Batch Processing

Process multiple requests in batch:

```python
# Batch embeddings
vectors = embeddings.embed_batch(texts)

# Batch generation (model-dependent)
# Check model documentation for batch support
```

---

## Troubleshooting

### Model Not Loading

**Problem**: Model file not found

**Solution**: 
- Verify model path is correct
- Check file permissions
- Ensure model format is supported

### Out of Memory

**Problem**: `CUDA out of memory` or system RAM exhausted

**Solution**:
- Use smaller model
- Enable model quantization
- Reduce batch size
- Close other applications

### Slow Performance

**Problem**: Inference is slow

**Solution**:
- Enable GPU acceleration
- Use quantized models
- Reduce `max_tokens`
- Use smaller model size

### GPU Not Detected

**Problem**: GPU not being used

**Solution**:
- Verify CUDA installation: `nvidia-smi`
- Install CUDA-enabled PyTorch
- Check GPU compatibility
- Fall back to CPU if GPU unavailable

---

## Best Practices

1. **Model Selection**: Choose model size based on hardware capabilities
2. **Quantization**: Use quantized models for better performance
3. **Caching**: Cache embeddings for repeated queries
4. **Batch Processing**: Process multiple items together when possible
5. **Error Handling**: Implement fallback to cloud AI if Edge AI fails

---

## Additional Resources

- [Model Download Links](./MODEL_DOWNLOADS.md)
- [Performance Benchmarks](./PERFORMANCE_BENCHMARKS.md)
- [GPU Setup Guide](./GPU_SETUP.md)
- [Model Fine-Tuning](./MODEL_FINE_TUNING.md)

---

**Document Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Maintained By:** Technical Writing Team


