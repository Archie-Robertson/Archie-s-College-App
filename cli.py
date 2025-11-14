"""Interactive CLI for College Competition AI"""
import sys
from main import CollegeCompetitionAI
from utils import ReportGenerator, StrategyRecommender
import json

class InteractiveCLI:
    """Interactive command-line interface for the AI"""
    
    def __init__(self):
        self.ai = CollegeCompetitionAI()
        self.running = True
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("COLLEGE COMPETITION AI - MAIN MENU")
        print("="*60)
        print("1. Setup your college data")
        print("2. Add competitor colleges to analyze")
        print("3. Generate competition report")
        print("4. View detailed analysis")
        print("5. Export report (JSON/CSV)")
        print("6. Generate geographic map")
        print("7. Get strategic recommendations")
        print("8. Exit")
        print("="*60)
    
    def setup_college_data(self):
        """Interactive college data setup"""
        print("\n--- Setup Your College ---")
        
        college_data = {}
        college_data['name'] = input("College name: ").strip()
        college_data['location'] = input("Location (city, state): ").strip()
        
        # Parse programs
        programs_input = input("Programs (comma-separated): ").strip()
        college_data['programs'] = [p.strip() for p in programs_input.split(',')]
        
        # Parse numeric fields
        try:
            college_data['tuition'] = float(input("Tuition ($): ").strip() or 0)
            college_data['enrollment'] = int(input("Enrollment: ").strip() or 0)
            college_data['acceptance_rate'] = float(input("Acceptance rate (0-1): ").strip() or 0.5)
            college_data['avg_gpa'] = float(input("Average GPA: ").strip() or 3.5)
            college_data['avg_sat'] = float(input("Average SAT: ").strip() or 1200)
            college_data['avg_act'] = float(input("Average ACT: ").strip() or 26)
        except ValueError:
            print("Invalid number format. Using default values.")
            college_data['tuition'] = college_data.get('tuition', 0)
            college_data['enrollment'] = college_data.get('enrollment', 0)
            college_data['acceptance_rate'] = college_data.get('acceptance_rate', 0.5)
            college_data['avg_gpa'] = college_data.get('avg_gpa', 3.5)
            college_data['avg_sat'] = college_data.get('avg_sat', 1200)
            college_data['avg_act'] = college_data.get('avg_act', 26)
        
        college_data['metadata'] = {'setup_date': str(__import__('datetime').datetime.now())}
        
        self.ai.setup_my_college(college_data)
        print("✓ College data saved successfully!")
    
    def add_competitors(self):
        """Add competitor colleges"""
        print("\n--- Add Competitor Colleges ---")
        print("Enter URLs to analyze (one per line, empty line to finish):")
        
        urls = []
        while True:
            url = input(f"URL {len(urls) + 1}: ").strip()
            if not url:
                break
            urls.append(url)
        
        if urls:
            print(f"\nAnalyzing {len(urls)} colleges...")
            results = self.ai.analyze_competitors(urls)
            print(f"✓ Analysis complete! Processed {len(results)} colleges.")
    
    def generate_report(self):
        """Generate and display competition report"""
        print("\nGenerating competition report...")
        report = self.ai.get_competition_report()
        self.ai.print_report(report)
    
    def view_detailed_analysis(self):
        """View detailed analysis for competitors"""
        comparisons = self.ai.db.get_comparisons()
        
        if not comparisons:
            print("\nNo comparisons available. Please add competitors first.")
            return
        
        print(f"\nFound {len(comparisons)} comparisons:")
        for i, comp in enumerate(comparisons[:10], 1):
            print(f"{i}. {comp[-1]} (Similarity: {comp[2]:.2%})")
        
        try:
            choice = int(input("\nSelect number to view detailed analysis (0 to skip): ").strip() or 0)
            if 1 <= choice <= len(comparisons):
                print(f"\n{comparisons[choice-1][-2]}")
        except ValueError:
            pass
    
    def export_report(self):
        """Export report to file"""
        print("\n--- Export Report ---")
        print("1. Export as JSON")
        print("2. Export as CSV")
        print("0. Cancel")
        
        choice = input("\nSelect format: ").strip()
        
        report = self.ai.get_competition_report()
        
        if choice == '1':
            filename = ReportGenerator.export_to_json(report)
            print(f"✓ Report exported to {filename}")
        elif choice == '2':
            comparisons = self.ai.db.get_comparisons()
            filename = ReportGenerator.export_to_csv(comparisons)
            print(f"✓ Comparisons exported to {filename}")
    
    def get_recommendations(self):
        """Get strategic recommendations"""
        report = self.ai.get_competition_report()
        recommendations = StrategyRecommender.recommend_actions(report)
        
        print("\n--- Strategic Recommendations ---")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    def generate_geographic_map(self):
        """Generate and display geographic map"""
        print("\n--- Geographic Map Options ---")
        print("1. Google Maps (interactive, web-based)")
        print("2. Apple Maps (optimized for iOS/Mac)")
        print("3. OpenStreetMap/Folium (offline, lightweight)")
        print("0. Cancel")
        
        choice = input("\nSelect map type: ").strip()
        
        if choice == '0':
            return
        
        map_type_map = {
            '1': 'google',
            '2': 'apple',
            '3': 'folium'
        }
        
        map_type = map_type_map.get(choice, 'google')
        
        print(f"\nGenerating {map_type.title()} map of competitors...")
        map_html = self.ai.generate_geographic_map(map_type=map_type, save_html=True)
        print(f"✓ Map generated and saved to 'competition_map.html'")
        print("  Open this file in your web browser to view the map.")
    
    def run(self):
        """Run the interactive CLI"""
        print("\n" + "="*60)
        print("Welcome to College Competition AI")
        print("="*60)
        
        while self.running:
            self.display_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.setup_college_data()
            elif choice == '2':
                self.add_competitors()
            elif choice == '3':
                self.generate_report()
            elif choice == '4':
                self.view_detailed_analysis()
            elif choice == '5':
                self.export_report()
            elif choice == '6':
                self.generate_geographic_map()
            elif choice == '7':
                self.get_recommendations()
            elif choice == '8':
                print("\nThank you for using College Competition AI!")
                self.running = False
            else:
                print("Invalid option. Please try again.")


if __name__ == '__main__':
    cli = InteractiveCLI()
    cli.run()
