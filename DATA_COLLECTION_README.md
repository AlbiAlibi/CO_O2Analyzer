# CO_O2Analyser Data Collection System

This document explains the new data collection architecture for the CO_O2Analyser system.

## Overview

The system has been refactored to separate data collection from data consumption:

1. **`CO_O2Analyser.py`** - Runs as a separate process, collects data from Teledyne N300M analyzer
2. **`instrument_communication.py`** - Harvests data from the local SQLite database
3. **Main application** - Uses the instrument communication module to get data

## Architecture

```
Teledyne N300M → CO_O2Analyser.py → tags.sqlite → instrument_communication.py → Main App
```

### Data Collection Service (`CO_O2Analyser.py`)

- **Runs independently** as a background service
- **Collects status data** every 10 minutes from `/api/valuelist`
- **Collects concentration data** every 2 seconds from individual tag endpoints
- **Stores all data** in `tags.sqlite` database
- **Full logging** to `logs/co_o2_analyser.log`
- **Configuration-driven** from `config.json`

### Data Harvesting (`instrument_communication.py`)

- **Reads from local database** instead of making HTTP requests
- **Fast data access** without network latency
- **Fallback to simulation** if database unavailable
- **Historical data access** for trends and analysis

## Configuration

The system uses `config.json` for configuration:

```json
{
  "instrument": {
    "ip_address": "192.168.1.100",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3,
    "simulation_mode": false,
    "tags": {
      "concentration_tags": ["CO_CONC", "O2_CONC"],
      "instrument_status": ["INSTRUMENT_TIME", "NETWORK_IP_ADDRESS"],
      "flow_tags": ["AI_PUMP_FLOW", "AI_SAMPLE_TEMP"],
      "temperature": ["AI_SAMPLE_TEMP", "AI_DETECTOR_TEMP"]
    }
  }
}
```

## Usage

### 1. Start Data Collection Service

```bash
# Option 1: Direct execution
python src/co_o2_analyser/core/CO_O2Analyser.py

# Option 2: Using startup script
python start_data_collector.py
```

### 2. Run Main Application

The main application will automatically use the database-harvesting mode when `simulation_mode` is `false`.

### 3. Monitor Data Collection

Check the logs:
```bash
tail -f logs/co_o2_analyser.log
```

Check database status:
```python
from src.co_o2_analyser.core.instrument_communication import InstrumentCommunication
from src.co_o2_analyser.utils.config import Config

config = Config()
comm = InstrumentCommunication(config)
status = comm.get_database_status()
print(status)
```

## Database Schema

### TagList Table
- `id`: Primary key
- `name`: Tag name (e.g., "CO_CONC", "O2_CONC")
- `type`: Data type
- `value`: Current value
- `properties`: JSON properties

### TagValues Table
- `id`: Primary key
- `TagName_id`: Foreign key to TagList
- `Value`: Tag value
- `DateTime`: Timestamp

## Data Flow

1. **Status Collection** (every 10 minutes):
   - Fetches from `/api/valuelist`
   - Stores all instrument status tags
   - Updates connection status

2. **Concentration Collection** (every 2 seconds):
   - Fetches from individual tag endpoints
   - Stores CO_CONC, O2_CONC values
   - High-frequency data for real-time monitoring

3. **Data Consumption**:
   - Main app reads from database
   - No network requests during normal operation
   - Fast response times

## Benefits

- **Separation of concerns**: Data collection vs. consumption
- **Reliability**: Local data storage, no network dependency during operation
- **Performance**: Fast database access vs. HTTP requests
- **Scalability**: Can run multiple consumers from same data source
- **Debugging**: Full logging and database inspection capabilities

## Troubleshooting

### Service Won't Start
- Check `config.json` exists and is valid
- Verify IP address and port are correct
- Check network connectivity to instrument

### No Data in Database
- Verify service is running: `ps aux | grep CO_O2Analyser`
- Check logs: `tail -f logs/co_o2_analyser.log`
- Verify database file exists: `ls -la tags.sqlite`

### Database Connection Issues
- Check file permissions on `tags.sqlite`
- Verify database integrity: `sqlite3 tags.sqlite ".schema"`
- Check available tags: `sqlite3 tags.sqlite "SELECT name FROM TagList;"`

## Migration from Old System

1. **Stop old system** if running
2. **Update configuration** in `config.json`
3. **Start new data collection service**
4. **Verify data is being collected**
5. **Start main application**

The main application will automatically detect the new architecture and use database harvesting instead of direct HTTP communication.
