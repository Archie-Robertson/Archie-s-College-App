#!/usr/bin/env python3
"""
Interactive CLI for course competition analysis with course selection dropdown.

Allows users to:
1. Select their college
2. Select which courses to analyze competitors for
3. Select geographic radius to filter competitors
4. Run matching and generate report
"""

import sys
from pathlib import Path
from colleges_config import MY_COLLEGES
from database import CollegeDatabase
from course_matcher import CourseMatcherAI
from importers import import_from_csv
import json
import math

# Use simple_term_menu if available, else fall back to manual selection
try:
    from simple_term_menu import TerminalMenu
    HAS_MENU = True
except ImportError:
    HAS_MENU = False


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in miles."""
    R = 3959  # Earth radius in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def print_header():
    """Print application header."""
    print("\n" + "="*80)
    print("  🎓 AI COURSE COMPETITION ANALYZER - Interactive Mode")
    print("="*80 + "\n")


def select_radius():
    """Interactive radius selection for geographic filtering."""
    print("🗺️  Step 2a: Select Search Radius")
    print("-" * 40)
    print("Filter competitors by distance from your college.\n")
    
    radius_options = [
        ("Within 50 miles", 50),
        ("Within 100 miles", 100),
        ("Within 250 miles", 250),
        ("Within 500 miles", 500),
        ("No radius limit (all)", None),
    ]
    
    labels = [r[0] for r in radius_options]
    
    if HAS_MENU:
        menu = TerminalMenu(labels, title="Search Radius:")
        idx = menu.show()
        if idx is None:
            return None
        return radius_options[idx][1]
    else:
        for i, (label, _) in enumerate(radius_options, 1):
            print(f"  {i}. {label}")
        
        choice = input("\nEnter number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        try:
            return radius_options[int(choice) - 1][1]
        except (ValueError, IndexError):
            print("Invalid choice, using no limit.")
            return None


def select_college():
    """Interactive college selection."""
    colleges = list(MY_COLLEGES.keys())
    
    if not colleges:
        print("❌ No colleges configured in colleges_config.py")
        sys.exit(1)
    
    print("📍 Step 1: Select Your College")
    print("-" * 40)
    
    if HAS_MENU and len(colleges) > 1:
        menu = TerminalMenu(colleges, title="Available Colleges:")
        idx = menu.show()
        if idx is None:
            print("Cancelled.")
            sys.exit(0)
        college_id = colleges[idx]
    else:
        for i, c in enumerate(colleges, 1):
            print(f"  {i}. {c}")
        choice = input("\nEnter number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        try:
            college_id = colleges[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            sys.exit(1)
    
    college = MY_COLLEGES[college_id]
    print(f"✓ Selected: {college.get('name', college_id)}\n")
    return college_id, college


def select_courses(college):
    """Interactive course selection for analysis."""
    all_courses = college.get('programs', [])
    
    if not all_courses:
        print("⚠️  No courses configured for this college.")
        return []
    
    print("\n📚 Step 2b: Select Courses to Analyze (for competition detection)")
    print("-" * 40)
    print(f"Available courses: {len(all_courses)}\n")
    
    # Suppress logging during menu interaction
    import logging
    logging.getLogger('scraper').setLevel(logging.WARNING)
    logging.getLogger('course_matcher').setLevel(logging.WARNING)
    
    if HAS_MENU:
        # Multi-select using simple-term-menu (select with space, confirm with enter)
        menu_items = [f"✓ ALL COURSES ({len(all_courses)} total)"] + all_courses
        menu = TerminalMenu(
            menu_items,
            multi_select=True,
            show_multi_select_hint=True,
            title="Select courses to analyze (space to toggle, enter to confirm):"
        )
        selected_indices = menu.show()
        
        if selected_indices is None:
            print("Cancelled.")
            sys.exit(0)
        
        selected = []
        for idx in selected_indices:
            if idx == 0:  # "ALL COURSES" option
                selected = all_courses.copy()
                break
            else:
                selected.append(all_courses[idx - 1])
        
        if not selected:
            print("⚠️  No courses selected. Using all courses by default.")
            selected = all_courses.copy()
    else:
        # Fallback: manual selection
        print("Courses:")
        for i, course in enumerate(all_courses, 1):
            print(f"  {i}. {course}")
        print(f"  0. ALL COURSES")
        
        choice = input("\nEnter course number(s) comma-separated, or 0 for all (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        
        if choice == '0':
            selected = all_courses.copy()
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [all_courses[i] for i in indices if 0 <= i < len(all_courses)]
            except (ValueError, IndexError):
                print("Invalid choice.")
                sys.exit(1)
    
    print(f"\n✓ Selected {len(selected)} course(s) for analysis:")
    for course in selected:
        print(f"  • {course}")
    print()
    
    return selected


def run_analysis(college_id, college, selected_courses, radius_miles):
    """Run competition analysis on selected courses with geographic filtering."""
    
    # Re-enable logging for analysis phase
    import logging
    logging.getLogger('scraper').setLevel(logging.INFO)
    logging.getLogger('course_matcher').setLevel(logging.INFO)
    
    db = CollegeDatabase()
    
    # Clear previous results
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM comparison_results')
    cur.execute('DELETE FROM competitor_colleges')
    conn.commit()
    conn.close()
    
    # Import sample CSV if present
    csv_path = Path('sample_competitors.csv')
    if csv_path.exists():
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
        import_from_csv(str(csv_path), COLUMN_MAP, db)
        print(f"📥 Imported competitor data from {csv_path}\n")
    
    # Get competitors
    competitors = db.get_all_competitors()
    
    # Get your college location
    your_lat = college.get('latitude')
    your_lon = college.get('longitude')
    
    # Filter by radius if applicable
    filtered_competitors = []
    if radius_miles is not None and your_lat is not None and your_lon is not None:
        print(f"📍 Filtering competitors within {radius_miles} miles...\n")
        for comp in competitors:
            comp_lat = comp.get('latitude')
            comp_lon = comp.get('longitude')
            if comp_lat is not None and comp_lon is not None:
                distance = haversine_distance(your_lat, your_lon, comp_lat, comp_lon)
                if distance <= radius_miles:
                    filtered_competitors.append((comp, distance))
    else:
        # No radius limit
        filtered_competitors = [(comp, None) for comp in competitors]
    
    if not filtered_competitors:
        print("⚠️  No competitors found within the selected radius.\n")
        return
    
    competitor_urls = [c[0].get('source_url') for c in filtered_competitors if c[0].get('source_url')]
    
    print(f"📊 Analysis: {len(competitor_urls)} competitors found, {len(selected_courses)} courses")
    if radius_miles:
        print(f"🗺️  Radius: {radius_miles} miles\n")
    print("=" * 80)
    
    # Run matcher with selected courses
    matcher = CourseMatcherAI()
    
    print("\n🔍 Step 3: Scraping Competitor Websites...")
    print("-" * 40)
    
    # Detect courses from competitors (using all their programs, not filtered yet)
    competitor_programs = {}
    competitor_distances = {}
    for comp, distance in filtered_competitors:
        url = comp.get('source_url')
        comp_name = comp.get('name') or url
        result = matcher.scraper.scrape_college(url)
        if result:
            name = result.get('name') or comp_name
            programs = result.get('programs', [])
            competitor_programs[name] = programs
            if distance is not None:
                competitor_distances[name] = distance
    
    # Match selected courses against competitor programs
    print("\n🔄 Step 4: Matching Selected Courses...")
    print("-" * 40)
    
    report = {
        'college_id': college_id,
        'college_name': college.get('name', college_id),
        'college_location': college.get('location'),
        'selected_courses': selected_courses,
        'radius_miles': radius_miles,
        'analysis_timestamp': __import__('datetime').datetime.now().isoformat(),
        'competitors': {}
    }
    
    for competitor_name, competitor_programs_list in competitor_programs.items():
        matches = matcher._find_exact_matches(selected_courses, competitor_programs_list)
        close_matches = matcher._find_close_matches(selected_courses, competitor_programs_list)
        
        competition_score = matcher._calculate_competition_score(
            len(matches),
            len(close_matches),
            len(selected_courses)
        )
        
        distance = competitor_distances.get(competitor_name)
        
        report['competitors'][competitor_name] = {
            'exact_matches': matches,
            'similar_matches': close_matches,
            'competition_score': competition_score,
            'distance_miles': distance,
            'competitor_total_programs': len(competitor_programs_list)
        }
    
    # Print summary
    print("\n📈 COMPETITION ANALYSIS RESULTS")
    print("=" * 80)
    print(f"College: {college.get('name', college_id)}")
    print(f"Courses Analyzed: {', '.join(selected_courses)}")
    if radius_miles:
        print(f"Search Radius: {radius_miles} miles")
    print(f"Competitors Found: {len(competitor_programs)}\n")
    
    # Sort by competition score
    sorted_competitors = sorted(
        report['competitors'].items(),
        key=lambda x: x[1]['competition_score'],
        reverse=True
    )
    
    for comp_name, comp_data in sorted_competitors:
        score = comp_data['competition_score']
        if score > 0.7:
            level = "🔴 VERY HIGH"
        elif score > 0.5:
            level = "🟠 HIGH"
        elif score > 0.3:
            level = "🟡 MEDIUM"
        else:
            level = "🟢 LOW"
        
        distance_str = ""
        if comp_data['distance_miles'] is not None:
            distance_str = f" ({comp_data['distance_miles']:.1f} mi)"
        
        print(f"\n{comp_name}{distance_str}")
        print(f"  Competition Level: {level} ({score:.1%})")
        print(f"  Exact Matches: {len(comp_data['exact_matches'])}")
        if comp_data['exact_matches']:
            for match in comp_data['exact_matches']:
                print(f"    ✓ {match}")
        
        if comp_data['similar_matches']:
            print(f"  Similar Courses: {len(comp_data['similar_matches'])}")
            for match in comp_data['similar_matches']:
                print(f"    ~ {match}")
    
    # Save report
    report_file = f"competition_report_{college_id}.json"
    with open(report_file, 'w') as fh:
        json.dump(report, fh, indent=2)
    print(f"\n💾 Report saved to: {report_file}\n")


def main():
    """Main interactive flow."""
    print_header()
    
    try:
        # Step 1: Select college
        college_id, college = select_college()
        
        # Step 2a: Select radius
        radius_miles = select_radius()
        if radius_miles is None:
            print("✓ Using all competitors (no radius limit)\n")
        else:
            print(f"✓ Selected: Within {radius_miles} miles\n")
        
        # Step 2b: Select courses
        selected_courses = select_courses(college)
        
        if not selected_courses:
            print("No courses selected.")
            sys.exit(0)
        
        # Step 3: Run analysis
        run_analysis(college_id, college, selected_courses, radius_miles)
        
        print("✅ Analysis complete!\n")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
