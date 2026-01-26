#!/usr/bin/env python3
"""
Download the Stagehand SEA binary for local browser automation.

This binary is required to run Stagehand in local mode without Browserbase cloud.
Run this once after installing the project.

Usage:
    uv run python scripts/download-stagehand-binary.py
"""

import urllib.request
import json
import os
import sys
from pathlib import Path


def main():
    # Get latest version from GitHub releases
    releases_url = "https://api.github.com/repos/browserbase/stagehand/releases?per_page=100"
    req = urllib.request.Request(releases_url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "stagehand-python/download",
    })
    
    print("Finding latest stagehand-server release...")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            releases = json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching releases: {e}")
        sys.exit(1)
    
    # Find latest stagehand-server/v* tag
    tag = None
    for r in releases:
        t = r.get("tag_name", "")
        if t.startswith("stagehand-server/v"):
            tag = t
            print(f"Found: {tag}")
            break
    
    if not tag:
        print("No stagehand-server releases found")
        sys.exit(1)
    
    # Determine platform
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        plat = "darwin"
    elif system == "windows":
        plat = "win32"
    else:
        plat = "linux"
    
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    
    binary_filename = f"stagehand-server-{plat}-{arch}"
    local_filename = f"stagehand-{plat}-{arch}"
    
    if plat == "win32":
        binary_filename += ".exe"
        local_filename += ".exe"
    
    url = f"https://github.com/browserbase/stagehand/releases/download/{tag}/{binary_filename}"
    
    # Find venv path
    venv_paths = [
        Path(".venv/lib/python3.12/bin/sea"),
        Path(".venv/lib/python3.11/bin/sea"),
        Path(".venv/bin/sea"),
    ]
    
    dest_dir = None
    for p in venv_paths:
        if p.parent.exists() or p.parent.parent.exists():
            dest_dir = p
            break
    
    if not dest_dir:
        dest_dir = Path(".venv/lib/python3.12/bin/sea")
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / local_filename
    
    if dest_path.exists():
        print(f"Binary already exists: {dest_path}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Skipping download.")
            return
    
    print(f"Downloading from {url}...")
    print(f"To: {dest_path}")
    
    try:
        def progress(count, block_size, total_size):
            if total_size > 0:
                percent = count * block_size * 100 / total_size
                mb = count * block_size / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                print(f"\rProgress: {percent:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end="")
        
        urllib.request.urlretrieve(url, dest_path, progress)
        print()
        
        if plat != "win32":
            os.chmod(dest_path, 0o755)
        
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"Downloaded: {dest_path} ({size_mb:.1f} MB)")
        print("\nStagehand is ready for local mode!")
        
    except urllib.error.HTTPError as e:
        print(f"\nError: Failed to download (HTTP {e.code})")
        print(f"URL: {url}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
