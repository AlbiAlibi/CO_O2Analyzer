"""
Main window for CO_O2_Analyser GUI.

This module contains the main application window and coordinates
all GUI components.
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QApplication, QSplitter
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ..core.analyzer import COO2Analyzer
from ..utils.config import Config
from .plot_widget import PlotWidget
from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    measurement_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool)
    
    def __init__(self, config):
        """Initialize main window.
        
        Args:
            config: Application configuration object
        """
        super().__init__()
        self.config = config
        self.analyzer = None
        self.monitoring_timer = None
        self.data_collector_process = None
        
        # Initialize UI
        self._init_ui()
        self._init_analyzer()
        self._setup_timers()
        
        # Apply configuration
        self._apply_config()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("CO_O2_Analyser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon("icon.ico"))
        except:
            pass
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create main content area
        self._create_main_content(main_layout)
        
        # Create status bar
        self._create_status_bar()
        
        # Apply configuration
        self._apply_config()
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Export action
        export_action = QAction("&Export Data", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create application toolbar."""
        toolbar = self.addToolBar("Main Toolbar")
        
        # Start/Stop monitoring button
        self.monitor_button = QPushButton("Start Monitoring")
        self.monitor_button.clicked.connect(self._toggle_monitoring)
        toolbar.addWidget(self.monitor_button)
        
        # Start/Stop data collection service button
        self.data_collector_button = QPushButton("Start Data Collection")
        self.data_collector_button.clicked.connect(self._toggle_data_collection)
        toolbar.addWidget(self.data_collector_button)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_data)
        toolbar.addWidget(refresh_button)
        
        # Export button
        export_button = QPushButton("Export")
        export_button.clicked.connect(self._export_data)
        toolbar.addWidget(export_button)
    
    def _create_main_content(self, main_layout):
        """Create main content area."""
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Status and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Status widget
        self.status_widget = StatusWidget(self.config)
        left_layout.addWidget(self.status_widget)
        
        # Add some spacing
        left_layout.addStretch()
        
        # Right panel - Plot
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Plot widget
        self.plot_widget = PlotWidget()
        right_layout.addWidget(self.plot_widget)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([360, 840])
    
    def _create_status_bar(self):
        """Create application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.status_bar.addWidget(self.connection_label)
        
        # Measurement count
        self.measurement_label = QLabel("Measurements: 0")
        self.status_bar.addPermanentWidget(self.measurement_label)
    
    def _apply_config(self):
        """Apply configuration settings to UI."""
        # Window size
        width = self.config.get('gui.window_width', 1200)
        height = self.config.get('gui.window_height', 800)
        self.resize(width, height)
        
        # Theme (if implemented)
        theme = self.config.get('gui.theme', 'light')
        # TODO: Implement theme switching
    
    def _init_analyzer(self):
        """Initialize the analyzer component."""
        try:
            self.analyzer = COO2Analyzer(self.config)
            logger.info("Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize analyzer: {e}")
    
    def _setup_timers(self):
        """Setup application timers."""
        # Timer for periodic data updates
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._update_data)
        
        # Timer for connection status updates
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connection)
        self.connection_timer.start(5000)  # Check every 5 seconds
        
        # Timer for data collector status updates
        self.data_collector_timer = QTimer()
        self.data_collector_timer.timeout.connect(self._check_data_collector_status)
        self.data_collector_timer.start(2000)  # Check every 2 seconds
    
    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.monitoring_timer.isActive():
            self._stop_monitoring()
        else:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """Start continuous monitoring."""
        if not self.analyzer:
            QMessageBox.warning(self, "Warning", "Analyzer not initialized")
            return
        
        try:
            if self.analyzer.start_monitoring():
                self.monitoring_timer.start(1000)  # Update every second
                self.monitor_button.setText("Stop Monitoring")
                self.status_bar.showMessage("Monitoring started")
                logger.info("Monitoring started")
            else:
                QMessageBox.warning(self, "Warning", "Failed to start monitoring")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start monitoring: {e}")
    
    def _stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_timer.stop()
        self.monitor_button.setText("Start Monitoring")
        self.status_bar.showMessage("Monitoring stopped")
        
        if self.analyzer:
            self.analyzer.stop_monitoring()
        
        logger.info("Monitoring stopped")
    
    def _toggle_data_collection(self):
        """Toggle data collection service on/off."""
        if self.data_collector_process and self.data_collector_process.poll() is None:
            self._stop_data_collection()
        else:
            self._start_data_collection()
    
    def _start_data_collection(self):
        """Start the data collection service."""
        try:
            # Start data collection service as a subprocess
            script_path = Path(__file__).parent.parent.parent.parent / "start_data_collector.py"
            
            if not script_path.exists():
                # Try alternative path
                script_path = Path("start_data_collector.py")
            
            if not script_path.exists():
                QMessageBox.critical(self, "Error", "Data collector script not found")
                return
            
            # Start the data collection service
            self.data_collector_process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Update UI
            self.data_collector_button.setText("Stop Data Collection")
            self.status_bar.showMessage("Data collection service started")
            logger.info("Data collection service started")
            
            # Start monitoring timer to update status widget
            if not self.monitoring_timer.isActive():
                self.monitoring_timer.start(1000)
            
        except Exception as e:
            logger.error(f"Failed to start data collection service: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start data collection service: {e}")
    
    def _stop_data_collection(self):
        """Stop the data collection service."""
        try:
            if self.data_collector_process:
                # Terminate the process
                self.data_collector_process.terminate()
                
                # Wait for it to finish
                try:
                    self.data_collector_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.data_collector_process.kill()
                
                self.data_collector_process = None
            
            # Update UI
            self.data_collector_button.setText("Start Data Collection")
            self.status_bar.showMessage("Data collection service stopped")
            logger.info("Data collection service stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop data collection service: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop data collection service: {e}")
    
    def _check_data_collector_status(self):
        """Check if data collection service is still running."""
        if self.data_collector_process and self.data_collector_process.poll() is not None:
            # Process has terminated
            self.data_collector_button.setText("Start Data Collection")
            self.status_bar.showMessage("Data collection service stopped unexpectedly")
            logger.warning("Data collection service stopped unexpectedly")
            self.data_collector_process = None
    
    def _update_data(self):
        """Update measurement data."""
        if not self.analyzer:
            return
        
        try:
            measurement = self.analyzer.get_current_measurement()
            if measurement:
                # Update plot
                self.plot_widget.add_measurement(measurement)
                
                # Update status
                self.status_widget.update_measurement(measurement)
                
                # Update measurement count
                self._update_measurement_count()
                
                # Emit signal
                self.measurement_received.emit(measurement.to_dict())
                
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
    
    def _refresh_data(self):
        """Refresh data manually."""
        self._update_data()
        self.status_bar.showMessage("Data refreshed", 2000)
    
    def _check_connection(self):
        """Check connection status."""
        if not self.analyzer:
            self.connection_label.setText("Disconnected")
            return
        
        try:
            is_connected = self.analyzer.instrument.test_connection()
            self.connection_label.setText("Connected" if is_connected else "Disconnected")
            self.connection_status_changed.emit(is_connected)
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self.connection_label.setText("Error")
    
    def _update_measurement_count(self):
        """Update measurement count display."""
        if not self.analyzer:
            return
        
        try:
            measurements = self.analyzer.get_measurement_history(limit=1)
            count = len(measurements)
            self.measurement_label.setText(f"Measurements: {count}")
        except Exception as e:
            logger.error(f"Failed to update measurement count: {e}")
    
    def _export_data(self):
        """Export measurement data."""
        if not self.analyzer:
            QMessageBox.warning(self, "Warning", "Analyzer not initialized")
            return
        
        try:
            # TODO: Add export dialog for format and date range selection
            export_path = self.analyzer.export_data(format='csv')
            QMessageBox.information(self, "Export Complete", f"Data exported to: {export_path}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")
    
    def _show_settings(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About CO_O2_Analyser", 
                         "CO_O2_Analyser v1.0.0\n\n"
                         "Carbon Monoxide and Oxygen Analyzer Software\n"
                         "Designed for Teledyne N300M analyzer")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop monitoring
            if self.monitoring_timer.isActive():
                self._stop_monitoring()
            
            # Save configuration
            if self.config:
                self.config.set('gui.window_width', self.width())
                self.config.set('gui.window_height', self.height())
                self.config.save_config()
            
            # Close analyzer
            if self.analyzer:
                self.analyzer.close()
            
            logger.info("Main window closed")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during close: {e}")
            event.accept()
