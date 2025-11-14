#!/usr/bin/env python3
"""
QUICK START - AI Course Competition Analyzer

TL;DR: This system lets you import your college's course data,
analyze competitors' websites, and get a report showing which
colleges compete with you based on shared courses.

Usage: 3 steps
"""

print("""
╔════════════════════════════════════════════════════════════════════════╗
║           AI COURSE COMPETITION ANALYZER - QUICK START                 ║
╚════════════════════════════════════════════════════════════════════════╝

WHAT IT DOES:
✓ Import your college's course database (CSV, SQLite, or SQL)
✓ Scrape competitor websites to find their courses
✓ Match courses and identify direct competitors
✓ Generate strategic competition reports

YOUR QUESTION: "Can I import my college's database and use AI to find 
competitors who offer the same courses?"

ANSWER: YES! ✅

════════════════════════════════════════════════════════════════════════

STEP 1: Add Your College's Courses
──────────────────────────────────

Edit: colleges_config.py

Add your college name, location, and list all courses offered

See colleges_config.py for format and examples

════════════════════════════════════════════════════════════════════════

STEP 2: Import Competitor Data
──────────────────────────────

Your college provides competitor list in Excel/CSV/Database

Code: See example_complete_workflow.py for full import example

Quick version:
    from importers import import_from_csv
    from database import CollegeDatabase
    
    db = CollegeDatabase()
    import_from_csv('competitors.csv', column_map, db)

════════════════════════════════════════════════════════════════════════

STEP 3: Run Competition Analysis
─────────────────────────────────

See example_complete_workflow.py for full code example

Quick version runs course matching and generates report
with competition scores and insights.

Output will show:
    Competition levels from Very High to Very Low
    With number of exact course matches

════════════════════════════════════════════════════════════════════════

QUICK TEST (Try Right Now)
──────────────────────────

Run with sample data:

    python test_course_matcher.py

This will:
1. Import 5 sample colleges
2. Analyze course competition
3. Show example report
4. Take ~10 seconds

════════════════════════════════════════════════════════════════════════

WHAT YOU GET
─────────────

Competition Report showing:

1. EXACT MATCHES
   ✓ Colleges that offer the same courses you do
   ✓ Direct competition indicator
   
2. SIMILAR COURSES  
   ✓ Keyword overlap (e.g., "Software Engineering" vs "Software Dev")
   ✓ Near-competitor identification

3. UNIQUE OFFERINGS
   ✓ Their courses you don't offer → opportunities to add
   ✓ Your courses they don't → competitive advantages

4. COMPETITION SCORES
   ✓ 0-100% match percentage
   ✓ Competition level classification
   ✓ Prioritized list of threats

════════════════════════════════════════════════════════════════════════

EXAMPLE OUTPUT
───────────────

YOUR COLLEGE: North Notts College
Courses: Computer Science, Business, Engineering

COMPETITOR ANALYSIS:

📍 Harvard University
   Competition Level: VERY HIGH (65% match)
   Exact Matches: 3 courses
   Similar Courses: 2
   Unique to Them: Medicine, Law, Philosophy
   Unique to You: Digital Media

════════════════════════════════════════════════════════════════════════

DATA SOURCES SUPPORTED
───────────────────────

✓ CSV/Excel files
✓ SQLite databases (.db, .sqlite)
✓ MySQL databases
✓ PostgreSQL databases
✓ MSSQL databases

════════════════════════════════════════════════════════════════════════

FILES YOU GET
──────────────

Documentation:
  • COURSE_COMPETITION_SYSTEM.md - Full guide
  • COURSE_COMPETITION_GUIDE.md - Detailed instructions
  
Code:
  • course_matcher.py - AI matching engine
  • example_complete_workflow.py - Full example
  • test_course_matcher.py - Test with sample data

════════════════════════════════════════════════════════════════════════

INTEGRATION WITH YOUR SYSTEM
──────────────────────────────

This system works with:
  ✓ Your existing course database
  ✓ Competitor website scraping
  ✓ Geographic mapping
  ✓ Competitive analysis reports
  ✓ Historical tracking

All data stored in SQLite for persistent analysis

════════════════════════════════════════════════════════════════════════

NEXT ACTION
───────────

1. Run test: python test_course_matcher.py
2. Review output to understand reports
3. Prepare your actual college data
4. Import and analyze

════════════════════════════════════════════════════════════════════════
""")

if __name__ == '__main__':
    input("Press Enter to continue...")
