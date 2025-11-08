"""
Email Parser Module
Handles MBOX parsing and email data extraction with streaming support for large files.
"""

import mailbox
import logging
from pathlib import Path
from typing import List, Dict, Optional, Iterator
from email.message import Message

import config
import utils

logger = logging.getLogger(__name__)


class EmailParser:
    """
    Parses MBOX files and extracts email data.
    Supports streaming for memory-efficient processing of large mailboxes.
    """

    def __init__(self, mbox_path: str, attachments_dir: Optional[Path] = None):
        """
        Initialize the parser with an MBOX file path.

        Args:
            mbox_path: Path to the MBOX file
            attachments_dir: Optional directory to save attachments
        """
        self.mbox_path = mbox_path
        self.mbox = None
        self.total_emails = 0
        self.attachments_dir = Path(attachments_dir) if attachments_dir else None

    def get_email_count(self) -> int:
        """
        Get total number of emails in the MBOX file.

        Returns:
            Number of emails, or 0 if file cannot be opened
        """
        try:
            mbox = mailbox.mbox(self.mbox_path)
            count = len(mbox)
            mbox.close()
            return count
        except Exception as e:
            logger.error(f"Failed to count emails in MBOX: {e}")
            return 0

    def parse_all_emails(self) -> List[Dict]:
        """
        Parse all emails from the MBOX file.
        For large files, consider using parse_emails_streaming() instead.

        Returns:
            List of email data dictionaries
        """
        emails_data = []

        for email_data in self.parse_emails_streaming():
            emails_data.append(email_data)

        return emails_data

    def parse_emails_streaming(self) -> Iterator[Dict]:
        """
        Stream emails from MBOX file one at a time.
        Memory-efficient for large mailboxes (>1GB, >10k emails).

        Yields:
            Email data dictionaries one at a time
        """
        try:
            self.mbox = mailbox.mbox(self.mbox_path)
            self.total_emails = len(self.mbox)
            logger.info(f"Found {self.total_emails} emails in MBOX file")
        except FileNotFoundError:
            logger.error(f"MBOX file not found: {self.mbox_path}")
            return
        except PermissionError:
            logger.error(f"Permission denied reading MBOX file: {self.mbox_path}")
            return
        except Exception as e:
            logger.error(f"Error opening MBOX file: {e}")
            return

        for idx, message in enumerate(self.mbox, 1):
            try:
                email_data = self._parse_single_email(message, idx)

                # Progress indicator
                if idx % config.PROGRESS_UPDATE_INTERVAL == 0 or idx == self.total_emails:
                    progress = (idx / self.total_emails) * 100
                    subject_preview = email_data['subject'][:50]
                    logger.info(
                        f"Processing: {idx}/{self.total_emails} "
                        f"({progress:.1f}%) - {subject_preview}"
                    )

                yield email_data

            except Exception as e:
                logger.warning(f"Error processing email {idx}: {e}")
                # Continue processing other emails
                continue

        if self.mbox:
            self.mbox.close()

    def _parse_single_email(self, message: Message, email_id: int) -> Dict:
        """
        Parse a single email message.

        Args:
            message: Email message object from mailbox
            email_id: Unique identifier for this email

        Returns:
            Dictionary containing email data
        """
        # Extract basic email metadata
        subject = utils.decode_mime_words(
            message.get('Subject', '(No Subject)')
        )
        from_addr = utils.decode_mime_words(
            message.get('From', 'Unknown')
        )
        to_addr = utils.decode_mime_words(
            message.get('To', 'Unknown')
        )
        date = message.get('Date', 'Unknown Date')

        # Extract name from email addresses
        from_name = utils.extract_name_from_email(from_addr)

        # Get email body
        body_text, body_html, is_html = self._extract_email_body(message)

        # Create preview (first N chars of plain text)
        preview = body_text[:config.EMAIL_PREVIEW_LENGTH].replace('\n', ' ').strip()
        if len(body_text) > config.EMAIL_PREVIEW_LENGTH:
            preview += '...'

        # Store email data
        email_data = {
            'id': email_id,
            'subject': subject,
            'from': from_addr,
            'from_name': from_name,
            'to': to_addr,
            'date': date,
            'body_text': body_text,
            'body_html': body_html,
            'is_html': is_html,
            'preview': preview,
            'attachments': []  # Will be populated if save_attachments is called
        }

        return email_data

    def _extract_email_body(self, msg: Message) -> tuple:
        """
        Extract the body from an email message.
        Handles both plain text and HTML emails.

        Args:
            msg: Email message object

        Returns:
            Tuple of (body_text, body_html, is_html)
        """
        body_text = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue

                    # Try to decode payload
                    try:
                        decoded_payload = payload.decode(config.DEFAULT_ENCODING, errors='ignore')
                    except (UnicodeDecodeError, AttributeError):
                        try:
                            decoded_payload = payload.decode(config.FALLBACK_ENCODING, errors='ignore')
                        except (UnicodeDecodeError, AttributeError):
                            logger.debug(f"Failed to decode email part with type {content_type}")
                            continue

                    if content_type == "text/plain":
                        body_text = decoded_payload
                    elif content_type == "text/html":
                        body_html = decoded_payload

                except Exception as e:
                    logger.debug(f"Error extracting email part: {e}")
                    continue
        else:
            # Non-multipart message
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    try:
                        decoded_text = payload.decode(config.DEFAULT_ENCODING, errors='ignore')
                    except (UnicodeDecodeError, AttributeError):
                        decoded_text = payload.decode(config.FALLBACK_ENCODING, errors='ignore')
                    
                    # Check content type to determine if it's HTML or plain text
                    content_type = msg.get_content_type()
                    if content_type == "text/html":
                        body_html = decoded_text
                        body_text = ""  # Will be extracted from HTML later
                    else:
                        body_text = decoded_text
            except Exception as e:
                logger.debug(f"Error extracting single-part email body: {e}")
                body_text = str(msg.get_payload())

        # Determine which body to use
        # Check if body_text contains HTML even if there's no explicit HTML part
        # This handles cases where promotional emails have HTML in the text/plain part
        is_html_content = False
        
        if body_html:
            # Explicit HTML part exists
            is_html_content = True
        elif body_text:
            # Check if the "plain text" actually contains HTML markup
            # Look for common HTML tags
            html_indicators = ['<html', '<head', '<body', '<div', '<table', '<style', '<!DOCTYPE']
            text_lower = body_text.lower()
            if any(indicator in text_lower for indicator in html_indicators):
                # This is actually HTML, not plain text
                body_html = body_text
                is_html_content = True
                logger.debug("Detected HTML content in text/plain part")
        
        if is_html_content:
            return body_text or utils.strip_html_tags(body_html), body_html, True

        return body_text, body_text, False

    def save_attachments(
        self,
        msg: Message,
        email_id: int,
        attachments_dir: Path
    ) -> List[Dict]:
        """
        Save email attachments to disk.

        Args:
            msg: Email message object
            email_id: Unique ID for this email
            attachments_dir: Directory to save attachments

        Returns:
            List of attachment info dictionaries
        """
        attachments = []

        if not msg.is_multipart():
            return attachments

        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" not in content_disposition:
                continue

            filename = part.get_filename()
            if not filename:
                continue

            # Decode and sanitize filename
            filename = utils.decode_mime_words(filename)
            filename = utils.sanitize_filename(filename)

            # Create email-specific attachment folder
            email_attach_dir = Path(attachments_dir) / str(email_id)
            email_attach_dir.mkdir(parents=True, exist_ok=True)

            filepath = email_attach_dir / filename

            try:
                payload = part.get_payload(decode=True)
                if payload:
                    with open(filepath, 'wb') as f:
                        f.write(payload)

                    file_size = len(payload)
                    attachments.append({
                        'filename': filename,
                        'path': f'{config.ATTACHMENTS_DIRNAME}/{email_id}/{filename}',
                        'size': file_size
                    })

                    logger.debug(
                        f"Saved attachment: {filename} "
                        f"({utils.format_file_size(file_size)})"
                    )

            except IOError as e:
                logger.warning(f"Could not save attachment {filename}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error saving attachment {filename}: {e}")

        return attachments
