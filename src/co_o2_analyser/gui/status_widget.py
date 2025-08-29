"""
Status widget for CO_O2_Analyser.

This module contains the status widget that displays
current measurement values and instrument status.
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor

from ..data.models import Measurement

logger = logging.getLogger(__name__)


class StatusWidget(QWidget):
    """Widget for displaying current status and measurements."""
    
    def __init__(self):
        """Initialize status widget."""
        super().__init__()
        self.current_measurement: Optional[Measurement] = None
        
        self._init_ui()
        
        # Timer for status updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
        
        logger.info("Status widget initialized")
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Connection status group
        connection_group = QGroupBox("Connection Status")
        connection_layout = QVBoxLayout(connection_group)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_status)
        
        layout.addWidget(connection_group)
        
        # Current measurements group
        measurements_group = QGroupBox("Current Measurements")
        measurements_layout = QGridLayout(measurements_group)
        
        # CO concentration
        measurements_layout.addWidget(QLabel("CO Concentration:"), 0, 0)
        self.co_label = QLabel("--")
        self.co_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        measurements_layout.addWidget(self.co_label, 0, 1)
        measurements_layout.addWidget(QLabel("ppm"), 0, 2)
        
        # O2 concentration
        measurements_layout.addWidget(QLabel("O₂ Concentration:"), 1, 0)
        self.o2_label = QLabel("--")
        self.o2_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        measurements_layout.addWidget(self.o2_label, 1, 1)
        measurements_layout.addWidget(QLabel("%"), 1, 2)
        
        # Temperature
        measurements_layout.addWidget(QLabel("Temperature:"), 2, 0)
        self.temp_label = QLabel("--")
        measurements_layout.addWidget(self.temp_label, 2, 1)
        measurements_layout.addWidget(QLabel("°C"), 2, 2)
        
        # Humidity
        measurements_layout.addWidget(QLabel("Humidity:"), 3, 0)
        self.humidity_label = QLabel("--")
        measurements_layout.addWidget(self.humidity_label, 3, 1)
        measurements_layout.addWidget(QLabel("%"), 3, 2)
        
        # Pressure
        measurements_layout.addWidget(QLabel("Pressure:"), 4, 0)
        self.pressure_label = QLabel("--")
        measurements_layout.addWidget(self.pressure_label, 4, 1)
        measurements_layout.addWidget(QLabel("hPa"), 4, 2)
        
        layout.addWidget(measurements_group)
        
        # Exhaust Fume Limit group
        status_group = QGroupBox("Exhaust Fume Limit")
        status_layout = QVBoxLayout(status_group)
        
        # Fume limit value display
        self.fume_limit_label = QLabel("-- mg/m³")
        self.fume_limit_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.fume_limit_label.setToolTip("Normalized CO concentration corrected for oxygen content (21% O₂ reference). Used for regulatory compliance.")
        status_layout.addWidget(self.fume_limit_label)
        
        # Air quality indicator
        self.air_quality_label = QLabel("Calculating...")
        self.air_quality_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.air_quality_label)
        
        # Status progress bar
        self.status_progress = QProgressBar()
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        status_layout.addWidget(self.status_progress)
        
        layout.addWidget(status_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Last update time
        stats_layout.addWidget(QLabel("Last Update:"), 0, 0)
        self.last_update_label = QLabel("Never")
        stats_layout.addWidget(self.last_update_label, 0, 1)
        
        # Measurement count
        stats_layout.addWidget(QLabel("Total Measurements:"), 1, 0)
        self.measurement_count_label = QLabel("0")
        stats_layout.addWidget(self.measurement_count_label, 1, 1)
        
        # Data quality indicator
        stats_layout.addWidget(QLabel("Data Quality:"), 2, 0)
        self.quality_label = QLabel("Unknown")
        stats_layout.addWidget(self.quality_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def update_measurement(self, measurement: Measurement):
        """Update the display with a new measurement.
        
        Args:
            measurement: New measurement to display
        """
        try:
            self.current_measurement = measurement
            
            # Update CO concentration
            if measurement.co_concentration is not None:
                self.co_label.setText(f"{measurement.co_concentration:.2f}")
                self._set_value_color(self.co_label, measurement.co_concentration, 0, 50, 100)
            else:
                self.co_label.setText("--")
                self.co_label.setStyleSheet("color: gray;")
            
            # Update O2 concentration
            if measurement.o2_concentration is not None:
                self.o2_label.setText(f"{measurement.o2_concentration:.2f}")
                self._set_value_color(self.o2_label, measurement.o2_concentration, 18, 21, 25)
            else:
                self.o2_label.setText("--")
                self.o2_label.setStyleSheet("color: gray;")
            
            # Update temperature
            if measurement.temperature is not None:
                self.temp_label.setText(f"{measurement.temperature:.1f}")
                self._set_value_color(self.temp_label, measurement.temperature, 15, 25, 35)
            else:
                self.temp_label.setText("--")
                self.temp_label.setStyleSheet("color: gray;")
            
            # Update humidity
            if measurement.humidity is not None:
                self.humidity_label.setText(f"{measurement.humidity:.1f}")
                self._set_value_color(self.humidity_label, measurement.humidity, 30, 50, 70)
            else:
                self.humidity_label.setText("--")
                self.humidity_label.setStyleSheet("color: gray;")
            
            # Update pressure
            if measurement.pressure is not None:
                self.pressure_label.setText(f"{measurement.pressure:.1f}")
                self._set_value_color(self.pressure_label, measurement.pressure, 950, 1013, 1100)
            else:
                self.pressure_label.setText("--")
                self.pressure_label.setStyleSheet("color: gray;")
            
            # Calculate and update exhaust fume limit
            if (measurement.co_concentration is not None and 
                measurement.o2_concentration is not None):
                
                # Check if this is fresh air (O2 close to 21%, CO low)
                if (measurement.o2_concentration >= 18.0 and 
                    measurement.co_concentration <= 50):
                    # Fresh air conditions - show low normalized value
                    fume_limit = measurement.co_concentration * 1.25  # Simple conversion to mg/m³
                    self.fume_limit_label.setText(f"{fume_limit:.1f} mg/m³")
                    self.air_quality_label.setText("🟢 Fresh Air")
                    self.air_quality_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px;")
                    self.status_progress.setValue(100)
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
                    
                elif measurement.o2_concentration < 18.0:  # Industrial exhaust conditions
                    # Calculate exhaust fume limit using the formula:
                    # CO[ppm] * 1.25 * ((21-13)/(21- O2[%])) = mg/m³
                    fume_limit = (measurement.co_concentration * 1.25 * 
                                 ((21 - 13) / (21 - measurement.o2_concentration)))
                    
                    # CO limit is 500 mg/m³ - calculate percentage to limit
                    co_limit = 500.0  # mg/m³
                    percentage_to_limit = (fume_limit / co_limit) * 100
                    
                    # Display the result in mg/m³ with percentage to limit
                    self.fume_limit_label.setText(f"{fume_limit:.1f} mg/m³ ({percentage_to_limit:.1f}% of limit)")
                    
                    # Color coding based on percentage to limit:
                    # Green: 0-50% of limit, Yellow: 50-100% of limit, Red: over 100% of limit
                    if percentage_to_limit < 50:  # 0-49% of limit - Green
                        self.air_quality_label.setText("🟢 Low Fumes")
                        self.air_quality_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px;")
                        self.status_progress.setValue(int(percentage_to_limit))  # Direct percentage: 0-49%
                        self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
                    elif percentage_to_limit <= 100:  # 50-100% of limit - Yellow
                        self.air_quality_label.setText("🟡 Medium Fumes")
                        self.air_quality_label.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 12px;")  # Light yellow
                        self.status_progress.setValue(int(percentage_to_limit))  # Direct percentage: 50-100%
                        self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: #FFD700; }")  # Light yellow
                    else:  # Over 100% of limit - Red (exceeds limit)
                        self.air_quality_label.setText("🔴 EXCEEDS LIMIT!")
                        self.air_quality_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px;")
                        self.status_progress.setValue(100)  # Maximum at 100%
                        self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                else:
                    self.fume_limit_label.setText("-- mg/m³")
                    self.air_quality_label.setText("Invalid O₂")
                    self.air_quality_label.setStyleSheet("color: gray; font-weight: bold; font-size: 12px;")
                    self.status_progress.setValue(50)
                    self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: gray; }")
            else:
                self.fume_limit_label.setText("-- mg/m³")
                self.air_quality_label.setText("No Data")
                self.air_quality_label.setStyleSheet("color: gray; font-weight: bold; font-size: 12px;")
                self.status_progress.setValue(0)
                self.status_progress.setStyleSheet("QProgressBar::chunk { background-color: gray; }")
            
            # Update last update time
            self.last_update_label.setText(measurement.timestamp.strftime("%H:%M:%S"))
            
            logger.debug(f"Status updated with measurement: {measurement}")
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def update_connection_status(self, is_connected: bool):
        """Update connection status display.
        
        Args:
            is_connected: True if connected, False otherwise
        """
        if is_connected:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
    
    def update_measurement_count(self, count: int):
        """Update measurement count display.
        
        Args:
            count: Total number of measurements
        """
        self.measurement_count_label.setText(str(count))
    
    def update_data_quality(self, quality: str):
        """Update data quality indicator.
        
        Args:
            quality: Quality indicator (Good, Fair, Poor)
        """
        self.quality_label.setText(quality)
        
        # Set color based on quality
        if quality.lower() == "good":
            self.quality_label.setStyleSheet("color: green; font-weight: bold;")
        elif quality.lower() == "fair":
            self.quality_label.setStyleSheet("color: orange; font-weight: bold;")
        elif quality.lower() == "poor":
            self.quality_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.quality_label.setStyleSheet("color: gray;")
    
    def _set_value_color(self, label: QLabel, value: float, low: float, mid: float, high: float):
        """Set label color based on value range.
        
        Args:
            label: Label to color
            value: Current value
            low: Low threshold
            mid: Mid threshold
            high: High threshold
        """
        if value <= low:
            color = "blue"
        elif value <= mid:
            color = "green"
        elif value <= high:
            color = "orange"
        else:
            color = "red"
        
        label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
    
    def _set_status_color(self, status: str):
        """Set status color based on instrument status.
        
        Args:
            status: Instrument status string
        """
        status_lower = status.lower()
        
        if "ok" in status_lower or "normal" in status_lower:
            color = "green"
        elif "warning" in status_lower:
            color = "orange"
        elif "error" in status_lower or "fault" in status_lower:
            color = "red"
        elif "calibrating" in status_lower:
            color = "blue"
        else:
            color = "gray"
        
        self.instrument_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
    
    def _update_display(self):
        """Update the display (called by timer)."""
        # This method can be used for periodic updates if needed
        pass
    
    def clear_display(self):
        """Clear all displayed values."""
        self.co_label.setText("--")
        self.o2_label.setText("--")
        self.temp_label.setText("--")
        self.humidity_label.setText("--")
        self.pressure_label.setText("--")
        self.instrument_status.setText("Unknown")
        self.last_update_label.setText("Never")
        self.measurement_count_label.setText("0")
        self.quality_label.setText("Unknown")
        
        # Reset colors
        for label in [self.co_label, self.o2_label, self.temp_label, 
                     self.humidity_label, self.pressure_label]:
            label.setStyleSheet("color: gray;")
        
        self.instrument_status.setStyleSheet("color: gray; font-weight: bold; font-size: 12px;")
        self.quality_label.setStyleSheet("color: gray;")
        
        # Reset progress bar
        self.status_progress.setValue(0)
        
        logger.info("Status display cleared")

    def get_fume_limit_value(self) -> Optional[float]:
        """Get the current exhaust fume limit value for export.
        
        Returns:
            Fume limit value in mg/m³ or None if not available
        """
        if (self.current_measurement and 
            self.current_measurement.co_concentration is not None and
            self.current_measurement.o2_concentration is not None and
            self.current_measurement.o2_concentration < 21.0):
            
            fume_limit = (self.current_measurement.co_concentration * 1.25 * 
                         ((21 - 13) / (21 - self.current_measurement.o2_concentration)))
            return fume_limit
        return None
    
    def get_air_quality_status(self) -> str:
        """Get the current air quality status for export.
        
        Returns:
            Air quality status string
        """
        if self.air_quality_label:
            return self.air_quality_label.text()
        return "Unknown"
