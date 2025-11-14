"""Main entry point for College Competition AI"""
import logging
from database import CollegeDatabase
from scraper import CollegeScraper
from analyzer import CompetitionAnalyzer
from geo_mapper import GeoMapper
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CollegeCompetitionAI:
    """Main AI system for analyzing college competition"""
    
    def __init__(self):
        self.db = CollegeDatabase()
        self.scraper = CollegeScraper()
        self.analyzer = CompetitionAnalyzer()
        self.mapper = GeoMapper()
    
    def setup_my_college(self, college_data: Dict):
        """Set up your college data in the database"""
        logger.info(f"Setting up college: {college_data.get('name')}")
        self.db.add_my_college(college_data)
        logger.info("College data stored successfully")
    
    def analyze_competitors(self, college_urls: List[str]) -> List[Dict]:
        """
        Scrape and analyze competitor colleges
        
        Args:
            college_urls: List of URLs to scrape
            
        Returns:
            List of analysis results
        """
        logger.info(f"Starting analysis of {len(college_urls)} competitor colleges")
        
        my_college = self.db.get_my_college()
        if not my_college:
            logger.error("Your college data not found. Please set it up first using setup_my_college()")
            return []
        
        # Get coordinates for your college
        my_college_coords = self.mapper.get_coordinates(my_college.get('location'))
        if my_college_coords:
            logger.info(f"Your college location: {my_college_coords}")
        
        results = []
        
        for i, url in enumerate(college_urls, 1):
            logger.info(f"Processing college {i}/{len(college_urls)}: {url}")
            
            # Scrape college data
            competitor_data = self.scraper.scrape_college(url)
            if not competitor_data:
                logger.warning(f"Could not scrape {url}")
                continue
            
            # Get geographic coordinates
            coords = self.mapper.get_coordinates(competitor_data.get('location'))
            if coords:
                competitor_data['latitude'] = coords[0]
                competitor_data['longitude'] = coords[1]
            
            # Store in database
            self.db.add_competitor(competitor_data)
            
            # Analyze competition (ONLY courses/programs focused)
            similarity_score, competition_level, analysis = self.analyzer.compare_colleges(
                my_college, 
                competitor_data
            )
            
            # Skip if not a real competitor (no program overlap)
            if competition_level == "NONE":
                logger.info(f"⊘ Skipped {competitor_data.get('name')} - No program overlap")
                continue
            
            # Store comparison results
            self.db.save_comparison(
                competitor_data['college_id'],
                similarity_score,
                competition_level,
                analysis
            )
            
            result = {
                'college_name': competitor_data.get('name', 'Unknown'),
                'location': competitor_data.get('location'),
                'coordinates': coords,
                'similarity_score': similarity_score,
                'competition_level': competition_level,
                'programs': competitor_data.get('programs', []),
                'analysis': analysis
            }
            results.append(result)
            
            logger.info(f"✓ Analyzed {competitor_data.get('name')} - Level: {competition_level}")
        
        return results
    
    def get_competition_report(self) -> Dict:
        """Generate a comprehensive competition report"""
        logger.info("Generating competition report")
        
        my_college = self.db.get_my_college()
        competitors = self.db.get_all_competitors()
        comparisons = self.db.get_comparisons()
        
        # Categorize by competition level
        high_competition = [c for c in comparisons if c[-3] == 'HIGH']
        medium_competition = [c for c in comparisons if c[-3] == 'MEDIUM']
        low_competition = [c for c in comparisons if c[-3] == 'LOW']
        
        report = {
            'my_college': my_college,
            'total_competitors_analyzed': len(competitors),
            'competition_summary': {
                'high_competition': len(high_competition),
                'medium_competition': len(medium_competition),
                'low_competition': len(low_competition),
            },
            'top_competitors': [
                {
                    'name': c[-1],
                    'similarity_score': c[2],
                    'competition_level': c[3],
                }
                for c in sorted(comparisons, key=lambda x: x[2], reverse=True)[:10]
            ],
            'all_comparisons': comparisons
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print competition report in human-readable format"""
        print("\n" + "="*80)
        print("COLLEGE COMPETITION ANALYSIS REPORT")
        print("="*80)
        
        if report['my_college']:
            college = report['my_college']
            print(f"\nYour College: {college.get('name')}")
            print(f"Location: {college.get('location')}")
            print(f"Enrollment: {college.get('enrollment'):,}" if college.get('enrollment') else "Enrollment: N/A")
            print(f"Tuition: ${college.get('tuition'):,.2f}" if college.get('tuition') else "Tuition: N/A")
        
        print(f"\n\nCompetition Summary:")
        print(f"Total Competitors Analyzed: {report['total_competitors_analyzed']}")
        print(f"  - High Competition: {report['competition_summary']['high_competition']}")
        print(f"  - Medium Competition: {report['competition_summary']['medium_competition']}")
        print(f"  - Low Competition: {report['competition_summary']['low_competition']}")
        
        print(f"\n\nTop 10 Competitors by Similarity:")
        for i, competitor in enumerate(report['top_competitors'], 1):
            print(f"\n{i}. {competitor['name']}")
            print(f"   Competition Level: {competitor['competition_level']}")
            print(f"   Similarity Score: {competitor['similarity_score']:.2%}")
        
        print("\n" + "="*80 + "\n")
    
    def generate_geographic_map(self, map_type: str = 'google', save_html: bool = False) -> str:
        """Generate geographic map of competitors
        
        Args:
            map_type: 'google', 'apple', or 'folium'
            save_html: Whether to save to file
            
        Returns:
            HTML string or URL
        """
        my_college = self.db.get_my_college()
        if not my_college:
            logger.error("Your college data not found")
            return ""
        
        # Get coordinates for your college
        my_location = my_college.get('location')
        my_coords = self.mapper.get_coordinates(my_location)
        
        if not my_coords:
            logger.error(f"Could not geocode your college location: {my_location}")
            return ""
        
        # Get all competitors with coordinates
        competitors = self.db.get_all_competitors()
        comparisons = self.db.get_comparisons()
        
        # Build comparison map
        comp_map = {c[1]: {
            'similarity': c[2],
            'level': c[3]
        } for c in comparisons}
        
        # Add coordinates and comparison data to competitors
        competitors_with_data = []
        for comp in competitors:
            comp_id = comp.get('college_id')
            coords = self.mapper.get_coordinates(comp.get('location'))
            
            if coords:
                competitors_with_data.append({
                    'name': comp.get('name'),
                    'location': comp.get('location'),
                    'coordinates': coords,
                    'similarity_score': comp_map.get(comp_id, {}).get('similarity', 0),
                    'competition_level': comp_map.get(comp_id, {}).get('level', 'UNKNOWN'),
                    'programs': comp.get('programs', [])
                })
        
        # Generate map
        try:
            map_html = self.mapper.generate_html_map(
                competitors_with_data,
                my_coords,
                my_college.get('name'),
                map_type=map_type
            )
            
            if save_html:
                filename = 'competition_map.html'
                with open(filename, 'w') as f:
                    f.write(map_html)
                logger.info(f"Map saved to {filename}")
            
            return map_html
        except Exception as e:
            logger.warning(f"Could not generate HTML map: {e}")
            # Fall back to text map
            return self.mapper.generate_distance_report(competitors_with_data, my_coords)


def example_usage():
    """Example usage of the College Competition AI"""
    
    # Initialize the AI
    ai = CollegeCompetitionAI()
    
    # Set up your college
    my_college_data = {
        'name': 'Your College Name',
        'location': 'Your City, State',
        'programs': ['Computer Science', 'Engineering', 'Business', 'Arts'],
        'tuition': 50000,
        'enrollment': 15000,
        'acceptance_rate': 0.25,
        'avg_gpa': 3.8,
        'avg_sat': 1450,
        'avg_act': 33,
        'metadata': {'founded': 1990, 'type': 'Private'}
    }
    
    ai.setup_my_college(my_college_data)
    
    # List of competitor colleges to analyze
    competitor_urls = [
        'https://www.example.com/college1',
        'https://www.example.com/college2',
        'https://www.example.com/college3',
    ]
    
    # Analyze competitors
    results = ai.analyze_competitors(competitor_urls)
    
    # Generate and print report
    report = ai.get_competition_report()
    ai.print_report(report)
    
    # Print detailed analysis for each
    logger.info("\n\nDetailed Analysis:")
    for result in results:
        print(f"\n{result['college_name']}")
        print(result['analysis'])


if __name__ == '__main__':
    example_usage()
