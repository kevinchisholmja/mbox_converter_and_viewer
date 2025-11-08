"""
Tests for utility functions.
Run with: python3 -m pytest tests/test_utils.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import utils


class TestDecodeMimeWords(unittest.TestCase):
    """Tests for MIME word decoding."""

    def test_simple_string(self):
        """Test decoding a simple ASCII string."""
        result = utils.decode_mime_words("Hello World")
        self.assertEqual(result, "Hello World")

    def test_empty_string(self):
        """Test decoding empty/None strings."""
        self.assertEqual(utils.decode_mime_words(""), "")
        self.assertEqual(utils.decode_mime_words(None), "")

    def test_utf8_encoded(self):
        """Test decoding UTF-8 encoded MIME words."""
        encoded = "=?UTF-8?Q?Hello_World?="
        result = utils.decode_mime_words(encoded)
        self.assertEqual(result, "Hello World")


class TestExtractNameFromEmail(unittest.TestCase):
    """Tests for email name extraction."""

    def test_name_and_email(self):
        """Test extracting name from 'Name <email@domain.com>' format."""
        result = utils.extract_name_from_email("John Doe <john@example.com>")
        self.assertEqual(result, "John Doe")

    def test_email_only(self):
        """Test when only email is provided."""
        result = utils.extract_name_from_email("john@example.com")
        self.assertEqual(result, "john@example.com")

    def test_empty_string(self):
        """Test with empty/None input."""
        self.assertEqual(utils.extract_name_from_email(""), "Unknown")
        self.assertEqual(utils.extract_name_from_email(None), "Unknown")

    def test_quoted_name(self):
        """Test extracting quoted names."""
        result = utils.extract_name_from_email('"John Doe" <john@example.com>')
        self.assertEqual(result, "John Doe")


class TestSanitizeFilename(unittest.TestCase):
    """Tests for filename sanitization."""

    def test_simple_filename(self):
        """Test sanitizing a simple filename."""
        result = utils.sanitize_filename("document.pdf")
        self.assertEqual(result, "document.pdf")

    def test_dangerous_characters(self):
        """Test removing dangerous characters."""
        result = utils.sanitize_filename("my<file>name?.pdf")
        self.assertEqual(result, "my_file_name_.pdf")

    def test_path_traversal(self):
        """Test preventing path traversal."""
        result = utils.sanitize_filename("../../etc/passwd")
        self.assertNotIn("..", result)
        self.assertNotIn("/", result)

    def test_empty_filename(self):
        """Test with empty filename."""
        result = utils.sanitize_filename("")
        self.assertEqual(result, "unnamed_file")

    def test_long_filename(self):
        """Test truncating very long filenames."""
        long_name = "a" * 300 + ".txt"
        result = utils.sanitize_filename(long_name)
        self.assertLessEqual(len(result), 255)
        self.assertTrue(result.endswith(".txt"))


class TestFormatFileSize(unittest.TestCase):
    """Tests for file size formatting."""

    def test_bytes(self):
        """Test formatting bytes."""
        self.assertEqual(utils.format_file_size(500), "500.0 B")

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        self.assertEqual(utils.format_file_size(2048), "2.0 KB")

    def test_megabytes(self):
        """Test formatting megabytes."""
        self.assertEqual(utils.format_file_size(5 * 1024 * 1024), "5.0 MB")

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        self.assertEqual(utils.format_file_size(3 * 1024 * 1024 * 1024), "3.0 GB")


class TestStripHtmlTags(unittest.TestCase):
    """Tests for HTML tag stripping."""

    def test_simple_html(self):
        """Test stripping simple HTML tags."""
        html = "<p>Hello <b>World</b></p>"
        result = utils.strip_html_tags(html)
        self.assertEqual(result, "Hello World")

    def test_script_tags(self):
        """Test removing script tags."""
        html = "<p>Text</p><script>alert('xss')</script>"
        result = utils.strip_html_tags(html)
        self.assertNotIn("script", result)
        self.assertNotIn("alert", result)

    def test_style_tags(self):
        """Test removing style tags."""
        html = "<style>body { color: red; }</style><p>Text</p>"
        result = utils.strip_html_tags(html)
        self.assertNotIn("color", result)
        self.assertIn("Text", result)

    def test_empty_string(self):
        """Test with empty string."""
        self.assertEqual(utils.strip_html_tags(""), "")

    def test_whitespace_cleanup(self):
        """Test whitespace is normalized."""
        html = "<p>Hello\n\n\nWorld</p>"
        result = utils.strip_html_tags(html)
        self.assertEqual(result, "Hello World")


if __name__ == '__main__':
    unittest.main()
