"""
Utility functions for MBOX to HTML converter.
Shared helper functions used across modules.
"""

import re
from email.header import decode_header
from typing import Optional
import config


def decode_mime_words(text: Optional[str]) -> str:
    """
    Decode MIME encoded-word strings (like =?UTF-8?Q?...?=).

    Args:
        text: String to decode

    Returns:
        Decoded string, or empty string if input is None
    """
    if not text:
        return ""

    decoded_fragments = []

    try:
        for fragment, encoding in decode_header(text):
            if isinstance(fragment, bytes):
                # Try to decode with specified encoding, fallback to UTF-8
                enc = encoding or config.DEFAULT_ENCODING
                try:
                    decoded_fragments.append(
                        fragment.decode(enc, errors='ignore')
                    )
                except (LookupError, UnicodeDecodeError):
                    # Unknown encoding or decode error, try fallback
                    decoded_fragments.append(
                        fragment.decode(config.DEFAULT_ENCODING, errors='ignore')
                    )
            else:
                decoded_fragments.append(str(fragment))
    except Exception as e:
        # If all decoding fails, return original text as string
        return str(text)

    return ''.join(decoded_fragments)


def extract_name_from_email(email_str: Optional[str]) -> str:
    """
    Extract just the name from an email address.

    Examples:
        "John Doe <john@example.com>" -> "John Doe"
        "john@example.com" -> "john@example.com"

    Args:
        email_str: Email string to parse

    Returns:
        Name or email address, "Unknown" if None/empty
    """
    if not email_str:
        return "Unknown"

    # Pattern: "Name <email@domain.com>"
    match = re.match(r'^"?([^"<]+)"?\s*<(.+)>$', email_str.strip())
    if match:
        return match.group(1).strip()

    return email_str.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove dangerous or problematic characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    if not filename:
        return "unnamed_file"

    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '_').replace('\\', '_')

    # Remove dangerous characters, keep alphanumeric, spaces, dots, dashes, underscores
    filename = re.sub(r'[^\w\s.-]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            # Preserve extension
            name, ext = name_parts
            filename = name[:250] + '.' + ext
        else:
            filename = filename[:255]

    return filename


def format_file_size(bytes_size: int) -> str:
    """
    Format byte size to human-readable format.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def strip_html_tags(html_text: str) -> str:
    """
    Strip HTML tags to create plain text preview.

    Args:
        html_text: HTML string

    Returns:
        Plain text string
    """
    if not html_text:
        return ""

    # Remove script and style elements
    text = re.sub(
        r'<script[^>]*>.*?</script>',
        '',
        html_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(
        r'<style[^>]*>.*?</style>',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
