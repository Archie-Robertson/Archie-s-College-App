"""
COMPLETE WORKFLOW: Import College Database + AI Course Matching

This example shows the full end-to-end process:
1. Import your college's course database (CSV, SQLite, or SQL)
2. Scrape competitor college websites automatically
3. Use AI to match courses and identify competition
4. Generate competitive analysis report
5. Map competitors geographically
"""

import logging
from pathlib import Path
from importers import import_from_csv, import_from_sqlite_file
from database import CollegeDatabase
from course_matcher import CourseMatcherAI
from main import CollegeCompetitionAI

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Cleaner output for demo
)
logger = logging.getLogger(__name__)


def example_full_workflow():
    """Complete workflow: import → scrape → match → report"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║        COLLEGE COMPETITION ANALYZER - COMPLETE WORKFLOW               ║
    ║                                                                        ║
    ║  This example demonstrates:                                           ║
    ║  1. Importing competitor college data from CSV/SQLite                 ║
    ║  2. Using AI to scrape competitor websites for courses                ║
    ║  3. Matching courses to identify direct competition                   ║
    ║  4. Generating competition analysis report                            ║
    ║  5. Storing everything in database for analysis                       ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize system
    print("\n[STEP 1] Initializing systems...")
    db = CollegeDatabase()
    ai_system = CollegeCompetitionAI()
    course_matcher = CourseMatcherAI()
    
    print("✓ Systems initialized\n")
    
    # ========================================================================
    # OPTION A: Import competitor data from CSV file
    # ========================================================================
    print("="*80)
    print("[STEP 2A] IMPORTING COMPETITOR DATA FROM CSV")
    print("="*80)
    
    csv_path = "sample_competitors.csv"
    
    if Path(csv_path).exists():
        print(f"\n📁 Found {csv_path}, importing...")
        
        # Define how to map CSV columns to our standard schema
        column_map = {
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
        
        try:
            import_from_csv(csv_path, column_map, db)
            print("✓ CSV import completed successfully")
            
            # Verify import
            competitors = db.get_all_competitors()
            print(f"✓ Loaded {len(competitors)} competitors into database")
            
            for comp in competitors[:3]:
                print(f"   - {comp['name']} ({comp['location']})")
            
        except Exception as e:
            print(f"✗ CSV import failed: {e}")
    else:
        print(f"⚠️  {csv_path} not found, skipping CSV import")
    
    # ========================================================================
    # OPTION B: Import from SQLite file
    # ========================================================================
    print("\n" + "="*80)
    print("[STEP 2B] IMPORTING COMPETITOR DATA FROM SQLITE")
    print("="*80)
    
    sqlite_path = "competitors.db"
    
    if Path(sqlite_path).exists():
        print(f"\n📁 Found {sqlite_path}, importing...")
        
        sqlite_column_map = {
            'college_id': 'id',
            'name': 'college_name',
            'location': 'city_state',
            'programs': 'majors_json',
            'enrollment': 'total_enrollment',
            'tuition': 'annual_tuition',
            'source_url': 'website_url',
        }
        
        try:
            import_from_sqlite_file(sqlite_path, 'colleges', sqlite_column_map, db)
            print("✓ SQLite import completed successfully")
        except Exception as e:
            print(f"⚠️  SQLite import not available: {e}")
    else:
        print(f"⚠️  {sqlite_path} not found, skipping SQLite import")
    
    # ========================================================================
    # STEP 3: Get competitor URLs from database
    # ========================================================================
    print("\n" + "="*80)
    print("[STEP 3] EXTRACTING COMPETITOR WEBSITES")
    print("="*80)
    
    print("\n🌐 Retrieving competitor website URLs from database...")
    competitors = db.get_all_competitors()
    
    # Extract URLs from database records
    competitor_urls = []
    for comp in competitors:
        source_url = comp.get('source_url')
        if source_url and source_url.startswith('http'):
            competitor_urls.append(source_url)
    
    if competitor_urls:
        print(f"✓ Found {len(competitor_urls)} competitor websites:")
        for url in competitor_urls[:3]:
            print(f"   • {url}")
        if len(competitor_urls) > 3:
            print(f"   ... and {len(competitor_urls) - 3} more")
    else:
        print("⚠️  No website URLs found in competitor data")
        print("Note: Provide source_url in your imported data for web scraping")
        # Use placeholder URLs for demo
        competitor_urls = [
            'https://www.example.com/college1',
            'https://www.example.com/college2',
        ]
    
    # ========================================================================
    # STEP 4: Use AI to scrape competitor websites and detect courses
    # ========================================================================
    print("\n" + "="*80)
    print("[STEP 4] AI COURSE DETECTION - SCRAPING COMPETITOR WEBSITES")
    print("="*80)
    
    print("\n🤖 Using AI to scrape competitor websites for course data...")
    print("   (This searches for course/program listings on their websites)")
    
    # This step will:
    # - Visit each competitor URL
    # - Parse HTML to find course offerings
    # - Extract program names
    # - Normalize course names
    print("\n   Scraping in progress...")
    print("   ⏳ (In production, this would take 10-60 seconds per site)")
    
    # ========================================================================
    # STEP 5: AI Course Matching - Compare courses
    # ========================================================================
    print("\n" + "="*80)
    print("[STEP 5] INTELLIGENT COURSE MATCHING")
    print("="*80)
    
    print("\n🔄 Matching detected courses against your college's courses...")
    print("   Identifying:")
    print("   • Exact course matches (direct competition)")
    print("   • Similar courses (keyword overlap)")
    print("   • Unique courses (opportunities/threats)")
    
    # Generate the course competition report
    if competitor_urls and len(competitor_urls) > 0:
        print("\n📊 Generating comprehensive report...")
        report = course_matcher.generate_competition_report('college_1', competitor_urls)
        
        # ====================================================================
        # STEP 6: Display Results
        # ====================================================================
        print("\n" + "="*80)
        print("[STEP 6] COURSE COMPETITION ANALYSIS RESULTS")
        print("="*80)
        
        if report:
            course_matcher.print_report(report)
            
            # ================================================================
            # STEP 7: Additional Analysis
            # ================================================================
            print("\n" + "="*80)
            print("[STEP 7] STRATEGIC INSIGHTS")
            print("="*80)
            
            summary = report.get('summary', {})
            
            if summary.get('very_high_competition', 0) > 0:
                print(f"\n⚠️  ALERT: You have {summary['very_high_competition']} direct competitors")
                print("   Recommendation: Review their course quality and pricing")
            
            if summary.get('average_match_percentage', 0) > 50:
                print("\n💡 High course overlap detected")
                print("   Recommendation: Differentiate through:")
                print("   • Course quality improvements")
                print("   • Unique specializations")
                print("   • Better industry partnerships")
            
            biggest_comps = summary.get('biggest_competitors', [])
            if biggest_comps:
                print(f"\n👁️  Top Competitor to Monitor: {biggest_comps[0]['name']}")
                print(f"   Match Score: {biggest_comps[0]['score']:.1%}")
                print(f"   Shared Courses: {biggest_comps[0]['matches']}")
    
    # ========================================================================
    # STEP 8: Data Persistence
    # ========================================================================
    print("\n" + "="*80)
    print("[STEP 8] DATA STORAGE & PERSISTENCE")
    print("="*80)
    
    print("\n💾 All results are stored in the database for:")
    print("   ✓ Historical comparison tracking")
    print("   ✓ Geographic mapping")
    print("   ✓ Future analysis and reporting")
    
    # Verify storage
    all_competitors = db.get_all_competitors()
    print(f"\n✓ Total competitors in database: {len(all_competitors)}")
    
    # ========================================================================
    # STEP 9: Integration Examples
    # ========================================================================
    print("\n" + "="*80)
    print("[NEXT STEPS] INTEGRATION OPTIONS")
    print("="*80)
    
    print("""
    Your data is now ready for advanced analysis:
    
    1. GEOGRAPHIC ANALYSIS
       from main import CollegeCompetitionAI
       ai = CollegeCompetitionAI()
       ai.generate_geographic_map(map_type='folium', save_html=True)
    
    2. DETAILED COMPETITION REPORTS
       report = ai.get_competition_report()
       ai.print_report(report)
    
    3. TRACK COMPETITION OVER TIME
       # Store current results, re-run analysis in 3 months
       # Compare competition scores to track market changes
    
    4. EXPORT FOR EXTERNAL ANALYSIS
       import json
       with open('competition_analysis.json', 'w') as f:
           json.dump(report, f, indent=2)
    """)


def example_with_custom_database():
    """Example: Import data from YOUR college's database"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║     USING YOUR COLLEGE'S DATABASE - STEP BY STEP                      ║
    ╚════════════════════════════════════════════════════════════════════════╝
    
    When your college provides their database:
    
    1. CSV FORMAT:
       If they provide an Excel/CSV file with columns:
       college_id, name, location, programs, enrollment, tuition
       
       Usage:
       from importers import import_from_csv
       from database import CollegeDatabase
       
       db = CollegeDatabase()
       column_map = {
           'college_id': 'ID',
           'name': 'College Name',
           'location': 'City/State',
           'programs': 'Courses',
           'enrollment': 'Students',
           'tuition': 'Annual Fee',
       }
       import_from_csv('college_data.csv', column_map, db)
    
    
    2. SQLITE DATABASE:
       If they provide a .db or .sqlite3 file
       
       Usage:
       from importers import import_from_sqlite_file
       from database import CollegeDatabase
       
       db = CollegeDatabase()
       column_map = {
           'college_id': 'college_id',
           'name': 'name',
           'location': 'location',
           'programs': 'programs_json',
           'enrollment': 'enrollment',
           'tuition': 'tuition',
       }
       import_from_sqlite_file('their_database.db', 'table_name', column_map, db)
    
    
    3. LIVE DATABASE CONNECTION (Optional):
       If they allow direct database access (MySQL, PostgreSQL)
       
       Usage:
       from importers import import_via_sqlalchemy
       from database import CollegeDatabase
       
       db = CollegeDatabase()
       connection_string = 'mysql://user:password@host:3306/database_name'
       import_via_sqlalchemy(connection_string, 'colleges_table', column_map, db)
    """)


if __name__ == '__main__':
    # Run the full workflow
    example_full_workflow()
    
    # Uncomment to see instructions for your own database:
    # print("\n\n")
    # example_with_custom_database()
