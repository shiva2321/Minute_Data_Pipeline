"""
Log Email Alerter - Sends email notifications for critical errors
Includes dashboard screenshot with error context
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LogEmailAlerter:
    """Sends email alerts for critical log events"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_emails: List[str],
        use_tls: bool = True
    ):
        """
        Initialize email alerter

        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (usually 587 for TLS, 465 for SSL)
            sender_email: Sender email address
            sender_password: Sender password or app password
            recipient_emails: List of recipient email addresses
            use_tls: Use TLS (True) or SSL (False)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        self.use_tls = use_tls
        self.enabled = True

        # Track sent alerts to prevent spam
        self.last_alert_time = {}  # error_key -> timestamp
        self.min_alert_interval = 300  # Minimum 5 minutes between same error type

    def send_critical_error_alert(
        self,
        error_message: str,
        error_type: str = "CRITICAL ERROR",
        context: Optional[str] = None,
        screenshot_path: Optional[Path] = None,
        additional_logs: Optional[List[str]] = None
    ) -> bool:
        """
        Send email alert for critical error

        Args:
            error_message: The critical error message
            error_type: Type of error (default: "CRITICAL ERROR")
            context: Additional context about the error
            screenshot_path: Path to dashboard screenshot
            additional_logs: List of recent log messages for context

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled or not self.recipient_emails:
            return False

        # Check rate limiting
        if not self._should_send_alert(error_type):
            logger.debug(f"Skipping alert for {error_type} (rate limited)")
            return False

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = f"🚨 Pipeline Alert: {error_type}"
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)
            message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Create HTML body
            html_body = self._create_html_body(
                error_message,
                error_type,
                context,
                additional_logs
            )

            # Attach HTML
            part = MIMEText(html_body, 'html')
            message.attach(part)

            # Attach screenshot if provided
            if screenshot_path and screenshot_path.exists():
                self._attach_file(message, screenshot_path, 'dashboard_error.png')

            # Send email
            self._send_email(message)
            logger.info(f"Critical error alert sent: {error_type}")
            self.last_alert_time[error_type] = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Failed to send error alert: {e}")
            return False

    def send_processing_summary(
        self,
        summary_stats: dict,
        successful_symbols: List[str],
        failed_symbols: List[str],
        duration_seconds: float
    ) -> bool:
        """
        Send email summary of processing run

        Args:
            summary_stats: Dictionary with processing statistics
            successful_symbols: List of successfully processed symbols
            failed_symbols: List of failed symbols
            duration_seconds: Total processing duration

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled or not self.recipient_emails:
            return False

        try:
            message = MIMEMultipart()
            message['Subject'] = f"✅ Pipeline Processing Complete - {len(successful_symbols)}/{len(successful_symbols) + len(failed_symbols)} Success"
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)

            # Create summary HTML
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>📊 Pipeline Processing Summary</h2>
                    
                    <h3>Results</h3>
                    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
                        <tr style="background-color: #f0f0f0;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><b>Total Symbols</b></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{len(successful_symbols) + len(failed_symbols)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><b>✅ Successful</b></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: green;"><b>{len(successful_symbols)}</b></td>
                        </tr>
                        <tr style="background-color: #f0f0f0;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><b>❌ Failed</b></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: red;"><b>{len(failed_symbols)}</b></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><b>⏱️ Duration</b></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{duration_seconds/60:.1f} minutes</td>
                        </tr>
                    </table>

                    <h3>Additional Stats</h3>
                    <ul>
                        <li><b>API Calls Used:</b> {summary_stats.get('api_calls', 0)}</li>
                        <li><b>Data Points Fetched:</b> {summary_stats.get('data_points', 0):,}</li>
                        <li><b>Features Engineered:</b> {summary_stats.get('features_count', 0)}</li>
                    </ul>

                    {f"<h3>Successful Symbols</h3><p>{', '.join(successful_symbols)}</p>" if successful_symbols else ""}
                    {f"<h3>Failed Symbols</h3><p style='color: red;'>{', '.join(failed_symbols)}</p>" if failed_symbols else ""}

                    <hr>
                    <p style="color: #999; font-size: 12px;">Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
            </html>
            """

            part = MIMEText(html_body, 'html')
            message.attach(part)

            self._send_email(message)
            logger.info("Processing summary email sent")
            return True

        except Exception as e:
            logger.error(f"Failed to send summary email: {e}")
            return False

    def _create_html_body(
        self,
        error_message: str,
        error_type: str,
        context: Optional[str],
        additional_logs: Optional[List[str]]
    ) -> str:
        """Create HTML email body"""
        logs_html = ""
        if additional_logs:
            logs_html = """
            <h3>Recent Logs</h3>
            <pre style="background-color: #f5f5f5; padding: 10px; overflow-x: auto; max-width: 600px;">
            """
            logs_html += '\n'.join(additional_logs[-20:])  # Last 20 logs
            logs_html += "</pre>"

        context_html = f"<p><b>Context:</b> {context}</p>" if context else ""

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: red;">🚨 Critical Error Alert</h2>
                
                <p><b>Error Type:</b> {error_type}</p>
                <p><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Error Message</h3>
                <pre style="background-color: #ffe0e0; padding: 10px; border-left: 4px solid red; max-width: 600px;">
                {error_message}
                </pre>

                {context_html}
                {logs_html}

                <hr>
                <p style="color: #999; font-size: 12px;">
                    This is an automated alert from the Stock Pipeline Dashboard.
                    Please review the dashboard or logs for more details.
                </p>
            </body>
        </html>
        """
        return html

    def _attach_file(self, message: MIMEMultipart, file_path: Path, filename: str):
        """Attach a file to the email message"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            message.attach(part)

        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {e}")

    def _send_email(self, message: MIMEMultipart):
        """Send the email message"""
        try:
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)

        except Exception as e:
            logger.error(f"Failed to send email via {self.smtp_server}: {e}")
            raise

    def _should_send_alert(self, error_type: str) -> bool:
        """Check if we should send alert (rate limiting)"""
        last_time = self.last_alert_time.get(error_type)
        if last_time is None:
            return True

        time_since_last = (datetime.now() - last_time).total_seconds()
        return time_since_last >= self.min_alert_interval

    def test_connection(self) -> bool:
        """Test email connection without sending"""
        try:
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)

            logger.info("Email connection test successful")
            return True

        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False

