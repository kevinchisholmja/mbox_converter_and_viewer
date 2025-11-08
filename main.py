#!/usr/bin/env python3
"""
Gmail MBOX to HTML Converter - Main Entry Point
Converts Gmail MBOX files into browsable, searchable HTML archives for offline viewing.
Optimized for large mailboxes (>1GB, 10k+ emails).
"""

import sys
import os
import logging
from pathlib import Path

import config
from email_parser import EmailParser
from html_generator import HTMLGenerator


def setup_logging():
    """Configure logging for the application."""
    log_format = config.LOG_FORMAT
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_usage():
    """Print usage information."""
    print("Usage: python3 main.py <input.mbox> <output_directory>")
    print()
    print("Example:")
    print('  python3 main.py "Gmail.mbox" "gmail_archive"')
    print()
    print("This creates a browsable HTML archive of your Gmail MBOX file.")
    print("Optimized for large mailboxes (>1GB, 10k+ emails).")


def main():
    """Main execution function."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check command line arguments
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    mbox_file = sys.argv[1]
    output_directory = sys.argv[2]

    # Validate input file exists
    if not os.path.exists(mbox_file):
        logger.error(f"MBOX file not found: {mbox_file}")
        sys.exit(1)

    # Check file size and warn if large
    file_size = os.path.getsize(mbox_file)
    file_size_mb = file_size / (1024 * 1024)

    print("=" * 60)
    print("  Gmail MBOX to HTML Converter")
    print("  Offline-Optimized Archive Generator")
    print("=" * 60)
    print(f"Input:  {mbox_file} ({file_size_mb:.1f} MB)")
    print(f"Output: {output_directory}")
    print()

    if file_size_mb > 100:
        logger.info(
            f"Large mailbox detected ({file_size_mb:.1f} MB). "
            "Using streaming mode for memory efficiency..."
        )

    # Step 1: Parse emails from MBOX
    logger.info("Step 1: Parsing MBOX file...")
    # Set up attachments directory
    attachments_dir = Path(output_directory) / config.ATTACHMENTS_DIRNAME
    parser = EmailParser(mbox_file, attachments_dir)

    try:
        emails_data = parser.parse_all_emails()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to parse MBOX file: {e}")
        sys.exit(1)

    if not emails_data:
        logger.error("No emails found in MBOX file!")
        sys.exit(1)

    logger.info(f"Successfully parsed {len(emails_data)} emails")
    print()

    # Step 2: Generate HTML archive
    logger.info("Step 2: Generating HTML archive...")
    generator = HTMLGenerator(output_directory)

    try:
        generator.create_archive(emails_data)
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to generate HTML archive: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("  Conversion Complete!")
    print("=" * 60)
    print(f"Processed: {len(emails_data)} emails")
    print(f"Location:  {Path(output_directory).absolute()}")
    print()
    print("To view your archive:")
    print(f"  1. Open: {Path(output_directory).absolute() / 'index.html'}")
    print("  2. Or copy the entire folder to a USB drive for portable access")
    print()
    print("Features:")
    print("  - Fully offline - no internet required")
    print("  - Searchable by subject, sender, and content")
    print("  - External images removed (won't load offline anyway)")
    print("  - HTML bloat cleaned up for faster loading")
    print()


if __name__ == '__main__':
    main()
