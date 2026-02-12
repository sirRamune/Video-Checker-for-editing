"""
Utils Module
Contains misc functions that could be used project wide.
"""

import pycountry



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
