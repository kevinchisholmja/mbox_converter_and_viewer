"""
HTML Sanitization Module
Handles all HTML cleaning, security sanitization, and offline optimization.
"""

import re
import logging
import config

logger = logging.getLogger(__name__)


class HTMLSanitizer:
    """
    Sanitizes and optimizes HTML content for offline viewing.
    Removes security risks and cleans up bloat from email HTML.
    """

    def __init__(self):
        """Initialize the sanitizer."""
        self.stats = {
            'scripts_removed': 0,
            'external_images_removed': 0,
            'base64_images_removed': 0,
            'styles_removed': 0,
            'tracking_pixels_removed': 0
        }

    def sanitize(self, html_content: str) -> str:
        """
        Main sanitization method - applies all cleaning steps.

        Args:
            html_content: Raw HTML content from email

        Returns:
            Sanitized and optimized HTML
        """
        if not html_content:
            return ""

        # Apply sanitization steps in order
        html_content = self._remove_scripts(html_content)
        html_content = self._remove_event_handlers(html_content)
        html_content = self._remove_javascript_links(html_content)

        # Offline optimization
        if config.STRIP_EXTERNAL_IMAGES:
            html_content = self._handle_external_images(html_content)

        if config.STRIP_BASE64_IMAGES:
            html_content = self._handle_base64_images(html_content)

        if config.STRIP_INLINE_STYLES:
            html_content = self._strip_excessive_styles(html_content)

        if config.STRIP_EXTERNAL_STYLESHEETS:
            html_content = self._remove_external_stylesheets(html_content)

        if config.STRIP_TRACKING_PIXELS:
            html_content = self._remove_tracking_pixels(html_content)

        return html_content

    def _remove_scripts(self, html_content: str) -> str:
        """Remove all script tags for security."""
        original = html_content
        html_content = re.sub(
            r'<script[^>]*>.*?</script>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Also remove noscript tags as they're not needed
        html_content = re.sub(
            r'<noscript[^>]*>.*?</noscript>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        if original != html_content:
            self.stats['scripts_removed'] += 1
            logger.debug("Removed script tags from HTML")

        return html_content

    def _remove_event_handlers(self, html_content: str) -> str:
        """Remove inline event handlers (onclick, onerror, etc.)."""
        # Match on + event name + = + quoted value
        html_content = re.sub(
            r'\s*on\w+\s*=\s*["\'][^"\']*["\']',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        return html_content

    def _remove_javascript_links(self, html_content: str) -> str:
        """Remove javascript: protocol from links."""
        html_content = re.sub(
            r'href\s*=\s*["\']javascript:[^"\']*["\']',
            'href="#"',
            html_content,
            flags=re.IGNORECASE
        )
        return html_content

    def _handle_external_images(self, html_content: str) -> str:
        """
        Replace external images with placeholder for offline viewing.
        External images won't load anyway without internet connection.
        """
        placeholder = (
            '<div style="padding:10px;background:#f0f0f0;border:1px dashed #ccc;'
            'text-align:center;color:#666;font-size:12px;border-radius:4px;">'
            '🖼️ [External image - not available offline]</div>'
        )

        original_count = len(re.findall(r'<img[^>]*src="https?://', html_content, re.IGNORECASE))

        html_content = re.sub(
            r'<img[^>]*src="https?://[^"]*"[^>]*>',
            placeholder,
            html_content,
            flags=re.IGNORECASE
        )

        if original_count > 0:
            self.stats['external_images_removed'] += original_count
            logger.debug(f"Replaced {original_count} external images with placeholders")

        return html_content

    def _handle_base64_images(self, html_content: str) -> str:
        """
        Remove large base64 inline images that bloat HTML.
        Small ones can stay, but large ones (>100KB) create massive files.
        """
        placeholder = (
            '<div style="padding:10px;background:#fff3cd;border:1px dashed #ffc107;'
            'text-align:center;color:#856404;font-size:12px;border-radius:4px;">'
            '📷 [Inline image removed - prevented HTML bloat]</div>'
        )

        # Find all base64 images
        pattern = r'<img[^>]*src="data:image/[^"]*"[^>]*>'
        matches = re.findall(pattern, html_content, re.IGNORECASE)

        removed_count = 0
        for match in matches:
            # Check if this is a large base64 image
            # Rough estimate: if the tag is > 1000 chars, the image is probably large
            if len(match) > 1000:  # ~750 bytes base64 encoded
                html_content = html_content.replace(match, placeholder)
                removed_count += 1

        if removed_count > 0:
            self.stats['base64_images_removed'] += removed_count
            logger.debug(f"Removed {removed_count} large base64 images to prevent bloat")

        return html_content

    def _strip_excessive_styles(self, html_content: str) -> str:
        """
        Remove inline style blocks and excessive style attributes.
        Gmail emails often have thousands of lines of inline CSS.
        """
        # Remove <style> blocks entirely
        original = html_content
        html_content = re.sub(
            r'<style[^>]*>.*?</style>',
            '',
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        if original != html_content:
            self.stats['styles_removed'] += 1
            logger.debug("Removed inline <style> blocks")

        # Truncate overly long style attributes
        def truncate_style(match):
            full_attr = match.group(0)
            if len(full_attr) > config.MAX_STYLE_ATTRIBUTE_LENGTH:
                # Keep just basic styles
                return 'style="max-width:100%;word-wrap:break-word;"'
            return full_attr

        html_content = re.sub(
            r'style="[^"]*"',
            truncate_style,
            html_content,
            flags=re.IGNORECASE
        )

        return html_content

    def _remove_external_stylesheets(self, html_content: str) -> str:
        """Remove external stylesheet links (won't work offline anyway)."""
        html_content = re.sub(
            r'<link[^>]*rel=["\']stylesheet["\'][^>]*>',
            '',
            html_content,
            flags=re.IGNORECASE
        )

        html_content = re.sub(
            r'<link[^>]*>',
            '',
            html_content,
            flags=re.IGNORECASE
        )

        return html_content

    def _remove_tracking_pixels(self, html_content: str) -> str:
        """
        Remove tracking pixels (1x1 invisible images).
        Common pattern: <img width="1" height="1" ...>
        """
        tracking_pattern = (
            r'<img[^>]*(?:width|height)\s*=\s*["\']?1(?:px)?["\']?[^>]*'
            r'(?:width|height)\s*=\s*["\']?1(?:px)?["\']?[^>]*>'
        )

        original_count = len(re.findall(tracking_pattern, html_content, re.IGNORECASE))

        html_content = re.sub(
            tracking_pattern,
            '',
            html_content,
            flags=re.IGNORECASE
        )

        if original_count > 0:
            self.stats['tracking_pixels_removed'] += original_count
            logger.debug(f"Removed {original_count} tracking pixels")

        return html_content

    def get_stats(self) -> dict:
        """Get sanitization statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics counters."""
        for key in self.stats:
            self.stats[key] = 0
