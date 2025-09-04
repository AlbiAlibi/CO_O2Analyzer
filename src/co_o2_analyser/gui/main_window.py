"""
Main window for CO_O2_Analyser GUI.

This module contains the main application window and coordinates
all GUI components.
"""

import sys
import logging
import subprocess
import os
import signal
import time
from pathlib import Path

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QApplication, QSplitter, QInputDialog
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QProcess, QThread
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
        
        # Data collector process management
        self.data_collector_process = None
        self.data_collector_monitoring = False
        
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
        
        # Start/Stop measurement session button
        self.measurement_session_button = QPushButton("Start Measurement Session")
        self.measurement_session_button.clicked.connect(self._toggle_measurement_session)
        toolbar.addWidget(self.measurement_session_button)
        
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
        self.measurement_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.measurement_label)
        
        # Session measurement counter
        self.session_measurement_count = 0
    
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
        

    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.data_collector_monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """Start continuous monitoring using data collector process."""
        try:
            # Check if data collector is already running
            if self.data_collector_process and self.data_collector_process.poll() is None:
                QMessageBox.warning(self, "Warning", "Data collector is already running")
                return
            
            # Get the path to start_data_collector.py
            project_root = Path(__file__).parent.parent.parent.parent
            collector_script = project_root / "start_data_collector.py"
            
            if not collector_script.exists():
                QMessageBox.critical(self, "Error", f"Data collector script not found: {collector_script}")
                return
            
            # Start the data collector process
            logger.info(f"Starting data collector process: {collector_script}")
            
            # Use the virtual environment Python if available
            venv_python = project_root / "venv" / "Scripts" / "python3.12.exe"
            if venv_python.exists():
                python_executable = str(venv_python)
                logger.info(f"Using virtual environment Python: {python_executable}")
            else:
                python_executable = sys.executable
                logger.info(f"Using system Python: {python_executable}")
            
            # Start the process
            self.data_collector_process = subprocess.Popen(
                [python_executable, str(collector_script)],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Update UI
            self.data_collector_monitoring = True
            self.monitor_button.setText("Stop Monitoring")
            self.status_bar.showMessage("Data collector started")
            
            # Start monitoring timer for GUI updates
            self.monitoring_timer.start(1000)  # Update every second
            
            # Start connection status monitoring
            self._start_connection_monitoring()
            
            logger.info("Data collector process started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start data collector: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start data collector: {e}")
            self.data_collector_monitoring = False
    
    def _stop_monitoring(self):
        """Stop continuous monitoring and data collector process."""
        try:
            # Stop the data collector process
            if self.data_collector_process and self.data_collector_process.poll() is None:
                logger.info("Stopping data collector process...")
                
                # Try graceful termination first
                self.data_collector_process.terminate()
                
                # Wait for process to terminate (max 5 seconds)
                try:
                    self.data_collector_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    logger.warning("Data collector process did not terminate gracefully, forcing kill...")
                    self.data_collector_process.kill()
                    self.data_collector_process.wait()
                
                logger.info("Data collector process stopped")
            
            # Update UI
            self.data_collector_monitoring = False
            self.monitor_button.setText("Start Monitoring")
            self.status_bar.showMessage("Monitoring stopped")
            
            # Stop monitoring timer
            self.monitoring_timer.stop()
            
            # Update connection status to disconnected
            self._update_connection_status(False)
            
            logger.info("Monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop monitoring: {e}")
    
    def _toggle_measurement_session(self):
        """Toggle measurement session on/off."""
        if not self.analyzer:
            QMessageBox.warning(self, "Warning", "Analyzer not initialized")
            return
        
        session_status = self.analyzer.get_measurement_session_status()
        
        if session_status.get('is_collecting', False):
            self._stop_measurement_session()
        else:
            self._start_measurement_session()
    
    def _start_measurement_session(self):
        """Start a new measurement session."""
        try:
            # Get duration from user (default 10 minutes)
            duration, ok = QInputDialog.getInt(
                self, 
                "Measurement Session Duration", 
                "Enter duration in minutes:", 
                10, 1, 60, 1
            )
            
            if not ok:
                return
            
            # Start the measurement session
            session_path = self.analyzer.start_measurement_session(duration)
            
            # Update UI
            self.measurement_session_button.setText("Stop Measurement Session")
            self.measurement_session_button.setStyleSheet("color: red;")
            self.status_bar.showMessage(f"Measurement session started: {session_path}")
            logger.info(f"Measurement session started: {session_path}")
            
            # Start a timer to automatically stop the session after duration
            self.measurement_timer = QTimer()
            self.measurement_timer.timeout.connect(self._auto_stop_measurement_session)
            self.measurement_timer.start(duration * 60 * 1000)  # Convert minutes to milliseconds
            
            # Start monitoring timer to collect data during session
            if not self.monitoring_timer.isActive():
                self.monitoring_timer.start(1000)  # Collect data every second
            
        except Exception as e:
            logger.error(f"Failed to start measurement session: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start measurement session: {e}")
    
    def _stop_measurement_session(self):
        """Stop the current measurement session."""
        try:
            if not self.analyzer:
                return
            
            # Stop the measurement session
            session_path = self.analyzer.stop_measurement_session()
            
            # Stop the auto-stop timer
            if hasattr(self, 'measurement_timer') and self.measurement_timer:
                self.measurement_timer.stop()
                self.measurement_timer = None
            
            # Update UI
            self.measurement_session_button.setText("Start Measurement Session")
            self.measurement_session_button.setStyleSheet("")  # Reset button color
            if session_path:
                self.status_bar.showMessage(f"Measurement session completed: {session_path}")
                logger.info(f"Measurement session completed: {session_path}")
                
                # Show completion message
                QMessageBox.information(
                    self, 
                    "Measurement Session Complete", 
                    f"Measurement session completed successfully!\n\n"
                    f"Data saved to: {session_path}\n"
                    f"You can export this data using the Export button."
                )
            else:
                self.status_bar.showMessage("Measurement session stopped")
                logger.info("Measurement session stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop measurement session: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop measurement session: {e}")
    
    def _auto_stop_measurement_session(self):
        """Automatically stop measurement session when duration is reached."""
        try:
            logger.info("Auto-stopping measurement session - duration reached")
            self._stop_measurement_session()
        except Exception as e:
            logger.error(f"Failed to auto-stop measurement session: {e}")
    
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
                
                # If we're in a measurement session, add data to the session database
                session_status = self.analyzer.get_measurement_session_status()
                if session_status.get('is_collecting', False):
                    if (measurement.co_concentration is not None and 
                        measurement.o2_concentration is not None):
                        success = self.analyzer.add_measurement_to_session(
                            co_concentration=measurement.co_concentration,
                            o2_concentration=measurement.o2_concentration,
                            sample_temp=measurement.sample_temp,
                            sample_flow=measurement.sample_flow
                        )
                        if success:
                            logger.debug("Added measurement to session database")
                            # Increment session measurement counter
                            self.session_measurement_count += 1
                            self.measurement_label.setText(f"Measurements: {self.session_measurement_count}")
                        else:
                            logger.warning("Failed to add measurement to session database")
                
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
    
    def _refresh_data(self):
        """Refresh data manually by sending signal to data collector."""
        try:
            # Send refresh signal to data collector process
            if self.data_collector_monitoring and self.data_collector_process:
                # Create refresh signal file
                refresh_file = Path("refresh_signal.txt")
                refresh_file.write_text("REFRESH_ALL_DATA")
                
                logger.info("Refresh signal sent to data collector")
                self.status_bar.showMessage("Refresh signal sent to data collector", 2000)
                
                # Force immediate update of status widget
                self._force_status_widget_refresh()
                
                # Schedule a delayed refresh to catch the updated data from the data collector
                QTimer.singleShot(3000, self._force_status_widget_refresh)  # 3 seconds delay
            else:
                # If data collector is not running, just update from database
                self._update_data()
                self.status_bar.showMessage("Data refreshed from database", 2000)
                
        except Exception as e:
            logger.error(f"Failed to send refresh signal: {e}")
            self.status_bar.showMessage("Failed to refresh data", 2000)
    
    def _force_status_widget_refresh(self):
        """Force a comprehensive refresh of the status widget."""
        try:
            if hasattr(self, 'status_widget'):
                # Use the comprehensive refresh method
                self.status_widget.force_comprehensive_refresh()
                logger.info("Status widget force refreshed")
        except Exception as e:
            logger.error(f"Failed to force refresh status widget: {e}")
    
    def _start_connection_monitoring(self):
        """Start monitoring connection status from data collector."""
        # Check connection status every 5 seconds
        self.connection_timer.start(5000)
    
    def _check_connection(self):
        """Check connection status by looking at recent data in database."""
        try:
            # Check if data collector process is still running
            if not self.data_collector_process or self.data_collector_process.poll() is not None:
                # Process has stopped
                self._update_connection_status(False)
                if self.data_collector_monitoring:
                    logger.warning("Data collector process has stopped unexpectedly")
                    self._stop_monitoring()
                return
            
            # Check if we have recent data in the database (within last 5 seconds)
            if self.analyzer and hasattr(self.analyzer, 'db_manager'):
                try:
                    # Get the most recent timestamp from TagValues table
                    recent_data = self.analyzer.db_manager.get_recent_data(seconds=5)
                    
                    if recent_data:
                        # We have recent data, so we're connected
                        self._update_connection_status(True)
                    else:
                        # No recent data, so we're disconnected
                        self._update_connection_status(False)
                        
                except Exception as e:
                    logger.error(f"Error checking database for recent data: {e}")
                    self._update_connection_status(False)
            else:
                # No analyzer available, assume disconnected
                self._update_connection_status(False)
                
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self._update_connection_status(False)
    
    def _update_connection_status(self, is_connected: bool):
        """Update connection status in UI.
        
        Args:
            is_connected: True if connected, False otherwise
        """
        if is_connected:
            self.connection_label.setText("Connected")
            self.connection_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_label.setText("Disconnected")
            self.connection_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Update status widget connection status
        if hasattr(self, 'status_widget'):
            self.status_widget.update_connection_status(is_connected)
        
        # Emit signal for other components
        self.connection_status_changed.emit(is_connected)
    
    def _update_measurement_count(self):
        """Update measurement count display."""
        # Use session measurement counter instead of database count
        self.measurement_label.setText(f"Measurements: {self.session_measurement_count}")
    
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
    
    def _cleanup_signal_files(self):
        """Clean up signal files when closing the application."""
        try:
            # Remove refresh signal file
            refresh_file = Path("refresh_signal.txt")
            if refresh_file.exists():
                refresh_file.unlink()
                logger.info("Removed refresh_signal.txt")
            ata 
        except Exception as e:
            logger.error(f"Error cleaning up signal files: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Stop data collector process
            if self.data_collector_monitoring:
                self._stop_monitoring()
            
            # Stop measurement session if active
            if hasattr(self, 'analyzer') and self.analyzer:
                session_status = self.analyzer.get_measurement_session_status()
                if session_status.get('is_collecting', False):
                    # Use force stop to ensure end_time is recorded
                    self.analyzer.force_stop_measurement_session()
                    logger.info("Force stopped measurement session during application close")
            
            # Save configuration
            if self.config:
                self.config.set('gui.window_width', self.width())
                self.config.set('gui.window_height', self.height())
                self.config.save_config()
            
            # Close analyzer
            if self.analyzer:
                self.analyzer.close()
            
            # Clean up signal files
            self._cleanup_signal_files()
            
            logger.info("Main window closed")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during close: {e}")
            event.accept()
