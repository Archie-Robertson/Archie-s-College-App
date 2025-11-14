"""
Configuration file for your college network
Add your 3 colleges and their courses here
"""

# ============================================================================
# YOUR COLLEGES CONFIGURATION
# ============================================================================
# Add your college information below. Format:
# 'college_id': {
#     'name': 'College Name',
#     'location': 'City, State',
#     'latitude': 40.1234,          # Optional: auto-geocoded if not provided
#     'longitude': -71.5678,        # Optional: auto-geocoded if not provided
#     'enrollment': 15000,
#     'acceptance_rate': 0.25,
#     'avg_gpa': 3.8,
#     'avg_sat': 1450,
#     'avg_act': 33,
#     'tuition': 50000,
#     'programs': [
#         'Program 1',
#         'Program 2',
#         'Program 3',
#     ]
# }

MY_COLLEGES = {
    'college_1': {
        'name': 'North Notts College',
        'location': 'Worksop, UK',
        'programs': [
            'Computer Science',
            'Engineering',
            'Business',
            'Mathematics',
            'Data Science'
        ]
    },
    
    'college_2': {
        'name': 'City Central College',
        'location': 'Anytown, USA',
        'programs': [
            'Business',
            'Finance',
            'Accounting',
            'Economics'
        ]
    },
    
    'college_3': {
        'name': 'College Name 3',
        'location': 'City, State',
        'enrollment': 0,
        'acceptance_rate': 0.0,
        'avg_gpa': 0.0,
        'avg_sat': 0,
        'avg_act': 0,
        'tuition': 0,
        'programs': [
            'Biology',
            'Pre-Medicine',
            'Chemistry',
            'Computer Science'
        ]
    },
}

# ============================================================================
# COMPETITOR COLLEGES (Optional - for analysis)
# ============================================================================
# Add competitor colleges to analyze automatically
# These will be compared against your colleges' courses

COMPETITOR_COLLEGES = [
    {
        'name': 'Competitor College 1',
        'location': 'City, State',
        'url': 'https://competitor1.edu',
        'programs': [
            # Add their programs to compare
            # Example: 'Computer Science',
            # Example: 'Data Science',
        ]
    },
    {
        'name': 'Competitor College 2',
        'location': 'City, State',
        'url': 'https://competitor2.edu',
        'programs': [
            # Add their programs to compare
        ]
    },
    # Add more competitors as needed
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_your_colleges():
    """Get all your colleges"""
    return MY_COLLEGES


def get_college(college_id):
    """Get a specific college by ID"""
    return MY_COLLEGES.get(college_id)


def get_all_programs():
    """Get all programs across all your colleges"""
    all_programs = set()
    for college in MY_COLLEGES.values():
        all_programs.update(college.get('programs', []))
    return sorted(list(all_programs))


def get_college_programs(college_id):
    """Get programs for a specific college"""
    college = MY_COLLEGES.get(college_id)
    if college:
        return college.get('programs', [])
    return []


def get_program_overlap(college_id_1, college_id_2):
    """Calculate program overlap between two of your colleges"""
    programs_1 = set(get_college_programs(college_id_1))
    programs_2 = set(get_college_programs(college_id_2))
    
    if not programs_1 or not programs_2:
        return 0.0
    
    overlap = len(programs_1.intersection(programs_2))
    total = len(programs_1.union(programs_2))
    
    return (overlap / total * 100) if total > 0 else 0.0


def print_college_summary():
    """Print summary of all your colleges and programs"""
    print("\n" + "="*70)
    print("YOUR COLLEGE NETWORK SUMMARY")
    print("="*70)
    
    for college_id, college in MY_COLLEGES.items():
        print(f"\n{college.get('name')}")
        print(f"  Location: {college.get('location')}")
        # Safely format numeric fields (display N/A when missing)
        enrollment = college.get('enrollment')
        enrollment_text = f"{enrollment:,}" if isinstance(enrollment, int) and enrollment > 0 else "N/A"

        acceptance = college.get('acceptance_rate')
        acceptance_text = f"{acceptance:.1%}" if isinstance(acceptance, (int, float)) and acceptance > 0 else "N/A"

        avg_gpa = college.get('avg_gpa')
        avg_gpa_text = f"{avg_gpa:.2f}" if isinstance(avg_gpa, (int, float)) and avg_gpa > 0 else "N/A"

        avg_sat = college.get('avg_sat')
        avg_sat_text = f"{avg_sat}" if isinstance(avg_sat, int) and avg_sat > 0 else "N/A"

        avg_act = college.get('avg_act')
        avg_act_text = f"{avg_act}" if isinstance(avg_act, (int, float)) and avg_act > 0 else "N/A"

        tuition = college.get('tuition')
        tuition_text = f"${tuition:,}" if isinstance(tuition, (int, float)) and tuition > 0 else "N/A"

        print(f"  Enrollment: {enrollment_text}")
        print(f"  Acceptance Rate: {acceptance_text}")
        print(f"  Average GPA: {avg_gpa_text}")
        print(f"  Average SAT: {avg_sat_text}")
        print(f"  Average ACT: {avg_act_text}")
        print(f"  Tuition: {tuition_text}")
        print(f"  Programs: {len(college.get('programs', []))}")
        for program in college.get('programs', []):
            print(f"    • {program}")
    
    print("\n" + "-"*70)
    print(f"Total Unique Programs: {len(get_all_programs())}")
    print("="*70 + "\n")


def print_program_overlap():
    """Print program overlap between your colleges"""
    colleges = list(MY_COLLEGES.items())
    
    if len(colleges) < 2:
        print("Need at least 2 colleges to compare overlap")
        return
    
    print("\n" + "="*70)
    print("PROGRAM OVERLAP ANALYSIS")
    print("="*70)
    
    for i, (id1, college1) in enumerate(colleges):
        for id2, college2 in colleges[i+1:]:
            overlap = get_program_overlap(id1, id2)
            print(f"\n{college1['name']} ↔ {college2['name']}")
            print(f"  Overlap: {overlap:.1f}%")
            
            # Show shared programs
            progs1 = set(college1.get('programs', []))
            progs2 = set(college2.get('programs', []))
            shared = progs1.intersection(progs2)
            
            if shared:
                print(f"  Shared Programs: {', '.join(sorted(list(shared)))}")
    
    print("\n" + "="*70 + "\n")


# ============================================================================
# INTEGRATION WITH MAIN SYSTEM
# ============================================================================

def setup_colleges_in_database(ai):
    """
    Setup all your colleges in the database for analysis
    
    Usage:
        from main import CollegeCompetitionAI
        from colleges_config import setup_colleges_in_database
        
        ai = CollegeCompetitionAI()
        setup_colleges_in_database(ai)
    """
    from database import CollegeDatabase
    
    db = CollegeDatabase()
    
    print("Setting up your colleges in the database...")
    
    for college_id, college_data in MY_COLLEGES.items():
        # Add each college to competitors for analysis
        competitor_data = {
            'college_id': college_id,
            'name': college_data['name'],
            'location': college_data['location'],
            'programs': college_data['programs'],
            'tuition': college_data['tuition'],
            'enrollment': college_data['enrollment'],
            'acceptance_rate': college_data['acceptance_rate'],
            'avg_gpa': college_data['avg_gpa'],
            'avg_sat': college_data['avg_sat'],
            'avg_act': college_data['avg_act'],
            'metadata': {'is_your_college': True}
        }
        
        db.add_competitor(competitor_data)
        print(f"✓ Added {college_data['name']}")
    
    print("✓ All colleges loaded into database")


def analyze_your_colleges(ai):
    """
    Analyze program overlap between your colleges
    
    Usage:
        from main import CollegeCompetitionAI
        from colleges_config import analyze_your_colleges
        
        ai = CollegeCompetitionAI()
        analyze_your_colleges(ai)
    """
    print("\n" + "="*70)
    print("ANALYZING YOUR COLLEGE NETWORK")
    print("="*70)
    
    colleges = list(MY_COLLEGES.items())
    
    for i, (id1, college1) in enumerate(colleges):
        for id2, college2 in colleges[i+1:]:
            print(f"\nComparing: {college1['name']} ↔ {college2['name']}")
            
            # Analyze using the AI system
            similarity_score, competition_level, analysis = ai.analyzer.compare_colleges(
                college1,
                college2
            )
            
            print(f"Similarity: {similarity_score:.1%}")
            print(f"Competition Level: {competition_level}")
            print(f"\n{analysis}")
    
    print("\n" + "="*70 + "\n")


# ============================================================================
# QUICK START
# ============================================================================

if __name__ == '__main__':
    """
    Quick test - Run this file directly to see your configuration
    
    Usage:
        python colleges_config.py
    """
    
    print("\n" + "="*70)
    print("COLLEGE CONFIGURATION TESTER")
    print("="*70)
    
    # Show summary
    print_college_summary()
    
    # Show overlap analysis
    print_program_overlap()
    
    # Show all programs
    print("\nAll Programs Offered:")
    for program in get_all_programs():
        print(f"  • {program}")
    
    print("\n" + "="*70)
    print("Edit this file to add your colleges and courses!")
    print("="*70 + "\n")
