"""
Data models for CO_O2_Analyser.

This module contains the data structures used throughout the application.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Measurement:
    """Represents a single measurement from the instrument."""
    
    timestamp: datetime
    co_concentration: Optional[float] = None
    o2_concentration: Optional[float] = None
    sample_temp: Optional[float] = None
    sample_flow: Optional[float] = None
    instrument_status: Optional[str] = None
    error_code: Optional[int] = None
    warning_flags: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary for storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Measurement':
        """Create measurement from dictionary."""
        # Convert timestamp string back to datetime if needed
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Tag:
    """Represents a tag/parameter from the instrument."""
    
    id: int
    name: str
    type: str
    unit: str
    description: Optional[str] = None


@dataclass
class LogEntry:
    """Represents a log entry."""
    
    timestamp: datetime
    level: str
    message: str
    module: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
