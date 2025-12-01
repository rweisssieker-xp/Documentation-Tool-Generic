#!/usr/bin/env python3
"""
Video Production Example
Complete video tutorial generation workflow.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video import VideoSynthesizer, VideoConfig


def main():
    print("=" * 60)
    print("Video Tutorial Synthesizer - Production Example")
    print("=" * 60)
    
    # Create sample session data
    session_data = {
        "title": "User Registration Tutorial",
        "steps": [
            {
                "action": "Click",
                "description": "Click on Register button",
                "element": "button#register"
            },
            {
                "action": "Type",
                "description": "Enter username",
                "element": "input#username"
            },
            {
                "action": "Type",
                "description": "Enter password",
                "element": "input#password"
            },
            {
                "action": "Click",
                "description": "Submit registration",
                "element": "button#submit"
            }
        ]
    }
    
    # Create dummy screenshots
    screenshots_dir = Path("data/temp_screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    screenshot_paths = []
    from PIL import Image
    for i in range(len(session_data["steps"])):
        img = Image.new('RGB', (1920, 1080), color=(50+i*50, 100, 150))
        path = screenshots_dir / f"step_{i+1}.png"
        img.save(path)
        screenshot_paths.append(path)
    
    print(f"\nCreated {len(screenshot_paths)} dummy screenshots")
    
    # Configure video
    config = VideoConfig(
        frame_rate=30,
        frame_duration=3.0,
        transition_type="ken_burns",
        language="de",
        include_narration=True,
        include_subtitles=True
    )
    
    synthesizer = VideoSynthesizer(config)
    
    # Generate video
    output_path = Path("data/output/tutorial.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nGenerating video...")
    print(f"  Output: {output_path}")
    print(f"  Config: {config.frame_rate} fps, {config.frame_duration}s per screenshot")
    
    success = synthesizer.generate_video(
        session_data,
        screenshot_paths,
        output_path,
        title=session_data["title"]
    )
    
    if success:
        print(f"\n[OK] Video generated: {output_path}")
        print("\nNote: Full video generation requires:")
        print("  - FFmpeg installed and in PATH")
        print("  - OpenAI API Key for narration (optional)")
    else:
        print("\n[WARNING] Video generation failed (FFmpeg may not be available)")
        print("Video frames were generated but rendering failed.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

