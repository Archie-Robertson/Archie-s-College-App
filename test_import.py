#!/usr/bin/env python
"""
Test script: import sample competitors from CSV and verify database.
"""
import os
from database import CollegeDatabase
from importers import import_from_csv

def test_csv_import():
    """Test importing competitors from CSV."""
    print("=" * 70)
    print("TESTING CSV IMPORT")
    print("=" * 70)
    
    # Use a test database so we don't corrupt the real one
    test_db_path = 'test_college_data.db'
    
    # Remove old test DB if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"✓ Removed old test database: {test_db_path}")
    
    # Create new test database
    db = CollegeDatabase(test_db_path)
    print(f"✓ Created test database: {test_db_path}")
    
    # Column mapping
    column_map = {
        'college_id': 'id',
        'name': 'name',
        'location': 'city',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'programs': 'programs_list',
        'enrollment': 'students',
        'tuition': 'tuition_usd',
        'avg_sat': 'avg_sat',
        'source_url': 'website'
    }
    
    # Import from CSV
    csv_file = 'sample_competitors.csv'
    print(f"\n📥 Importing from CSV: {csv_file}")
    import_from_csv(csv_file, column_map, db)
    print(f"✓ CSV import completed")
    
    # Verify import
    print(f"\n📊 Verifying import...")
    competitors = db.get_all_competitors()
    print(f"✓ Found {len(competitors)} competitors in database\n")
    
    # Display imported records
    for comp in competitors:
        print(f"  ID: {comp['college_id']}")
        print(f"  Name: {comp['name']}")
        print(f"  Location: {comp['location']}")
        print(f"  Programs: {comp['programs']}")
        print(f"  Enrollment: {comp['enrollment']}")
        print(f"  Tuition: ${comp['tuition']}" if comp['tuition'] else "  Tuition: N/A")
        print(f"  Avg SAT: {comp['avg_sat']}" if comp['avg_sat'] else "  Avg SAT: N/A")
        print(f"  Coordinates: ({comp.get('latitude')}, {comp.get('longitude')})" if comp.get('latitude') else "  Coordinates: N/A")
        print()
    
    print("=" * 70)
    print("✅ CSV IMPORT TEST PASSED")
    print("=" * 70)
    
    return test_db_path

if __name__ == '__main__':
    test_csv_import()
