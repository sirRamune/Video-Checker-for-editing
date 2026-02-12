#!/usr/bin/env python3
"""
Video File Scanner
Scans directories for video files and outputs their paths to a text file.
"""

import os
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv

from utils import get_array_from_env_and_file


def load_config():
    """Load configuration from .env file."""
    load_dotenv()

    # Get video extensions from config
    extensions_str = os.getenv('VIDEO_EXTENSIONS', '.mp4,.avi,.mkv,.mov,.wmv,.flv,.webm,.m4v,.mpg,.mpeg')
    extensions = [ext.strip().lower() for ext in extensions_str.split(',')]

    # Get paths from config or file
    scan_paths_str = os.getenv('SCAN_PATHS', '')
    paths_file = os.getenv('PATHS_FILE', 'paths.txt')
    exclusions_str = os.getenv('EXCLUSIONS', '')
    exclusions_file = os.getenv('EXCLUSIONS_FILE', 'exclusions.txt')
    output_file = os.getenv('OUTPUT_FILE', 'video_files.txt')

    return extensions, scan_paths_str, paths_file, exclusions_str, exclusions_file, output_file


def scan_for_videos(directory: str, extensions: Set[str], exclusions: List[str]) -> List[Path]:
    """Recursively scan directory for video files."""
    video_files = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Warning: Directory does not exist: {directory}")
        return video_files

    if not dir_path.is_dir():
        print(f"Warning: Not a directory: {directory}")
        return video_files

    print(f"Scanning: {directory}")

    try:
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() in extensions:
                    if not any(exclusion.lower() in file_path.as_posix().lower() for exclusion in exclusions):
                        video_files.append(file_path)
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except Exception as e:
        print(f"Error scanning {directory}: {e}")

    return video_files


def write_results(video_files: List[Path], output_file: str):
    """Write video file paths to output file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for video_path in sorted(video_files):
            f.write(f"{video_path.absolute()}\n")

    print(f"\nResults written to: {output_file}")
    print(f"Total video files found: {len(video_files)}")


def main():
    """Main function to scan for video files."""
    print("Video File Scanner")
    print("=" * 50)

    # Load configuration
    extensions, scan_paths_str, paths_file, exclusions_str, exclusions_file, output_file = load_config()
    extensions_set = set(extensions)

    print(f"Looking for extensions: {', '.join(extensions)}")
    print()

    # Get paths to scan
    scan_paths = get_array_from_env_and_file(scan_paths_str, paths_file, 'path')

    if not scan_paths:
        print("Error: No paths to scan. Please configure SCAN_PATHS in .env or create paths.txt")
        return

    # Get exclusions
    exclusions = get_array_from_env_and_file(exclusions_str, exclusions_file, 'exclusion')
    print()

    # Scan all directories
    all_videos = []
    for path in scan_paths:
        videos = scan_for_videos(path, extensions_set, exclusions)
        all_videos.extend(videos)
        print(f"  Found {len(videos)} video(s) in this directory")

    # Write results
    if all_videos:
        write_results(all_videos, output_file)
    else:
        print("\nNo video files found.")


if __name__ == "__main__":
    main()
