#!/usr/bin/env python3
"""
Download required models for Sentinel
"""

import os
import sys
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODELS = {
    "yolov8n.onnx": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.onnx"
}


def download_file(url: str, dest: Path):
    """Download file with progress"""
    print(f"📥 Downloading {dest.name}...")
    print(f"   From: {url}")

    try:
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            print(f"\r   [{bar}] {percent:.1f}%", end='', flush=True)

        urllib.request.urlretrieve(url, dest, reporthook=progress)
        print()  # New line after progress
        print(f"✅ Downloaded: {dest}")
        return True

    except Exception as e:
        print(f"\n❌ Failed to download {dest.name}: {e}", file=sys.stderr)
        return False


def main():
    """Download all required models"""
    print("🛡️  Sentinel Model Downloader")
    print("=" * 50)
    print()

    success_count = 0

    for filename, url in MODELS.items():
        dest = MODELS_DIR / filename

        if dest.exists():
            size_mb = dest.stat().st_size / 1024 / 1024
            print(f"⏭️  {filename} already exists ({size_mb:.1f} MB)")
            success_count += 1
            continue

        if download_file(url, dest):
            success_count += 1
        print()

    print("=" * 50)
    print(f"✅ {success_count}/{len(MODELS)} models ready")

    if success_count == len(MODELS):
        print("\n🎉 All models downloaded successfully!")
        print("\nNext steps:")
        print("  1. Install Ollama models: ollama pull qwen2.5:3b")
        print("  2. Install Ollama models: ollama pull moondream")
        print("  3. Test: ltl status")
    else:
        print("\n⚠️  Some models failed to download")
        print("You can manually download them from:")
        for filename, url in MODELS.items():
            print(f"  {filename}: {url}")
        sys.exit(1)


if __name__ == "__main__":
    main()
