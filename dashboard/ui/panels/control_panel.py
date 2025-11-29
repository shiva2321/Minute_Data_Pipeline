"""
Control Panel - User input and pipeline controls
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLineEdit, QPushButton, QRadioButton, QCheckBox,
                              QSpinBox, QLabel, QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict
import os
from pathlib import Path


class ControlPanel(QWidget):
    """
    Control panel for symbol input and processing configuration
    """

    # Signals
    start_clicked = pyqtSignal(list, dict)  # symbols, settings
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()

    def __init__(self, cache_store=None, parent=None):
        super().__init__(parent)

        self.cache_store = cache_store
        self.is_running = False
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Symbol Input Section
        symbol_group = QGroupBox("Symbol Input")
        symbol_layout = QVBoxLayout()

        # Manual input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Ticker Symbol(s):"))

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("AAPL, MSFT, GOOGL... (comma-separated)")
        input_layout.addWidget(self.symbol_input)

        self.browse_btn = QPushButton("📁 Browse")
        self.browse_btn.clicked.connect(self._browse_file)
        input_layout.addWidget(self.browse_btn)

        symbol_layout.addLayout(input_layout)

        # Company selector buttons
        company_btn_layout = QHBoxLayout()
        company_btn_layout.addWidget(QLabel("Quick Select:"))

        # Top N input
        company_btn_layout.addWidget(QLabel("Top N:"))
        self.top_n_spin = QSpinBox()
        self.top_n_spin.setMinimum(1)
        self.top_n_spin.setMaximum(500)
        self.top_n_spin.setValue(10)
        self.top_n_spin.setMaximumWidth(80)
        company_btn_layout.addWidget(self.top_n_spin)

        self.top_n_btn = QPushButton("📊 Select Top N")
        self.top_n_btn.setToolTip("Select top N US companies")
        self.top_n_btn.clicked.connect(self._on_top_n_clicked)
        company_btn_layout.addWidget(self.top_n_btn)

        self.browse_companies_btn = QPushButton("🔍 Browse Companies")
        self.browse_companies_btn.setToolTip("Browse and select from all listed companies")
        self.browse_companies_btn.clicked.connect(self._on_browse_companies)
        company_btn_layout.addWidget(self.browse_companies_btn)

        self.fetch_list_btn = QPushButton("⬇ Fetch Exchange List")
        self.fetch_list_btn.setToolTip("Fetch latest list of US exchange companies")
        self.fetch_list_btn.clicked.connect(self._on_fetch_exchange_list)
        company_btn_layout.addWidget(self.fetch_list_btn)

        company_btn_layout.addStretch()
        symbol_layout.addLayout(company_btn_layout)
        file_layout = QHBoxLayout()

        self.file_check = QCheckBox("Load from file:")
        self.file_check.stateChanged.connect(self._toggle_file_input)
        file_layout.addWidget(self.file_check)

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("symbols.txt or symbols.csv")
        self.file_path_input.setEnabled(False)
        file_layout.addWidget(self.file_path_input)

        self.file_browse_btn = QPushButton("Browse")
        self.file_browse_btn.setEnabled(False)
        self.file_browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.file_browse_btn)

        symbol_layout.addLayout(file_layout)

        symbol_group.setLayout(symbol_layout)
        layout.addWidget(symbol_group)

        # Processing Options Section
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))

        self.incremental_radio = QRadioButton("Incremental (update existing)")
        self.incremental_radio.setChecked(True)
        mode_layout.addWidget(self.incremental_radio)

        self.full_rebuild_radio = QRadioButton("Full Rebuild (from scratch)")
        mode_layout.addWidget(self.full_rebuild_radio)

        mode_layout.addStretch()
        options_layout.addLayout(mode_layout)

        # History years
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("History Years:"))

        # Replace spin with combo including 'All Available'
        self.history_years_combo = QComboBox()
        years = [str(y) for y in range(1, 31)]
        self.history_years_combo.addItems(years + ['All Available'])
        self.history_years_combo.setCurrentText('2')
        history_layout.addWidget(self.history_years_combo)

        history_layout.addWidget(QLabel("(1-30 or All Available)"))
        history_layout.addStretch()
        options_layout.addLayout(history_layout)

        # Chunk size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size:"))

        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setMinimum(1)
        self.chunk_size_spin.setMaximum(30)
        self.chunk_size_spin.setValue(30)  # Changed to 30 days
        self.chunk_size_spin.setSuffix(" days")
        chunk_layout.addWidget(self.chunk_size_spin)

        chunk_layout.addWidget(QLabel("(days per API call - 30 recommended)"))
        chunk_layout.addStretch()

        options_layout.addLayout(chunk_layout)

        # Parallel processing
        parallel_layout = QHBoxLayout()

        self.parallel_check = QCheckBox("Enable Parallel Processing")
        self.parallel_check.setChecked(True)
        self.parallel_check.stateChanged.connect(self._toggle_parallel)
        parallel_layout.addWidget(self.parallel_check)

        options_layout.addLayout(parallel_layout)

        # Max workers (optimized for Ryzen 5 7600)
        workers_layout = QHBoxLayout()
        workers_layout.addWidget(QLabel("Max Workers:"))

        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setMinimum(1)
        self.max_workers_spin.setMaximum(12)
        self.max_workers_spin.setValue(10)  # Optimized for 6-core CPU
        self.max_workers_spin.setSuffix(" threads")
        workers_layout.addWidget(self.max_workers_spin)

        workers_layout.addWidget(QLabel("(Optimized for Ryzen 5 7600)"))
        workers_layout.addStretch()

        options_layout.addLayout(workers_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Action Buttons Section
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start Pipeline")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setMinimumHeight(35)  # Reduced from 40
        self.start_btn.clicked.connect(self._start_pipeline)
        actions_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setObjectName("pauseButton")
        self.pause_btn.setMinimumHeight(35)  # Reduced from 40
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._pause_pipeline)
        actions_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setMinimumHeight(35)  # Reduced from 40
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_pipeline)
        actions_layout.addWidget(self.stop_btn)

        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self._clear_queue)
        actions_layout.addWidget(self.clear_btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        layout.addStretch()
        self.setLayout(layout)

    def _toggle_file_input(self, state: int):
        """Toggle file input controls"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.file_path_input.setEnabled(enabled)
        self.file_browse_btn.setEnabled(enabled)

        # Disable manual input when file input is enabled
        self.symbol_input.setEnabled(not enabled)

    def _toggle_parallel(self, state: int):
        """Toggle parallel processing controls"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.max_workers_spin.setEnabled(enabled)

    def _browse_file(self):
        """Browse for symbols file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Symbols File",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            self.file_path_input.setText(file_path)
            self.file_check.setChecked(True)

    def _parse_symbols(self) -> List[str]:
        """Parse symbols from input or file"""
        symbols = []

        if self.file_check.isChecked() and self.file_path_input.text():
            # Load from file
            file_path = self.file_path_input.text()

            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Not Found", f"File not found: {file_path}")
                return []

            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()

                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue

                        # Handle CSV (take first column)
                        if ',' in line:
                            symbol = line.split(',')[0].strip()
                        else:
                            symbol = line

                        # Validate symbol
                        if symbol and symbol.isalnum() and len(symbol) <= 5:
                            symbols.append(symbol.upper())

            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Failed to read file:\n{str(e)}")
                return []

        else:
            # Parse from manual input
            input_text = self.symbol_input.text().strip()

            if not input_text:
                QMessageBox.warning(self, "No Symbols", "Please enter at least one symbol")
                return []

            # Split by comma
            for symbol in input_text.split(','):
                symbol = symbol.strip().upper()

                # Validate symbol
                if symbol and symbol.isalnum() and len(symbol) <= 5:
                    symbols.append(symbol)

        # Remove duplicates while preserving order
        symbols = list(dict.fromkeys(symbols))

        if not symbols:
            QMessageBox.warning(self, "No Valid Symbols", "No valid symbols found")

        return symbols

    def _get_settings(self) -> Dict:
        """Get current processing settings"""
        hist_val = self.history_years_combo.currentText()
        max_years = None if hist_val == 'All Available' else int(hist_val)
        return {
            'mode': 'incremental' if self.incremental_radio.isChecked() else 'full_rebuild',
            'max_years': max_years,
            'chunk_days': self.chunk_size_spin.value(),
            'parallel_enabled': self.parallel_check.isChecked(),
            'max_workers': self.max_workers_spin.value() if self.parallel_check.isChecked() else 1,
            'api_calls_per_minute': 80,
            'api_calls_per_day': 95000
        }

    def _start_pipeline(self):
        """Start pipeline processing"""
        symbols = self._parse_symbols()

        if not symbols:
            return

        settings = self._get_settings()

        # Confirm if many symbols
        if len(symbols) > 50:
            reply = QMessageBox.question(
                self,
                "Confirm Start",
                f"Process {len(symbols)} symbols?\n\n"
                f"Mode: {settings['mode']}\n"
                f"Workers: {settings['max_workers']}\n"
                f"This may take a while.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        # Emit signal
        self.start_clicked.emit(symbols, settings)

        # Update UI state
        self.is_running = True
        self._update_button_states()

    def _pause_pipeline(self):
        """Pause pipeline"""
        self.pause_clicked.emit()

    def _stop_pipeline(self):
        """Stop pipeline"""
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            "Stop pipeline processing?\n\nCurrent jobs will be cancelled.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.stop_clicked.emit()
            self.is_running = False
            self._update_button_states()

    def _clear_queue(self):
        """Clear processing queue"""
        self.clear_clicked.emit()

    def _update_button_states(self):
        """Update button enabled/disabled states"""
        self.start_btn.setEnabled(not self.is_running)
        self.pause_btn.setEnabled(self.is_running)
        self.stop_btn.setEnabled(self.is_running)

        # Disable input controls while running
        self.symbol_input.setEnabled(not self.is_running)
        self.file_check.setEnabled(not self.is_running)
        self.file_path_input.setEnabled(not self.is_running and self.file_check.isChecked())
        self.file_browse_btn.setEnabled(not self.is_running and self.file_check.isChecked())
        self.browse_btn.setEnabled(not self.is_running)

    def pipeline_finished(self):
        """Called when pipeline finishes"""
        self.is_running = False
        self._update_button_states()

    def _on_top_n_clicked(self):
        """Handle top N companies quick select"""
        n = self.top_n_spin.value()

        # Top companies by market cap (2024-2025 data)
        # These are the actual largest US companies by market capitalization
        top_companies_by_market_cap = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'TSM', 'LLY',
            'V', 'UNH', 'XOM', 'WMT', 'JPM', 'MA', 'JNJ', 'PG', 'AVGO', 'HD',
            'ORCL', 'CVX', 'COST', 'MRK', 'ABBV', 'KO', 'BAC', 'CRM', 'NFLX', 'PEP',
            'AMD', 'TMO', 'ADBE', 'MCD', 'CSCO', 'ACN', 'LIN', 'ABT', 'NKE', 'TXN',
            'INTC', 'WFC', 'DHR', 'PM', 'VZ', 'DIS', 'CMCSA', 'QCOM', 'AMGN', 'NEE',
            'UNP', 'RTX', 'SPGI', 'HON', 'INTU', 'UPS', 'LOW', 'COP', 'BMY', 'BA',
            'AMAT', 'T', 'ELV', 'SBUX', 'DE', 'GE', 'BLK', 'ISRG', 'MDT', 'GILD',
            'AXP', 'PLD', 'TJX', 'BKNG', 'ADI', 'MDLZ', 'SYK', 'AMT', 'VRTX', 'CI',
            'SCHW', 'MO', 'LRCX', 'CVS', 'C', 'PGR', 'CB', 'ZTS', 'REGN', 'BSX',
            'SO', 'MMC', 'NOC', 'DUK', 'PYPL', 'BDX', 'EQIX', 'ETN', 'FI', 'MU'
        ]

        # Select top N from the list
        selected = top_companies_by_market_cap[:min(n, len(top_companies_by_market_cap))]
        
        # Set in symbol input field
        self.symbol_input.setText(', '.join(selected))
        
        # Show confirmation message
        QMessageBox.information(
            self, 
            "Top N Companies Selected", 
            f"Selected top {len(selected)} US companies by market cap:\n\n{', '.join(selected[:10])}"
            + (f"\n... and {len(selected) - 10} more" if len(selected) > 10 else "")
        )

    def _on_browse_companies(self):
        """Open company browser dialog"""
        try:
            from dashboard.dialogs import CompanySelectorDialog

            dialog = CompanySelectorDialog(self.cache_store, self)
            dialog.companies_selected.connect(self._on_companies_selected)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open company selector:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def _on_fetch_exchange_list(self):
        """Fetch latest exchange list from EODHD"""
        # Show progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt

        progress = QProgressDialog(
            "Fetching exchange list from EODHD...",
            "Cancel",
            0, 0,
            self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)  # No cancel during fetch
        progress.show()

        try:
            # Import fetcher
            from data_fetcher import EODHDDataFetcher

            fetcher = EODHDDataFetcher()

            # Fetch US exchange symbols
            progress.setLabelText("Fetching NASDAQ companies...")
            self._refresh_ui()
            nasdaq = fetcher.fetch_exchange_symbols('NASDAQ', skip_delisted=True)

            progress.setLabelText("Fetching NYSE companies...")
            self._refresh_ui()
            nyse = fetcher.fetch_exchange_symbols('NYSE', skip_delisted=True)

            progress.setLabelText("Fetching AMEX companies...")
            self._refresh_ui()
            amex = fetcher.fetch_exchange_symbols('AMEX', skip_delisted=True)

            # Combine all companies
            all_companies = nasdaq + nyse + amex

            # Cache them
            if self.cache_store:
                self.cache_store.save_company_list(all_companies)

            progress.close()

            QMessageBox.information(
                self,
                "Companies Fetched",
                f"Successfully fetched {len(all_companies)} companies from US exchanges:\n"
                f"  • NASDAQ: {len(nasdaq)}\n"
                f"  • NYSE: {len(nyse)}\n"
                f"  • AMEX: {len(amex)}\n\n"
                "Companies are now cached and available in Browse Companies."
            )

        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Failed to fetch exchange list:\n{str(e)}")

    def _refresh_ui(self):
        """Allow UI to refresh during long operations"""
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

    def _on_companies_selected(self, symbols: List[str]):
        """Handle companies selected from dialog"""
        self.symbol_input.setText(', '.join(symbols))
        QMessageBox.information(self, "Companies Selected", f"Selected {len(symbols)} companies")

    def reset(self):
        """Reset control panel to initial state"""
        self.symbol_input.clear()
        self.is_running = False
        self._update_button_states()
