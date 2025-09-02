#!/usr/bin/env python3
"""Check if required tags are present in the database."""

import sqlite3

def check_required_tags():
    """Check if required tags are present in the database."""
    required_tags = [
        "CO_CONC", "O2_CONC", "AI_SAMPLE_TEMP", "AI_PUMP_FLOW", 
        "SV_USER_UNITS", "SV_O2GAS_USER_UNITS"
    ]
    
    try:
        conn = sqlite3.connect('tags.sqlite')
        cursor = conn.cursor()
        
        print("🔍 Checking required tags in database...")
        print("=" * 50)
        
        found_tags = []
        missing_tags = []
        
        for tag in required_tags:
            cursor.execute('SELECT Name FROM TagList WHERE Name = ?', (tag,))
            result = cursor.fetchone()
            
            if result:
                found_tags.append(tag)
                print(f"✅ {tag}")
            else:
                missing_tags.append(tag)
                print(f"❌ {tag}")
        
        print("\n📊 Summary:")
        print(f"  Found: {len(found_tags)}/{len(required_tags)}")
        print(f"  Missing: {len(missing_tags)}")
        
        if missing_tags:
            print(f"\n⚠️  Missing tags: {', '.join(missing_tags)}")
        else:
            print("\n🎉 All required tags are present!")
        
        # Also check total tag count
        cursor.execute('SELECT COUNT(*) FROM TagList')
        total_tags = cursor.fetchone()[0]
        print(f"\n📈 Total tags in database: {total_tags}")
        
        conn.close()
        return len(missing_tags) == 0
        
    except Exception as e:
        print(f"❌ Error checking tags: {e}")
        return False

if __name__ == "__main__":
    success = check_required_tags()
    exit(0 if success else 1)
