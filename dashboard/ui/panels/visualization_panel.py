"""
Visualization Panel - Interactive data visualization and analysis
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QComboBox, QLabel, QSplitter, QMessageBox,
                              QGroupBox, QGridLayout, QCheckBox, QTextEdit,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtCharts import (QChart, QChartView, QLineSeries, QDateTimeAxis, 
                             QValueAxis, QScatterSeries, QBarSeries, QBarSet)
from PyQt6.QtGui import QPainter, QColor
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from dashboard.controllers.database_controller import DatabaseController


class VisualizationPanel(QWidget):
    """
    Interactive visualization panel for company profile data analysis
    """
    
    profile_selected = pyqtSignal(str)  # Emits symbol when profile is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.db_controller = DatabaseController()
        self.current_symbol = None
        self.current_profile = None
        self.current_dataframe = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Top control panel
        control_layout = self._create_control_panel()
        layout.addLayout(control_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Chart area
        chart_widget = self._create_chart_area()
        splitter.addWidget(chart_widget)
        
        # Right side: Data inspection and controls
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (70% chart, 30% controls)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("No profile loaded")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _create_control_panel(self) -> QHBoxLayout:
        """Create top control panel"""
        layout = QHBoxLayout()
        
        # Symbol selector
        layout.addWidget(QLabel("Symbol:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.setMinimumWidth(150)
        self.symbol_combo.currentTextChanged.connect(self._on_symbol_changed)
        layout.addWidget(self.symbol_combo)
        
        # Load button
        load_btn = QPushButton("📊 Load Profile")
        load_btn.clicked.connect(self._load_profile)
        layout.addWidget(load_btn)
        
        # Refresh symbols button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_symbols)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        # Chart type selector
        layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Price & Volume",
            "Candlestick",
            "Technical Indicators",
            "Multi-Timeframe",
            "Intraday Heatmap",
            "Volume Profile"
        ])
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)
        layout.addWidget(self.chart_type_combo)
        
        # Export button
        export_btn = QPushButton("📤 Export Chart Data")
        export_btn.clicked.connect(self._export_chart_data)
        layout.addWidget(export_btn)
        
        return layout
        
    def _create_chart_area(self) -> QWidget:
        """Create main chart display area"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Chart tabs for multiple views
        self.chart_tabs = QTabWidget()
        
        # Main price chart
        self.price_chart = QChart()
        self.price_chart.setTitle("Price & Volume")
        self.price_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        self.price_chart_view = QChartView(self.price_chart)
        self.price_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_tabs.addTab(self.price_chart_view, "Price Chart")
        
        # Technical indicators chart
        self.indicator_chart = QChart()
        self.indicator_chart.setTitle("Technical Indicators")
        self.indicator_chart_view = QChartView(self.indicator_chart)
        self.indicator_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_tabs.addTab(self.indicator_chart_view, "Indicators")
        
        # Volume chart
        self.volume_chart = QChart()
        self.volume_chart.setTitle("Volume Analysis")
        self.volume_chart_view = QChartView(self.volume_chart)
        self.volume_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_tabs.addTab(self.volume_chart_view, "Volume")
        
        layout.addWidget(self.chart_tabs)
        widget.setLayout(layout)
        
        return widget
        
    def _create_right_panel(self) -> QWidget:
        """Create right panel with data inspection and controls"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Profile metadata
        metadata_group = QGroupBox("Profile Metadata")
        metadata_layout = QVBoxLayout()
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(200)
        metadata_layout.addWidget(self.metadata_text)
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Granular analysis metrics
        granular_group = QGroupBox("Granular Minute Analysis")
        granular_layout = QVBoxLayout()
        self.granular_text = QTextEdit()
        self.granular_text.setReadOnly(True)
        self.granular_text.setMaximumHeight(250)
        granular_layout.addWidget(self.granular_text)
        granular_group.setLayout(granular_layout)
        layout.addWidget(granular_group)
        
        # Chart options
        options_group = QGroupBox("Display Options")
        options_layout = QGridLayout()
        
        self.show_sma_cb = QCheckBox("SMA")
        self.show_sma_cb.setChecked(True)
        self.show_sma_cb.stateChanged.connect(self._update_chart)
        options_layout.addWidget(self.show_sma_cb, 0, 0)
        
        self.show_ema_cb = QCheckBox("EMA")
        self.show_ema_cb.stateChanged.connect(self._update_chart)
        options_layout.addWidget(self.show_ema_cb, 0, 1)
        
        self.show_bollinger_cb = QCheckBox("Bollinger")
        self.show_bollinger_cb.stateChanged.connect(self._update_chart)
        options_layout.addWidget(self.show_bollinger_cb, 1, 0)
        
        self.show_volume_cb = QCheckBox("Volume")
        self.show_volume_cb.setChecked(True)
        self.show_volume_cb.stateChanged.connect(self._update_chart)
        options_layout.addWidget(self.show_volume_cb, 1, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Data table preview
        table_group = QGroupBox("Data Preview")
        table_layout = QVBoxLayout()
        self.data_table = QTableWidget()
        self.data_table.setMaximumHeight(200)
        self.data_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.data_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def _refresh_symbols(self):
        """Refresh the symbol list from database"""
        try:
            profiles = self.db_controller.load_all_profiles()
            self.symbol_combo.clear()
            
            symbols = sorted([p.get('symbol', '') for p in profiles if p.get('symbol')])
            self.symbol_combo.addItems(symbols)
            
            self.status_label.setText(f"Loaded {len(symbols)} symbols")
            self.status_label.setStyleSheet("color: #0e7c0e; padding: 5px;")
        except Exception as e:
            self.status_label.setText(f"Error loading symbols: {str(e)}")
            self.status_label.setStyleSheet("color: #c50f1f; padding: 5px;")
            
    @pyqtSlot(str)
    def _on_symbol_changed(self, symbol: str):
        """Handle symbol selection change"""
        if symbol:
            self.current_symbol = symbol
            self.profile_selected.emit(symbol)
            
    def _load_profile(self):
        """Load the selected profile and display data"""
        symbol = self.symbol_combo.currentText()
        if not symbol:
            QMessageBox.warning(self, "No Symbol", "Please select a symbol first")
            return
            
        try:
            profile = self.db_controller.get_profile(symbol)
            if not profile:
                QMessageBox.warning(self, "Profile Not Found", 
                                   f"Profile for {symbol} not found in database")
                return
                
            self.current_symbol = symbol
            self.current_profile = profile
            
            # Extract dataframe from profile
            if 'processed_df' in profile and profile['processed_df'] is not None:
                # If stored as dict, convert to DataFrame
                if isinstance(profile['processed_df'], dict):
                    self.current_dataframe = pd.DataFrame(profile['processed_df'])
                else:
                    self.current_dataframe = profile['processed_df']
            else:
                self.current_dataframe = None
                
            # Update displays
            self._update_metadata_display()
            self._update_granular_display()
            self._update_chart()
            self._update_data_table()
            
            self.status_label.setText(f"Loaded profile for {symbol}")
            self.status_label.setStyleSheet("color: #0e7c0e; padding: 5px;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load profile: {str(e)}")
            self.status_label.setText(f"Error loading {symbol}")
            self.status_label.setStyleSheet("color: #c50f1f; padding: 5px;")
            
    def _update_metadata_display(self):
        """Update metadata display"""
        if not self.current_profile:
            return
            
        metadata_text = f"Symbol: {self.current_profile.get('symbol', 'N/A')}\n"
        metadata_text += f"Exchange: {self.current_profile.get('exchange', 'N/A')}\n"
        metadata_text += f"Data Points: {self.current_profile.get('data_points_count', 0):,}\n"
        
        date_range = self.current_profile.get('data_date_range', {})
        metadata_text += f"Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}\n"
        
        # Statistical features
        stat_features = self.current_profile.get('statistical_features', {})
        if stat_features:
            metadata_text += f"\n--- Statistical Summary ---\n"
            metadata_text += f"Price Mean: ${stat_features.get('price_mean', 0):.2f}\n"
            metadata_text += f"Price Std: ${stat_features.get('price_std', 0):.2f}\n"
            metadata_text += f"Volatility: {stat_features.get('volatility_close_to_close', 0):.4f}\n"
            metadata_text += f"Sharpe Ratio: {stat_features.get('sharpe_ratio', 0):.2f}\n"
            
        self.metadata_text.setText(metadata_text)
        
    def _update_granular_display(self):
        """Update granular minute analysis display"""
        if not self.current_profile:
            return
            
        granular = self.current_profile.get('granular_minute_features', {})
        if not granular:
            self.granular_text.setText("No granular analysis data available")
            return
            
        text = "--- Granular Minute Analysis ---\n\n"
        
        # Liquidity metrics
        text += "LIQUIDITY METRICS:\n"
        text += f"  Avg Liquidity Depth: {granular.get('avg_liquidity_depth', 0):.2f}\n"
        text += f"  Liquidity Variability: {granular.get('liquidity_variability', 0):.2f}\n"
        text += f"  Volume Gini Coef: {granular.get('volume_gini_coefficient', 0):.4f}\n\n"
        
        # Price action patterns
        text += "PRICE ACTION PATTERNS:\n"
        text += f"  Max Momentum Burst: {granular.get('max_momentum_burst', 0):.6f}\n"
        text += f"  Reversal Frequency: {granular.get('price_reversal_frequency', 0):.4f}\n"
        text += f"  Extreme Moves (2σ): {granular.get('extreme_move_count_2sigma', 0)}\n"
        text += f"  Extreme Moves (3σ): {granular.get('extreme_move_count_3sigma', 0)}\n\n"
        
        # Volatility clustering
        text += "VOLATILITY CLUSTERING:\n"
        text += f"  Clustering Coefficient: {granular.get('volatility_clustering_coef', 0):.4f}\n\n"
        
        # Trading intensity
        text += "TRADING INTENSITY:\n"
        text += f"  Active Minutes: {granular.get('active_trading_minutes', 0)}\n"
        text += f"  Trading Intensity: {granular.get('trading_intensity', 0):.4f}\n"
        text += f"  Price Efficiency: {granular.get('price_efficiency_ratio', 0):.4f}\n\n"
        
        # Hourly VWAP volatility
        hourly_vol = granular.get('hourly_vwap_volatility', {})
        if hourly_vol:
            text += "HOURLY VWAP VOLATILITY:\n"
            for hour, vol in sorted(hourly_vol.items())[:5]:  # Show first 5 hours
                text += f"  Hour {hour}: {vol:.6f}\n"
                
        self.granular_text.setText(text)
        
    def _update_chart(self):
        """Update the chart with current data"""
        if self.current_dataframe is None or self.current_dataframe.empty:
            return
            
        try:
            # Clear existing series
            self.price_chart.removeAllSeries()
            
            # Create price series
            df = self.current_dataframe.head(500)  # Limit to 500 points for performance
            
            if 'close' not in df.columns:
                return
                
            price_series = QLineSeries()
            price_series.setName("Close Price")
            
            for idx, row in df.iterrows():
                if 'datetime' in row and pd.notna(row['close']):
                    try:
                        if isinstance(row['datetime'], str):
                            dt = pd.to_datetime(row['datetime'])
                        else:
                            dt = row['datetime']
                        timestamp = dt.timestamp() * 1000  # Convert to milliseconds
                        price_series.append(timestamp, float(row['close']))
                    except Exception:
                        continue
                        
            self.price_chart.addSeries(price_series)
            
            # Add SMA if checked
            if self.show_sma_cb.isChecked() and 'sma_20' in df.columns:
                sma_series = QLineSeries()
                sma_series.setName("SMA 20")
                sma_series.setColor(QColor(255, 165, 0))
                
                for idx, row in df.iterrows():
                    if 'datetime' in row and pd.notna(row.get('sma_20')):
                        try:
                            if isinstance(row['datetime'], str):
                                dt = pd.to_datetime(row['datetime'])
                            else:
                                dt = row['datetime']
                            timestamp = dt.timestamp() * 1000
                            sma_series.append(timestamp, float(row['sma_20']))
                        except Exception:
                            continue
                            
                self.price_chart.addSeries(sma_series)
                
            # Create axes
            self.price_chart.createDefaultAxes()
            self.price_chart.legend().setVisible(True)
            self.price_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            
        except Exception as e:
            print(f"Error updating chart: {e}")
            
    def _update_data_table(self):
        """Update the data preview table"""
        if self.current_dataframe is None or self.current_dataframe.empty:
            return
            
        df = self.current_dataframe.head(20)  # Show first 20 rows
        
        # Set up table
        self.data_table.setRowCount(len(df))
        cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        available_cols = [c for c in cols if c in df.columns]
        self.data_table.setColumnCount(len(available_cols))
        self.data_table.setHorizontalHeaderLabels(available_cols)
        
        # Populate table
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, col in enumerate(available_cols):
                value = row[col]
                if pd.notna(value):
                    if col == 'datetime':
                        item = QTableWidgetItem(str(value))
                    else:
                        item = QTableWidgetItem(f"{float(value):.2f}")
                else:
                    item = QTableWidgetItem("N/A")
                self.data_table.setItem(row_idx, col_idx, item)
                
        # Resize columns
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
    @pyqtSlot(str)
    def _on_chart_type_changed(self, chart_type: str):
        """Handle chart type change"""
        # For now, just update the current chart
        # In a full implementation, this would switch between different chart types
        self._update_chart()
        
    def _export_chart_data(self):
        """Export current chart data to CSV"""
        if self.current_dataframe is None or self.current_dataframe.empty:
            QMessageBox.warning(self, "No Data", "No data available to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chart Data",
            f"{self.current_symbol}_chart_data.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.current_dataframe.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", f"Data exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data:\n{str(e)}")
                
    def load_symbol_profile(self, symbol: str):
        """
        Public method to load a specific symbol's profile
        
        Args:
            symbol: Ticker symbol to load
        """
        self.symbol_combo.setCurrentText(symbol)
        self._load_profile()
