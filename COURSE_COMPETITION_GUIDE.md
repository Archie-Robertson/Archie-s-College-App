"""
COMPLETE COLLEGE COURSE COMPETITION ANALYSIS SYSTEM
====================================================

What This System Does:
1. Imports your college's course database (CSV, SQLite, or live SQL)
2. Imports competitor college data from multiple sources
3. Uses AI to analyze course overlap and competition
4. Maps competitors geographically
5. Generates strategic competitive analysis reports

====================================================================
ANSWER TO YOUR QUESTION:
"will this program allow me to give my colleges course database, use an ai 
to skim colleges websites and ping competition if they provide a same course"

YES - FULLY SUPPORTED
====================================================================

✅ YES - Import your college's database (CSV, SQLite, SQL)
✅ YES - Scrape competitor websites automatically  
✅ YES - Detect their courses using AI
✅ YES - Match against your courses
✅ YES - Flag direct competition ("ping")
✅ YES - Generate strategic insights


====================================================================
QUICK START - 3 STEPS
====================================================================

STEP 1: Add Your College's Courses
-----------------------------------

Edit colleges_config.py:

    MY_COLLEGES = {
        'college_1': {
            'name': 'Your College Name',
            'location': 'Your City, State',
            'programs': [
                'Computer Science',
                'Business Administration',
                'Engineering',
                'Mathematics',
                # Add all your courses here
            ]
        },
        'college_2': { ... },
        'college_3': { ... }
    }


STEP 2: Import Competitor Data
-------------------------------

From CSV file:
    from importers import import_from_csv
    from database import CollegeDatabase
    
    db = CollegeDatabase()
    
    column_map = {
        'college_id': 'id',
        'name': 'college_name',
        'location': 'location',
        'programs': 'courses',
        'enrollment': 'students',
        'tuition': 'annual_cost',
    }
    
    import_from_csv('your_colleges.csv', column_map, db)

From SQLite database:
    from importers import import_from_sqlite_file
    
    import_from_sqlite_file(
        'your_database.db',
        'colleges_table',
        column_map,
        db
    )

From Live Database (MySQL/PostgreSQL):
    from importers import import_via_sqlalchemy
    
    connection_string = 'mysql://user:pass@host/database'
    import_via_sqlalchemy(connection_string, 'colleges_table', column_map, db)


STEP 3: Run Course Competition Analysis
----------------------------------------

    from course_matcher import CourseMatcherAI
    
    matcher = CourseMatcherAI()
    
    # If you have website URLs in your data:
    competitor_urls = [
        'https://competitor1.edu',
        'https://competitor2.edu',
        'https://competitor3.edu',
    ]
    
    # Generate full report
    report = matcher.generate_competition_report('college_1', competitor_urls)
    
    # Display results
    matcher.print_report(report)


====================================================================
SYSTEM COMPONENTS
====================================================================

1. importers.py - Database Import
   ├─ import_from_csv()          - Read CSV files
   ├─ import_from_sqlite_file()  - Read SQLite files
   └─ import_via_sqlalchemy()    - Connect to live databases

2. course_matcher.py - AI Course Analysis
   ├─ detect_competitor_courses() - Scrape websites for courses
   ├─ match_courses()             - Compare against your courses
   ├─ _find_exact_matches()       - Exact course matches
   └─ _find_close_matches()       - Similar/related courses

3. database.py - Data Storage
   ├─ Stores imported competitor data
   ├─ Stores course matching results
   └─ Enables historical tracking

4. colleges_config.py - Your College Configuration
   └─ Define your college's courses here


====================================================================
HOW THE AI MATCHING WORKS
====================================================================

The system uses intelligent course matching:

1. EXACT MATCHES
   ✓ Harvard has "Computer Science" → You have "Computer Science"
   → This is direct competition (0.7-1.0 score)

2. CLOSE MATCHES (Keyword similarity)
   ✓ Harvard has "Software Engineering" → You have "Software Development"  
   → 60% keyword overlap → Similar competition (0.5-0.7 score)

3. UNIQUE COURSES
   ✓ They have courses you don't → Opportunities to add them
   ✓ You have courses they don't → Your competitive advantage

4. COMPETITION SCORING
   0.0-0.3:  LOW - Minimal overlap (⚪ Very Low)
   0.3-0.5:  MEDIUM - Some overlap (🟡 Medium)
   0.5-0.7:  HIGH - Significant overlap (🟠 High)
   0.7-1.0:  VERY HIGH - Direct competitor (🔴 Very High)


====================================================================
EXAMPLE: REAL WORKFLOW
====================================================================

Scenario: You have North Notts College and want to know about competitors

1. College gives you competitor data in Excel
   
2. Import into system:
   import_from_csv('competitors.csv', column_map, db)
   
3. Scrape their websites for courses:
   from course_matcher import CourseMatcherAI
   matcher = CourseMatcherAI()
   report = matcher.generate_competition_report('college_1', urls)
   
4. View results showing:
   ✓ Which competitors share your courses
   ✓ How many courses overlap
   ✓ Which competitors are true competitors vs. different focus
   ✓ What unique courses they offer
   ✓ What courses you offer that they don't
   
5. Use insights for:
   ✓ Marketing ("We offer X courses, competitor Y only offers Z")
   ✓ Strategy ("Add courses in high-demand areas")
   ✓ Pricing ("Align pricing with competitor value")
   ✓ Growth ("This niche has no competitors - opportunity!")


====================================================================
TESTING THE SYSTEM
====================================================================

We've included sample data to test:

1. Run the importer test:
   python test_import.py
   
2. Run the course matcher test:
   python test_course_matcher.py
   
3. Run the complete workflow:
   python example_complete_workflow.py

All tests use sample_competitors.csv with 5 colleges:
• Harvard University
• Stanford University  
• MIT
• UC Berkeley
• Yale University


====================================================================
YOUR COLLEGE'S DATABASE FORMAT
====================================================================

When your college provides the database, it can be:

CSV Format:
┌─────────┬──────────────────────────────────────────┐
│ id      │ name                  │ courses           │
├─────────┼──────────────────────────────────────────┤
│ C001    │ Harvard University    │ CS, ENG, BUS, MED │
│ C002    │ Stanford University   │ CS, ENG, BUS      │
└─────────┴──────────────────────────────────────────┘

SQLite Format:
CREATE TABLE colleges (
  id TEXT PRIMARY KEY,
  name TEXT,
  location TEXT,
  courses JSON,
  enrollment INTEGER,
  tuition REAL
);

The system handles:
✓ Different column names (you map them)
✓ Courses as comma-separated strings OR JSON arrays
✓ Missing data (NULL fields)
✓ Different data types (auto-converts)


====================================================================
ADVANCED FEATURES
====================================================================

1. GEOGRAPHIC MAPPING
   from main import CollegeCompetitionAI
   
   ai = CollegeCompetitionAI()
   ai.generate_geographic_map(map_type='folium', save_html=True)
   
   Creates interactive map with:
   ✓ Your college location
   ✓ Competitor locations
   ✓ Color-coded by competition level
   ✓ Clickable for details

2. HISTORICAL TRACKING
   # Run analysis monthly/quarterly
   # Compare competition scores over time
   # Identify emerging competitors
   # Track market changes

3. EXPORT RESULTS
   import json
   with open('analysis.json', 'w') as f:
       json.dump(report, f, indent=2)

4. LIVE DATABASE UPDATES
   # If college provides live database access
   # Can automatically sync competitor data
   # Real-time competition monitoring


====================================================================
COMMON WORKFLOWS
====================================================================

WORKFLOW 1: Initial Competitive Analysis
-------------------------------------------

Your college provides Excel spreadsheet of competitor list

$ python
>>> from importers import import_from_csv
>>> from course_matcher import CourseMatcherAI
>>> 
>>> # Import competitors
>>> column_map = {
...     'college_id': 'ID',
...     'name': 'Name',
...     'location': 'City',
...     'programs': 'Courses Offered',
...     'enrollment': 'Students'
... }
>>> import_from_csv('competitors.csv', column_map, db)
>>> 
>>> # Analyze
>>> matcher = CourseMatcherAI()
>>> report = matcher.generate_competition_report('college_1', urls)
>>> matcher.print_report(report)


WORKFLOW 2: Monthly Competition Update
---------------------------------------

Track changes in competitor offerings

$ python
>>> from database import CollegeDatabase
>>> db = CollegeDatabase()
>>> 
>>> # Get this month's competitors
>>> competitors = db.get_all_competitors()
>>> 
>>> # Compare with last month
>>> import json
>>> with open('last_month.json') as f:
>>>     last_month = json.load(f)
>>> 
>>> # Identify new courses, dropped courses
>>> # Alert if new competitor added


WORKFLOW 3: Quarterly Strategic Review
--------------------------------------

Full competitive landscape analysis

1. Import latest competitor data
2. Run course matching
3. Generate geographic map
4. Export results for board presentation
5. Identify strategic opportunities/threats


====================================================================
DATA PERSISTENCE
====================================================================

All analyzed data is stored in your database:

colleges_data.db (SQLite)
├─ my_college          - Your college(s)
├─ competitor_colleges - Imported competitors
└─ comparison_results  - Analysis results

Benefits:
✓ Historical tracking
✓ Trend analysis
✓ No need to re-import
✓ Can query/analyze further


====================================================================
TROUBLESHOOTING
====================================================================

Problem: "Column not found" error
Solution: Check column_map matches your CSV column names exactly

Problem: CSV imports but courses are empty
Solution: Make sure 'programs' column has data in expected format:
  ✓ "Computer Science, Engineering, Business" (comma-separated)
  ✓ '["Computer Science", "Engineering"]' (JSON array)

Problem: Website scraping fails
Solution: Some websites block scrapers. Provide course data directly
  in CSV/database format instead

Problem: No exact matches detected
Solution: Check that course names match closely (case-insensitive)
  "Computer Science" should match "computer science"


====================================================================
NEXT STEPS
====================================================================

1. Configure your college courses in colleges_config.py
2. Get your competitor data from college (CSV/DB)
3. Run import: python test_import.py
4. Run analysis: python test_course_matcher.py
5. Integrate into your workflow

For questions or customization:
- Review example_complete_workflow.py
- Check IMPORTING_EXTERNAL_DB.md for import details
- See course_matcher.py for algorithm details
"""
