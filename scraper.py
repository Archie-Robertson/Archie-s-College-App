"""Web scraper for college data"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional
from config import SCRAPING_TIMEOUT, MAX_RETRIES, USER_AGENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollegeScraper:
    """Scrapes college data from websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def scrape_college(self, url: str) -> Optional[Dict]:
        """Scrape college data from a URL"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=SCRAPING_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                college_data = self._extract_college_data(soup, url)
                
                logger.info(f"Successfully scraped {college_data.get('name', 'Unknown')}")
                return college_data
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to scrape {url} after {MAX_RETRIES} attempts")
                    return None
        
        return None
    
    def _extract_college_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract college information from BeautifulSoup object"""
        # Common selectors for college websites
        college_data = {
            'source_url': url,
            'college_id': self._generate_college_id(url),
            'name': self._extract_text(soup, ['h1', '.college-name', '.institution-name']),
            'location': self._extract_text(soup, ['.location', '.address', '[data-location]']),
            'tuition': self._extract_number(soup, ['.tuition', '[data-tuition]']),
            'enrollment': self._extract_number(soup, ['.enrollment', '[data-enrollment]']),
            'acceptance_rate': self._extract_percentage(soup, ['.acceptance-rate', '[data-acceptance]']),
            'avg_gpa': self._extract_number(soup, ['.avg-gpa', '[data-gpa]']),
            'avg_sat': self._extract_number(soup, ['.avg-sat', '[data-sat]']),
            'avg_act': self._extract_number(soup, ['.avg-act', '[data-act]']),
            'programs': self._extract_programs(soup)
        }
        
        return college_data
    
    @staticmethod
    def _extract_text(soup: BeautifulSoup, selectors: list) -> Optional[str]:
        """Extract text from first matching selector"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    @staticmethod
    def _extract_number(soup: BeautifulSoup, selectors: list) -> Optional[float]:
        """Extract number from first matching selector"""
        text = CollegeScraper._extract_text(soup, selectors)
        if text:
            try:
                return float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _extract_percentage(soup: BeautifulSoup, selectors: list) -> Optional[float]:
        """Extract percentage from first matching selector"""
        text = CollegeScraper._extract_text(soup, selectors)
        if text:
            try:
                num = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
                return num / 100 if num > 1 else num
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _extract_programs(soup: BeautifulSoup) -> list:
        """Extract academic programs"""
        programs = []
        program_selectors = ['.program', '.major', '[data-program]', 'li.program']
        
        for selector in program_selectors:
            elements = soup.select(selector)
            for elem in elements:
                program_text = elem.get_text(strip=True)
                if program_text:
                    programs.append(program_text)
        
        return list(set(programs))[:20]  # Return top 20 unique programs
    
    @staticmethod
    def _generate_college_id(url: str) -> str:
        """Generate unique ID from URL"""
        return url.replace('https://', '').replace('http://', '').replace('/', '_')
