"""
Run full analysis: import -> detect -> match -> save report + map

This script:
 - Clears previous competitor and comparison data
 - Imports `sample_competitors.csv` using the standard column map
 - Runs the CourseMatcherAI to generate a report for `college_1`
 - Saves the report to `competition_report.json`
 - Generates a geographic map (folium) and saves `competition_map.html`
"""
import json
from importers import import_from_csv
from course_matcher import CourseMatcherAI
from database import CollegeDatabase
from main import CollegeCompetitionAI
from pathlib import Path

# Column map used by examples
COLUMN_MAP = {
    'college_id': 'id',
    'name': 'name',
    'location': 'city',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'programs': 'programs_list',
    'enrollment': 'students',
    'tuition': 'tuition_usd',
    'source_url': 'website',
    'avg_sat': 'avg_sat',
}

REPORT_JSON = 'competition_report.json'
MAP_HTML = 'competition_map.html'


def clear_database(db: CollegeDatabase):
    """Remove previous competitor and comparison results"""
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM comparison_results')
    cur.execute('DELETE FROM competitor_colleges')
    conn.commit()
    conn.close()


def main():
    db = CollegeDatabase()

    # Clear previous results to keep runs idempotent
    clear_database(db)

    # Import sample CSV if present
    csv_path = Path('sample_competitors.csv')
    if csv_path.exists():
        import_from_csv(str(csv_path), COLUMN_MAP, db)
        print(f"Imported {csv_path}")
    else:
        print("No sample CSV found, skipping import")

    # Run matcher
    matcher = CourseMatcherAI()
    competitor_urls = [c.get('source_url') for c in db.get_all_competitors() if c.get('source_url')]

    report = matcher.generate_competition_report('college_1', competitor_urls)

    # Save report JSON
    with open(REPORT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)
    print(f"Saved report -> {REPORT_JSON}")

    # Generate geographic map using main AI wrapper (falls back to textual if missing coords)
    ai = CollegeCompetitionAI()
    map_html = ai.generate_geographic_map(map_type='folium', save_html=True)
    # generate_geographic_map already saves when save_html=True
    print(f"Saved map -> {MAP_HTML} (if folium available and coords present)")


if __name__ == '__main__':
    main()
