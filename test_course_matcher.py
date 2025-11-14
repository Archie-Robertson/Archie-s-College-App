"""
TEST: Course Matcher AI with Sample Data

This demonstrates the complete workflow:
1. Import colleges from CSV
2. Extract their courses
3. Match against your college
4. Generate competition report
"""

import sys
from pathlib import Path
from course_matcher import CourseMatcherAI
from importers import import_from_csv
from database import CollegeDatabase

# Clean up old test database if it exists
test_db = "test_course_match.db"
if Path(test_db).exists():
    Path(test_db).unlink()

# Initialize
db = CollegeDatabase(db_path=test_db)
matcher = CourseMatcherAI()

print("""
╔════════════════════════════════════════════════════════════════════════╗
║         COURSE MATCHER AI - DEMO WITH SAMPLE DATA                     ║
╚════════════════════════════════════════════════════════════════════════╝
""")

# ============================================================================
# STEP 1: Import Sample Competitor Data
# ============================================================================
print("\n[STEP 1] Importing sample competitor colleges from CSV...")

csv_path = "sample_competitors.csv"
if Path(csv_path).exists():
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
    
    import_from_csv(csv_path, column_map, db)
    print(f"✓ CSV import successful")
    
    # Verify
    competitors = db.get_all_competitors()
    print(f"✓ Loaded {len(competitors)} competitor colleges")
    
    print("\nCompetitors loaded:")
    for comp in competitors:
        programs = comp.get('programs', [])
        print(f"  • {comp['name']}: {len(programs)} courses")
        if programs:
            print(f"    Courses: {', '.join(programs[:3])}")
            if len(programs) > 3:
                print(f"    ... and {len(programs) - 3} more")
else:
    print(f"✗ {csv_path} not found")
    print("  Run: python test_import.py  (first to create sample data)")
    sys.exit(1)

# ============================================================================
# STEP 2: Show Your College's Courses
# ============================================================================
print("\n" + "="*80)
print("[STEP 2] Your College Courses")
print("="*80)

your_courses = matcher.get_your_courses()

for college_id, courses in your_courses.items():
    college_name = matcher.your_colleges.get(college_id, {}).get('name', college_id)
    print(f"\n{college_name}:")
    if courses:
        print(f"  Total: {len(courses)} courses")
        print(f"  Courses: {', '.join(courses[:5])}")
        if len(courses) > 5:
            print(f"  ... and {len(courses) - 5} more")
    else:
        print("  No courses configured")

# ============================================================================
# STEP 3: Extract Courses from Competitor Data
# ============================================================================
print("\n" + "="*80)
print("[STEP 3] Extracting Competitor Courses")
print("="*80)

print("\n🔍 Analyzing competitor course offerings...\n")

# Get all competitors we just imported
competitors = db.get_all_competitors()
competitor_courses = {}

for comp in competitors:
    name = comp.get('name')
    programs = comp.get('programs', [])
    
    competitor_courses[name] = {
        'url': comp.get('source_url', 'N/A'),
        'raw_courses': programs,
        'normalized_courses': [p.lower().strip() for p in programs if p],
        'course_count': len(programs)
    }
    
    print(f"📍 {name}")
    print(f"   Courses found: {len(programs)}")
    if programs:
        print(f"   • {programs[0]}")
        if len(programs) > 1:
            print(f"   • {programs[1]}")
        if len(programs) > 2:
            print(f"   ... and {len(programs) - 2} more")
    print()

# ============================================================================
# STEP 4: Match Courses - The AI Algorithm
# ============================================================================
print("="*80)
print("[STEP 4] INTELLIGENT COURSE MATCHING")
print("="*80)

print("\nRunning AI course matching algorithm...")
print("  Comparing each competitor against your college")
print("  Finding: exact matches, similar courses, unique offerings\n")

# Run the matching
report = matcher.match_courses('college_1', competitor_courses)

# ============================================================================
# STEP 5: Display Results
# ============================================================================
print("="*80)
print("[STEP 5] COMPETITION ANALYSIS RESULTS")
print("="*80)

if report:
    # Print the formatted report
    matcher.print_report(report)
    
    # Additional metrics
    summary = report.get('summary', {})
    
    print("\n" + "="*80)
    print("[ANALYSIS] Key Findings")
    print("="*80)
    
    print(f"\n✓ Analyzed {summary.get('total_competitors_analyzed')} competitors")
    print(f"✓ Average course overlap: {summary.get('average_match_percentage', 0):.1f}%")
    
    if summary.get('biggest_competitors'):
        print(f"\n🏆 BIGGEST COMPETITOR TO MONITOR:")
        top_comp = summary['biggest_competitors'][0]
        print(f"   {top_comp['name']}")
        print(f"   Competition Score: {top_comp['score']:.1%}")
        print(f"   Exact Course Matches: {top_comp['matches']}")
    
    print("\n" + "="*80)
    print("[NEXT] What This Means")
    print("="*80)
    
    print("""
This analysis shows which colleges are your TRUE competitors based on
course offerings - not just size or location.

USE THIS DATA FOR:
  ✓ Marketing strategy - target different programs
  ✓ Course development - add unique offerings
  ✓ Pricing strategy - compete where you overlap
  ✓ Geographic focus - identify regional competitors
  ✓ Program quality improvements - see what others offer

EXAMPLE ACTION ITEMS:
  1. If High Competition: Review their course quality, pricing
  2. If Unique Courses: Market these as competitive advantages
  3. If Gap: Develop programs they don't offer
  4. Track Over Time: Re-run quarterly to monitor changes
    """)
    
else:
    print("✗ No report generated")

print("\n✓ Demo complete!")
print(f"  Database saved: {test_db}")
print("\n")
