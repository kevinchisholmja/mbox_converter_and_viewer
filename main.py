#!/usr/bin/env python3
"""
Gmail MBOX to HTML Converter - Main Entry Point
Modular version for easier learning and modification
"""

import sys
import os
from pathlib import Path

# Import our custom modules
from email_parser import EmailParser
from html_generator import HTMLGenerator

def print_usage():
    """Print usage information."""
    print("Usage: python3 main.py <input.mbox> <output_directory>")
    print()
    print("Example:")
    print('  python3 main.py "Gmail.mbox" "gmail_archive"')
    print()
    print("This will create a browsable HTML archive of your Gmail MBOX file.")

def main():
    """Main execution function."""
    
    # Check command line arguments
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    
    mbox_file = sys.argv[1]
    output_directory = sys.argv[2]
    
    # Validate input file exists
    if not os.path.exists(mbox_file):
        print(f"❌ Error: MBOX file not found: {mbox_file}")
        sys.exit(1)
    
    print("🚀 Gmail MBOX to HTML Converter")
    print("=" * 50)
    print(f"📂 Input:  {mbox_file}")
    print(f"📁 Output: {output_directory}")
    print()
    
    # Step 1: Parse emails from MBOX
    print("📧 Step 1: Parsing MBOX file...")
    parser = EmailParser(mbox_file)
    emails_data = parser.parse_all_emails()
    
    if not emails_data:
        print("❌ No emails found in MBOX file!")
        sys.exit(1)
    
    print(f"✅ Successfully parsed {len(emails_data)} emails")
    print()
    
    # Step 2: Generate HTML archive
    print("🎨 Step 2: Generating HTML archive...")
    generator = HTMLGenerator(output_directory)
    generator.create_archive(emails_data)
    
    print()
    print("=" * 50)
    print("✅ Conversion complete!")
    print(f"📧 Processed {len(emails_data)} emails")
    print(f"🌐 Open this file in your browser:")
    print(f"   {Path(output_directory).absolute() / 'index.html'}")
    print()
    print("💡 Tip: Copy the entire output folder to your external drive")
    print("   for portable, offline access on any computer!")

if __name__ == '__main__':
    main()