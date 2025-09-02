# Database Architecture Analysis

## Current Database Structure

### 1. **tags.sqlite** (Instrument Metadata & Data)
```
┌─────────────────────────────────────────────────────────────┐
│                    tags.sqlite                              │
├─────────────────────────────────────────────────────────────┤
│ TagList Table (807 rows)                                   │
│ ├─ id (PRIMARY KEY)                                        │
│ ├─ Name (TAG NAME)                                         │
│ ├─ Type (string, int, float, bool, enum)                  │
│ ├─ Value (CURRENT VALUE)                                   │
│ ├─ Description (HUMAN READABLE)                            │
│ ├─ TagGroup (CFG, LOG, TRIG, etc.)                        │
│ ├─ Units (%, HOURS, KB, etc.)                             │
│ ├─ RawMin/RawMax (RAW RANGES)                             │
│ ├─ EuMin/EuMax (ENGINEERING UNITS)                        │
│ ├─ IsReadOnly, IsNetwork, IsVisible (FLAGS)               │
│ ├─ CANNodeID, CANDataID (CAN BUS INFO)                    │
│ └─ Enums (AVAILABLE VALUES)                               │
├─────────────────────────────────────────────────────────────┤
│ TagValues Table (494 rows)                                │
│ ├─ id (PRIMARY KEY)                                        │
│ ├─ TagName_id (FOREIGN KEY → TagList.id)                  │
│ ├─ Value (MEASURED VALUE)                                  │
│ ├─ DateTime (TIMESTAMP)                                    │
│ └─ Quality (GOOD/BAD)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2. **data_store.sqlite** (Application Data)
```
┌─────────────────────────────────────────────────────────────┐
│                  data_store.sqlite                         │
├─────────────────────────────────────────────────────────────┤
│ measurements Table (75 rows)                              │
│ ├─ id (PRIMARY KEY)                                        │
│ ├─ timestamp (DATETIME)                                    │
│ ├─ co_concentration (REAL)                                 │
│ ├─ o2_concentration (REAL)                                 │
│ ├─ temperature (REAL)                                      │
│ ├─ humidity (REAL)                                         │
│ ├─ pressure (REAL)                                         │
│ ├─ instrument_status (TEXT)                                │
│ └─ created_at (TIMESTAMP)                                  │
├─────────────────────────────────────────────────────────────┤
│ tags Table (0 rows) - UNUSED                              │
│ ├─ id, name, description, unit, data_type, created_at     │
├─────────────────────────────────────────────────────────────┤
│ log_entries Table (0 rows) - UNUSED                       │
│ ├─ id, timestamp, level, message, source, created_at      │
└─────────────────────────────────────────────────────────────┘
```

## Problems Identified

### 1. **Why Two Separate Databases?**

**Historical Development:**
- `tags.sqlite` was created for the **data collection service** (CO_O2Analyser.py)
- `data_store.sqlite` was created for the **GUI application** (main_gui.py)
- **No coordination** between the two systems

**Current Issues:**
- **Data Duplication**: Same data stored in different formats
- **Inconsistency**: Different schemas for the same information
- **Maintenance Overhead**: Two databases to manage
- **Performance**: Unnecessary complexity

### 2. **data_store.sqlite Construction Problems**

**Wrong Schema Design:**
- **Fixed columns**: Only CO, O2, temperature, humidity, pressure
- **Missing flexibility**: Cannot store other instrument tags
- **Unused tables**: `tags` and `log_entries` tables are empty
- **Limited scalability**: Cannot add new measurement types

**Data Flow Issues:**
- **No relationship** to instrument tag metadata
- **Hardcoded fields** instead of dynamic tag system
- **Missing context** about what each measurement represents

### 3. **Data Flow Problems**

**Current Flow:**
```
Instrument → CO_O2Analyser.py → tags.sqlite (TagValues)
     ↓
GUI Application → data_store.sqlite (measurements)
```

**Issues:**
- **Two separate data paths**
- **No data synchronization**
- **Different data formats**
- **Missing real-time updates**

## Recommended Solution

### **Unified Database Architecture**

**Single Database: `tags.sqlite`**
- **TagList**: Instrument metadata (807 tags)
- **TagValues**: All measurement data (real-time)
- **Views**: Pre-defined views for GUI consumption

**Benefits:**
- **Single source of truth**
- **Real-time data access**
- **Consistent schema**
- **Better performance**
- **Easier maintenance**

### **Data Flow Redesign**

```
Instrument → /api/valuelist → CO_O2Analyser.py → tags.sqlite
     ↓
GUI Application ← tags.sqlite (real-time access)
```

**Implementation:**
1. **Remove data_store.sqlite**
2. **Modify GUI** to read from tags.sqlite
3. **Create views** for common queries
4. **Implement real-time updates**
