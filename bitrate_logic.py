"""
Bitrate Logic Module
Contains logic to determine if a video's bitrate can be reduced.
"""

import os
from dotenv import load_dotenv


def load_video_config():
    """Load configuration from .env file."""
    load_dotenv()

    # Get scaling values (floats)
    pixel_scaling = float(os.getenv('PIXEL_SCALING', '90.0'))
    framerate_scaling = float(os.getenv('FRAMERATE_SCALING', '75.0'))

    # Get video reference values (integers)
    reference_width = int(os.getenv('REFERENCE_WIDTH', '1920'))
    reference_height = int(os.getenv('REFERENCE_HEIGHT', '1080'))
    reference_framerate = int(os.getenv('REFERENCE_FRAMERATE', '24'))
    reference_bitrate = int(os.getenv('REFERENCE_BITRATE', '6000000'))

    # Get encoder (string)
    reference_encoder = os.getenv('REFERENCE_ENCODER', 'AVC')

    return pixel_scaling, framerate_scaling, reference_width, reference_height, reference_framerate, reference_bitrate, reference_encoder


def obtain_encoder_efficiency(encoder: str) -> float:
    """Obtain the encoder efficiency from a list."""
    ENCODER_MAP = {
        # Editing
        "prores": 3.0,
        "dnxhd": 3.0,
        "dnxhr": 3.0,

        # Legacy
        "mpeg-1": 2.0,
        "mpeg-2": 1.8,
        "vc-1": 1.5,
        "wmv": 1.6,
        "realvideo": 2.0,

        # MPEG-4 Part 2
        "mpeg-4 visual": 1.3,
        "iso/asp": 1.3,
        "xvid": 1.3,
        "divx": 1.3,
        "dx50": 1.3,
        "mp4v": 1.3,

        # AVC / H.264
        "avc": 1.0,
        "h.264": 1.0,
        "iso/avc": 1.0,

        # HEVC / H.265
        "hevc": .75,
        "h.265": .75,
        "iso/hevc": .75,

        # Google codecs
        "vp8": 1.2,
        "vp9": 0.7,

        # AV1
        "av1": 0.6,
    }

    return ENCODER_MAP.get(encoder.lower(), 0)



def calculate_suggested_video_bitrate(width: int, height: int, framerate: float, encoder:str) -> int:
    """
    Determine if the video bitrate can be reduced based on resolution and framerate.

    Args:
        width: Video width in pixels
        height: Video height in pixels
        framerate: Video framerate (fps)
        current_bitrate: Current video bitrate in bits per second
        encoder: Format of the video (AVC, HEVC, AV1)

    Returns:
        suggested_bitrate: int suggested bitrate in bits per second
    """

    # Get configuration
    pixel_scaling, framerate_scaling, reference_width, reference_height, reference_framerate, reference_bitrate, reference_encoder = load_video_config()

    # Get pixel count
    pixel_count = width * height
    reference_pixel_count = reference_width * reference_height

    # Obtain the efficiency of the encoder, compared to AVC
    encoder_efficiency = obtain_encoder_efficiency(encoder)
    reference_encoder_efficiency = obtain_encoder_efficiency(reference_encoder)

    # Obtain pixel difference multiplier
    pixel_multiplier = (pixel_count / reference_pixel_count) ** (pixel_scaling / 100)

    # Obtain framerate difference multiplier
    framerate_multiplier = (framerate / reference_framerate) ** (framerate_scaling / 100)

    # Obtain encoder difference multiplier
    encoder_multiplier = encoder_efficiency / reference_encoder_efficiency

    # Obtain suggested bitrate
    suggested_bitrate = reference_bitrate * pixel_multiplier * framerate_multiplier * encoder_multiplier

    # Round suggested bitrate
    rounded_suggested_bitrate = int(suggested_bitrate / 100000) * 100000

    return rounded_suggested_bitrate


def load_output_config():
    """Load output encoding configuration from .env file."""
    load_dotenv()

    # Get output encoding settings
    output_encoder = os.getenv('OUTPUT_ENCODER', 'libx265')

    return output_encoder


def calculate_encoding_parameters(
    source_width: int,
    source_height: int,
    source_framerate: float
) -> dict:
    """
    Calculate encoding parameters (target bitrate, maxrate, bufsize) based on source video
    properties and output encoder configuration from .env.

    This calculates the appropriate bitrate for re-encoding the source video at its
    original resolution using the target encoder (e.g., HEVC instead of AVC).

    Args:
        source_width: Source video width in pixels
        source_height: Source video height in pixels
        source_framerate: Source video framerate (fps)

    Returns:
        Dictionary with encoding parameters:
        - target_bitrate: Target bitrate in bits per second
        - maxrate: Maximum bitrate in bits per second
        - bufsize: Buffer size in bits per second
        - encoder: Encoder codec name (from .env)
    """
    # Load output configuration
    output_encoder = load_output_config()

    # Determine target encoder format for calculation
    # Map ffmpeg codec names to our encoder efficiency names
    encoder_map = {
        'libx264': 'AVC',
        'libx265': 'HEVC',
        'libaom-av1': 'AV1',
        'libvpx-vp9': 'VP9',
    }
    target_encoder = encoder_map.get(output_encoder, 'HEVC')

    # Calculate suggested bitrate using SOURCE dimensions and framerate
    # but with the TARGET encoder
    target_bitrate = calculate_suggested_video_bitrate(
        source_width,
        source_height,
        source_framerate,
        target_encoder
    )

    # Calculate maxrate (1.3x target bitrate)
    maxrate = int(target_bitrate * 1.15)

    # Calculate bufsize (2x maxrate)
    bufsize = maxrate * 2

    return {
        'target_bitrate': target_bitrate,
        'maxrate': maxrate,
        'bufsize': bufsize,
        'encoder': output_encoder
    }


def format_bitrate(bitrate: int) -> str:
    """Format bitrate for human-readable output."""
    if bitrate >= 1_000_000:
        return f"{bitrate / 1_000_000:.2f} Mbps"
    elif bitrate >= 1_000:
        return f"{bitrate / 1_000:.2f} Kbps"
    else:
        return f"{bitrate} bps"
