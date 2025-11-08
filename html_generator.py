"""
HTML Generator Module
Creates the HTML archive from parsed email data
"""

import json
import html as html_lib
import re
from pathlib import Path


class HTMLGenerator:
    """Generates HTML files for the email archive."""
    
    def __init__(self, output_dir):
        """
        Initialize the generator.
        
        Args:
            output_dir: Directory where HTML files will be created
        """
        self.output_dir = Path(output_dir)
        
    def setup_directories(self):
        """Create necessary output directories."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'emails').mkdir(exist_ok=True)
        (self.output_dir / 'attachments').mkdir(exist_ok=True)
    
    def make_links_clickable(self, text):
        """
        Convert URLs in text to clickable HTML links.
        
        Args:
            text: Plain text containing URLs
            
        Returns:
            HTML with clickable links
        """
        url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
        
        def replace_url(match):
            url = match.group(0)
            href = url if url.startswith('http') else f'https://{url}'
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{url}</a>'
        
        return re.sub(url_pattern, replace_url, text)
    
    def sanitize_html(self, html_content):
        """
        Sanitize HTML content for safe display.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Sanitized HTML
        """
        # Remove script tags
        html_content = re.sub(
            r'<script[^>]*>.*?</script>', 
            '', 
            html_content, 
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Remove event handlers
        html_content = re.sub(
            r'\s*on\w+\s*=\s*["\'][^"\']*["\']',
            '',
            html_content,
            flags=re.IGNORECASE
        )
        
        # Remove javascript: links
        html_content = re.sub(
            r'href\s*=\s*["\']javascript:[^"\']*["\']',
            'href="#"',
            html_content,
            flags=re.IGNORECASE
        )
        
        return html_content
    
    def _format_size(self, bytes_size):
        """Format byte size to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def create_email_html(self, email_data):
        """
        Create HTML file for a single email.
        
        Args:
            email_data: Dictionary containing email data
        """
        email_id = email_data['id']
        filepath = self.output_dir / 'emails' / f'{email_id}.html'
        
        # Format attachments section
        attachments_html = ""
        if email_data['attachments']:
            attachments_html = '<div class="attachments"><h3>📎 Attachments</h3><ul>'
            for att in email_data['attachments']:
                size = self._format_size(att['size'])
                filename = html_lib.escape(att['filename'])
                attachments_html += f'<li><a href="../{att["path"]}" download>{filename} ({size})</a></li>'
            attachments_html += '</ul></div>'
        
        # Format email body
        if email_data['is_html']:
            body_html = self.sanitize_html(email_data['body_html'])
            body_content = f'<div class="body-html">{body_html}</div>'
        else:
            escaped_text = html_lib.escape(email_data['body_text'])
            linked_text = self.make_links_clickable(escaped_text)
            body_content = f'<div class="body-text">{linked_text}</div>'
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_lib.escape(email_data['subject'])}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            background: #f5f5f5; 
        }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; min-height: 100vh; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ 
            background: linear-gradient(135deg, #4285f4 0%, #357ae8 100%); 
            color: white; 
            padding: 30px 40px; 
        }}
        .header h1 {{ font-size: 26px; margin-bottom: 20px; line-height: 1.3; }}
        .meta {{ font-size: 14px; opacity: 0.95; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; }}
        .meta div {{ margin: 5px 0; }}
        .meta strong {{ opacity: 0.8; }}
        .content {{ padding: 40px; }}
        .back {{ 
            display: inline-block; 
            margin-bottom: 30px; 
            padding: 12px 24px; 
            background: #4285f4; 
            color: white; 
            text-decoration: none; 
            border-radius: 6px; 
            transition: background 0.2s;
            font-weight: 500;
        }}
        .back:hover {{ background: #357ae8; }}
        .body-text {{ 
            white-space: pre-wrap; 
            background: #f9f9f9; 
            padding: 25px; 
            border-radius: 8px; 
            border-left: 4px solid #4285f4; 
            margin: 20px 0; 
            font-size: 15px;
            line-height: 1.7;
        }}
        .body-text a {{ color: #1a73e8; text-decoration: none; border-bottom: 1px solid #1a73e8; }}
        .body-text a:hover {{ background: #e8f0fe; }}
        .body-html {{ 
            padding: 25px; 
            background: white; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            margin: 20px 0; 
        }}
        .body-html a {{ color: #1a73e8; }}
        .attachments {{ 
            margin-top: 30px; 
            padding: 20px; 
            background: #fff3cd; 
            border-radius: 8px; 
            border-left: 4px solid #ffc107;
        }}
        .attachments h3 {{ margin-bottom: 15px; color: #856404; font-size: 18px; }}
        .attachments ul {{ list-style: none; }}
        .attachments li {{ 
            padding: 12px 0; 
            border-bottom: 1px solid #ffeaa7; 
            transition: background 0.2s;
        }}
        .attachments li:hover {{ background: rgba(255,193,7,0.1); }}
        .attachments li:last-child {{ border-bottom: none; }}
        .attachments a {{ color: #004085; text-decoration: none; font-weight: 500; }}
        .attachments a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{html_lib.escape(email_data['subject'])}</h1>
            <div class="meta">
                <div><strong>From:</strong> {html_lib.escape(email_data['from'])}</div>
                <div><strong>To:</strong> {html_lib.escape(email_data['to'])}</div>
                <div><strong>Date:</strong> {html_lib.escape(email_data['date'])}</div>
            </div>
        </div>
        <div class="content">
            <a href="../index.html" class="back">← Back to All Emails</a>
            {body_content}
            {attachments_html}
        </div>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def create_index_html(self, emails_data):
        """
        Create the main index page with search functionality.
        
        Args:
            emails_data: List of email data dictionaries
        """
        cleaned_data = []
        for email in emails_data:
            cleaned_email = {
                'id': email['id'],
                'subject': email['subject'],
                'from': email['from'],
                'from_name': email['from_name'],
                'to': email['to'],
                'date': email['date'],
                'preview': email['preview'].replace('\r', '').replace('\n', ' '),
                'attachments': email['attachments']
            }
            cleaned_data.append(cleaned_email)
        
        js_data = json.dumps(cleaned_data, ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail Archive</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5; 
        }}
        .header {{ 
            background: linear-gradient(135deg, #4285f4 0%, #357ae8 100%); 
            color: white; 
            padding: 40px 30px; 
            text-align: center; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.15); 
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 15px; font-weight: 600; }}
        .stats {{ font-size: 15px; opacity: 0.95; margin-top: 10px; }}
        .search-container {{ max-width: 900px; margin: 40px auto 30px; padding: 0 20px; }}
        .search-box {{ 
            width: 100%; 
            padding: 16px 24px; 
            font-size: 16px; 
            border: 2px solid #ddd; 
            border-radius: 50px; 
            outline: none; 
            transition: all 0.3s;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}
        .search-box:focus {{ 
            border-color: #4285f4; 
            box-shadow: 0 4px 12px rgba(66,133,244,0.2); 
        }}
        .container {{ max-width: 900px; margin: 0 auto 50px; padding: 0 20px; }}
        .email-list {{ list-style: none; }}
        .email-item {{ 
            background: white; 
            margin-bottom: 15px; 
            padding: 24px; 
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08); 
            transition: all 0.2s; 
            cursor: pointer;
            border: 1px solid #f0f0f0;
        }}
        .email-item:hover {{ 
            box-shadow: 0 6px 16px rgba(0,0,0,0.12); 
            transform: translateY(-2px);
            border-color: #4285f4;
        }}
        .email-subject {{ 
            font-size: 18px; 
            font-weight: 600; 
            color: #202124; 
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        .email-meta {{ 
            font-size: 14px; 
            color: #5f6368; 
            margin-bottom: 10px;
        }}
        .email-meta strong {{ color: #202124; }}
        .email-preview {{ 
            font-size: 14px; 
            color: #80868b; 
            margin-top: 12px; 
            line-height: 1.5;
            overflow: hidden;
            text-overflow: ellipsis; 
            display: -webkit-box; 
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical; 
        }}
        .no-results {{ 
            text-align: center; 
            padding: 60px 20px; 
            color: #5f6368;
            font-size: 16px;
        }}
        .attachment-badge {{ 
            display: inline-block; 
            background: #fff3cd; 
            color: #856404; 
            padding: 4px 10px;
            border-radius: 4px; 
            font-size: 12px; 
            margin-left: 10px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📧 Gmail Archive</h1>
        <div class="stats">
            <span id="total-emails">{len(emails_data)}</span> emails archived • 
            <span id="filtered-count">{len(emails_data)}</span> showing
        </div>
    </div>
    
    <div class="search-container">
        <input type="text" id="search" class="search-box" placeholder="🔍 Search emails by subject, sender, or content...">
    </div>
    
    <div class="container">
        <ul class="email-list" id="email-list"></ul>
        <div class="no-results" id="no-results" style="display: none;">
            No emails found matching your search.
        </div>
    </div>

    <script>
        const emailsData = {js_data};
        const emailList = document.getElementById('email-list');
        const searchBox = document.getElementById('search');
        const noResults = document.getElementById('no-results');
        const filteredCount = document.getElementById('filtered-count');

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function renderEmails(emails) {{
            if (emails.length === 0) {{
                emailList.style.display = 'none';
                noResults.style.display = 'block';
                filteredCount.textContent = '0';
                return;
            }}

            emailList.style.display = 'block';
            noResults.style.display = 'none';
            filteredCount.textContent = emails.length;

            const emailsHTML = emails.map(email => {{
                const attachmentBadge = email.attachments && email.attachments.length > 0 
                    ? `<span class="attachment-badge">📎 ${{email.attachments.length}}</span>` 
                    : '';
                
                return `
                    <li class="email-item" onclick="window.location.href='emails/${{email.id}}.html'">
                        <div class="email-subject">${{escapeHtml(email.subject)}}${{attachmentBadge}}</div>
                        <div class="email-meta">
                            <strong>${{escapeHtml(email.from_name)}}</strong> • ${{escapeHtml(email.date)}}
                        </div>
                        <div class="email-preview">${{escapeHtml(email.preview)}}</div>
                    </li>
                `;
            }}).join('');
            
            emailList.innerHTML = emailsHTML;
        }}

        function searchEmails(query) {{
            if (!query.trim()) {{
                renderEmails(emailsData);
                return;
            }}

            const lowerQuery = query.toLowerCase();
            const filtered = emailsData.filter(email => 
                email.subject.toLowerCase().includes(lowerQuery) ||
                email.from.toLowerCase().includes(lowerQuery) ||
                email.from_name.toLowerCase().includes(lowerQuery) ||
                email.to.toLowerCase().includes(lowerQuery) ||
                email.preview.toLowerCase().includes(lowerQuery)
            );

            renderEmails(filtered);
        }}

        searchBox.addEventListener('input', (e) => searchEmails(e.target.value));
        
        // Initial render
        renderEmails(emailsData);
    </script>
</body>
</html>"""
        
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def create_archive(self, emails_data):
        """
        Create the complete HTML archive.
        
        Args:
            emails_data: List of email data dictionaries
        """
        self.setup_directories()
        
        print("📝 Creating individual email pages...")
        for idx, email in enumerate(emails_data, 1):
            self.create_email_html(email)
            if idx % 100 == 0 or idx == len(emails_data):
                progress = (idx / len(emails_data)) * 100
                print(f"   {idx}/{len(emails_data)} ({progress:.1f}%)")
        
        print("🏠 Creating main index page...")
        self.create_index_html(emails_data)
        
        print("✅ HTML generation complete!")
