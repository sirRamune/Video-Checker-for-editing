"""
Utils Module
Contains misc functions that could be used project wide.
"""

import pycountry


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
    
    print()
    
    # Then, read from file
    paths.extend(read_lines_from_file(file, array_type))

    return paths


def normalize_language(code: str) -> str:
    if not code:
        return None

    code = code.lower()

    # Try ISO 639-1 (2-letter)
    lang = pycountry.languages.get(alpha_2=code)
    if lang:
        return lang.alpha_2

    # Try ISO 639-2 / 639-3 (3-letter)
    lang = pycountry.languages.get(alpha_3=code)
    if lang:
        return lang.alpha_2 if hasattr(lang, 'alpha_2') else None

    return None
