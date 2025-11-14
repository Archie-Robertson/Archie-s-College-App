"""AI-powered course matching and competitor course detection.

This module uses AI to:
1. Scrape competitor websites for their course offerings
2. Match scraped courses against your college's database
3. Flag direct course competition
4. Suggest marketing strategies based on course overlap
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
import json
from colleges_config import MY_COLLEGES
from database import CollegeDatabase
from scraper import CollegeScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourseMatcherAI:
    """AI system for detecting and matching courses across colleges"""
    
    def __init__(self):
        self.db = CollegeDatabase()
        self.scraper = CollegeScraper()
        self.your_colleges = MY_COLLEGES
    
    def get_your_courses(self) -> Dict[str, List[str]]:
        """Get all courses offered by your colleges
        
        Returns:
            Dict mapping college_id to list of courses
        """
        your_courses = {}
        for college_id, college_data in self.your_colleges.items():
            programs = college_data.get('programs', [])
            your_courses[college_id] = [p.lower().strip() for p in programs if p]
        return your_courses
    
    def detect_competitor_courses(self, competitor_urls: List[str]) -> Dict[str, Dict]:
        """Scrape competitor websites and extract their courses
        
        Args:
            competitor_urls: List of competitor college website URLs
            
        Returns:
            Dict mapping college names to their detected courses
        """
        competitor_courses = {}
        
        for url in competitor_urls:
            logger.info(f"🔍 Scraping courses from: {url}")
            
            # Scrape the college website
            college_data = self.scraper.scrape_college(url)
            
            if not college_data:
                logger.warning(f"⚠️  Could not scrape {url}")
                continue
            
            college_name = college_data.get('name', url)
            programs = college_data.get('programs', [])
            
            # Normalize programs to lowercase
            normalized_programs = [p.lower().strip() for p in programs if p]
            
            competitor_courses[college_name] = {
                'url': url,
                'raw_courses': programs,
                'normalized_courses': normalized_programs,
                'course_count': len(normalized_programs)
            }
            
            logger.info(f"✓ Found {len(normalized_programs)} courses at {college_name}")
        
        return competitor_courses
    
    def match_courses(self, your_college_id: str, competitor_courses: Dict) -> Dict:
        """Match competitor courses against your college's courses
        
        Args:
            your_college_id: Your college identifier (e.g., 'college_1')
            competitor_courses: Dict from detect_competitor_courses()
            
        Returns:
            Detailed matching report with matches, close matches, and gaps
        """
        your_colleges = self.get_your_courses()
        
        if your_college_id not in your_colleges:
            logger.error(f"College {your_college_id} not found in configuration")
            return {}
        
        your_courses_list = your_colleges[your_college_id]
        your_college = self.your_colleges[your_college_id]
        
        report = {
            'your_college': {
                'id': your_college_id,
                'name': your_college.get('name'),
                'location': your_college.get('location'),
                'total_courses': len(your_courses_list),
                'courses': your_courses_list
            },
            'competitors': [],
            'summary': {}
        }
        
        for comp_name, comp_data in competitor_courses.items():
            comp_courses = comp_data.get('normalized_courses', [])
            
            # Find exact matches
            exact_matches = self._find_exact_matches(your_courses_list, comp_courses)
            
            # Find close/similar matches
            close_matches = self._find_close_matches(
                your_courses_list, 
                comp_courses, 
                exclude=set(exact_matches)
            )
            
            # Courses unique to competitor
            unique_to_competitor = [c for c in comp_courses 
                                   if c not in exact_matches 
                                   and c not in [m[0] for m in close_matches]]
            
            # Courses unique to your college
            unique_to_yours = [c for c in your_courses_list
                              if c not in exact_matches 
                              and c not in [m[1] for m in close_matches]]
            
            # Calculate competition score
            competition_score = self._calculate_competition_score(
                len(exact_matches),
                len(close_matches),
                len(comp_courses)
            )
            
            competitor_info = {
                'name': comp_name,
                'url': comp_data.get('url'),
                'total_courses': len(comp_courses),
                'exact_matches': exact_matches,
                'exact_match_count': len(exact_matches),
                'close_matches': close_matches,
                'close_match_count': len(close_matches),
                'unique_to_competitor': unique_to_competitor[:10],  # Top 10
                'unique_to_yours': unique_to_yours[:10],
                'competition_level': self._classify_competition(competition_score),
                'competition_score': competition_score,
                'match_percentage': (len(exact_matches) / len(comp_courses) * 100) if comp_courses else 0
            }
            
            report['competitors'].append(competitor_info)
        
        # Generate summary statistics
        report['summary'] = self._generate_summary(report)
        
        return report
    
    @staticmethod
    def _find_exact_matches(your_courses: List[str], competitor_courses: List[str]) -> List[str]:
        """Find exact course name matches (case-insensitive)"""
        your_set = set(your_courses)
        matches = [c for c in competitor_courses if c in your_set]
        return list(set(matches))  # Remove duplicates
    
    @staticmethod
    def _find_close_matches(your_courses: List[str], competitor_courses: List[str], 
                           exclude: set = None) -> List[Tuple[str, str]]:
        """Find similar course names using keyword matching
        
        Returns:
            List of tuples: (competitor_course, your_course)
        """
        if exclude is None:
            exclude = set()
        
        matches = []
        keywords_map = {}
        
        # Build keyword map for your courses
        for course in your_courses:
            if course not in exclude:
                keywords = set(course.split())
                keywords_map[course] = keywords
        
        # Find matches in competitor courses
        for comp_course in competitor_courses:
            if comp_course in exclude:
                continue
            
            comp_keywords = set(comp_course.split())
            
            # Check for keyword overlap
            for your_course, your_keywords in keywords_map.items():
                overlap = len(comp_keywords & your_keywords)
                total_keywords = len(comp_keywords | your_keywords)
                
                if overlap > 0 and total_keywords > 0:
                    similarity = overlap / total_keywords
                    
                    # Consider it a close match if >40% keyword overlap
                    if similarity > 0.4:
                        matches.append((comp_course, your_course))
                        break  # Each competitor course only matches to best your course
        
        return list(set(matches))
    
    @staticmethod
    def _calculate_competition_score(exact_matches: int, close_matches: int, 
                                    competitor_total: int) -> float:
        """Calculate competition score (0.0 to 1.0)"""
        if competitor_total == 0:
            return 0.0
        
        # Weight exact matches at 2x close matches
        weighted_overlap = (exact_matches * 2) + close_matches
        score = weighted_overlap / competitor_total
        
        # Cap at 1.0
        return min(1.0, score)
    
    @staticmethod
    def _classify_competition(score: float) -> str:
        """Classify competition level based on score"""
        if score >= 0.7:
            return "🔴 VERY HIGH - Direct course competitor"
        elif score >= 0.5:
            return "🟠 HIGH - Significant course overlap"
        elif score >= 0.3:
            return "🟡 MEDIUM - Some course overlap"
        elif score >= 0.1:
            return "🟢 LOW - Minimal course overlap"
        else:
            return "⚪ VERY LOW - Few to no overlapping courses"
    
    @staticmethod
    def _generate_summary(report: Dict) -> Dict:
        """Generate summary statistics from matching report"""
        competitors = report.get('competitors', [])
        
        if not competitors:
            return {
                'total_competitors_analyzed': 0,
                'very_high_competition': 0,
                'high_competition': 0,
                'medium_competition': 0,
                'low_competition': 0,
                'average_match_percentage': 0.0,
                'biggest_competitors': []
            }
        
        # Count by competition level
        levels = {}
        total_match_pct = 0
        
        for comp in competitors:
            level = comp['competition_level'].split()[0]  # Get emoji
            levels[level] = levels.get(level, 0) + 1
            total_match_pct += comp['match_percentage']
        
        # Sort competitors by competition score
        sorted_comps = sorted(
            competitors,
            key=lambda x: x['competition_score'],
            reverse=True
        )
        
        return {
            'total_competitors_analyzed': len(competitors),
            'very_high_competition': len([c for c in competitors if c['competition_score'] >= 0.7]),
            'high_competition': len([c for c in competitors if 0.5 <= c['competition_score'] < 0.7]),
            'medium_competition': len([c for c in competitors if 0.3 <= c['competition_score'] < 0.5]),
            'low_competition': len([c for c in competitors if c['competition_score'] < 0.3]),
            'average_match_percentage': total_match_pct / len(competitors) if competitors else 0,
            'biggest_competitors': [
                {'name': c['name'], 'score': c['competition_score'], 'matches': c['exact_match_count']}
                for c in sorted_comps[:5]
            ]
        }
    
    def generate_competition_report(self, your_college_id: str, competitor_urls: List[str]) -> Dict:
        """Generate complete course competition analysis report
        
        Args:
            your_college_id: Your college identifier
            competitor_urls: List of competitor URLs to analyze
            
        Returns:
            Complete report with course matches and competitive analysis
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎓 COURSE COMPETITION ANALYSIS")
        logger.info(f"{'='*80}\n")
        
        # Step 1: Detect competitor courses
        logger.info("📍 STEP 1: Detecting competitor courses from websites...")
        competitor_courses = self.detect_competitor_courses(competitor_urls)
        
        if not competitor_courses:
            logger.warning("⚠️  No competitor data collected")
            return {}
        
        # Step 2: Match courses
        logger.info("\n🔄 STEP 2: Matching courses against your college...")
        match_report = self.match_courses(your_college_id, competitor_courses)
        
        # Step 3: Store results in database
        logger.info("\n💾 STEP 3: Storing competitor data in database...")
        self._store_competitors_in_db(match_report)
        
        return match_report
    
    def _store_competitors_in_db(self, report: Dict):
        """Store matched competitors in the database

        Handles missing names by falling back to the source URL or a
        generated identifier so storing won't crash on None values.
        """
        for competitor_info in report.get('competitors', []):
            # Safe name and ID generation
            raw_name = competitor_info.get('name') or ''
            source_url = competitor_info.get('url') or ''
            if raw_name and isinstance(raw_name, str) and raw_name.strip():
                name = raw_name.strip()
            elif source_url:
                # derive a readable name from URL
                name = re.sub(r"https?://(www\.)?", "", source_url).strip('/').split('/')[0]
            else:
                name = 'unknown_competitor'

            # create a filesystem/db-safe id
            college_id = re.sub(r"[^a-z0-9_]+", "_", name.lower())

            competitor_data = {
                'college_id': college_id,
                'name': name,
                'location': competitor_info.get('location') or 'Unknown',
                'programs': competitor_info.get('unique_to_competitor', []),
                'source_url': source_url,
                'metadata': {
                    'competition_score': competitor_info.get('competition_score'),
                    'exact_matches': competitor_info.get('exact_match_count', 0),
                    'close_matches': competitor_info.get('close_match_count', 0),
                    'competition_level': competitor_info.get('competition_level')
                }
            }

            try:
                self.db.add_competitor(competitor_data)
                logger.info(f"✓ Stored {name} in database")
            except Exception as e:
                logger.warning(f"Could not store {name}: {e}")
    
    def print_report(self, report: Dict):
        """Print formatted competition analysis report"""
        if not report:
            print("No report data available")
            return
        
        your_college = report.get('your_college', {})
        summary = report.get('summary', {})
        
        print(f"\n{'='*80}")
        print(f"COURSE COMPETITION ANALYSIS REPORT")
        print(f"{'='*80}\n")
        
        # Your college info
        print(f"YOUR COLLEGE: {your_college.get('name')}")
        print(f"Location: {your_college.get('location')}")
        print(f"Total Courses Offered: {your_college.get('total_courses')}")
        print(f"Courses: {', '.join(your_college.get('courses', [])[:5])}")
        if len(your_college.get('courses', [])) > 5:
            print(f"         ... and {len(your_college.get('courses', [])) - 5} more")
        
        # Summary statistics
        print(f"\n\n{'='*80}")
        print("COMPETITIVE LANDSCAPE SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Total Competitors Analyzed: {summary.get('total_competitors_analyzed')}")
        print(f"  🔴 Very High Competition: {summary.get('very_high_competition')}")
        print(f"  🟠 High Competition: {summary.get('high_competition')}")
        print(f"  🟡 Medium Competition: {summary.get('medium_competition')}")
        print(f"  🟢 Low Competition: {summary.get('low_competition')}")
        print(f"\nAverage Course Overlap: {summary.get('average_match_percentage', 0):.1f}%")
        
        # Top competitors
        if summary.get('biggest_competitors'):
            print(f"\n\nTOP 5 COMPETITORS:")
            for i, comp in enumerate(summary.get('biggest_competitors', []), 1):
                print(f"\n{i}. {comp['name']}")
                print(f"   Competition Score: {comp['score']:.2%}")
                print(f"   Course Matches: {comp['matches']} exact matches")
        
        # Detailed competitor analysis
        print(f"\n\n{'='*80}")
        print("DETAILED COMPETITOR ANALYSIS")
        print(f"{'='*80}\n")
        
        for competitor in report.get('competitors', []):
            print(f"\n📍 {competitor['name']}")
            print(f"   Website: {competitor['url']}")
            print(f"   Total Courses: {competitor['total_courses']}")
            print(f"   Competition Level: {competitor['competition_level']}")
            print(f"   Match Score: {competitor['match_percentage']:.1f}%")
            
            # Exact matches
            if competitor['exact_matches']:
                print(f"\n   🎯 EXACT COURSE MATCHES ({len(competitor['exact_matches'])}):")
                for course in competitor['exact_matches'][:5]:
                    print(f"      • {course}")
                if len(competitor['exact_matches']) > 5:
                    print(f"      ... and {len(competitor['exact_matches']) - 5} more")
            
            # Close matches
            if competitor['close_matches']:
                print(f"\n   ≈ SIMILAR COURSES ({len(competitor['close_matches'])}):")
                for comp_course, your_course in competitor['close_matches'][:3]:
                    print(f"      • {comp_course} ≈ {your_course}")
                if len(competitor['close_matches']) > 3:
                    print(f"      ... and {len(competitor['close_matches']) - 3} more")
            
            # Their unique courses
            if competitor['unique_to_competitor']:
                print(f"\n   ⭐ THEIR UNIQUE COURSES ({len(competitor['unique_to_competitor'])} shown):")
                for course in competitor['unique_to_competitor'][:3]:
                    print(f"      • {course}")
                if len(competitor['unique_to_competitor']) > 3:
                    print(f"      ... {len(competitor['unique_to_competitor']) - 3} more unique courses")
            
            # Opportunities
            if competitor['unique_to_yours']:
                print(f"\n   💡 YOUR UNIQUE ADVANTAGE ({len(competitor['unique_to_yours'])} courses):")
                for course in competitor['unique_to_yours'][:3]:
                    print(f"      • {course}")
        
        print(f"\n{'='*80}\n")


def example_usage():
    """Example of using the Course Matcher AI"""
    
    matcher = CourseMatcherAI()
    
    # Example competitor URLs (would come from user input)
    competitor_urls = [
        'https://www.harvard.edu',
        'https://www.stanford.edu',
        'https://www.mit.edu',
    ]
    
    # Generate comprehensive report
    report = matcher.generate_competition_report('college_1', competitor_urls)
    
    # Print formatted report
    matcher.print_report(report)


if __name__ == '__main__':
    example_usage()
