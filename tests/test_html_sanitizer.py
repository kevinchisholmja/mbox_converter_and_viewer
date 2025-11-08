"""
Tests for HTML sanitizer module.
Run with: python3 -m pytest tests/test_html_sanitizer.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from html_sanitizer import HTMLSanitizer


class TestHTMLSanitizer(unittest.TestCase):
    """Tests for HTML sanitization."""

    def setUp(self):
        """Set up test fixtures."""
        self.sanitizer = HTMLSanitizer()

    def test_remove_scripts(self):
        """Test that script tags are removed."""
        html = '<p>Hello</p><script>alert("xss")</script><p>World</p>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert', result)
        self.assertIn('Hello', result)
        self.assertIn('World', result)

    def test_remove_event_handlers(self):
        """Test that event handlers are removed."""
        html = '<button onclick="malicious()">Click</button>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('onclick', result)
        self.assertIn('button', result)

    def test_remove_javascript_links(self):
        """Test that javascript: links are removed."""
        html = '<a href="javascript:alert(\'xss\')">Link</a>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('javascript:', result)
        self.assertIn('href="#"', result)

    def test_external_images_removed(self):
        """Test that external images are replaced with placeholder."""
        html = '<img src="https://example.com/image.jpg" alt="test">'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('https://example.com', result)
        self.assertIn('External image', result)

    def test_base64_images_removed(self):
        """Test that large base64 images are removed."""
        # Create a large base64 image (> 1000 chars)
        large_base64 = "a" * 1500
        html = f'<img src="data:image/png;base64,{large_base64}">'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('base64', result)
        self.assertIn('Inline image removed', result)

    def test_small_base64_images_kept(self):
        """Test that small base64 images are kept."""
        # Small base64 image (< 1000 chars)
        small_base64 = "a" * 500
        html = f'<img src="data:image/png;base64,{small_base64}">'
        result = self.sanitizer.sanitize(html)
        # Small images should be kept
        self.assertIn('base64', result)

    def test_inline_styles_removed(self):
        """Test that <style> blocks are removed."""
        html = '<style>body { color: red; }</style><p>Text</p>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('<style>', result)
        self.assertNotIn('color: red', result)
        self.assertIn('Text', result)

    def test_tracking_pixels_removed(self):
        """Test that 1x1 tracking pixels are removed."""
        html = '<img src="track.gif" width="1" height="1"><p>Text</p>'
        result = self.sanitizer.sanitize(html)
        # Tracking pixel should be removed
        self.assertNotIn('track.gif', result)
        self.assertIn('Text', result)

    def test_empty_html(self):
        """Test sanitizing empty HTML."""
        result = self.sanitizer.sanitize("")
        self.assertEqual(result, "")

    def test_safe_html_unchanged(self):
        """Test that safe HTML is mostly preserved."""
        html = '<p>Hello <b>World</b></p>'
        result = self.sanitizer.sanitize(html)
        self.assertIn('<p>', result)
        self.assertIn('<b>', result)
        self.assertIn('Hello', result)

    def test_sanitize_stats(self):
        """Test that sanitization statistics are tracked."""
        self.sanitizer.reset_stats()
        html = '''
            <script>alert(1)</script>
            <img src="https://example.com/img.jpg">
            <style>body{}</style>
        '''
        self.sanitizer.sanitize(html)
        stats = self.sanitizer.get_stats()

        self.assertGreater(stats['scripts_removed'], 0)
        self.assertGreater(stats['external_images_removed'], 0)
        self.assertGreater(stats['styles_removed'], 0)


class TestHTMLSanitizerEdgeCases(unittest.TestCase):
    """Tests for edge cases in HTML sanitization."""

    def setUp(self):
        """Set up test fixtures."""
        self.sanitizer = HTMLSanitizer()

    def test_nested_scripts(self):
        """Test handling of nested script tags."""
        html = '<div><div><script>alert(1)</script></div></div>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('script', result.lower())

    def test_malformed_html(self):
        """Test that malformed HTML doesn't crash."""
        html = '<p>Hello<b>World</p></b><img src="test.jpg"'
        result = self.sanitizer.sanitize(html)
        # Should not crash
        self.assertIsInstance(result, str)

    def test_case_insensitive_removal(self):
        """Test that tag removal is case-insensitive."""
        html = '<SCRIPT>alert(1)</SCRIPT><Script>alert(2)</Script>'
        result = self.sanitizer.sanitize(html)
        self.assertNotIn('alert', result)


if __name__ == '__main__':
    unittest.main()
