#!/usr/bin/env python3
"""Check what CO and O2 related tags are in the database."""

import sqlite3

def check_co_o2_tags():
    """Check CO and O2 related tags in the database."""
    try:
        conn = sqlite3.connect('tags.sqlite')
        cursor = conn.cursor()
        
        print("🔍 Checking CO and O2 related tags in database...")
        print("=" * 50)
        
        # Check for CO related tags
        cursor.execute('SELECT Name FROM TagList WHERE Name LIKE "%CO%" LIMIT 10')
        co_tags = cursor.fetchall()
        
        print(f"\n📊 CO related tags (showing first 10):")
        for tag in co_tags:
            print(f"  {tag[0]}")
        
        # Check for O2 related tags
        cursor.execute('SELECT Name FROM TagList WHERE Name LIKE "%O2%" LIMIT 10')
        o2_tags = cursor.fetchall()
        
        print(f"\n📊 O2 related tags (showing first 10):")
        for tag in o2_tags:
            print(f"  {tag[0]}")
        
        # Check for exact matches
        exact_tags = ["CO_CONC", "O2_CONC", "CO_CONC", "O2_CONC"]
        print(f"\n🔍 Checking exact tag matches:")
        for tag in exact_tags:
            cursor.execute('SELECT Name FROM TagList WHERE Name = ?', (tag,))
            result = cursor.fetchone()
            if result:
                print(f"  ✅ {tag} found")
            else:
                print(f"  ❌ {tag} NOT found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_co_o2_tags()
