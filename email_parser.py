"""
Email Parser Module
Handles all MBOX parsing and email data extraction
"""

import mailbox
import re
from email.header import decode_header
from pathlib import Path

class EmailParser:
    """Parses MBOX files and extracts email data."""
    
    def __init__(self, mbox_path):
        """
        Initialize the parser with an MBOX file path.
        
        Args:
            mbox_path: Path to the MBOX file
        """
        self.mbox_path = mbox_path
        self.mbox = None
        self.output_dir = None
        
    def decode_mime_words(self, s):
        """
        Decode MIME encoded-word strings (like =?UTF-8?Q?...?=).
        
        Args:
            s: String to decode
            
        Returns:
            Decoded string
        """
        if not s:
            return ""
        
        decoded_fragments = []
        for fragment, encoding in decode_header(s):
            if isinstance(fragment, bytes):
                try:
                    decoded_fragments.append(
                        fragment.decode(encoding or 'utf-8', errors='ignore')
                    )
                except:
                    decoded_fragments.append(
                        fragment.decode('utf-8', errors='ignore')
                    )
            else:
                decoded_fragments.append(fragment)
        
        return ''.join(decoded_fragments)
    
    def extract_name_from_email(self, email_str):
        """
        Extract just the name from an email address.
        
        Examples:
            "John Doe <john@example.com>" -> "John Doe"
            "john@example.com" -> "john@example.com"
        
        Args:
            email_str: Email string to parse
            
        Returns:
            Name or email address
        """
        if not email_str:
            return "Unknown"
        
        # Pattern: "Name <email@domain.com>"
        match = re.match(r'^"?([^"<]+)"?\s*<(.+)>$', email_str.strip())
        if match:
            return match.group(1).strip()
        
        return email_str.strip()
    
    def get_email_body(self, msg):
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
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    
                    decoded_payload = payload.decode('utf-8', errors='ignore')
                    
                    if content_type == "text/plain":
                        body_text = decoded_payload
                    elif content_type == "text/html":
                        body_html = decoded_payload
                except:
                    pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body_text = payload.decode('utf-8', errors='ignore')
            except:
                body_text = str(msg.get_payload())
        
        # Determine which body to use
        # Prefer plain text for preview, but keep HTML if available
        if body_html:
            return body_text or self._strip_html_tags(body_html), body_html, True
        
        return body_text, body_text, False
    
    def _strip_html_tags(self, html_text):
        """
        Strip HTML tags for plain text preview.
        
        Args:
            html_text: HTML string
            
        Returns:
            Plain text string
        """
        # Remove script and style elements
        html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def save_attachments(self, msg, email_id, attachments_dir):
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
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" not in content_disposition:
                continue
            
            filename = part.get_filename()
            if not filename:
                continue
            
            filename = self.decode_mime_words(filename)
            # Sanitize filename (remove dangerous characters)
            filename = re.sub(r'[^\w\s.-]', '_', filename)
            
            # Create email-specific attachment folder
            email_attach_dir = Path(attachments_dir) / str(email_id)
            email_attach_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = email_attach_dir / filename
            
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    with open(filepath, 'wb') as f:
                        f.write(payload)
                    
                    attachments.append({
                        'filename': filename,
                        'path': f'attachments/{email_id}/{filename}',
                        'size': len(payload)
                    })
            except Exception as e:
                print(f"  ⚠️  Could not save attachment {filename}: {e}")
        
        return attachments
    
    def parse_all_emails(self):
        """
        Parse all emails from the MBOX file.
        
        Returns:
            List of email data dictionaries
        """
        try:
            self.mbox = mailbox.mbox(self.mbox_path)
            total_emails = len(self.mbox)
            print(f"📊 Found {total_emails} emails in MBOX file")
            print()
        except Exception as e:
            print(f"❌ Error opening MBOX file: {e}")
            return []
        
        emails_data = []
        
        for idx, message in enumerate(self.mbox, 1):
            try:
                # Extract basic email metadata
                subject = self.decode_mime_words(
                    message.get('Subject', '(No Subject)')
                )
                from_addr = self.decode_mime_words(
                    message.get('From', 'Unknown')
                )
                to_addr = self.decode_mime_words(
                    message.get('To', 'Unknown')
                )
                date = message.get('Date', 'Unknown Date')
                
                # Extract name from email addresses
                from_name = self.extract_name_from_email(from_addr)
                
                # Get email body
                body_text, body_html, is_html = self.get_email_body(message)
                
                # Create preview (first 200 chars of plain text)
                preview = body_text[:200].replace('\n', ' ').strip()
                if len(body_text) > 200:
                    preview += '...'
                
                # Store email data
                email_data = {
                    'id': idx,
                    'subject': subject,
                    'from': from_addr,
                    'from_name': from_name,
                    'to': to_addr,
                    'date': date,
                    'body_text': body_text,
                    'body_html': body_html,
                    'is_html': is_html,
                    'preview': preview,
                    'attachments': []  # Will be populated if needed
                }
                
                emails_data.append(email_data)
                
                # Progress indicator
                if idx % 100 == 0 or idx == total_emails:
                    progress = (idx / total_emails) * 100
                    print(f"⏳ Processing: {idx}/{total_emails} ({progress:.1f}%) - {subject[:50]}")
            
            except Exception as e:
                print(f"⚠️  Error processing email {idx}: {e}")
                continue
        
        return emails_data
