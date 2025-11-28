"""
Settings Panel - Application configuration
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLineEdit, QPushButton, QSpinBox, QCheckBox,
                              QRadioButton, QLabel, QMessageBox, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt
import json
import os

from config import settings


class SettingsPanel(QWidget):
    """
    Settings panel for API and database configuration
    """

    settings_changed = pyqtSignal(dict)  # Updated settings

    def __init__(self, parent=None):
        super().__init__(parent)

        self.config_path = os.path.expanduser('~/.pipeline_dashboard_config.json')
        self.current_settings = self._load_settings()

        self.init_ui()
        self._populate_from_settings()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_layout = QVBoxLayout()

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("EODHD API Key:"))

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your API key...")
        api_key_layout.addWidget(self.api_key_input)

        show_key_btn = QPushButton("👁")
        show_key_btn.setMaximumWidth(40)
        show_key_btn.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(show_key_btn)

        test_api_btn = QPushButton("Test")
        test_api_btn.clicked.connect(self._test_api_connection)
        api_key_layout.addWidget(test_api_btn)

        api_layout.addLayout(api_key_layout)

        # API Status
        self.api_status_label = QLabel("Status: Not tested")
        self.api_status_label.setStyleSheet("color: #ca5010;")
        api_layout.addWidget(self.api_status_label)

        # Rate Limits
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Calls per Minute:"))

        self.minute_limit_spin = QSpinBox()
        self.minute_limit_spin.setMinimum(1)
        self.minute_limit_spin.setMaximum(200)
        self.minute_limit_spin.setValue(80)
        rate_layout.addWidget(self.minute_limit_spin)

        rate_layout.addWidget(QLabel("(default: 80)"))
        rate_layout.addStretch()

        api_layout.addLayout(rate_layout)

        daily_layout = QHBoxLayout()
        daily_layout.addWidget(QLabel("Calls per Day:"))

        self.daily_limit_spin = QSpinBox()
        self.daily_limit_spin.setMinimum(1000)
        self.daily_limit_spin.setMaximum(100000)
        self.daily_limit_spin.setValue(95000)
        self.daily_limit_spin.setSingleStep(1000)
        daily_layout.addWidget(self.daily_limit_spin)

        daily_layout.addWidget(QLabel("(default: 95,000)"))
        daily_layout.addStretch()

        api_layout.addLayout(daily_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # MongoDB Configuration
        mongo_group = QGroupBox("MongoDB Configuration")
        mongo_layout = QVBoxLayout()

        # Connection URI
        uri_layout = QHBoxLayout()
        uri_layout.addWidget(QLabel("Connection URI:"))

        self.mongo_uri_input = QLineEdit()
        self.mongo_uri_input.setPlaceholderText("mongodb://localhost:27017")
        uri_layout.addWidget(self.mongo_uri_input)

        test_mongo_btn = QPushButton("Test")
        test_mongo_btn.clicked.connect(self._test_mongo_connection)
        uri_layout.addWidget(test_mongo_btn)

        mongo_layout.addLayout(uri_layout)

        # Database Name
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Database Name:"))

        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("stock_analysis")
        db_layout.addWidget(self.db_name_input)

        db_layout.addStretch()

        mongo_layout.addLayout(db_layout)

        # MongoDB Status
        self.mongo_status_label = QLabel("Status: Not connected")
        self.mongo_status_label.setStyleSheet("color: #ca5010;")
        mongo_layout.addWidget(self.mongo_status_label)

        mongo_group.setLayout(mongo_layout)
        layout.addWidget(mongo_group)

        # Pipeline Defaults
        pipeline_group = QGroupBox("Pipeline Defaults")
        pipeline_layout = QVBoxLayout()

        # Default history years
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("Default History Years:"))

        self.default_years_spin = QSpinBox()
        self.default_years_spin.setMinimum(1)
        self.default_years_spin.setMaximum(5)
        self.default_years_spin.setValue(2)
        self.default_years_spin.setSuffix(" years")
        history_layout.addWidget(self.default_years_spin)

        history_layout.addStretch()
        pipeline_layout.addLayout(history_layout)

        # Default chunk size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Default Chunk Size:"))

        self.default_chunk_spin = QSpinBox()
        self.default_chunk_spin.setMinimum(1)
        self.default_chunk_spin.setMaximum(30)
        self.default_chunk_spin.setValue(30)  # Changed to 30 days
        self.default_chunk_spin.setSuffix(" days")
        chunk_layout.addWidget(self.default_chunk_spin)

        chunk_layout.addStretch()
        pipeline_layout.addLayout(chunk_layout)

        # Max parallel workers
        workers_layout = QHBoxLayout()
        workers_layout.addWidget(QLabel("Max Parallel Workers:"))

        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setMinimum(1)
        self.max_workers_spin.setMaximum(12)
        self.max_workers_spin.setValue(10)
        self.max_workers_spin.setSuffix(" threads")
        workers_layout.addWidget(self.max_workers_spin)

        workers_layout.addStretch()
        pipeline_layout.addLayout(workers_layout)

        # Options
        self.store_metadata_check = QCheckBox("Store Backfill Metadata")
        self.store_metadata_check.setChecked(True)
        pipeline_layout.addWidget(self.store_metadata_check)

        self.auto_retry_check = QCheckBox("Enable Auto-Retry on Failure (max 3 attempts)")
        self.auto_retry_check.setChecked(True)
        pipeline_layout.addWidget(self.auto_retry_check)

        pipeline_group.setLayout(pipeline_layout)
        layout.addWidget(pipeline_group)

        # UI Settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QVBoxLayout()

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))

        self.dark_radio = QRadioButton("Dark")
        self.dark_radio.setChecked(True)
        theme_layout.addWidget(self.dark_radio)

        self.light_radio = QRadioButton("Light")
        theme_layout.addWidget(self.light_radio)

        self.auto_radio = QRadioButton("Auto (system)")
        theme_layout.addWidget(self.auto_radio)

        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)

        # Log level
        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel("Log Level:"))

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level_combo.setCurrentText('INFO')
        log_layout.addWidget(self.log_level_combo)

        log_layout.addStretch()
        ui_layout.addLayout(log_layout)

        # Refresh rate
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Refresh Rate:"))

        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setMinimum(1)
        self.refresh_rate_spin.setMaximum(10)
        self.refresh_rate_spin.setValue(2)
        self.refresh_rate_spin.setSuffix(" seconds")
        refresh_layout.addWidget(self.refresh_rate_spin)

        refresh_layout.addStretch()
        ui_layout.addLayout(refresh_layout)

        # Options
        self.notifications_check = QCheckBox("Enable Desktop Notifications")
        self.notifications_check.setChecked(False)
        ui_layout.addWidget(self.notifications_check)

        self.minimize_tray_check = QCheckBox("Minimize to System Tray")
        self.minimize_tray_check.setChecked(False)
        ui_layout.addWidget(self.minimize_tray_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        # Email Configuration
        email_group = QGroupBox("Email Alerts Configuration")
        email_layout = QVBoxLayout()

        # Enable email alerts
        self.email_enabled_check = QCheckBox("Enable Email Alerts on Critical Errors")
        self.email_enabled_check.setChecked(False)
        email_layout.addWidget(self.email_enabled_check)

        # SMTP Server
        smtp_layout = QHBoxLayout()
        smtp_layout.addWidget(QLabel("SMTP Server:"))
        self.smtp_server_input = QLineEdit()
        self.smtp_server_input.setPlaceholderText("smtp.gmail.com")
        smtp_layout.addWidget(self.smtp_server_input)
        email_layout.addLayout(smtp_layout)

        # SMTP Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("SMTP Port:"))
        self.smtp_port_spin = QSpinBox()
        self.smtp_port_spin.setMinimum(1)
        self.smtp_port_spin.setMaximum(65535)
        self.smtp_port_spin.setValue(587)
        port_layout.addWidget(self.smtp_port_spin)
        port_layout.addStretch()
        email_layout.addLayout(port_layout)

        # Sender Email
        sender_layout = QHBoxLayout()
        sender_layout.addWidget(QLabel("Sender Email:"))
        self.sender_email_input = QLineEdit()
        self.sender_email_input.setPlaceholderText("your_email@gmail.com")
        sender_layout.addWidget(self.sender_email_input)
        email_layout.addLayout(sender_layout)

        # Sender Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Sender Password:"))
        self.sender_password_input = QLineEdit()
        self.sender_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.sender_password_input.setPlaceholderText("App password or account password")
        password_layout.addWidget(self.sender_password_input)

        show_pwd_btn = QPushButton("👁")
        show_pwd_btn.setMaximumWidth(40)
        show_pwd_btn.clicked.connect(self._toggle_password_visibility)
        password_layout.addWidget(show_pwd_btn)

        email_layout.addLayout(password_layout)

        # Recipient Emails
        recipient_layout = QHBoxLayout()
        recipient_layout.addWidget(QLabel("Recipient Email(s):"))
        self.recipient_emails_input = QLineEdit()
        self.recipient_emails_input.setPlaceholderText("admin@example.com, ops@example.com")
        recipient_layout.addWidget(self.recipient_emails_input)
        email_layout.addLayout(recipient_layout)

        # Test button
        test_email_btn = QPushButton("🔧 Test Email Configuration")
        test_email_btn.clicked.connect(self._test_email_configuration)
        email_layout.addWidget(test_email_btn)

        email_group.setLayout(email_layout)
        layout.addWidget(email_group)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("↺ Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        layout.addStretch()
        self.setLayout(layout)

    def _load_settings(self) -> dict:
        """Load settings from file"""
        default_settings = {
            'api_key': settings.eodhd_api_key,
            'mongo_uri': settings.mongodb_uri,
            'db_name': settings.mongodb_database,  # Changed from database_name to mongodb_database
            'minute_limit': 80,
            'daily_limit': 95000,
            'default_years': 2,
            'default_chunk': 30,  # Changed to 30 days
            'max_workers': 10,
            'store_metadata': True,
            'auto_retry': True,
            'theme': 'dark',
            'log_level': 'INFO',
            'refresh_rate': 2,
            'notifications': False,
            'minimize_tray': False
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
            except Exception as e:
                print(f"Failed to load settings: {e}")

        return default_settings

    def _populate_from_settings(self):
        """Populate UI from current settings"""
        self.api_key_input.setText(self.current_settings.get('api_key', ''))
        self.mongo_uri_input.setText(self.current_settings.get('mongo_uri', ''))
        self.db_name_input.setText(self.current_settings.get('db_name', ''))
        self.minute_limit_spin.setValue(self.current_settings.get('minute_limit', 80))
        self.daily_limit_spin.setValue(self.current_settings.get('daily_limit', 95000))
        self.default_years_spin.setValue(self.current_settings.get('default_years', 2))
        self.default_chunk_spin.setValue(self.current_settings.get('default_chunk', 30))
        self.max_workers_spin.setValue(self.current_settings.get('max_workers', 10))
        self.store_metadata_check.setChecked(self.current_settings.get('store_metadata', True))
        self.auto_retry_check.setChecked(self.current_settings.get('auto_retry', True))

        # Email settings
        self.email_enabled_check.setChecked(self.current_settings.get('email_enabled', False))
        self.smtp_server_input.setText(self.current_settings.get('smtp_server', 'smtp.gmail.com'))
        self.smtp_port_spin.setValue(self.current_settings.get('smtp_port', 587))
        self.sender_email_input.setText(self.current_settings.get('sender_email', ''))
        self.sender_password_input.setText(self.current_settings.get('sender_password', ''))
        self.recipient_emails_input.setText(self.current_settings.get('recipient_emails', ''))
        self.log_level_combo.setCurrentText(self.current_settings.get('log_level', 'INFO'))
        self.refresh_rate_spin.setValue(self.current_settings.get('refresh_rate', 2))
        self.notifications_check.setChecked(self.current_settings.get('notifications', False))
        self.minimize_tray_check.setChecked(self.current_settings.get('minimize_tray', False))

        theme = self.current_settings.get('theme', 'dark')
        if theme == 'dark':
            self.dark_radio.setChecked(True)
        elif theme == 'light':
            self.light_radio.setChecked(True)
        else:
            self.auto_radio.setChecked(True)

    def _toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _test_api_connection(self):
        """Test API connection"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "No API Key", "Please enter an API key")
            return

        # Simple test - could make actual API call
        self.api_status_label.setText("✅ API key configured")
        self.api_status_label.setStyleSheet("color: #0e7c0e;")

        QMessageBox.information(
            self,
            "API Test",
            "API key configured.\n\nNote: Actual validation happens during data fetching."
        )

    def _test_mongo_connection(self):
        """Test MongoDB connection"""
        # Import here to avoid circular dependencies
        try:
            from pymongo import MongoClient

            uri = self.mongo_uri_input.text().strip() or "mongodb://localhost:27017"

            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.server_info()  # Force connection

            self.mongo_status_label.setText("✅ Connected successfully")
            self.mongo_status_label.setStyleSheet("color: #0e7c0e;")

            QMessageBox.information(self, "Success", "MongoDB connection successful!")

        except Exception as e:
            self.mongo_status_label.setText(f"❌ Connection failed: {str(e)}")
            self.mongo_status_label.setStyleSheet("color: #c50f1f;")

            QMessageBox.critical(self, "Connection Failed", f"Failed to connect:\n{str(e)}")

    def _toggle_password_visibility(self):
        """Toggle email password visibility"""
        if self.sender_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.sender_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.sender_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _test_email_configuration(self):
        """Test email configuration"""
        if not self.email_enabled_check.isChecked():
            QMessageBox.warning(self, "Email Disabled", "Email alerts are disabled. Enable them first.")
            return

        # Validate inputs
        if not self.sender_email_input.text().strip():
            QMessageBox.warning(self, "Missing Email", "Please enter sender email address")
            return

        if not self.recipient_emails_input.text().strip():
            QMessageBox.warning(self, "Missing Recipient", "Please enter at least one recipient email")
            return

        if not self.sender_password_input.text().strip():
            QMessageBox.warning(self, "Missing Password", "Please enter sender password")
            return

        # Test connection
        try:
            from dashboard.services import LogEmailAlerter
            import smtplib

            smtp_server = self.smtp_server_input.text().strip() or "smtp.gmail.com"
            smtp_port = self.smtp_port_spin.value()
            sender_email = self.sender_email_input.text().strip()
            password = self.sender_password_input.text().strip()

            # Test SMTP connection
            with smtplib.SMTP(smtp_server, smtp_port, timeout=5) as server:
                server.starttls()
                server.login(sender_email, password)

            QMessageBox.information(
                self,
                "Email Test Success",
                "Email configuration is valid!\n\n"
                "✅ SMTP server connection successful\n"
                "✅ Authentication successful\n\n"
                "Email alerts will be sent on critical errors."
            )

        except smtplib.SMTPAuthenticationError:
            QMessageBox.critical(self, "Auth Failed", "Email authentication failed.\nCheck email and password.")
        except smtplib.SMTPException as e:
            QMessageBox.critical(self, "SMTP Error", f"SMTP error:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to test email:\n{str(e)}")

    def _save_settings(self):
        """Save current settings"""
        # Gather settings
        theme = 'dark' if self.dark_radio.isChecked() else ('light' if self.light_radio.isChecked() else 'auto')

        settings_dict = {
            'api_key': self.api_key_input.text().strip(),
            'mongo_uri': self.mongo_uri_input.text().strip(),
            'db_name': self.db_name_input.text().strip(),
            'minute_limit': self.minute_limit_spin.value(),
            'daily_limit': self.daily_limit_spin.value(),
            'default_years': self.default_years_spin.value(),
            'default_chunk': self.default_chunk_spin.value(),
            'max_workers': self.max_workers_spin.value(),
            'store_metadata': self.store_metadata_check.isChecked(),
            'auto_retry': self.auto_retry_check.isChecked(),
            'theme': theme,
            'log_level': self.log_level_combo.currentText(),
            'refresh_rate': self.refresh_rate_spin.value(),
            'notifications': self.notifications_check.isChecked(),
            'minimize_tray': self.minimize_tray_check.isChecked(),
            # Email settings
            'email_enabled': self.email_enabled_check.isChecked(),
            'smtp_server': self.smtp_server_input.text().strip(),
            'smtp_port': self.smtp_port_spin.value(),
            'sender_email': self.sender_email_input.text().strip(),
            'sender_password': self.sender_password_input.text().strip(),
            'recipient_emails': self.recipient_emails_input.text().strip()
        }

        try:
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(settings_dict, f, indent=2)

            self.current_settings = settings_dict
            self.settings_changed.emit(settings_dict)

            QMessageBox.information(self, "Success", "Settings saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save settings:\n{str(e)}")

    def _reset_to_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self._load_settings()
            self._populate_from_settings()

    def get_email_settings(self) -> dict:
        """Return current email alert configuration."""
        return {
            'email_enabled': self.email_enabled_check.isChecked(),
            'smtp_server': self.smtp_server_input.text().strip(),
            'smtp_port': self.smtp_port_spin.value(),
            'sender_email': self.sender_email_input.text().strip(),
            'sender_password': self.sender_password_input.text().strip(),
            'recipient_emails': self.recipient_emails_input.text().strip()
        }
