
import smtplib
from email.message import EmailMessage
from typing import List, Optional
import traceback
import os
from datetime import datetime, timedelta
from PyQt6.QtGui import QGuiApplication

class EmailAlerter:
    """Handles sending email alerts for critical pipeline errors."""
    def __init__(self, config: Optional[dict] = None):
        self.enabled = False
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.sender_email = ''
        self.sender_password = ''
        self.recipient_emails: List[str] = []
        self.cooldown_minutes = 5  # avoid spamming
        self.last_sent_time: Optional[datetime] = None
        if config:
            self.update_config(config)

    def update_config(self, config: dict):
        """Update internal configuration from settings panel."""
        self.enabled = bool(config.get('email_enabled', False))
        self.smtp_server = config.get('smtp_server', self.smtp_server)
        self.smtp_port = int(config.get('smtp_port', self.smtp_port))
        # Allow env override for security
        self.sender_email = os.getenv('PIPELINE_ALERT_EMAIL', config.get('sender_email', self.sender_email))
        self.sender_password = os.getenv('PIPELINE_ALERT_PASSWORD', config.get('sender_password', self.sender_password))
        recipients = config.get('recipient_emails', '')
        self.recipient_emails = [r.strip() for r in recipients.split(',') if r.strip()]

    def _in_cooldown(self) -> bool:
        if not self.last_sent_time:
            return False
        return datetime.utcnow() - self.last_sent_time < timedelta(minutes=self.cooldown_minutes)

    def _capture_screenshot(self, window) -> Optional[bytes]:
        try:
            if window is None:
                return None
            screen = QGuiApplication.primaryScreen()
            if not screen:
                return None
            pixmap = screen.grabWindow(window.winId())
            # Save to bytes (PNG)
            from io import BytesIO
            buffer = BytesIO()
            pixmap.save(buffer, 'PNG')
            return buffer.getvalue()
        except Exception:
            return None

    def send_alert(self, subject: str, message: str, window=None):
        """Send an email alert if enabled and not in cooldown."""
        if not self.enabled:
            return
        if not self.sender_email or not self.sender_password or not self.recipient_emails:
            return
        if self._in_cooldown():
            return
        try:
            email = EmailMessage()
            email['From'] = self.sender_email
            email['To'] = ', '.join(self.recipient_emails)
            email['Subject'] = subject
            body = f"Time: {datetime.utcnow().isoformat()}\n\n{message}\n"
            email.set_content(body)
            # Attach screenshot
            screenshot_bytes = self._capture_screenshot(window)
            if screenshot_bytes:
                email.add_attachment(screenshot_bytes, maintype='image', subtype='png', filename='dashboard.png')
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(email)
            self.last_sent_time = datetime.utcnow()
        except Exception as e:
            # Log to stderr - we don't rethrow to avoid cascading failures
            traceback.print_exc()


