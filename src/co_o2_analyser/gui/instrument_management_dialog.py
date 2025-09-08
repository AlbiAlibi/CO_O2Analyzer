"""
Instrument Management Dialog for CO_O2_Analyser.

This module provides a dialog window for managing instrument operations
like time synchronization, shutdown, and restart.
"""

import logging
import requests
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QMessageBox, QProgressBar, QTextEdit, QFrame, QLineEdit, QApplication
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QFont, QPixmap

logger = logging.getLogger(__name__)


class InstrumentManagementDialog(QDialog):
    """Dialog for managing instrument operations."""
    
    # Signals
    operation_completed = pyqtSignal(str, bool)  # operation_name, success
    
    def __init__(self, parent=None):
        """Initialize the instrument management dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Instrument Management")
        self.setModal(True)
        self.resize(500, 400)
        
        # Instrument settings
        self.instrument_ip = "192.168.1.1"
        self.instrument_port = "8180"
        self.api_base = f"http://{self.instrument_ip}:{self.instrument_port}/api"
        
        # Data collector process
        self.data_collector_process = None
        
        self._setup_ui()
        self._check_data_collector_status()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Instrument Management")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Time Management Group
        time_group = QGroupBox("Time Management")
        time_layout = QVBoxLayout()
        
        # Current time display
        self.current_time_label = QLabel("Current Computer Time: " + datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        time_layout.addWidget(self.current_time_label)
        
        # Sync time button
        self.sync_time_btn = QPushButton("🕐 Synchronize Instrument Time")
        self.sync_time_btn.clicked.connect(self._sync_instrument_time)
        self.sync_time_btn.setToolTip("Set instrument time to match computer time")
        time_layout.addWidget(self.sync_time_btn)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # CO Auto Zero Group - DISABLED (IN DEVELOPMENT)
        # TODO: This module is currently in development and has been disabled
        # The CO Auto Zero functionality allows setting CO zero point correction
        # using the CO_ZERO_CONC_1 tag and SV_DYNAMIC_ZERO_ENABLE tag
        # 
        # co_zero_group = QGroupBox("CO Auto Zero")
        # co_zero_layout = QVBoxLayout()
        # 
        # # CO Zero value input
        # co_zero_input_layout = QHBoxLayout()
        # co_zero_input_layout.addWidget(QLabel("CO Zero Value:"))
        # self.co_zero_value_input = QLineEdit("0.0")
        # self.co_zero_value_input.setPlaceholderText("Enter CO zero correction value")
        # self.co_zero_value_input.setToolTip("Enter a float value to set CO zero point correction")
        # co_zero_input_layout.addWidget(self.co_zero_value_input)
        # co_zero_layout.addLayout(co_zero_input_layout)
        # 
        # # CO Zero buttons
        # co_zero_button_layout = QHBoxLayout()
        # 
        # self.enable_dynamic_zero_btn = QPushButton("🔓 Enable Dynamic Zero")
        # self.enable_dynamic_zero_btn.clicked.connect(self._enable_dynamic_zero)
        # self.enable_dynamic_zero_btn.setToolTip("Enable dynamic zero calibration (required for CO zero)")
        # co_zero_button_layout.addWidget(self.enable_dynamic_zero_btn)
        # 
        # self.disable_dynamic_zero_btn = QPushButton("🔒 Disable Dynamic Zero")
        # self.disable_dynamic_zero_btn.clicked.connect(self._disable_dynamic_zero)
        # self.disable_dynamic_zero_btn.setToolTip("Disable dynamic zero calibration")
        # co_zero_button_layout.addWidget(self.disable_dynamic_zero_btn)
        # 
        # co_zero_layout.addLayout(co_zero_button_layout)
        # 
        # # CO Zero control buttons
        # co_zero_control_layout = QHBoxLayout()
        # 
        # self.set_co_zero_btn = QPushButton("🎯 Set CO Zero")
        # self.set_co_zero_btn.clicked.connect(self._set_co_zero)
        # self.set_co_zero_btn.setToolTip("Set CO zero point using CO_ZERO_CONC_1 tag")
        # co_zero_control_layout.addWidget(self.set_co_zero_btn)
        # 
        # self.test_co_zero_btn = QPushButton("🧪 Test CO Zero Sequence")
        # self.test_co_zero_btn.clicked.connect(self._test_co_zero_sequence)
        # self.test_co_zero_btn.setToolTip("Test CO zero with values: -3, 0, 3, 4 (5 sec delays)")
        # co_zero_control_layout.addWidget(self.test_co_zero_btn)
        # 
        # co_zero_layout.addLayout(co_zero_control_layout)
        # co_zero_group.setLayout(co_zero_layout)
        # layout.addWidget(co_zero_group)
        
        # Instrument Control Group
        control_group = QGroupBox("Instrument Control")
        control_layout = QVBoxLayout()
        
        # Data collector status
        self.data_collector_status = QLabel("Data Collector: Checking...")
        control_layout.addWidget(self.data_collector_status)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.restart_btn = QPushButton("🔄 Restart Instrument")
        self.restart_btn.clicked.connect(self._restart_instrument)
        self.restart_btn.setToolTip("Restart the instrument immediately")
        button_layout.addWidget(self.restart_btn)
        
        self.shutdown_btn = QPushButton("⏹️ Shutdown Instrument")
        self.shutdown_btn.clicked.connect(self._shutdown_instrument)
        self.shutdown_btn.setToolTip("Shutdown the instrument immediately")
        button_layout.addWidget(self.shutdown_btn)
        
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Progress and Log
        progress_group = QGroupBox("Operation Status")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Operation logs will appear here...")
        progress_layout.addWidget(self.log_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Update time display every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time_display)
        self.time_timer.start(1000)
    
    def _update_time_display(self):
        """Update the current time display."""
        self.current_time_label.setText("Current Computer Time: " + datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    
    def _check_data_collector_status(self):
        """Check if data collector is running."""
        try:
            # Check if start_data_collector.py is running
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True, text=True, shell=True
            )
            
            if "start_data_collector.py" in result.stdout:
                self.data_collector_status.setText("Data Collector: Running")
                self.data_collector_status.setStyleSheet("color: green;")
            else:
                self.data_collector_status.setText("Data Collector: Not Running")
                self.data_collector_status.setStyleSheet("color: red;")
        except Exception as e:
            self.data_collector_status.setText("Data Collector: Status Unknown")
            self.data_collector_status.setStyleSheet("color: orange;")
            logger.warning(f"Could not check data collector status: {e}")
    
    def _log_message(self, message: str):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def _show_progress(self, show: bool = True):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def _stop_data_collector(self):
        """Stop the data collector process."""
        try:
            self._log_message("Stopping data collector...")
            
            # Find and kill start_data_collector.py process
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq start_data_collector.py*"],
                capture_output=True, text=True, shell=True
            )
            
            if result.returncode == 0:
                self._log_message("Data collector stopped successfully")
                return True
            else:
                # Try alternative method
                result = subprocess.run(
                    ["wmic", "process", "where", "commandline like '%start_data_collector.py%'", "delete"],
                    capture_output=True, text=True, shell=True
                )
                if result.returncode == 0:
                    self._log_message("Data collector stopped successfully (alternative method)")
                    return True
                else:
                    self._log_message("Warning: Could not stop data collector automatically")
                    return False
        except Exception as e:
            self._log_message(f"Error stopping data collector: {e}")
            return False
    
    def _sync_instrument_time(self):
        """Synchronize instrument time with computer time."""
        self._show_progress(True)
        self.sync_time_btn.setEnabled(False)
        
        try:
            self._log_message("Starting time synchronization...")
            
            # Get current computer time
            current_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            self._log_message(f"Setting instrument time to: {current_time}")
            
            # Setup time sync configuration
            self._log_message("Configuring time sync settings...")
            
            # Enable manual time sync
            response1 = requests.put(
                f"{self.api_base}/tag/TIME_SYNC_USE_MANUAL/value",
                json={"value": "True"},
                timeout=5
            )
            
            if response1.status_code != 200:
                raise Exception(f"Failed to enable manual time sync: {response1.status_code}")
            
            # Disable automatic sync
            response2 = requests.put(
                f"{self.api_base}/tag/TIME_SYNC/value",
                json={"value": "False"},
                timeout=5
            )
            
            if response2.status_code != 200:
                raise Exception(f"Failed to disable automatic sync: {response2.status_code}")
            
            # Set target time
            response3 = requests.put(
                f"{self.api_base}/tag/DATE_TIME_TARGET_VALUE/value",
                json={"value": current_time},
                timeout=5
            )
            
            if response3.status_code != 200:
                raise Exception(f"Failed to set target time: {response3.status_code}")
            
            self._log_message("Time synchronization completed successfully!")
            self.operation_completed.emit("Time Sync", True)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Success", 
                f"Instrument time has been synchronized to:\n{current_time}"
            )
            
        except requests.exceptions.ConnectionError:
            self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
            QMessageBox.warning(
                self, 
                "Connection Error", 
                "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
            )
            self.operation_completed.emit("Time Sync", False)
        except Exception as e:
            self._log_message(f"Error during time synchronization: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Time synchronization failed:\n{str(e)}"
            )
            self.operation_completed.emit("Time Sync", False)
        finally:
            self._show_progress(False)
            self.sync_time_btn.setEnabled(True)
    
    def _restart_instrument(self):
        """Restart the instrument."""
        self._show_progress(True)
        self.restart_btn.setEnabled(False)
        
        try:
            self._log_message("Preparing to restart instrument...")
            
            # Stop data collector first
            if not self._stop_data_collector():
                reply = QMessageBox.question(
                    self,
                    "Data Collector Warning",
                    "Could not stop data collector automatically.\nDo you want to continue with restart?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self._log_message("Restart cancelled by user")
                    return
            
            self._log_message("Sending restart command to instrument...")
            
            # Send restart command
            response = requests.put(
                f"{self.api_base}/tag/INSTRUMENT_SHUTDOWN_CONTROL/value",
                json={"value": "RESTART"},
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send restart command: {response.status_code}")
            
            self._log_message("Restart command sent successfully!")
            self.operation_completed.emit("Restart", True)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Success", 
                "Restart command sent to instrument.\nThe instrument will restart shortly."
            )
            
        except requests.exceptions.ConnectionError:
            self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
            QMessageBox.warning(
                self, 
                "Connection Error", 
                "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
            )
            self.operation_completed.emit("Restart", False)
        except Exception as e:
            self._log_message(f"Error during restart: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Restart command failed:\n{str(e)}"
            )
            self.operation_completed.emit("Restart", False)
        finally:
            self._show_progress(False)
            self.restart_btn.setEnabled(True)
    
    def _shutdown_instrument(self):
        """Shutdown the instrument."""
        self._show_progress(True)
        self.shutdown_btn.setEnabled(False)
        
        try:
            self._log_message("Preparing to shutdown instrument...")
            
            # Stop data collector first
            if not self._stop_data_collector():
                reply = QMessageBox.question(
                    self,
                    "Data Collector Warning",
                    "Could not stop data collector automatically.\nDo you want to continue with shutdown?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self._log_message("Shutdown cancelled by user")
                    return
            
            # Confirm shutdown
            reply = QMessageBox.question(
                self,
                "Confirm Shutdown",
                "Are you sure you want to shutdown the instrument?\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                self._log_message("Shutdown cancelled by user")
                return
            
            self._log_message("Sending shutdown command to instrument...")
            
            # Send shutdown command
            response = requests.put(
                f"{self.api_base}/tag/INSTRUMENT_SHUTDOWN_CONTROL/value",
                json={"value": "SHUTDOWN"},
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to send shutdown command: {response.status_code}")
            
            self._log_message("Shutdown command sent successfully!")
            self.operation_completed.emit("Shutdown", True)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Success", 
                "Shutdown command sent to instrument.\nThe instrument will shutdown shortly."
            )
            
        except requests.exceptions.ConnectionError:
            self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
            QMessageBox.warning(
                self, 
                "Connection Error", 
                "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
            )
            self.operation_completed.emit("Shutdown", False)
        except Exception as e:
            self._log_message(f"Error during shutdown: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Shutdown command failed:\n{str(e)}"
            )
            self.operation_completed.emit("Shutdown", False)
        finally:
            self._show_progress(False)
            self.shutdown_btn.setEnabled(True)
    
    # CO Auto Zero Methods - DISABLED (IN DEVELOPMENT)
    # TODO: These methods are currently in development and have been disabled
    # They implement CO zero point correction functionality using CO_ZERO_CONC_1 and SV_DYNAMIC_ZERO_ENABLE tags
    # 
    # def _set_co_zero(self):
    #     """Set CO zero point using CO_ZERO_CONC_1 tag."""
    #     self._show_progress(True)
    #     self.set_co_zero_btn.setEnabled(False)
    #     
    #     try:
    #         # Get the value from input
    #         value_text = self.co_zero_value_input.text().strip()
    #         if not value_text:
    #             QMessageBox.warning(self, "Input Error", "Please enter a CO zero value")
    #             return
    #         
    #         try:
    #             co_zero_value = float(value_text)
    #         except ValueError:
    #             QMessageBox.warning(self, "Input Error", "Please enter a valid number")
    #             return
    #         
    #         # First, ensure dynamic zero is enabled
    #         self._log_message("Ensuring dynamic zero calibration is enabled...")
    #         enable_response = requests.put(
    #             f"{self.api_base}/tag/SV_DYNAMIC_ZERO_ENABLE/value",
    #             json={"value": True},
    #             timeout=5
    #         )
    #         
    #         if enable_response.status_code != 200:
    #             raise Exception(f"Failed to enable dynamic zero: {enable_response.status_code}")
    #         
    #         self._log_message("Dynamic zero calibration enabled")
    #         
    #         self._log_message(f"Setting CO zero to: {co_zero_value}")
    #         
    #         # Send CO zero value to instrument
    #         response = requests.put(
    #             f"{self.api_base}/tag/CO_ZERO_CONC_1/value",
    #             json={"value": co_zero_value},
    #             timeout=5
    #         )
    #         
    #         if response.status_code != 200:
    #             raise Exception(f"Failed to set CO zero: {response.status_code}")
    #         
    #         self._log_message(f"CO zero set successfully to: {co_zero_value}")
    #         self.operation_completed.emit("CO Zero Set", True)
    #         
    #         # Show success message
    #         QMessageBox.information(
    #             self, 
    #             "Success", 
    #             f"CO zero point has been set to: {co_zero_value}\n\nDynamic zero calibration was automatically enabled."
    #         )
    #         
    #     except requests.exceptions.ConnectionError:
    #         self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
    #         QMessageBox.warning(
    #             self, 
    #             "Connection Error", 
    #             "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
    #         )
    #         self.operation_completed.emit("CO Zero Set", False)
    #     except Exception as e:
    #         self._log_message(f"Error setting CO zero: {e}")
    #         QMessageBox.critical(
    #             self, 
    #             "Error", 
    #             f"Failed to set CO zero:\n{str(e)}"
    #         )
    #         self.operation_completed.emit("CO Zero Set", False)
    #     finally:
    #         self._show_progress(False)
    #         self.set_co_zero_btn.setEnabled(True)
    
    # def _test_co_zero_sequence(self):
    #     """Test CO zero sequence with values -3, 0, 3, 4 with 5-second delays."""
    #     self._show_progress(True)
    #     self.test_co_zero_btn.setEnabled(False)
    #     
    #     try:
    #         # First, ensure dynamic zero is enabled
    #         self._log_message("Ensuring dynamic zero calibration is enabled...")
    #         enable_response = requests.put(
    #             f"{self.api_base}/tag/SV_DYNAMIC_ZERO_ENABLE/value",
    #             json={"value": True},
    #             timeout=5
    #         )
    #         
    #         if enable_response.status_code != 200:
    #             raise Exception(f"Failed to enable dynamic zero: {enable_response.status_code}")
    #         
    #         self._log_message("Dynamic zero calibration enabled")
    #         
    #         test_values = [-3.0, 0.0, 3.0, 4.0]
    #         self._log_message("Starting CO zero test sequence...")
    #         
    #         for i, value in enumerate(test_values, 1):
    #             self._log_message(f"Test {i}/4: Setting CO zero to {value}")
    #             
    #             # Send CO zero value to instrument
    #             response = requests.put(
    #                 f"{self.api_base}/tag/CO_ZERO_CONC_1/value",
    #                 json={"value": value},
    #                 timeout=5
    #             )
    #             
    #             if response.status_code != 200:
    #                 raise Exception(f"Failed to set CO zero to {value}: {response.status_code}")
    #             
    #             self._log_message(f"Successfully set CO zero to: {value}")
    #             
    #             # Wait 5 seconds before next value (except for the last one)
    #             if i < len(test_values):
    #                 self._log_message("Waiting 5 seconds before next test...")
    #                 QApplication.processEvents()  # Keep UI responsive
    #                 time.sleep(5)
    #         
    #         self._log_message("CO zero test sequence completed successfully!")
    #         self.operation_completed.emit("CO Zero Test", True)
    #         
    #         # Show success message
    #         QMessageBox.information(
    #             self, 
    #             "Test Complete", 
    #             "CO zero test sequence completed successfully!\n\n"
    #             "Tested values: -3, 0, 3, 4\n"
    #             "Each value was set with 5-second intervals.\n\n"
    #             "Dynamic zero calibration was automatically enabled."
    #         )
    #         
    #     except requests.exceptions.ConnectionError:
    #         self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
    #         QMessageBox.warning(
    #             self, 
    #             "Connection Error", 
    #             "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
    #         )
    #         self.operation_completed.emit("CO Zero Test", False)
    #     except Exception as e:
    #         self._log_message(f"Error during CO zero test: {e}")
    #         QMessageBox.critical(
    #             self, 
    #             "Error", 
    #             f"CO zero test failed:\n{str(e)}"
    #         )
    #         self.operation_completed.emit("CO Zero Test", False)
    #     finally:
    #         self._show_progress(False)
    #         self.test_co_zero_btn.setEnabled(True)
    # 
    # def _enable_dynamic_zero(self):
    #     """Enable dynamic zero calibration."""
    #     self._show_progress(True)
    #     self.enable_dynamic_zero_btn.setEnabled(False)
    #     
    #     try:
    #         self._log_message("Enabling dynamic zero calibration...")
    #         
    #         # Enable dynamic zero calibration
    #         response = requests.put(
    #             f"{self.api_base}/tag/SV_DYNAMIC_ZERO_ENABLE/value",
    #             json={"value": True},
    #             timeout=5
    #         )
    #         
    #         if response.status_code != 200:
    #             raise Exception(f"Failed to enable dynamic zero: {response.status_code}")
    #         
    #         self._log_message("Dynamic zero calibration enabled successfully!")
    #         self.operation_completed.emit("Enable Dynamic Zero", True)
    #         
    #         # Show success message
    #         QMessageBox.information(
    #             self, 
    #             "Success", 
    #             "Dynamic zero calibration has been enabled.\nYou can now set CO zero values."
    #         )
    #         
    #     except requests.exceptions.ConnectionError:
    #         self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
    #         QMessageBox.warning(
    #             self, 
    #             "Connection Error", 
    #             "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
    #         )
    #         self.operation_completed.emit("Enable Dynamic Zero", False)
    #     except Exception as e:
    #         self._log_message(f"Error enabling dynamic zero: {e}")
    #         QMessageBox.critical(
    #             self, 
    #             "Error", 
    #             f"Failed to enable dynamic zero:\n{str(e)}"
    #         )
    #         self.operation_completed.emit("Enable Dynamic Zero", False)
    #     finally:
    #         self._show_progress(False)
    #         self.enable_dynamic_zero_btn.setEnabled(True)
    # 
    # def _disable_dynamic_zero(self):
    #     """Disable dynamic zero calibration."""
    #     self._show_progress(True)
    #     self.disable_dynamic_zero_btn.setEnabled(False)
    #     
    #     try:
    #         self._log_message("Disabling dynamic zero calibration...")
    #         
    #         # Disable dynamic zero calibration
    #         response = requests.put(
    #             f"{self.api_base}/tag/SV_DYNAMIC_ZERO_ENABLE/value",
    #             json={"value": False},
    #             timeout=5
    #         )
    #         
    #         if response.status_code != 200:
    #             raise Exception(f"Failed to disable dynamic zero: {response.status_code}")
    #         
    #         self._log_message("Dynamic zero calibration disabled successfully!")
    #         self.operation_completed.emit("Disable Dynamic Zero", True)
    #         
    #         # Show success message
    #         QMessageBox.information(
    #             self, 
    #             "Success", 
    #             "Dynamic zero calibration has been disabled."
    #         )
    #         
    #     except requests.exceptions.ConnectionError:
    #         self._log_message("Error: Cannot connect to instrument. Please check if instrument is powered on.")
    #         QMessageBox.warning(
    #             self, 
    #             "Connection Error", 
    #             "Cannot connect to instrument.\nPlease ensure the instrument is powered on and connected to the network."
    #         )
    #         self.operation_completed.emit("Disable Dynamic Zero", False)
    #     except Exception as e:
    #         self._log_message(f"Error disabling dynamic zero: {e}")
    #         QMessageBox.critical(
    #             self, 
    #             "Error", 
    #             f"Failed to disable dynamic zero:\n{str(e)}"
    #         )
    #         self.operation_completed.emit("Disable Dynamic Zero", False)
    #     finally:
    #         self._show_progress(False)
    #         self.disable_dynamic_zero_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        self.time_timer.stop()
        event.accept()
