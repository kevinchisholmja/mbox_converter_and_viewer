"""
Configuration constants for MBOX to HTML converter.
Centralized configuration for easy customization.
"""

# Email processing configuration
EMAIL_PREVIEW_LENGTH = 200
PROGRESS_UPDATE_INTERVAL = 100  # Show progress every N emails

# File size thresholds (in bytes)
LARGE_ATTACHMENT_THRESHOLD = 10 * 1024 * 1024  # 10 MB
MAX_INLINE_IMAGE_SIZE = 100 * 1024  # 100 KB - strip larger base64 images

# HTML sanitization settings
STRIP_EXTERNAL_IMAGES = True
STRIP_BASE64_IMAGES = True
STRIP_INLINE_STYLES = True
STRIP_EXTERNAL_STYLESHEETS = True
STRIP_TRACKING_PIXELS = True
MINIFY_HTML = True  # Remove unnecessary whitespace and compress HTML
MAX_STYLE_ATTRIBUTE_LENGTH = 500  # Characters

# Batch processing for memory efficiency
BATCH_SIZE = 500  # Process emails in batches for large mailboxes
ENABLE_STREAMING = True  # Use streaming for large MBOX files

# Output directories
EMAILS_DIRNAME = 'emails'
ATTACHMENTS_DIRNAME = 'attachments'

# Encoding settings
DEFAULT_ENCODING = 'utf-8'
FALLBACK_ENCODING = 'latin-1'

# Logging configuration
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(levelname)s: %(message)s'
