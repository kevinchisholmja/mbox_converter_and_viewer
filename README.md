# Gmail MBOX to HTML Converter

A robust, offline-optimized tool for converting Gmail MBOX archives into browsable, searchable HTML archives. Designed specifically for large mailboxes (>1GB, 10k+ emails) and offline viewing.

## Features

- **Offline-First**: Fully functional without internet connection
- **Memory Efficient**: Streaming architecture handles multi-gigabyte MBOX files
- **HTML Sanitization**: Removes external images, tracking pixels, and bloat for clean offline viewing
- **Searchable**: Client-side search across subjects, senders, and content
- **Responsive Design**: Mobile-friendly HTML output
- **Zero Dependencies**: Uses only Python standard library

## Why This Tool?

When exporting Gmail archives as MBOX files, you get a single large file that's difficult to browse. This tool converts that MBOX into a clean, searchable HTML archive that:

- Loads quickly (no huge base64 images or external resources)
- Works completely offline (perfect for USB drives or archival storage)
- Handles large archives without running out of memory
- Removes tracking pixels and Gmail bloat

## Installation

No installation required! Just Python 3.8+

```bash
# Clone or download this repository
git clone <repository-url>
cd mbox_converter_and_viewer

# Run directly
python3 main.py <input.mbox> <output_directory>
```

## Usage

### Basic Usage

```bash
python3 main.py "Gmail.mbox" "gmail_archive"
```

This creates a browsable HTML archive in the `gmail_archive/` directory.

### Viewing Your Archive

1. Open `gmail_archive/index.html` in any web browser
2. Use the search box to find emails
3. Click any email to view full content

### For Large Mailboxes (>1GB)

The tool automatically detects large files and uses streaming mode:

```bash
# Works efficiently even with 5GB+ MBOX files
python3 main.py "Large-Gmail-Archive.mbox" "archive_output"
```

## Project Structure

```
mbox_converter_and_viewer/
├── main.py              # Entry point
├── config.py            # Configuration constants
├── utils.py             # Shared utility functions
├── email_parser.py      # MBOX parsing with streaming support
├── html_sanitizer.py    # HTML cleaning and optimization
├── html_generator.py    # HTML file generation
├── tests/               # Test suite
│   ├── test_utils.py
│   └── test_html_sanitizer.py
└── README.md           # This file
```

## Configuration

Edit `config.py` to customize behavior:

```python
# Email preview length in index
EMAIL_PREVIEW_LENGTH = 200

# Strip external images (recommended for offline use)
STRIP_EXTERNAL_IMAGES = True

# Remove large base64 inline images (prevents HTML bloat)
STRIP_BASE64_IMAGES = True

# Batch size for processing
BATCH_SIZE = 500
```

## What Gets Cleaned/Removed

For optimal offline viewing, the tool removes:

- **External images** - Won't load offline anyway
- **Large base64 images** - Can make HTML files 10MB+ each
- **Tracking pixels** - 1x1 invisible images used for tracking
- **Inline style blocks** - Gmail adds thousands of lines of CSS
- **External stylesheets** - Won't load offline
- **Script tags** - Security risk
- **Event handlers** - onclick, onerror, etc.
- **JavaScript links** - `javascript:` protocol

## Testing

Run the test suite:

```bash
# Run all tests
python3 -m unittest discover tests

# Run specific test file
python3 -m unittest tests/test_utils.py

# Run with verbose output
python3 -m unittest discover tests -v
```

## Examples

### Example 1: Small Personal Archive

```bash
python3 main.py "personal.mbox" "my_emails"
# Creates: my_emails/index.html
```

### Example 2: Large Corporate Archive

```bash
python3 main.py "work-archive-2020-2024.mbox" "work_archive"
# Handles multi-GB files efficiently with streaming
```

### Example 3: Portable USB Archive

```bash
python3 main.py "Gmail.mbox" "/media/usb/email_archive"
# Copy entire folder to USB for offline access anywhere
```

## Performance

Tested with:

- **10k emails**: ~2 minutes
- **50k emails**: ~8 minutes
- **100k emails**: ~15 minutes

Memory usage remains constant (~100-200MB) regardless of mailbox size thanks to streaming architecture.

## Troubleshooting

### "No emails found in MBOX file"

- Verify the file is a valid MBOX format (Gmail export)
- Check file permissions

### "Out of memory" error

- Update to latest version (older versions loaded entire file to RAM)
- Increase `BATCH_SIZE` in config.py

### Images showing as broken

- This is intentional! External images are replaced with placeholders
- For offline viewing, this prevents broken image icons

### HTML emails look plain

- Some styling is intentionally removed to reduce file size
- Content is preserved, just simplified for offline viewing

## How Gmail Export Works

1. Go to Google Takeout (takeout.google.com)
2. Select "Mail"
3. Choose "Export once"
4. Download the .mbox file
5. Use this tool to convert to HTML

## Technical Details

### Memory Efficiency

- **Streaming Parser**: Processes emails one at a time
- **Generator Pattern**: Yields results instead of building large lists
- **Batched HTML Generation**: Writes files incrementally

### Error Handling

- Specific exception types (no bare `except:` clauses)
- Graceful degradation (skips malformed emails, continues processing)
- Detailed logging for debugging

### Security

- HTML sanitization prevents XSS attacks
- Filename sanitization prevents path traversal
- No code execution from email content

## Contributing

Contributions welcome! Areas for improvement:

- Email threading/conversation grouping
- Attachment preview/thumbnails
- Dark mode toggle
- Export to other formats (PDF, JSON)
- Incremental updates (add new emails to existing archive)

## License

This project is provided as-is for personal and educational use.

## Frequently Asked Questions

### Q: Why not just use Gmail's web interface?

A: This tool is for offline archival. Perfect for:
- Legal/compliance requirements
- Backing up before closing an account
- Accessing emails without internet
- Long-term archival storage

### Q: Can I search the archive?

A: Yes! The index.html includes client-side JavaScript search across all emails.

### Q: Will this work with other email providers?

A: Yes, if they export to MBOX format. Tested with:
- Gmail (primary use case)
- Thunderbird exports
- Apple Mail exports

### Q: How big can the MBOX file be?

A: Tested up to 5GB. Streaming architecture should handle any size that fits on disk.

### Q: Can I customize the HTML design?

A: Yes! Edit the CSS in `html_generator.py`. The design is intentionally simple for easy customization.

## Author

Created for personal use and shared for the benefit of anyone needing to archive Gmail exports for offline viewing.

## Changelog

### Version 2.0 (Current)

- Added streaming support for large mailboxes
- Implemented HTML sanitization for offline optimization
- Removed all bare `except:` clauses
- Added comprehensive test suite
- Added proper logging system
- Modular architecture with separation of concerns
- Configuration file for easy customization

### Version 1.0 (Original)

- Basic MBOX to HTML conversion
- Simple search functionality
- Mobile-responsive design
