"""
Utils Module
Contains misc functions that could be used project wide.
"""

import pycountry
from pymediainfo import MediaInfo
from typing import List, Dict, Any, Optional


def read_lines_from_file(file_path: str, line_type: str) -> List[str]:
    """Read lines from a text file."""
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    lines.append(line)
        print(f"Loaded {len(lines)} {line_type}(s) from {file_path}")
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
    return lines


def get_array_from_env_and_file(env_str: str, file: str, array_type: str) -> List[str]:
    """Get list of paths to scan from config or file."""
    paths = []

    # First, try to get items from environment variable
    if env_str:
        paths = [p.strip() for p in env_str.split(',') if p.strip()]
        print(f"Using {len(paths)} {array_type}(s) from .env")
    else:
        print(f"Warning: No {array_type}(s) specified in .env") 
    
    # Then, read from file
    paths.extend(read_lines_from_file(file, array_type))

    return paths


def extract_media_info(file_path: str) -> Optional[Dict[str, Any]]:
    """Extract media information from a video file."""
    try:
        media_info = MediaInfo.parse(file_path)

        # Extract general info
        general = media_info.general_tracks[0] if media_info.general_tracks else None

        # Extract video tracks
        video_tracks = []
        for track in media_info.video_tracks:
            video_tracks.append({
                "track_id": track.track_id,
                "stream_order": track.stream_order,
                "format": track.format,
                "codec_id": track.codec_id,
                "width": track.width,
                "height": track.height,
                "framerate": float(track.frame_rate) if track.frame_rate else None,
                "bitrate": track.bit_rate,
                "bit_depth": track.bit_depth,
                "default": track.default if hasattr(track, 'default') else None,
                "forced": track.forced if hasattr(track, 'forced') else None,
            })

        # Extract audio tracks
        audio_tracks = []
        for track in media_info.audio_tracks:
            audio_tracks.append({
                "track_id": track.track_id,
                "stream_order": track.stream_order,
                "format": track.format,
                "codec_id": track.codec_id,
                "channels": track.channel_s,
                "sampling_rate": track.sampling_rate,
                "bitrate": track.bit_rate,
                "language": track.language if hasattr(track, 'language') else None,
                "title": track.title if hasattr(track, 'title') else None,
                "default": track.default if hasattr(track, 'default') else None,
                "forced": track.forced if hasattr(track, 'forced') else None,
            })

        # Extract subtitle tracks
        subtitle_tracks = []
        for track in media_info.text_tracks:
            subtitle_tracks.append({
                "track_id": track.track_id,
                "stream_order": track.stream_order,
                "format": track.format,
                "codec_id": track.codec_id,
                "language": track.language if hasattr(track, 'language') else None,
                "title": track.title if hasattr(track, 'title') else None,
                "default": track.default if hasattr(track, 'default') else None,
                "forced": track.forced if hasattr(track, 'forced') else None,
            })

        return {
            "file_path": file_path,
            "file_size": general.file_size if general else None,
            "duration": general.duration if general else None,
            "format": general.format if general else None,
            "video_tracks": video_tracks,
            "audio_tracks": audio_tracks,
            "subtitle_tracks": subtitle_tracks,
        }

    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
    except PermissionError as e:
        print(f"Permission denied from {file_path}: {e}")
    except Exception as e:
        print(f"Error extracting media info from {file_path}: {e}")
        return None


def normalize_language(code: str, to_alpha3: bool = False) -> Optional[str]:
    if not code:
        return None

    code = code.lower()

    lang = None

    # Try 2-letter
    lang = pycountry.languages.get(alpha_2=code)

    # Try 3-letter
    if not lang:
        lang = pycountry.languages.get(alpha_3=code)

    if not lang:
        return None

    if to_alpha3:
        return getattr(lang, "alpha_3", None)
    else:
        return getattr(lang, "alpha_2", None)

