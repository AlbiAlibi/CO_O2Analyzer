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
from .instrument_management_dialog import InstrumentManagementDialog
from .settings_dialog import SettingsDialog

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
        self.data_collector_start_time = None  # Track when data collector started
        
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
        export_action = QAction("💾 &Export Data", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        # Exit action
        exit_action = QAction("❌ E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings action
        settings_action = QAction("⚙️ &App Settings", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Instrument Settings action
        instrument_settings_action = QAction("🔧 &Instrument Settings", self)
        instrument_settings_action.triggered.connect(self._show_instrument_management)
        tools_menu.addAction(instrument_settings_action)
        
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
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            
            # Update UI
            self.data_collector_monitoring = True
            self.data_collector_start_time = time.time()  # Record start time
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
            self.data_collector_start_time = None  # Reset start time
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
            
            # Notify plot widget about measurement session start
            self.plot_widget.start_measurement_session()
            
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
            
            # Notify plot widget about measurement session stop
            self.plot_widget.stop_measurement_session()
            
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
            
            # Give data collector time to start up (30 seconds grace period)
            if self.data_collector_start_time and (time.time() - self.data_collector_start_time) < 30:
                # Still in grace period, assume connected if process is running
                self._update_connection_status(True)
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
        """Export data from all measurement sessions to CSV files."""
        if not self.analyzer:
            QMessageBox.warning(self, "Warning", "Analyzer not initialized")
            return
        
        try:
            # Get list of all measurement sessions
            sessions = self.analyzer.list_measurement_sessions()
            
            if not sessions:
                QMessageBox.information(self, "No Data", "No measurement sessions found to export")
                return
            
            # Export each session to a separate CSV file
            exported_files = []
            for session in sessions:
                try:
                    export_path = self.analyzer.export_measurement_session(
                        session['file_path'], format='csv'
                    )
                    exported_files.append(export_path)
                    logger.info(f"Exported session: {session['file_path']} -> {export_path}")
                except Exception as e:
                    logger.error(f"Failed to export session {session['file_path']}: {e}")
                    continue
            
            if exported_files:
                message = f"Successfully exported {len(exported_files)} measurement sessions to the 'results' folder:\n\n"
                for file_path in exported_files:
                    message += f"• {file_path}\n"
                QMessageBox.information(self, "Export Complete", message)
            else:
                QMessageBox.warning(self, "Export Failed", "No sessions could be exported")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {e}")
    
    def _show_settings(self):
        """Show settings dialog."""
        try:
            # Get config path from config object or use default
            config_path = getattr(self.config, 'config_path', None)
            if not config_path:
                # Try to find config file in common locations
                possible_paths = [
                    Path.home() / ".co_o2_analyser" / "config.json",
                    Path.cwd() / "config.json",
                    Path("config.json")
                ]
                
                for path in possible_paths:
                    if path.exists():
                        config_path = str(path)
                        break
                else:
                    # Use default location
                    config_path = str(Path.home() / ".co_o2_analyser" / "config.json")
            
            dialog = SettingsDialog(config_path, self)
            dialog.settings_changed.connect(self._on_settings_changed)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing settings dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open settings dialog:\n{str(e)}")
    
    def _on_settings_changed(self, new_config: dict):
        """Handle settings changes."""
        try:
            logger.info("Settings changed, updating configuration...")
            
            # Update config object if it exists
            if self.config:
                # Update config with new values
                for section, values in new_config.items():
                    if hasattr(self.config, section):
                        for key, value in values.items():
                            self.config.set(f"{section}.{key}", value)
                
                # Save config
                self.config.save_config()
                logger.info("Configuration updated and saved")
            
            # Show notification
            self.statusBar().showMessage("Settings updated successfully", 5000)
            
            # Optionally restart analyzer with new settings
            if self.analyzer:
                reply = QMessageBox.question(
                    self,
                    "Restart Required",
                    "Some settings changes require restarting the analyzer.\nDo you want to restart now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self._restart_analyzer()
            
        except Exception as e:
            logger.error(f"Error handling settings changes: {e}")
            QMessageBox.warning(self, "Settings Update", f"Settings were saved but some updates failed:\n{str(e)}")
    
    def _restart_analyzer(self):
        """Restart the analyzer with new settings."""
        try:
            if self.analyzer:
                self.analyzer.close()
                self.analyzer = None
            
            # Reinitialize analyzer with new config
            self.analyzer = COO2Analyzer(self.config)
            self.analyzer.measurement_received.connect(self._on_measurement_received)
            self.analyzer.connection_status_changed.connect(self._on_connection_status_changed)
            
            logger.info("Analyzer restarted with new settings")
            self.statusBar().showMessage("Analyzer restarted with new settings", 3000)
            
        except Exception as e:
            logger.error(f"Error restarting analyzer: {e}")
            QMessageBox.critical(self, "Restart Error", f"Failed to restart analyzer:\n{str(e)}")
    
    def _show_instrument_management(self):
        """Show instrument management dialog."""
        try:
            dialog = InstrumentManagementDialog(self)
            dialog.operation_completed.connect(self._on_instrument_operation_completed)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing instrument management dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open instrument management dialog:\n{str(e)}")
    
    def _on_instrument_operation_completed(self, operation_name: str, success: bool):
        """Handle instrument operation completion."""
        status = "successful" if success else "failed"
        logger.info(f"Instrument operation '{operation_name}' {status}")
        
        # Update status bar or show notification
        if success:
            self.statusBar().showMessage(f"Instrument operation '{operation_name}' completed successfully", 5000)
        else:
            self.statusBar().showMessage(f"Instrument operation '{operation_name}' failed", 5000)
    
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
        except Exception as e:
            logger.error(f"Error cleaning up signal files: {e}")
    
    def _shutdown_instrument_on_exit(self):
        """Shutdown the instrument when exiting the application."""
        try:
            logger.info("Shutting down instrument on application exit...")
            
            # Stop data collector first
            if self.data_collector_monitoring:
                self._stop_monitoring()
            
            # Send shutdown command to instrument
            import requests
            instrument_ip = "192.168.1.1"
            instrument_port = "8180"
            api_base = f"http://{instrument_ip}:{instrument_port}/api"
            
            response = requests.put(
                f"{api_base}/tag/INSTRUMENT_SHUTDOWN_CONTROL/value",
                json={"value": "SHUTDOWN"},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("Shutdown command sent to instrument successfully")
                return True
            else:
                logger.error(f"Failed to send shutdown command: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning("Cannot connect to instrument for shutdown")
            return False
        except Exception as e:
            logger.error(f"Error during instrument shutdown: {e}")
            return False
    
    def _perform_cleanup(self):
        """Perform all cleanup operations."""
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
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Ask user if they want to shutdown the instrument
            reply = QMessageBox.question(
                self,
                "Shutdown Instrument",
                "Do you want to shutdown the instrument before closing the software?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                # User cancelled, don't close the application
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # User wants to shutdown instrument
                if not self._shutdown_instrument_on_exit():
                    # If shutdown failed, ask if they still want to close
                    reply2 = QMessageBox.question(
                        self,
                        "Shutdown Failed",
                        "Failed to shutdown instrument. Do you still want to close the software?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply2 == QMessageBox.StandardButton.No:
                        event.ignore()
                        return
            
            # Continue with normal cleanup
            self._perform_cleanup()
            
            logger.info("Main window closed")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during close: {e}")
            event.accept()


def main():
    """Main entry point for the GUI application."""
    import sys
    from PyQt6.QtWidgets import QApplication
    from ..utils.config import Config
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("CO_O2_Analyser")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CO_O2_Analyser")
    
    try:
        # Load configuration
        config = Config()
        
        # Create and show main window
        window = MainWindow(config)
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)