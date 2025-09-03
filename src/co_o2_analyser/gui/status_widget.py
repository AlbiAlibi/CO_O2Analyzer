"""
Status widget for CO_O2_Analyser.

This module contains the status widget that displays
current measurement values and instrument status.
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QGridLayout, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor

from ..data.models import Measurement

logger = logging.getLogger(__name__)


class StatusWidget(QWidget):
    """Widget for displaying current status and measurements."""
    
    def __init__(self, config=None):
        """Initialize status widget."""
        super().__init__()
        self.current_measurement: Optional[Measurement] = None
        self.config = config
        
        self._init_ui()
        
        # Timer for status updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(2000)  # Update every 2 seconds to match CO/O2 data collection
        
        logger.info("Status widget initialized")
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # 1. Connection Status
        connection_group = QGroupBox("Connection Status")
        connection_layout = QVBoxLayout(connection_group)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_status)
        
        layout.addWidget(connection_group)
        
        # 2. Current Measurements
        measurements_group = QGroupBox("Current Measurements")
        measurements_layout = QGridLayout(measurements_group)
        
        # CO concentration
        measurements_layout.addWidget(QLabel("CO Concentration:"), 0, 0)
        self.co_label = QLabel("--")
        self.co_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        measurements_layout.addWidget(self.co_label, 0, 1)
        self.co_units_label = QLabel("ppm")  # Will be updated from database
        measurements_layout.addWidget(self.co_units_label, 0, 2)
        
        # O2 concentration
        measurements_layout.addWidget(QLabel("O₂ Concentration:"), 1, 0)
        self.o2_label = QLabel("--")
        self.o2_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        measurements_layout.addWidget(self.o2_label, 1, 1)
        self.o2_units_label = QLabel("%")  # Will be updated from database
        measurements_layout.addWidget(self.o2_units_label, 1, 2)
        
        # Temperature
        measurements_layout.addWidget(QLabel("Sample Temperature:"), 2, 0)
        self.temp_label = QLabel("--")
        measurements_layout.addWidget(self.temp_label, 2, 1)
        measurements_layout.addWidget(QLabel("°C"), 2, 2)
        
        # Pressure (Sample flow rate)
        measurements_layout.addWidget(QLabel("Sample flow rate:"), 3, 0)
        self.pressure_label = QLabel("--")
        measurements_layout.addWidget(self.pressure_label, 3, 1)
        measurements_layout.addWidget(QLabel("cc/min"), 3, 2)
        
        layout.addWidget(measurements_group)
        
        # 3. Exhaust Fume Limit
        fume_group = QGroupBox("Exhaust Fume Limit")
        fume_layout = QVBoxLayout(fume_group)
        
        # Fume limit value display
        self.fume_limit_label = QLabel("-- mg/m³")
        self.fume_limit_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.fume_limit_label.setToolTip("Normalized CO concentration corrected for oxygen content (21% O₂ reference). Used for regulatory compliance.")
        fume_layout.addWidget(self.fume_limit_label)
        
        # Air quality indicator
        self.air_quality_label = QLabel("Calculating...")
        self.air_quality_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        fume_layout.addWidget(self.air_quality_label)
        
        # Status progress bar
        self.status_progress = QProgressBar()
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        fume_layout.addWidget(self.status_progress)
        
        layout.addWidget(fume_group)
        
        # 4. Instrument Status (Combined all tags with different colors)
        instrument_group = QGroupBox("Instrument Status")
        instrument_layout = QGridLayout(instrument_group)
        
        # Store references to all instrument status labels
        self.instrument_labels = {}
        
        # Create instrument status sections with different colors
        self._create_instrument_status_sections(instrument_layout)
        
        layout.addWidget(instrument_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Display default tags from configuration if available
        if hasattr(self, 'config') and self.config:
            self.display_default_tags(self.config)
    
    def _create_instrument_status_sections(self, layout):
        """Create instrument status sections with different colors."""
        try:
            # Get tag groups from configuration
            if not hasattr(self, 'config') or not self.config:
                logger.warning("No configuration available for instrument status sections")
                return
            
            tags_config = self.config.get('instrument.tags', {})
            if not tags_config:
                logger.warning("No instrument tags in configuration")
                return
            
            row = 0
            
            # Define colors for different tag groups
            colors = {
                'instrument_status': 'blue',
                'warning_tags': 'red', 
                'flow_tags': 'green',
                'temperature': 'orange'
            }
            
            # Create sections for each tag group
            for group_name, tag_list in tags_config.items():
                if not tag_list or not isinstance(tag_list, list):
                    continue
                
                # Skip concentration_tags as they are handled by Current Measurements
                if group_name == 'concentration_tags':
                    continue
                
                # Get color for this group
                color = colors.get(group_name, 'black')
                
                # Create section header
                header_label = QLabel(f"{group_name.replace('_', ' ').title()}:")
                header_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
                layout.addWidget(header_label, row, 0)
                
                # Create value label for this section
                value_label = QLabel("--")
                value_label.setStyleSheet(f"color: {color}; font-size: 10px; font-family: monospace;")
                value_label.setWordWrap(True)
                layout.addWidget(value_label, row, 1)
                
                # Store reference
                self.instrument_labels[group_name] = value_label
                
                row += 1
                logger.info(f"Created instrument status section '{group_name}' with color {color}")
            
            logger.info(f"Created {len(self.instrument_labels)} instrument status sections")
            
        except Exception as e:
            logger.error(f"Failed to create instrument status sections: {e}")
    

    
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
                self._set_value_color(self.o2_label, measurement.o2_concentration, 18, 22, 25)
            else:
                self.o2_label.setText("--")
                self.o2_label.setStyleSheet("color: gray;")
            
            # Update temperature
            if measurement.sample_temp is not None:
                self.temp_label.setText(f"{measurement.sample_temp:.1f}")
                self._set_value_color(self.temp_label, measurement.sample_temp, 40, 60, 100)
            else:
                self.temp_label.setText("--")
                self.temp_label.setStyleSheet("color: gray;")
            
            # Update pressure
            if measurement.sample_flow is not None:
                self.pressure_label.setText(f"{measurement.sample_flow:.1f}")
                self._set_flow_color(self.pressure_label, measurement.sample_flow, 600, 700, 800)
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
            
            # Last update time removed - no longer displayed
            
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
    
    def update_instrument_tags(self, tags_data: dict):
        """Update instrument tags display.
        
        Args:
            tags_data: Dictionary containing instrument tags data
        """
        try:
            # Update Instrument Status Tags
            if 'instrument_status' in tags_data:
                status_tags = tags_data['instrument_status']
                if isinstance(status_tags, dict):
                    status_text = "\n".join([f"{key}: {value}" for key, value in status_tags.items()])
                else:
                    status_text = str(status_tags)
                self.instrument_status_tags_label.setText(status_text)
                self.instrument_status_tags_label.setStyleSheet("color: blue; font-size: 9px; font-family: monospace;")
            else:
                self.instrument_status_tags_label.setText("--")
                self.instrument_status_tags_label.setStyleSheet("color: gray;")
            
            # Update Order Tags
            if 'flow_tags' in tags_data:
                flow_tags = tags_data['flow_tags']
                if isinstance(flow_tags, dict):
                    flow_text = "\n".join([f"{key}: {value}" for key, value in flow_tags.items()])
                else:
                    flow_text = str(flow_tags)
                self.flow_tags_label.setText(flow_text)
                self.flow_tags_label.setStyleSheet("color: green; font-size: 9px; font-family: monospace;")
            else:
                self.flow_tags_label.setText("--")
                self.flow_tags_label.setStyleSheet("color: gray;")
            
            # Update Temperature Tags
            if 'temperature' in tags_data:
                temp_tags = tags_data['temperature']
                if isinstance(temp_tags, dict):
                    temp_text = "\n".join([f"{key}: {value}" for key, value in temp_tags.items()])
                else:
                    temp_text = str(temp_tags)
                self.temperature_tags_label.setText(temp_text)
                self.temperature_tags_label.setStyleSheet("color: orange; font-size: 9px; font-family: monospace;")
            else:
                self.temperature_tags_label.setText("--")
                self.temperature_tags_label.setStyleSheet("color: gray;")
                
            logger.debug(f"Instrument tags updated: {tags_data}")
            
        except Exception as e:
            logger.error(f"Failed to update instrument tags: {e}")
            # Reset all tag labels on error
            for label in [self.instrument_status_tags_label, self.flow_tags_label, self.temperature_tags_label]:
                label.setText("--")
                label.setStyleSheet("color: gray;")
    
    def display_default_tags(self, config):
        """Display default tags from configuration.
        
        Args:
            config: Configuration object containing instrument tags
        """
        try:
            tags = config.get('instrument.tags', {})
            
            # Initialize instrument status sections with default values
            for group_name, tag_list in tags.items():
                if group_name in getattr(self, 'instrument_labels', {}):
                    if group_name == 'warning_tags':
                        # Initialize warning tags with yellow text (UNKNOWN)
                        html_lines = []
                        for tag in tag_list:
                            html_line = f'{tag.replace("_", " ")}: <span style="color: yellow; font-weight: bold;">UNKNOWN</span>'
                            html_lines.append(html_line)
                        default_text = "<br>".join(html_lines)
                        self.instrument_labels[group_name].setText(default_text)
                    else:
                        # Initialize regular tags with default text
                        default_lines = [f"{tag}: --" for tag in tag_list]
                        default_text = "\n".join(default_lines)
                        self.instrument_labels[group_name].setText(default_text)
                    
                    logger.debug(f"Initialized {group_name} section with {len(tag_list)} tags")
            
            logger.debug("Default tags displayed from configuration")
            
        except Exception as e:
            logger.error(f"Failed to display default tags: {e}")
            # Reset all instrument labels on error
            for label in getattr(self, 'instrument_labels', {}).values():
                label.setText("--")
    
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
    
    def _set_flow_color(self, label: QLabel, value: float, low: float, mid: float, high: float):
        """Set label color for sample flow (reversed pattern).
        
        Args:
            label: Label to color
            value: Current value
            low: Low threshold (red below this - pipe locked)
            mid: Mid threshold (orange between low and mid - medium flow)
            high: High threshold (green above mid - good flow)
        """
        if value < low:
            color = "red"      # < 600: pipe locked
        elif value < mid:
            color = "orange"   # 600-700: medium flow
        else:
            color = "green"    # > 700: good flow
        
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
        
        # Note: This method is kept for compatibility but no longer used
        # as instrument status is now displayed via tags
        pass
    
    def _update_display(self):
        """Update the display (called by timer)."""
        try:
            # Update units from database
            self.update_units_from_database()
            
            # Update measurement values from database
            self.update_measurement_values_from_database()
            
            # Update instrument status sections from database
            self.update_instrument_status_sections_from_database()
            
        except Exception as e:
            logger.debug(f"Display update failed: {e}")
            # Continue with normal operation if database update fails
    
    def clear_display(self):
        """Clear all displayed values."""
        self.co_label.setText("--")
        self.o2_label.setText("--")
        self.temp_label.setText("--")
        self.pressure_label.setText("--")
        
        # Reset colors
        for label in [self.co_label, self.o2_label, self.temp_label, self.pressure_label]:
            label.setStyleSheet("color: gray;")
        
        # Clear instrument status sections
        for group_name, label in getattr(self, 'instrument_labels', {}).items():
            label.setText("--")
        
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
    
    def update_units_from_database(self):
        """Update measurement units from database configuration."""
        try:
            # Import here to avoid circular imports
            from ..core.data_harvester import SQLiteDataHarvester
            
            harvester = SQLiteDataHarvester()
            
            # Get CO units from SV_USER_UNITS
            co_units = harvester.get_latest_tag_value("SV_USER_UNITS")
            if co_units and co_units.get('value'):
                self.co_units_label.setText(co_units['value'])
                logger.debug(f"Updated CO units to: {co_units['value']}")
            
            # Get O2 units from SV_O2GAS_USER_UNITS
            o2_units = harvester.get_latest_tag_value("SV_O2GAS_USER_UNITS")
            if o2_units and o2_units.get('value'):
                self.o2_units_label.setText(o2_units['value'])
                logger.debug(f"Updated O2 units to: {o2_units['value']}")
                
        except Exception as e:
            logger.warning(f"Failed to update units from database: {e}")
            # Keep default units if database access fails
    
    def update_measurement_values_from_database(self):
        """Update measurement values from database."""
        try:
            # Import here to avoid circular imports
            from ..core.data_harvester import SQLiteDataHarvester
            
            harvester = SQLiteDataHarvester()
            
            # Get CO concentration from CO_CONC
            co_data = harvester.get_latest_tag_value("CO_CONC")
            if co_data and co_data.get('value') is not None:
                try:
                    co_value = float(co_data['value'])
                    # Use precision-based formatting (without units - shown separately)
                    formatted_co = harvester.format_tag_value("CO_CONC", co_value, include_units=False)
                    self.co_label.setText(formatted_co)
                    self._set_value_color(self.co_label, co_value, 0, 50, 100)
                    logger.debug(f"Updated CO concentration: {formatted_co}")
                except (ValueError, TypeError):
                    self.co_label.setText("--")
                    self.co_label.setStyleSheet("color: gray;")
            
            # Get O2 concentration from O2_CONC
            o2_data = harvester.get_latest_tag_value("O2_CONC")
            if o2_data and o2_data.get('value') is not None:
                try:
                    o2_value = float(o2_data['value'])
                    # Use precision-based formatting (without units - shown separately)
                    formatted_o2 = harvester.format_tag_value("O2_CONC", o2_value, include_units=False)
                    self.o2_label.setText(formatted_o2)
                    self._set_value_color(self.o2_label, o2_value, 18, 21, 25)
                    logger.debug(f"Updated O2 concentration: {formatted_o2}")
                    
                    # Last update time removed - no longer displayed
                except (ValueError, TypeError):
                    self.o2_label.setText("--")
                    self.o2_label.setStyleSheet("color: gray;")
            
            # Get temperature from AI_SAMPLE_TEMP
            temp_data = harvester.get_latest_tag_value("AI_SAMPLE_TEMP")
            if temp_data and temp_data.get('value'):
                try:
                    temp_value = float(temp_data['value'])
                    # Use precision-based formatting (without units - shown separately)
                    formatted_temp = harvester.format_tag_value("AI_SAMPLE_TEMP", temp_value, include_units=False)
                    self.temp_label.setText(formatted_temp)
                    self._set_value_color(self.temp_label, temp_value, 40, 60, 100)
                except (ValueError, TypeError):
                    self.temp_label.setText("--")
                    self.temp_label.setStyleSheet("color: gray;")
            
            # Get pressure/flow from AI_PUMP_FLOW
            flow_data = harvester.get_latest_tag_value("AI_PUMP_FLOW")
            if flow_data and flow_data.get('value'):
                try:
                    flow_value = float(flow_data['value'])
                    # Use precision-based formatting (without units - shown separately)
                    formatted_flow = harvester.format_tag_value("AI_PUMP_FLOW", flow_value, include_units=False)
                    self.pressure_label.setText(formatted_flow)
                    self._set_flow_color(self.pressure_label, flow_value, 600, 700, 800)
                except (ValueError, TypeError):
                    self.pressure_label.setText("--")
                    self.pressure_label.setStyleSheet("color: gray;")
                    
        except Exception as e:
            logger.warning(f"Failed to update measurement values from database: {e}")
            # Keep existing values if database access fails
    
    def update_instrument_status_sections_from_database(self):
        """Update instrument status sections from database."""
        try:
            # Import here to avoid circular imports
            from ..core.data_harvester import SQLiteDataHarvester
            
            harvester = SQLiteDataHarvester()
            
            # Update each instrument status section
            for group_name, label in getattr(self, 'instrument_labels', {}).items():
                # Get tags for this group from config
                tags_config = self.config.get('instrument.tags', {})
                tag_list = tags_config.get(group_name, [])
                
                if not tag_list:
                    continue
                
                # Special handling for warning tags - show colored dots instead of text
                if group_name == 'warning_tags':
                    self._update_warning_tags_with_dots(label, tag_list, harvester)
                else:
                    # Regular handling for other tag groups - show text values
                    self._update_regular_tags_with_text(label, tag_list, harvester)
                
                logger.debug(f"Updated instrument status section '{group_name}' with {len(tag_list)} tags")
                    
        except Exception as e:
            logger.warning(f"Failed to update instrument status sections from database: {e}")
            # Keep existing values if database access fails
    
    def _update_warning_tags_with_dots(self, label, tag_list, harvester):
        """Update warning tags with colored text only (no dots)."""
        try:
            # Create HTML content with colored text
            html_lines = []
            
            for tag_name in tag_list:
                tag_data = harvester.get_latest_tag_value(tag_name)
                if tag_data and tag_data.get('value') is not None:
                    value = tag_data['value']
                    warning_active = str(value).lower() in ['true', '1', 'yes', 'on']
                    
                    if warning_active:
                        # Red text for TRUE (warning active)
                        text_color = "red"
                        status_text = "WARNING"
                    else:
                        # Green text for FALSE (warning inactive)
                        text_color = "green"
                        status_text = "OK"
                else:
                    # Yellow text for UNKNOWN (no data)
                    text_color = "yellow"
                    status_text = "UNKNOWN"
                
                # Create HTML line with colored text only
                html_line = f'{tag_name.replace("_", " ")}: <span style="color: {text_color}; font-weight: bold;">{status_text}</span>'
                html_lines.append(html_line)
            
            # Set HTML content
            if html_lines:
                label.setText("<br>".join(html_lines))
            else:
                label.setText("--")
                
        except Exception as e:
            logger.warning(f"Failed to update warning tags with text: {e}")
            label.setText("--")
    
    def _update_regular_tags_with_text(self, label, tag_list, harvester):
        """Update regular tags with text values using precision formatting."""
        try:
            # Collect values for all tags in this group
            group_values = []
            for tag_name in tag_list:
                tag_data = harvester.get_latest_tag_value(tag_name)
                if tag_data and tag_data.get('value') is not None:
                    value = tag_data['value']
                    # Use precision-based formatting with units
                    formatted_value = harvester.format_tag_value(tag_name, value, include_units=True)
                    group_values.append(f"{tag_name}: {formatted_value}")
                else:
                    group_values.append(f"{tag_name}: --")
            
            # Update the label with all values
            if group_values:
                label.setText("\n".join(group_values))
            else:
                label.setText("--")
                
        except Exception as e:
            logger.warning(f"Failed to update regular tags with text: {e}")
            label.setText("--")
    

    



    
    def get_active_warnings_summary(self) -> dict:
        """Get a summary of all currently active warnings.
        
        Returns:
            Dictionary with warning status for each tag
        """
        try:
            # Import here to avoid circular imports
            from ..core.data_harvester import SQLiteDataHarvester
            
            harvester = SQLiteDataHarvester()
            warnings_summary = {}
            
            # Check each warning flag
            for tag_name in self.warning_labels.keys():
                tag_data = harvester.get_latest_tag_value(tag_name)
                if tag_data and tag_data.get('value') is not None:
                    warning_value = tag_data['value']
                    warning_active = str(warning_value).lower() in ['true', '1', 'yes', 'on']
                    warnings_summary[tag_name] = {
                        'active': warning_active,
                        'value': warning_value,
                        'timestamp': tag_data.get('timestamp')
                    }
                else:
                    warnings_summary[tag_name] = {
                        'active': False,
                        'value': None,
                        'timestamp': None
                    }
            
            return warnings_summary
            
        except Exception as e:
            logger.error(f"Failed to get warnings summary: {e}")
            return {}

    def discover_warning_tags(self) -> list[str]:
        """Get warning tags from configuration file.
        
        Returns:
            List of tag names from config, or empty list if not available.
        """
        try:
            # First try to get warning tags from configuration
            if hasattr(self, 'config') and self.config:
                config_tags = self.config.get('instrument.tags', {}).get('warning_tags', [])
                if config_tags:
                    logger.debug(f"Using {len(config_tags)} warning tags from configuration: {config_tags}")
                    return config_tags
            
            # Fallback to hardcoded list if no config available
            fallback_tags = [
                "BOX_TEMP_WARN",
                "BENCH_TEMP_WARN", 
                "WHEEL_TEMP_WARN",
                "LOW_MEMORY_WARNING",
                "SYS_INVALID_CONC_WARNING",
                "SF_O2_SENSOR_WARN_MALFUNCTION"
            ]
            logger.warning("No warning tags in configuration - using fallback list")
            return fallback_tags
            
        except Exception as e:
            logger.error(f"Failed to get warning tags from configuration: {e}")
            # Return fallback list on error
            return [
                "BOX_TEMP_WARN",
                "BENCH_TEMP_WARN", 
                "WHEEL_TEMP_WARN",
                "LOW_MEMORY_WARNING",
                "SYS_INVALID_CONC_WARNING",
                "SF_O2_SENSOR_WARN_MALFUNCTION"
            ]
    
    def refresh_warning_flags(self):
        """Refresh warning flags by reloading them from configuration.
        This allows dynamic addition/removal of warning flags when the configuration is updated.
        """
        try:
            logger.info("Refreshing warning flags from configuration...")
            
            # Get warning tags from configuration
            new_warning_tags = self.discover_warning_tags()
            
            if not new_warning_tags:
                logger.warning("No warning tags found in configuration - keeping existing configuration")
                return
            
            # Get the warning group widget
            warning_group = None
            for child in self.children():
                if isinstance(child, QGroupBox) and child.title() == "Warning Flags":
                    warning_group = child
                    break
            
            if not warning_group:
                logger.error("Warning Flags group not found")
                return
            
            # Clear existing warning flags
            for tag_name in list(self.warning_labels.keys()):
                if tag_name not in new_warning_tags:
                    # Remove this warning flag
                    if tag_name in self.warning_labels:
                        # Remove widgets from layout
                        warning_layout = warning_group.layout()
                        if warning_layout:
                            for i in reversed(range(warning_layout.count())):
                                item = warning_layout.itemAt(i)
                                if item.widget() in [self.warning_labels[tag_name]['dot'], 
                                                   self.warning_labels[tag_name]['text']]:
                                    warning_layout.removeItem(item)
                                    item.widget().deleteLater()
                        
                        # Remove from our tracking
                        del self.warning_labels[tag_name]
                        logger.info(f"Removed warning flag: {tag_name}")
            
            # Add new warning flags
            for tag_name in new_warning_tags:
                if tag_name not in self.warning_labels:
                    # Add new warning flag
                    warning_layout = warning_group.layout()
                    if warning_layout:
                        row = warning_layout.rowCount()
                        
                        # Warning name
                        warning_layout.addWidget(QLabel(f"{tag_name.replace('_', ' ')}:"), row, 0)
                        
                        # Status indicator (dot) - Yellow by default for UNKNOWN
                        status_dot = QLabel("●")
                        status_dot.setStyleSheet("color: yellow; font-size: 16px; font-weight: bold;")
                        status_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        warning_layout.addWidget(status_dot, row, 1)
                        
                        # Status text - UNKNOWN by default
                        status_text = QLabel("UNKNOWN")
                        status_text.setStyleSheet("color: yellow; font-weight: bold; font-size: 12px;")
                        warning_layout.addWidget(status_text, row, 2)
                        
                        # Store references
                        self.warning_labels[tag_name] = {
                            'dot': status_dot,
                            'text': status_text,
                            'has_real_data': False
                        }
                        
                        logger.info(f"Added new warning flag: {tag_name}")
            
            logger.info(f"Warning flags refreshed from configuration. Total: {len(self.warning_labels)}")
            
        except Exception as e:
            logger.error(f"Failed to refresh warning flags: {e}")
