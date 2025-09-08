"""
Settings Dialog for CO_O2_Analyser.

This module provides a dialog window for managing application settings
stored in config.json file.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QMessageBox, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTabWidget, QWidget, QFormLayout, QTextEdit, QComboBox,
    QFileDialog, QDialogButtonBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QValidator, QIntValidator, QDoubleValidator

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for managing application settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)  # new_settings
    
    def __init__(self, config_path: str, parent=None):
        """Initialize the settings dialog.
        
        Args:
            config_path: Path to the config.json file
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.original_config = {}
        self.current_config = {}
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        self._load_config()
        self._setup_ui()
        self._populate_fields()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.original_config = json.load(f)
                    self.current_config = json.loads(json.dumps(self.original_config))  # Deep copy
            else:
                # Create default config if file doesn't exist
                self.original_config = self._get_default_config()
                self.current_config = json.loads(json.dumps(self.original_config))
                self._save_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load configuration:\n{str(e)}")
            self.original_config = self._get_default_config()
            self.current_config = json.loads(json.dumps(self.original_config))
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "instrument": {
                "ip_address": "192.168.1.1",
                "port": 8180,
                "timeout": 30,
                "retry_attempts": 3,
                "simulation_mode": False,
                "data_simulation": False,
                "tags": {
                    "instrument_status": [
                        "INSTRUMENT_TIME",
                        "NETWORK_IP_ADDRESS",
                        "OS_VERSION"
                    ],
                    "concentration_tags": [
                        "CO_CONC",
                        "O2_CONC"
                    ],
                    "warning_tags": [
                        "BOX_TEMP_WARN",
                        "BENCH_TEMP_WARN",
                        "WHEEL_TEMP_WARN",
                        "LOW_MEMORY_WARNING",
                        "SYS_INVALID_CONC_WARNING",
                        "SF_O2_SENSOR_WARN_MALFUNCTION"
                    ],
                    "flow_tags": [
                        "AI_PUMP_FLOW",
                        "PUMP_CONTROL_MODULE_STATE",
                        "AI_SAMPLE_TEMP",
                        "AI_SAMPLE_PRESSURE",
                        "AI_ATMOSPHERIC_PRESSURE"
                    ],
                    "temperature": [
                        "AI_SAMPLE_TEMP",
                        "AI_DETECTOR_TEMP",
                        "AI_BOX_TEMP",
                        "AI_BENCH_TEMP",
                        "AI_O2_HEATER_TEMP"
                    ]
                }
            },
            "database": {
                "path": "data.sqlite",
                "backup_interval": 3600
            },
            "gui": {
                "window_width": 1920,
                "window_height": 940,
                "theme": "light"
            },
            "logging": {
                "level": "INFO",
                "file": "co_o2_analyser.log",
                "max_size": 10485760
            },
            "data_collection": {
                "intervals": {
                    "all_values_interval": 60,
                    "concentration_interval": 1.5,
                    "status_check_interval": 10
                }
            }
        }
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Application Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Instrument settings tab
        self.instrument_tab = self._create_instrument_tab()
        self.tab_widget.addTab(self.instrument_tab, "Instrument")
        
        # Database settings tab
        self.database_tab = self._create_database_tab()
        self.tab_widget.addTab(self.database_tab, "Database")
        
        # GUI settings tab
        self.gui_tab = self._create_gui_tab()
        self.tab_widget.addTab(self.gui_tab, "GUI")
        
        # Data Collection settings tab
        self.data_collection_tab = self._create_data_collection_tab()
        self.tab_widget.addTab(self.data_collection_tab, "Data Collection")
        
        # Logging settings tab
        self.logging_tab = self._create_logging_tab()
        self.tab_widget.addTab(self.logging_tab, "Logging")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Settings")
        self.test_btn.clicked.connect(self._test_settings)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        self.button_box.accepted.connect(self._save_and_close)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)
        button_layout.addWidget(self.button_box)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _create_instrument_tab(self) -> QWidget:
        """Create instrument settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout()
        
        self.ip_address_edit = QLineEdit()
        self.ip_address_edit.setPlaceholderText("192.168.1.1")
        connection_layout.addRow("IP Address:", self.ip_address_edit)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(8180)
        connection_layout.addRow("Port:", self.port_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        connection_layout.addRow("Timeout:", self.timeout_spin)
        
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(0, 10)
        self.retry_attempts_spin.setValue(3)
        connection_layout.addRow("Retry Attempts:", self.retry_attempts_spin)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Simulation settings
        simulation_group = QGroupBox("Simulation Settings")
        simulation_layout = QVBoxLayout()
        
        self.simulation_mode_check = QCheckBox("Enable Simulation Mode")
        simulation_layout.addWidget(self.simulation_mode_check)
        
        self.data_simulation_check = QCheckBox("Enable Data Simulation")
        simulation_layout.addWidget(self.data_simulation_check)
        
        simulation_group.setLayout(simulation_layout)
        layout.addWidget(simulation_group)
        
        # Tag configuration
        tags_group = QGroupBox("Tag Configuration")
        tags_layout = QVBoxLayout()
        
        # Instrument status tags
        self.instrument_status_edit = QTextEdit()
        self.instrument_status_edit.setMaximumHeight(80)
        self.instrument_status_edit.setPlaceholderText("One tag per line")
        tags_layout.addWidget(QLabel("Instrument Status Tags:"))
        tags_layout.addWidget(self.instrument_status_edit)
        
        # Concentration tags
        self.concentration_tags_edit = QTextEdit()
        self.concentration_tags_edit.setMaximumHeight(60)
        self.concentration_tags_edit.setPlaceholderText("One tag per line")
        tags_layout.addWidget(QLabel("Concentration Tags:"))
        tags_layout.addWidget(self.concentration_tags_edit)
        
        # Warning tags
        self.warning_tags_edit = QTextEdit()
        self.warning_tags_edit.setMaximumHeight(100)
        self.warning_tags_edit.setPlaceholderText("One tag per line")
        tags_layout.addWidget(QLabel("Warning Tags:"))
        tags_layout.addWidget(self.warning_tags_edit)
        
        # Flow tags
        self.flow_tags_edit = QTextEdit()
        self.flow_tags_edit.setMaximumHeight(80)
        self.flow_tags_edit.setPlaceholderText("One tag per line")
        tags_layout.addWidget(QLabel("Flow Tags:"))
        tags_layout.addWidget(self.flow_tags_edit)
        
        # Temperature tags
        self.temperature_tags_edit = QTextEdit()
        self.temperature_tags_edit.setMaximumHeight(80)
        self.temperature_tags_edit.setPlaceholderText("One tag per line")
        tags_layout.addWidget(QLabel("Temperature Tags:"))
        tags_layout.addWidget(self.temperature_tags_edit)
        
        tags_group.setLayout(tags_layout)
        layout.addWidget(tags_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_database_tab(self) -> QWidget:
        """Create database settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Database path
        path_group = QGroupBox("Database Settings")
        path_layout = QFormLayout()
        
        path_widget = QWidget()
        path_widget_layout = QHBoxLayout()
        path_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        self.database_path_edit = QLineEdit()
        self.database_path_edit.setPlaceholderText("data.sqlite")
        path_widget_layout.addWidget(self.database_path_edit)
        
        self.browse_db_btn = QPushButton("Browse...")
        self.browse_db_btn.clicked.connect(self._browse_database)
        path_widget_layout.addWidget(self.browse_db_btn)
        
        path_widget.setLayout(path_widget_layout)
        path_layout.addRow("Database Path:", path_widget)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(60, 86400)
        self.backup_interval_spin.setValue(3600)
        self.backup_interval_spin.setSuffix(" seconds")
        path_layout.addRow("Backup Interval:", self.backup_interval_spin)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_gui_tab(self) -> QWidget:
        """Create GUI settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Window settings
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout()
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 4000)
        self.window_width_spin.setValue(1920)
        window_layout.addRow("Window Width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 3000)
        self.window_height_spin.setValue(940)
        window_layout.addRow("Window Height:", self.window_height_spin)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        window_layout.addRow("Theme:", self.theme_combo)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_data_collection_tab(self) -> QWidget:
        """Create data collection settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Collection intervals
        intervals_group = QGroupBox("Collection Intervals")
        intervals_layout = QFormLayout()
        
        self.all_values_interval_spin = QSpinBox()
        self.all_values_interval_spin.setRange(1, 3600)
        self.all_values_interval_spin.setValue(60)
        self.all_values_interval_spin.setSuffix(" seconds")
        intervals_layout.addRow("All Values Interval:", self.all_values_interval_spin)
        
        self.concentration_interval_spin = QDoubleSpinBox()
        self.concentration_interval_spin.setRange(0.1, 60.0)
        self.concentration_interval_spin.setValue(1.5)
        self.concentration_interval_spin.setDecimals(1)
        self.concentration_interval_spin.setSuffix(" seconds")
        intervals_layout.addRow("Concentration Interval:", self.concentration_interval_spin)
        
        self.status_check_interval_spin = QSpinBox()
        self.status_check_interval_spin.setRange(1, 300)
        self.status_check_interval_spin.setValue(10)
        self.status_check_interval_spin.setSuffix(" seconds")
        intervals_layout.addRow("Status Check Interval:", self.status_check_interval_spin)
        
        intervals_group.setLayout(intervals_layout)
        layout.addWidget(intervals_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_logging_tab(self) -> QWidget:
        """Create logging settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Logging settings
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.log_file_edit = QLineEdit()
        self.log_file_edit.setPlaceholderText("co_o2_analyser.log")
        logging_layout.addRow("Log File:", self.log_file_edit)
        
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1024, 104857600)  # 1KB to 100MB
        self.max_size_spin.setValue(10485760)  # 10MB
        self.max_size_spin.setSuffix(" bytes")
        logging_layout.addRow("Max File Size:", self.max_size_spin)
        
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _populate_fields(self):
        """Populate form fields with current configuration."""
        try:
            # Instrument settings
            instrument = self.current_config.get("instrument", {})
            self.ip_address_edit.setText(instrument.get("ip_address", "192.168.1.1"))
            self.port_spin.setValue(instrument.get("port", 8180))
            self.timeout_spin.setValue(instrument.get("timeout", 30))
            self.retry_attempts_spin.setValue(instrument.get("retry_attempts", 3))
            self.simulation_mode_check.setChecked(instrument.get("simulation_mode", False))
            self.data_simulation_check.setChecked(instrument.get("data_simulation", False))
            
            # Tags
            tags = instrument.get("tags", {})
            self.instrument_status_edit.setText("\n".join(tags.get("instrument_status", [])))
            self.concentration_tags_edit.setText("\n".join(tags.get("concentration_tags", [])))
            self.warning_tags_edit.setText("\n".join(tags.get("warning_tags", [])))
            self.flow_tags_edit.setText("\n".join(tags.get("flow_tags", [])))
            self.temperature_tags_edit.setText("\n".join(tags.get("temperature", [])))
            
            # Database settings
            database = self.current_config.get("database", {})
            self.database_path_edit.setText(database.get("path", "data.sqlite"))
            self.backup_interval_spin.setValue(database.get("backup_interval", 3600))
            
            # GUI settings
            gui = self.current_config.get("gui", {})
            self.window_width_spin.setValue(gui.get("window_width", 1920))
            self.window_height_spin.setValue(gui.get("window_height", 940))
            self.theme_combo.setCurrentText(gui.get("theme", "light"))
            
            # Data collection settings
            data_collection = self.current_config.get("data_collection", {})
            intervals = data_collection.get("intervals", {})
            self.all_values_interval_spin.setValue(intervals.get("all_values_interval", 60))
            self.concentration_interval_spin.setValue(intervals.get("concentration_interval", 1.5))
            self.status_check_interval_spin.setValue(intervals.get("status_check_interval", 10))
            
            # Logging settings
            logging_config = self.current_config.get("logging", {})
            self.log_level_combo.setCurrentText(logging_config.get("level", "INFO"))
            self.log_file_edit.setText(logging_config.get("file", "co_o2_analyser.log"))
            self.max_size_spin.setValue(logging_config.get("max_size", 10485760))
            
        except Exception as e:
            logger.error(f"Error populating fields: {e}")
            QMessageBox.warning(self, "Warning", f"Error loading some settings:\n{str(e)}")
    
    def _browse_database(self):
        """Browse for database file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database File", "", "SQLite Files (*.sqlite *.db);;All Files (*)"
        )
        if file_path:
            self.database_path_edit.setText(file_path)
    
    def _test_settings(self):
        """Test the current settings."""
        try:
            # Collect current form data
            test_config = self._collect_form_data()
            
            # Test instrument connection
            self._test_instrument_connection(test_config)
            
            # Test database path
            self._test_database_path(test_config)
            
            # Test logging configuration
            self._test_logging_config(test_config)
            
            QMessageBox.information(
                self, 
                "Settings Test", 
                "Settings test completed successfully!\nAll configurations appear to be valid."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Settings Test Failed", 
                f"Settings test failed:\n{str(e)}"
            )
    
    def _test_instrument_connection(self, config: Dict[str, Any]):
        """Test instrument connection."""
        import requests
        
        instrument = config.get("instrument", {})
        ip_address = instrument.get("ip_address", "192.168.1.1")
        port = instrument.get("port", 8180)
        timeout = instrument.get("timeout", 30)
        
        try:
            # Test basic connectivity
            response = requests.get(
                f"http://{ip_address}:{port}/api/tag/INSTRUMENT_TIME/value",
                timeout=timeout
            )
            
            if response.status_code == 200:
                logger.info("Instrument connection test successful")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to instrument at {ip_address}:{port}")
        except requests.exceptions.Timeout:
            raise Exception(f"Connection timeout after {timeout} seconds")
        except Exception as e:
            raise Exception(f"Instrument connection test failed: {str(e)}")
    
    def _test_database_path(self, config: Dict[str, Any]):
        """Test database path."""
        import sqlite3
        
        database = config.get("database", {})
        db_path = database.get("path", "data.sqlite")
        
        try:
            # Test if we can connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                raise Exception("Database exists but contains no tables")
                
            logger.info(f"Database test successful: {len(tables)} tables found")
            
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Database test failed: {str(e)}")
    
    def _test_logging_config(self, config: Dict[str, Any]):
        """Test logging configuration."""
        logging_config = config.get("logging", {})
        log_file = logging_config.get("file", "co_o2_analyser.log")
        max_size = logging_config.get("max_size", 10485760)
        
        try:
            # Test if we can write to the log file
            test_path = Path(log_file)
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_path, 'a', encoding='utf-8') as f:
                f.write("Settings test log entry\n")
            
            # Check file size
            if test_path.exists() and test_path.stat().st_size > max_size:
                raise Exception(f"Log file size ({test_path.stat().st_size}) exceeds maximum ({max_size})")
            
            logger.info("Logging configuration test successful")
            
        except Exception as e:
            raise Exception(f"Logging test failed: {str(e)}")
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Collect data from form fields."""
        config = {}
        
        # Instrument settings
        config["instrument"] = {
            "ip_address": self.ip_address_edit.text().strip() or "192.168.1.1",
            "port": self.port_spin.value(),
            "timeout": self.timeout_spin.value(),
            "retry_attempts": self.retry_attempts_spin.value(),
            "simulation_mode": self.simulation_mode_check.isChecked(),
            "data_simulation": self.data_simulation_check.isChecked(),
            "tags": {
                "instrument_status": [tag.strip() for tag in self.instrument_status_edit.toPlainText().split('\n') if tag.strip()],
                "concentration_tags": [tag.strip() for tag in self.concentration_tags_edit.toPlainText().split('\n') if tag.strip()],
                "warning_tags": [tag.strip() for tag in self.warning_tags_edit.toPlainText().split('\n') if tag.strip()],
                "flow_tags": [tag.strip() for tag in self.flow_tags_edit.toPlainText().split('\n') if tag.strip()],
                "temperature": [tag.strip() for tag in self.temperature_tags_edit.toPlainText().split('\n') if tag.strip()]
            }
        }
        
        # Database settings
        config["database"] = {
            "path": self.database_path_edit.text().strip() or "data.sqlite",
            "backup_interval": self.backup_interval_spin.value()
        }
        
        # GUI settings
        config["gui"] = {
            "window_width": self.window_width_spin.value(),
            "window_height": self.window_height_spin.value(),
            "theme": self.theme_combo.currentText()
        }
        
        # Data collection settings
        config["data_collection"] = {
            "intervals": {
                "all_values_interval": self.all_values_interval_spin.value(),
                "concentration_interval": self.concentration_interval_spin.value(),
                "status_check_interval": self.status_check_interval_spin.value()
            }
        }
        
        # Logging settings
        config["logging"] = {
            "level": self.log_level_combo.currentText(),
            "file": self.log_file_edit.text().strip() or "co_o2_analyser.log",
            "max_size": self.max_size_spin.value()
        }
        
        return config
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write config file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise Exception(f"Failed to save configuration:\n{str(e)}")
    
    def _save_and_close(self):
        """Save configuration and close dialog."""
        try:
            # Collect form data
            self.current_config = self._collect_form_data()
            
            # Save to file
            self._save_config()
            
            # Emit signal
            self.settings_changed.emit(self.current_config)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings:\n{str(e)}")
    
    def _restore_defaults(self):
        """Restore default settings."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_config = self._get_default_config()
            self._populate_fields()
            QMessageBox.information(self, "Defaults Restored", "Settings have been restored to default values.")
