#!/usr/bin/env python3
"""
Video File Scanner
Scans directories for video files and outputs their paths to a text file.
"""

import os
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv

from utils import read_lines_from_file


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


def get_scan_paths(scan_paths_str: str, paths_file: str) -> List[str]:
    """Get list of paths to scan from config or file."""
    paths = []

    # First, try to get paths from environment variable
    if scan_paths_str:
        paths = [p.strip() for p in scan_paths_str.split(',') if p.strip()]
        print(f"Using {len(paths)} path(s) from .env")
    else:
        print(f"Warning: No paths specified in .env") 
    
    print()
    
    # Then, read from file
    paths.extend(read_lines_from_file(paths_file, 'path'))

    return paths


def get_exclusions(exclusions_str: str, exclusions_file: str) -> List[str]:
    """Get list of exclusions from config or file."""
    exclusions = []

    # First, try to get paths from environment variable
    if exclusions_str:
        exclusions_str = [p.strip() for p in exclusions_str.split(',') if p.strip()]
        print(f"Using {len(exclusions)} exclusion(s) from .env")
    else:
        print(f"Warning: No exclusions specified in .env") 
    
    print()
    
    # Then, read from file
    exclusions.extend(read_lines_from_file(exclusions_file, 'exclusion'))

    return exclusions


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
    scan_paths = get_scan_paths(scan_paths_str, paths_file)

    if not scan_paths:
        print("Error: No paths to scan. Please configure SCAN_PATHS in .env or create paths.txt")
        return

    # Get exclusions
    exclusions = get_exclusions(exclusions_str, exclusions_file)
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
