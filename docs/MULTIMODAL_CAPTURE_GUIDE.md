# Multi-Modal Capture Engine - User Guide

**Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Target Audience:** Content Creators, Video Producers, Training Developers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Capture Modes](#capture-modes)
4. [Recording Workflow](#recording-workflow)
5. [Synchronization](#synchronization)
6. [Export Options](#export-options)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is Multi-Modal Capture?

Multi-Modal Capture Engine records multiple data streams simultaneously:

- **Video**: Screen recording with high-quality capture
- **Audio**: Microphone recording for narration
- **Mouse Tracking**: Mouse movements and clicks
- **Keyboard Tracking**: Keyboard input and timing

All streams are synchronized to create rich, multi-layered documentation.

### Key Benefits

- **Rich Content**: Combine video, audio, and interaction data
- **Synchronized**: All streams perfectly synchronized
- **Flexible Export**: Export individual streams or combined formats
- **Professional Quality**: High-quality recording for tutorials

---

## Getting Started

### Prerequisites

- Windows 10/11
- Microphone (for audio recording)
- Sufficient disk space (video files can be large)
- OpenCV and sounddevice libraries

### Installation

```bash
pip install opencv-python sounddevice soundfile
```

### Configuration

#### Using GUI

1. Open AHG application
2. Navigate to: **🚀 Innovation** → **🎥 Multi-Modal Capture...**
3. Select output directory
4. Choose capture modes (Video, Audio, Mouse, Keyboard)
5. Click **Start Recording**

#### Using CLI

```bash
# Start recording
python cli/innovation_cli.py multimodal start --output data/recordings

# Stop recording
python cli/innovation_cli.py multimodal stop
```

#### Using Python

```python
from src.multimodal import MultiModalCaptureEngine

engine = MultiModalCaptureEngine()
engine.start_recording("data/recordings")

# ... perform actions ...

synchronized = engine.stop_recording()
```

---

## Capture Modes

### Video Recording

Records screen activity:

```python
from src.multimodal.video.recorder import VideoRecorder

recorder = VideoRecorder(fps=30)
recorder.start("output/video.mp4")
# ... recording ...
video_path = recorder.stop()
```

**Configuration**:
- **FPS**: Frames per second (default: 30)
- **Resolution**: Screen resolution (automatic)
- **Format**: MP4 (H.264)

### Audio Recording

Records microphone input:

```python
from src.multimodal.audio.recorder import AudioRecorder

recorder = AudioRecorder(sample_rate=44100)
recorder.start("output/audio.wav")
# ... recording ...
audio_path = recorder.stop()
```

**Configuration**:
- **Sample Rate**: 44100 Hz (CD quality)
- **Channels**: Mono or Stereo
- **Format**: WAV (uncompressed)

### Mouse Tracking

Tracks mouse movements:

```python
from src.multimodal.sensors.mouse_tracker import MouseTracker

tracker = MouseTracker()
tracker.start()
# ... tracking ...
mouse_data = tracker.stop()
```

**Data Format**:
```python
[
    {"timestamp": 1234567890.1, "x": 100, "y": 200},
    {"timestamp": 1234567890.2, "x": 105, "y": 205},
    ...
]
```

### Keyboard Tracking

Tracks keyboard input:

```python
from src.multimodal.sensors.keyboard_tracker import KeyboardTracker

tracker = KeyboardTracker()
tracker.start()
# ... tracking ...
keyboard_data = tracker.stop()
```

---

## Recording Workflow

### Complete Workflow

```python
from src.multimodal import MultiModalCaptureEngine

# Initialize engine
engine = MultiModalCaptureEngine()

# Start recording
engine.start_recording("data/recordings")

# Perform actions to document
# ... user interactions ...

# Stop recording and synchronize
synchronized = engine.stop_recording()

# Access synchronized streams
video_path = synchronized['video']['path']
audio_path = synchronized['audio']['path']
mouse_data = synchronized['mouse']['data']
keyboard_data = synchronized['keyboard']['data']
```

### Recording Status

Check if recording is active:

```python
if engine.is_recording():
    print("Recording in progress")
else:
    print("Not recording")
```

---

## Synchronization

### How Synchronization Works

All streams are synchronized using timestamps:

1. **Timestamp Alignment**: All streams use same timebase
2. **Frame Matching**: Video frames matched with audio samples
3. **Event Matching**: Mouse/keyboard events matched with video frames
4. **Output Generation**: Synchronized streams exported together

### Synchronized Output

```python
synchronized = engine.stop_recording()

# Synchronized data structure
{
    'video': {
        'path': 'data/recordings/video.mp4',
        'synchronized': True
    },
    'audio': {
        'path': 'data/recordings/audio.wav',
        'synchronized': True
    },
    'mouse': {
        'data': [...],
        'synchronized': True
    },
    'keyboard': {
        'data': [...],
        'synchronized': True
    }
}
```

---

## Export Options

### Video Export

Export synchronized video:

```python
# Video already exported during recording
video_path = synchronized['video']['path']
```

### Audio Export

Export synchronized audio:

```python
audio_path = synchronized['audio']['path']
```

### Combined Export

Create combined video with audio:

```python
# Use video editing tools to combine
# FFmpeg example:
# ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac output.mp4
```

### Interaction Data Export

Export mouse/keyboard data:

```python
import json

# Export mouse data
with open('mouse_data.json', 'w') as f:
    json.dump(synchronized['mouse']['data'], f)

# Export keyboard data
with open('keyboard_data.json', 'w') as f:
    json.dump(synchronized['keyboard']['data'], f)
```

---

## Best Practices

### Recording Quality

1. **Clean Desktop**: Close unnecessary applications
2. **Good Lighting**: Ensure screen is clearly visible
3. **Stable Setup**: Avoid screen resolution changes during recording
4. **Audio Quality**: Use good microphone in quiet environment

### Performance

1. **Disk Space**: Ensure sufficient disk space (video files are large)
2. **CPU Usage**: Recording uses CPU resources
3. **Frame Rate**: Lower FPS for better performance
4. **Resolution**: Consider recording at lower resolution if needed

### Content Creation

1. **Script**: Prepare script before recording
2. **Practice**: Practice workflow before recording
3. **Pauses**: Use pauses for editing later
4. **Annotations**: Add annotations during recording

---

## Troubleshooting

### Video Not Recording

**Problem**: Video file not created

**Solution**:
- Check OpenCV installation
- Verify screen permissions
- Check disk space
- Review error logs

### Audio Not Recording

**Problem**: Audio file empty or missing

**Solution**:
- Check microphone permissions
- Verify microphone is connected
- Check sounddevice installation
- Test microphone in system settings

### Synchronization Issues

**Problem**: Streams not synchronized

**Solution**:
- Ensure all streams started simultaneously
- Check system clock accuracy
- Review synchronization logic
- Manually align if needed

### Performance Issues

**Problem**: Recording causes system slowdown

**Solution**:
- Lower frame rate
- Reduce resolution
- Close other applications
- Use dedicated recording machine

---

## Use Cases

### Video Tutorials

Create professional video tutorials:

```python
engine.start_recording("tutorials/login_tutorial")
# ... demonstrate login process ...
synchronized = engine.stop_recording()
# Combine video + audio + annotations
```

### Training Materials

Create interactive training materials:

```python
# Record with mouse/keyboard tracking
engine.start_recording("training/user_onboarding")
# ... training session ...
synchronized = engine.stop_recording()
# Export with interaction data for analysis
```

### Documentation Videos

Create documentation videos:

```python
# Record documentation process
engine.start_recording("docs/feature_demo")
# ... document feature ...
synchronized = engine.stop_recording()
# Export for documentation site
```

---

## Additional Resources

- [Video Editing Guide](./VIDEO_EDITING.md)
- [Audio Processing](./AUDIO_PROCESSING.md)
- [Interaction Analysis](./INTERACTION_ANALYSIS.md)
- [Export Formats](./EXPORT_FORMATS.md)

---

**Document Version:** 3.0.0  
**Last Updated:** 2025-12-01  
**Maintained By:** Technical Writing Team



