"""
Company Selector Dialog - Browse and select companies to process
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QSpinBox, QFileDialog, QMessageBox, QCheckBox, QProgressDialog
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt6.QtGui import QIcon
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class CompanySelectorDialog(QDialog):
    """Dialog for selecting companies to process"""

    # Signals
    companies_selected = pyqtSignal(list)  # List of symbols

    def __init__(self, company_cache_manager, parent=None):
        """
        Initialize company selector

        Args:
            company_cache_manager: CacheStore instance for company list
            parent: Parent widget
        """
        super().__init__(parent)
        self.cache_store = company_cache_manager  # Store as cache_store
        self.companies = []
        self.selected_symbols = []
        self.cache_status_label = None  # Initialize to None, will be set in create_top_n_tab

        self.setWindowTitle("Company Selector")
        self.setGeometry(100, 100, 900, 600)

        self.init_ui()

        # Try to load cached companies first (avoid expensive API calls)
        self.load_cached_companies()

        # If no cached companies, show message
        if not self.companies:
            QMessageBox.information(
                self,
                "No Cached Companies",
                "No companies found in cache.\n\n"
                "Please click 'Load from Cache' to load company list.\n"
                "(This only needs to be done once per 24 hour period)"
            )

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Top 100 Companies
        top_n_tab = self.create_top_n_tab()
        tabs.addTab(top_n_tab, "Top 100 Companies")

        # Tab 2: Search
        search_tab = self.create_search_tab()
        tabs.addTab(search_tab, "Search")

        # Tab 3: File Upload
        file_tab = self.create_file_tab()
        tabs.addTab(file_tab, "From File")

        # Tab 4: Custom Input
        custom_tab = self.create_custom_input_tab()
        tabs.addTab(custom_tab, "Custom Input")

        layout.addWidget(tabs)

        # Status label - shows cumulative selection
        self.status_label = QLabel("💡 Tip: Check companies to add to processing list. Selections persist across sessions!")
        self.status_label.setStyleSheet("color: #007ACC; font-size: 11px; padding: 5px;")
        layout.addWidget(self.status_label)

        # Selected companies display
        selected_layout = QHBoxLayout()
        selected_layout.addWidget(QLabel("📋 Selected for Processing:"))
        self.selected_display = QLabel("")
        self.selected_display.setStyleSheet("color: #0E7C0E; font-weight: bold;")
        selected_layout.addWidget(self.selected_display)
        selected_layout.addStretch()
        layout.addLayout(selected_layout)

        # Bottom buttons
        button_layout = QHBoxLayout()

        remove_all_btn = QPushButton("🗑️ Remove All Selected")
        remove_all_btn.clicked.connect(self.on_remove_all_clicked)
        remove_all_btn.setStyleSheet("background-color: #FF6B6B; color: white;")
        button_layout.addWidget(remove_all_btn)

        close_btn = QPushButton("✗ Close")
        close_btn.clicked.connect(self.on_close_clicked)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_top_n_tab(self) -> QWidget:
        """Create tab for selecting top 100 companies"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Control layout
        control_layout = QHBoxLayout()

        # Cache status label
        self.cache_status_label = QLabel("Cache: Loading...")
        self.cache_status_label.setStyleSheet("color: #666; font-size: 10px;")
        control_layout.addWidget(self.cache_status_label)

        control_layout.addStretch()

        fetch_btn = QPushButton("Load from Cache")
        fetch_btn.clicked.connect(self.on_fetch_from_eodhd)
        control_layout.addWidget(fetch_btn)

        # Force refresh button
        force_refresh_btn = QPushButton("🔄 Force Refresh")
        force_refresh_btn.setMaximumWidth(120)
        force_refresh_btn.clicked.connect(self.on_force_refresh)
        force_refresh_btn.setStyleSheet("background-color: #FF6B6B; color: white;")
        control_layout.addWidget(force_refresh_btn)

        layout.addLayout(control_layout)

        # Table for display (Top 100)
        self.top_n_table = QTableWidget()
        self.top_n_table.setColumnCount(4)
        self.top_n_table.setHorizontalHeaderLabels(['Select', 'Symbol', 'Company Name', 'Exchange'])
        self.top_n_table.setColumnWidth(0, 60)
        self.top_n_table.setColumnWidth(1, 80)
        self.top_n_table.setColumnWidth(2, 300)
        self.top_n_table.setColumnWidth(3, 100)

        layout.addWidget(self.top_n_table)

        widget.setLayout(layout)
        return widget

    def create_search_tab(self) -> QWidget:
        """Create tab for searching companies"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type symbol or company name...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        # Results table
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(4)
        self.search_table.setHorizontalHeaderLabels(['Select', 'Symbol', 'Company Name', 'Exchange'])
        self.search_table.setColumnWidth(0, 60)
        self.search_table.setColumnWidth(1, 80)
        self.search_table.setColumnWidth(2, 300)
        self.search_table.setColumnWidth(3, 100)

        layout.addWidget(self.search_table)

        widget.setLayout(layout)
        return widget

    def create_file_tab(self) -> QWidget:
        """Create tab for file upload"""
        widget = QWidget()
        layout = QVBoxLayout()

        # File selector
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Select file:"))

        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("symbols.txt or symbols.csv")
        file_layout.addWidget(self.file_path_input)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.on_browse_file)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # File content table
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(['Select', 'Symbol', 'Name (optional)'])
        self.file_table.setColumnWidth(0, 60)
        self.file_table.setColumnWidth(1, 100)
        self.file_table.setColumnWidth(2, 400)

        layout.addWidget(self.file_table)

        widget.setLayout(layout)
        return widget

    def create_custom_input_tab(self) -> QWidget:
        """Create tab for custom symbol input"""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter symbols (comma or newline separated):"))

        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("AAPL, MSFT, GOOGL or paste symbols from file")
        layout.addWidget(self.custom_input)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    @pyqtSlot()
    def load_cached_companies(self):
        """Load company list from cache and populate tables"""
        if not self.cache_store:
            return

        try:
            # Check if cache exists and is fresh (24 hours)
            companies = self.cache_store.get_company_list()

            if not companies:
                # No companies in cache
                if self.cache_status_label:
                    self.cache_status_label.setText("Cache: Empty - Click 'Fetch from EODHD'")
                logging.info("No companies in cache")
                return

            # Check if cache is stale
            is_stale = self.cache_store.is_company_list_stale(max_age_hours=24)
            fetch_time = self.cache_store.get_company_list_fetch_time()

            # Update status label if available
            if self.cache_status_label and fetch_time:
                # Calculate age
                age = datetime.now() - fetch_time
                if age.seconds < 60:
                    age_str = "just now"
                elif age.seconds < 3600:
                    age_str = f"{age.seconds // 60}m ago"
                elif age.days == 0:
                    age_str = f"{age.seconds // 3600}h ago"
                else:
                    age_str = f"{age.days}d ago"

                status_color = "#0E7C0E" if not is_stale else "#FF6B6B"
                self.cache_status_label.setText(f"Cache: {len(companies)} companies ({age_str})")
                self.cache_status_label.setStyleSheet(f"color: {status_color}; font-size: 10px;")

            # Store companies
            self.companies = companies

            # Populate top_n_table with first 100 (for Top 100 Companies tab)
            if hasattr(self, 'top_n_table'):
                self.populate_top_n_table(companies)

            logging.info(f"Loaded {len(companies)} companies from cache (fresh={not is_stale})")

            # Load previously selected companies and check them
            self.load_previously_selected()

            # Update selection display
            self.update_selected_display()

        except Exception as e:
            logging.error(f"Failed to load companies from cache: {e}")
            if self.cache_status_label:
                self.cache_status_label.setText(f"Cache: Error loading")

    def populate_top_n_table(self, companies):
        """Populate top_n_table with top 100 companies"""
        if not hasattr(self, 'top_n_table'):
            return

        # Show only top 100
        companies_to_show = companies[:100]
        self.top_n_table.setRowCount(len(companies_to_show))

        for row, company in enumerate(companies_to_show):
            # Checkbox - use proper checkbox widget
            from PyQt6.QtWidgets import QCheckBox
            checkbox = QCheckBox()
            checkbox.setChecked(False)

            # Get symbol - could be 'Code' (from API) or 'symbol' (from cache)
            symbol = company.get('Code') or company.get('symbol', '')
            selected_companies = self.cache_store.get_selected_companies() if self.cache_store else []
            if symbol in selected_companies:
                checkbox.setChecked(True)

            # Connect to immediate add/remove
            checkbox.stateChanged.connect(lambda state, s=symbol: self.on_checkbox_changed(s, state))
            self.top_n_table.setCellWidget(row, 0, checkbox)

            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            self.top_n_table.setItem(row, 1, symbol_item)

            # Company name - could be 'Name' (from API) or 'company_name' (from cache)
            company_name = company.get('Name') or company.get('company_name', '')
            name_item = QTableWidgetItem(company_name)
            self.top_n_table.setItem(row, 2, name_item)

            # Exchange
            exchange = company.get('Exchange') or company.get('exchange', '')
            exchange_item = QTableWidgetItem(exchange)
            self.top_n_table.setItem(row, 3, exchange_item)

    @pyqtSlot()
    def on_fetch_from_eodhd(self):
        """Load or fetch company list from EODHD API"""
        # First, try to load from cache
        cache_companies = self.cache_store.get_company_list() if self.cache_store else []

        if cache_companies:
            # Cache exists, load it
            logging.info(f"Loading {len(cache_companies)} companies from cache")
            self.companies = cache_companies
            self.populate_top_n_table(cache_companies)
            self.update_selected_display()

            fetch_time = self.cache_store.get_company_list_fetch_time()
            if fetch_time:
                age = datetime.now() - fetch_time
                if age.days == 0 and age.seconds < 3600:
                    age_str = f"{age.seconds // 60}m ago"
                elif age.days == 0:
                    age_str = f"{age.seconds // 3600}h ago"
                else:
                    age_str = f"{age.days}d ago"

                QMessageBox.information(
                    self,
                    "Companies Loaded",
                    f"Loaded {len(cache_companies)} companies from cache (cached {age_str})\n\n"
                    f"Click 'Force Refresh' to fetch fresh data if needed."
                )
            return

        # No cache exists, fetch from EODHD
        try:
            progress = QProgressDialog("Fetching companies from EODHD...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            from data_fetcher import EODHDDataFetcher
            from config import settings

            fetcher = EODHDDataFetcher(settings.eodhd_api_key)

            exchanges = ['NASDAQ', 'NYSE', 'AMEX']
            all_companies = []

            for exchange in exchanges:
                companies = fetcher.fetch_exchange_symbols(exchange)
                if companies:
                    all_companies.extend(companies)
                    logging.info(f"Fetched {len(companies)} from {exchange}")

            progress.close()

            if all_companies:
                # Cache the fetched companies
                if self.cache_store:
                    self.cache_store.save_company_list(all_companies)

                # Store in memory
                self.companies = all_companies

                # Populate table
                self.populate_top_n_table(all_companies)

                QMessageBox.information(
                    self,
                    "Companies Fetched",
                    f"Successfully fetched {len(all_companies)} companies from US exchanges:\n"
                    f"• NASDAQ: {len([c for c in all_companies if c.get('Exchange') == 'NASDAQ'])}\n"
                    f"• NYSE: {len([c for c in all_companies if c.get('Exchange') == 'NYSE'])}\n"
                    f"• AMEX: {len([c for c in all_companies if c.get('Exchange') == 'AMEX'])}\n\n"
                    f"Companies are now cached. You won't need to fetch again for 24 hours."
                )
            else:
                QMessageBox.warning(self, "No Companies", "Failed to fetch companies from EODHD")

        except Exception as e:
            logging.error(f"Error fetching from EODHD: {e}")
            QMessageBox.critical(self, "Error", f"Failed to fetch companies: {e}")

    @pyqtSlot(str)
    def on_search_changed(self, text: str):
        """Handle search text change"""
        if not text:
            self.search_table.setRowCount(0)
            return

        # Search through cached companies
        text_upper = text.upper()
        results = []

        for company in self.companies:
            # Support both API format (Code/Name) and cache format (symbol/company_name)
            symbol = (company.get('Code') or company.get('symbol', '')).upper()
            name = (company.get('Name') or company.get('company_name', '')).upper()

            if text_upper in symbol or text_upper in name:
                results.append(company)

        self.display_search_results(results)

    def display_search_results(self, results: List[Dict]):
        """Display search results in table"""
        self.search_table.setRowCount(len(results))

        for row, company in enumerate(results):
            # Checkbox - use proper checkbox widget
            from PyQt6.QtWidgets import QCheckBox
            checkbox = QCheckBox()
            checkbox.setChecked(False)

            # Get symbol - support both formats
            symbol = company.get('Code') or company.get('symbol', '')
            selected_companies = self.cache_store.get_selected_companies() if self.cache_store else []
            if symbol in selected_companies:
                checkbox.setChecked(True)

            # Connect signal
            checkbox.stateChanged.connect(lambda state, s=symbol: self.on_checkbox_changed(s, state))
            self.search_table.setCellWidget(row, 0, checkbox)

            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            self.search_table.setItem(row, 1, symbol_item)

            # Company name - support both formats
            company_name = company.get('Name') or company.get('company_name', '')
            name_item = QTableWidgetItem(company_name)
            self.search_table.setItem(row, 2, name_item)

            # Exchange
            exchange = company.get('Exchange') or company.get('exchange', '')
            exchange_item = QTableWidgetItem(exchange)
            self.search_table.setItem(row, 3, exchange_item)

    @pyqtSlot()
    def on_browse_file(self):
        """Browse for file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company File",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            self.file_path_input.setText(file_path)
            self.load_companies_from_file(file_path)

    def load_companies_from_file(self, file_path: str):
        """Load companies from text or CSV file"""
        try:
            companies = []
            path = Path(file_path)

            if path.suffix.lower() == '.csv':
                # CSV format: symbol, name
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if parts:
                            companies.append({
                                'symbol': parts[0].strip(),
                                'name': parts[1].strip() if len(parts) > 1 else ''
                            })
            else:
                # Text format: one symbol per line
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        symbol = line.strip()
                        if symbol:
                            companies.append({
                                'symbol': symbol,
                                'name': ''
                            })

            self.display_file_companies(companies)
            logger.info(f"Loaded {len(companies)} companies from file")

        except Exception as e:
            logger.error(f"Failed to load companies from file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")

    def display_file_companies(self, companies: List[Dict]):
        """Display companies from file in table"""
        self.file_table.setRowCount(len(companies))

        for row, company in enumerate(companies):
            # Checkbox - use proper checkbox widget
            from PyQt6.QtWidgets import QCheckBox
            checkbox = QCheckBox()
            checkbox.setChecked(False)

            # Check if already selected
            symbol = company.get('symbol', '')
            if symbol in self.cache_store.get_selected_companies():
                checkbox.setChecked(True)

            # Connect signal
            checkbox.stateChanged.connect(lambda state, s=symbol: self.on_checkbox_changed(s, state))
            self.file_table.setCellWidget(row, 0, checkbox)

            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            self.file_table.setItem(row, 1, symbol_item)

            # Name
            name_item = QTableWidgetItem(company.get('name', ''))
            self.file_table.setItem(row, 2, name_item)

    @pyqtSlot()
    def on_select_clicked(self):
        """Get selected symbols"""
        selected_symbols = []

        # Check top_n tab
        for row in range(self.top_n_table.rowCount()):
            checkbox_widget = self.top_n_table.cellWidget(row, 0)
            if checkbox_widget and checkbox_widget.isChecked():
                symbol_item = self.top_n_table.item(row, 1)
                if symbol_item:
                    selected_symbols.append(symbol_item.text())

        # Check search tab
        for row in range(self.search_table.rowCount()):
            checkbox_widget = self.search_table.cellWidget(row, 0)
            if checkbox_widget and checkbox_widget.isChecked():
                symbol_item = self.search_table.item(row, 1)
                if symbol_item:
                    selected_symbols.append(symbol_item.text())

        # Check file tab
        for row in range(self.file_table.rowCount()):
            checkbox_widget = self.file_table.cellWidget(row, 0)
            if checkbox_widget and checkbox_widget.isChecked():
                symbol_item = self.file_table.item(row, 1)
                if symbol_item:
                    selected_symbols.append(symbol_item.text())

        # Check custom input
        custom_text = self.custom_input.text().strip()
        if custom_text:
            # Parse as comma or newline separated
            symbols = [s.strip().upper() for s in custom_text.replace('\n', ',').split(',') if s.strip()]
            selected_symbols.extend(symbols)

        # Remove duplicates
        selected_symbols = list(set(selected_symbols))

        if not selected_symbols:
            QMessageBox.warning(self, "No Selection", "Please select at least one company")
            return

        # Save selected companies to persistent cache
        if self.cache_store:
            self.cache_store.add_selected_companies(selected_symbols)
            logging.info(f"Saved {len(selected_symbols)} companies to persistent selection")

        self.companies_selected.emit(selected_symbols)
        self.accept()

    @pyqtSlot()
    def on_force_refresh(self):
        """Force refresh companies from EODHD regardless of cache age"""
        reply = QMessageBox.question(
            self,
            "Force Refresh",
            "This will fetch fresh data from EODHD and use API quota.\n\n"
            "Cache is automatically refreshed every 24 hours.\n"
            "Are you sure you want to force refresh now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.on_fetch_from_eodhd()

    def load_previously_selected(self):
        """Load and check previously selected companies"""
        if not self.cache_store:
            return

        try:
            selected = self.cache_store.get_selected_companies()
            if not selected:
                return

            # Create a set for faster lookup
            selected_set = set(selected)

            # Check items in all tables
            for row in range(self.top_n_table.rowCount()):
                checkbox = self.top_n_table.cellWidget(row, 0)
                symbol_item = self.top_n_table.item(row, 1)
                if checkbox and symbol_item and symbol_item.text() in selected_set:
                    checkbox.setChecked(True)

            for row in range(self.search_table.rowCount()):
                checkbox = self.search_table.cellWidget(row, 0)
                symbol_item = self.search_table.item(row, 1)
                if checkbox and symbol_item and symbol_item.text() in selected_set:
                    checkbox.setChecked(True)

            for row in range(self.file_table.rowCount()):
                checkbox = self.file_table.cellWidget(row, 0)
                symbol_item = self.file_table.item(row, 1)
                if checkbox and symbol_item and symbol_item.text() in selected_set:
                    checkbox.setChecked(True)

            logging.info(f"Loaded {len(selected)} previously selected companies")

        except Exception as e:
            logging.error(f"Failed to load previously selected: {e}")

    @pyqtSlot(str, int)
    def on_checkbox_changed(self, symbol: str, state):
        """Handle checkbox state change - immediately add/remove from selections"""
        from PyQt6.QtCore import Qt

        if state == Qt.CheckState.Checked.value:
            # Add to persistent cache
            if self.cache_store:
                self.cache_store.add_selected_company(symbol)
            logging.info(f"Added {symbol} to processing list")
        else:
            # Remove from persistent cache
            if self.cache_store:
                self.cache_store.remove_selected_company(symbol)
            logging.info(f"Removed {symbol} from processing list")

        # Update display
        self.update_selected_display()

    def update_selected_display(self):
        """Update the selected companies display"""
        if self.cache_store:
            selected = self.cache_store.get_selected_companies()
            if selected:
                display_text = f"{len(selected)} selected: {', '.join(selected[:10])}"
                if len(selected) > 10:
                    display_text += f" +{len(selected) - 10} more"
                self.selected_display.setText(display_text)
            else:
                self.selected_display.setText("None selected yet")

    @pyqtSlot()
    def on_close_clicked(self):
        """Close the dialog and process selected companies"""
        if self.cache_store:
            selected = self.cache_store.get_selected_companies()
            if selected:
                self.companies_selected.emit(selected)
                logging.info(f"Processing {len(selected)} selected companies")
        self.accept()

    @pyqtSlot()
    def on_remove_all_clicked(self):
        """Remove all selected companies"""
        if self.cache_store:
            self.cache_store.clear_selected_companies()
            logging.info("Cleared all selected companies")

        # Update display
        self.update_selected_display()

        # Uncheck all checkboxes
        for row in range(self.top_n_table.rowCount()):
            checkbox = self.top_n_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

        for row in range(self.search_table.rowCount()):
            checkbox = self.search_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

        for row in range(self.file_table.rowCount()):
            checkbox = self.file_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
