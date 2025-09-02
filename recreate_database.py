#!/usr/bin/env python3
"""
Dynamic Database Recreation Script

This script fetches the current tag list from the instrument's taglist endpoint
and recreates the data.sqlite database with all current tags and their metadata.
This ensures the database is always up-to-date with the instrument's firmware.
"""

import requests
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DynamicDatabaseRecreator:
    def __init__(self, instrument_ip="192.168.1.1", instrument_port="8180"):
        """Initialize the database recreator."""
        self.base_url = f"http://{instrument_ip}:{instrument_port}"
        self.taglist_url = f"{self.base_url}/api/taglist"
        self.db_path = "data.sqlite"
        
    def fetch_current_taglist(self):
        """Fetch the current taglist from the instrument's /api/taglist endpoint."""
        try:
            logger.info(f"Fetching current taglist from: {self.taglist_url}")
            response = requests.get(self.taglist_url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON content
            taglist_data = response.json()
            logger.info(f"Received taglist response with keys: {list(taglist_data.keys())}")
            
            # Extract tags array
            if 'tags' in taglist_data:
                tags = taglist_data['tags']
                logger.info(f"Found {len(tags)} tags in current taglist")
                return tags
            else:
                logger.error("No 'tags' key found in taglist response")
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch taglist: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing taglist: {e}")
            return None
    
    def backup_existing_database(self):
        """Backup the existing database if it exists."""
        if Path(self.db_path).exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"tags_backup_{timestamp}.sqlite"
            
            try:
                import shutil
                shutil.copy2(self.db_path, backup_path)
                logger.info(f"Backed up existing database to: {backup_path}")
                return backup_path
            except Exception as e:
                logger.warning(f"Failed to backup database: {e}")
                return None
        return None
    
    def create_database_structure(self):
        """Create the database structure with enhanced metadata fields."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Drop existing tables if they exist
            cursor.execute("DROP TABLE IF EXISTS TagValues")
            cursor.execute("DROP TABLE IF EXISTS TagList")
            
            # Create enhanced TagList table with all metadata fields
            cursor.execute("""
                CREATE TABLE TagList (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT UNIQUE NOT NULL,
                    Type TEXT,
                    Value TEXT,
                    Description TEXT,
                    TagGroup TEXT,
                    Units TEXT,
                    HmiLabel TEXT,
                    DefaultValue TEXT,
                    RawMin REAL,
                    RawMax REAL,
                    EuMin REAL,
                    EuMax REAL,
                    EuTag TEXT,
                    Precision INTEGER,
                    IsValueValid BOOLEAN,
                    IsReadOnly BOOLEAN,
                    IsNetwork BOOLEAN,
                    IsVisible BOOLEAN,
                    IsNonVolatile BOOLEAN,
                    IsDashboard BOOLEAN,
                    CanDashboard BOOLEAN,
                    CANNodeID INTEGER,
                    CANDataID INTEGER,
                    HmiValueMap TEXT,
                    Enums TEXT,
                    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create TagValues table
            cursor.execute("""
                CREATE TABLE TagValues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    TagName_id INTEGER NOT NULL,
                    Value TEXT,
                    DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Quality TEXT DEFAULT 'GOOD',
                    FOREIGN KEY (TagName_id) REFERENCES TagList (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tagvalues_tagname ON TagValues(TagName_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tagvalues_datetime ON TagValues(DateTime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_taglist_name ON TagList(Name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_taglist_group ON TagList(TagGroup)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_taglist_type ON TagList(Type)")
            
            conn.commit()
            logger.info("Enhanced database structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database structure: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def parse_properties(self, properties_str):
        """Parse the properties JSON string and extract all metadata."""
        try:
            if not properties_str:
                return {}
            
            # Handle both string and dict properties
            if isinstance(properties_str, str):
                props = json.loads(properties_str)
            else:
                props = properties_str
                
            return props
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse properties: {properties_str}")
            return {}
    
    def populate_tag_list(self, tags):
        """Populate the TagList table with all current tags and their metadata."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert all tags with their metadata
            for tag in tags:
                try:
                    # Extract basic tag info
                    name = tag.get('name', '')
                    tag_type = tag.get('type', '')
                    value = str(tag.get('value', ''))
                    
                    # Parse properties for metadata
                    properties = self.parse_properties(tag.get('properties', '{}'))
                    
                    # Extract all metadata fields
                    description = properties.get('Description', '')
                    tag_group = properties.get('Group', '')
                    units = properties.get('Units', '')
                    hmi_label = properties.get('HmiLabel', '')
                    default_value = str(properties.get('Default', ''))
                    
                    # Extract numeric ranges
                    raw_min = properties.get('RawMin')
                    raw_max = properties.get('RawMax')
                    eu_min = properties.get('EuMin')
                    eu_max = properties.get('EuMax')
                    eu_tag = properties.get('EuTag', '')
                    precision = properties.get('Precision')
                    
                    # Extract boolean flags
                    is_value_valid = properties.get('IsValueValid', False)
                    is_read_only = properties.get('IsReadOnly', False)
                    is_network = properties.get('IsNetwork', False)
                    is_visible = properties.get('IsVisible', False)
                    is_non_volatile = properties.get('IsNonVolatile', False)
                    is_dashboard = properties.get('IsDashboard', False)
                    can_dashboard = properties.get('CanDashboard', False)
                    
                    # Extract CAN bus info
                    can_node_id = properties.get('CANNodeID', -1)
                    can_data_id = properties.get('CANDataID', -1)
                    
                    # Extract HMI value mapping
                    hmi_value_map = properties.get('HmiValueMap', '')
                    
                    # Extract enums if present
                    enums = properties.get('Enums', [])
                    enums_json = json.dumps(enums) if enums else ''
                    
                    # Insert tag with all metadata
                    cursor.execute("""
                        INSERT INTO TagList (
                            Name, Type, Value, Description, TagGroup, Units, HmiLabel, DefaultValue,
                            RawMin, RawMax, EuMin, EuMax, EuTag, Precision,
                            IsValueValid, IsReadOnly, IsNetwork, IsVisible, IsNonVolatile, IsDashboard, CanDashboard,
                            CANNodeID, CANDataID, HmiValueMap, Enums
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name, tag_type, value, description, tag_group, units, hmi_label, default_value,
                        raw_min, raw_max, eu_min, eu_max, eu_tag, precision,
                        is_value_valid, is_read_only, is_network, is_visible, is_non_volatile, is_dashboard, can_dashboard,
                        can_node_id, can_data_id, hmi_value_map, enums_json
                    ))
                    
                except sqlite3.IntegrityError:
                    # Tag already exists (shouldn't happen with fresh DB)
                    logger.warning(f"Tag {name} already exists")
                except Exception as e:
                    logger.warning(f"Failed to insert tag {name}: {e}")
            
            conn.commit()
            logger.info(f"Successfully inserted {len(tags)} tags with metadata into TagList")
            return True
            
        except Exception as e:
            logger.error(f"Failed to populate tag list: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def verify_database(self):
        """Verify the database was created correctly."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check TagList count
            cursor.execute("SELECT COUNT(*) FROM TagList")
            tag_count = cursor.fetchone()[0]
            
            # Check TagValues table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TagValues'")
            tagvalues_exists = cursor.fetchone() is not None
            
            # Check database file size
            db_size = Path(self.db_path).stat().st_size
            
            # Get sample of tags with metadata
            cursor.execute("SELECT Name, Type, Description, Units, TagGroup FROM TagList LIMIT 5")
            sample_tags = cursor.fetchall()
            
            conn.close()
            
            logger.info(f"Database verification:")
            logger.info(f"  - TagList records: {tag_count}")
            logger.info(f"  - TagValues table exists: {tagvalues_exists}")
            logger.info(f"  - Database file size: {db_size} bytes")
            logger.info(f"  - Sample tags: {sample_tags}")
            
            return tag_count > 0 and tagvalues_exists and db_size > 0
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False
    
    def recreate_database(self):
        """Main method to recreate the database."""
        logger.info("Starting dynamic database recreation with enhanced metadata...")
        
        # Step 1: Backup existing database
        backup_path = self.backup_existing_database()
        
        # Step 2: Fetch current taglist from instrument
        tags = self.fetch_current_taglist()
        if not tags:
            logger.error("Failed to fetch tags from instrument. Cannot proceed.")
            return False
        
        # Step 3: Create new database structure
        if not self.create_database_structure():
            logger.error("Failed to create database structure.")
            return False
        
        # Step 4: Populate with current tags and metadata
        if not self.populate_tag_list(tags):
            logger.error("Failed to populate tag list.")
            return False
        
        # Step 5: Verify database
        if not self.verify_database():
            logger.error("Database verification failed.")
            return False
        
        logger.info("✅ Enhanced database recreation completed successfully!")
        logger.info(f"📊 Total tags in database: {len(tags)}")
        logger.info(f"💾 Database file: {self.db_path}")
        logger.info(f"🔍 Rich metadata extracted: descriptions, ranges, units, flags, enums, etc.")
        
        if backup_path:
            logger.info(f"🔄 Backup saved as: {backup_path}")
        
        return True

def main():
    """Main function."""
    print("🔄 Enhanced Dynamic Database Recreation Tool")
    print("=" * 60)
    print("This tool uses local tag_list.json to recreate the database with rich metadata")
    print("including descriptions, ranges, units, flags, enums, and more!")
    print("=" * 60)
    
    # Use local tag_list.json file
    tag_list_path = "notatki/tag_list.json"
    
    if not Path(tag_list_path).exists():
        print(f"❌ ERROR: {tag_list_path} not found!")
        return 1
    
    print(f"📁 Using local tag list file: {tag_list_path}")
    
    # Create recreator and run
    recreator = DynamicDatabaseRecreator("192.168.1.1", "8180")
    
    # Override the fetch method to use local file
    def fetch_from_local_file(self):
        """Fetch tags from local JSON file instead of API."""
        try:
            with open(tag_list_path, 'r') as f:
                data = json.load(f)
                tags = data.get('tags', [])
                logger.info(f"Loaded {len(tags)} tags from local file")
                return tags
        except Exception as e:
            logger.error(f"Failed to load local tag list: {e}")
            return None
    
    # Replace the fetch method
    recreator.fetch_current_taglist = lambda: fetch_from_local_file(recreator)
    
    if recreator.recreate_database():
        print("\n✅ SUCCESS: Enhanced database has been recreated with local tag data!")
        print("💡 Rich metadata has been extracted and stored for future use.")
        print("💡 You can now start the data collection service to begin harvesting data.")
    else:
        print("\n❌ FAILED: Database recreation failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
