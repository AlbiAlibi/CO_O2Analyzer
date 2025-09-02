# Database Setup and Management

This document describes the enhanced database setup functionality for the CO_O2Analyser project.

## Overview

The system now automatically creates and maintains a `tags.sqlite` database that contains rich metadata about all instrument tags, including:

- **Basic Information**: Name, Type, Current Value
- **Descriptions**: Human-readable descriptions of each tag
- **Units**: Measurement units (%, HOURS, KB, etc.)
- **Ranges**: Min/Max values (Raw and Engineering Units)
- **Groups**: Logical grouping (CFG, LOG, TRIG, etc.)
- **Flags**: Read-only, Network, Visible, Dashboard, etc.
- **Enums**: Available values for enum-type tags
- **CAN Bus**: Node ID and Data ID for CAN communication

## Automatic Database Setup

### At Startup

When you run `start_data_collector.py`, the system automatically:

1. **Checks Database**: Verifies if `tags.sqlite` exists and is recent (< 24 hours old)
2. **Creates/Updates**: If needed, fetches current tag list from instrument and creates/updates database
3. **Starts Collection**: Begins data collection service

### Manual Database Recreation

You can manually recreate the database anytime using:

```bash
python recreate_database.py
```

This will prompt for instrument IP and port, then fetch all current tags and recreate the database.

## Configuration

### Environment Variables

Set these environment variables to configure the instrument connection:

```bash
export INSTRUMENT_IP="192.168.1.1"
export INSTRUMENT_PORT="8180"
```

### Default Settings

- **IP Address**: 192.168.1.1
- **Port**: 8180
- **Endpoint**: `/api/taglist`

## Database Schema

### TagList Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| Name | TEXT | Tag name (unique) |
| Type | TEXT | Data type (string, int, float, bool, enum, event) |
| Value | TEXT | Current tag value |
| Description | TEXT | Human-readable description |
| TagGroup | TEXT | Logical grouping |
| Units | TEXT | Measurement units |
| HmiLabel | TEXT | HMI display label |
| DefaultValue | TEXT | Default value |
| RawMin | REAL | Raw minimum value |
| RawMax | REAL | Raw maximum value |
| EuMin | REAL | Engineering units minimum |
| EuMax | REAL | Engineering units maximum |
| Precision | INTEGER | Decimal precision |
| IsValueValid | BOOLEAN | Value validity flag |
| IsReadOnly | BOOLEAN | Read-only flag |
| IsNetwork | BOOLEAN | Network accessible flag |
| IsVisible | BOOLEAN | HMI visibility flag |
| IsNonVolatile | BOOLEAN | Non-volatile storage flag |
| IsDashboard | BOOLEAN | Dashboard display flag |
| CanDashboard | BOOLEAN | Dashboard capability flag |
| CANNodeID | INTEGER | CAN bus node ID |
| CANDataID | INTEGER | CAN bus data ID |
| HmiValueMap | TEXT | HMI value mapping |
| Enums | TEXT | Available enum values (JSON) |
| CreatedAt | TIMESTAMP | Creation timestamp |

### TagValues Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| TagName_id | INTEGER | Foreign key to TagList |
| Value | TEXT | Tag value |
| DateTime | TIMESTAMP | Value timestamp |
| Quality | TEXT | Data quality indicator |

## API Endpoint

The system fetches tag information from:

```
GET http://{instrument_ip}:{instrument_port}/api/taglist
```

### Response Format

```json
{
  "group": "",
  "tags": [
    {
      "name": "TAG_NAME",
      "type": "string|int|float|bool|enum|event",
      "value": "current_value",
      "properties": "{\"Description\":\"...\",\"Units\":\"...\",...}"
    }
  ]
}
```

## Testing

Test the database functionality with:

```bash
python test_database_recreation.py
```

This will create a test database with sample data and verify all functionality.

## Benefits

1. **Automatic Setup**: No manual database configuration needed
2. **Rich Metadata**: Access to all instrument tag information
3. **Always Current**: Database automatically updates with instrument firmware
4. **Comprehensive**: Captures descriptions, ranges, units, flags, and more
5. **Future-Proof**: Ready for advanced features like:
   - Tag filtering by group/type
   - Unit conversion
   - Range validation
   - Dashboard configuration
   - CAN bus integration

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check instrument IP and port
2. **JSON Parse Error**: Verify `/api/taglist` endpoint returns valid JSON
3. **Database Locked**: Ensure no other process is using the database
4. **Permission Denied**: Check write permissions in current directory

### Logs

Check the console output and logs for detailed error information. The system provides comprehensive logging for all operations.

## Example Usage

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('tags.sqlite')
cursor = conn.cursor()

# Get all tags with descriptions
cursor.execute("""
    SELECT Name, Description, Units, TagGroup 
    FROM TagList 
    WHERE Description != ''
    ORDER BY TagGroup, Name
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} ({row[2]}) - Group: {row[3]}")

conn.close()
```

This will output all tags with their descriptions, units, and groups for easy reference and analysis.
