"""Web scraper for college data with improved extraction and fallbacks"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional, List
from config import SCRAPING_TIMEOUT, MAX_RETRIES, USER_AGENT
from urllib.parse import urlparse
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollegeScraper:
    """Scrapes college data from websites with domain-aware parsing and fallbacks."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def scrape_college(self, url: str) -> Optional[Dict]:
        """Scrape college data from a URL with retry and safe fallbacks."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=SCRAPING_TIMEOUT)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                college_data = self._extract_college_data(soup, url)

                logger.info(f"Successfully scraped {college_data.get('name') or url}")
                return college_data

            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to scrape {url} after {MAX_RETRIES} attempts")
                    return None

        return None

    def _extract_college_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract college information from BeautifulSoup object using multiple strategies."""
        domain = self._get_domain(url)

        # Name: try common places, meta tags, title and fall back to domain
        name = self._extract_text(soup, ['h1', '.college-name', '.institution-name'])
        if not name:
            name = self._extract_meta(soup, ['og:site_name', 'application-name', 'og:title', 'twitter:title'])
        if not name:
            title = soup.title.string if soup.title and soup.title.string else None
            if title:
                name = title.strip()
        if not name:
            name = domain

        # Programs: try domain-specific parsers first, then structured data, then generic fallbacks
        programs = []
        parser = getattr(self, f"_parse_{domain.replace('.', '_')}", None)
        if callable(parser):
            try:
                programs = parser(soup)
            except Exception:
                programs = []

        if not programs:
            programs = self._extract_programs_from_jsonld(soup)

        if not programs:
            programs = self._extract_programs(soup)

        if not programs:
            programs = self._extract_programs_by_headers(soup)

        # Links-based extraction as a last-ditch: look for links that contain 'program' or 'major'
        if not programs:
            programs = self._extract_programs_from_links(soup)

        college_data = {
            'source_url': url,
            'college_id': self._generate_college_id(url),
            'name': name,
            'location': self._extract_text(soup, ['.location', '.address', '[data-location]']),
            'tuition': self._extract_number(soup, ['.tuition', '[data-tuition]']),
            'enrollment': self._extract_number(soup, ['.enrollment', '[data-enrollment]']),
            'acceptance_rate': self._extract_percentage(soup, ['.acceptance-rate', '[data-acceptance]']),
            'avg_gpa': self._extract_number(soup, ['.avg-gpa', '[data-gpa]']),
            'avg_sat': self._extract_number(soup, ['.avg-sat', '[data-sat]']),
            'avg_act': self._extract_number(soup, ['.avg-act', '[data-act]']),
            'programs': programs
        }

        return college_data

    @staticmethod
    def _get_domain(url: str) -> str:
        try:
            p = urlparse(url)
            domain = p.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain.replace('-', '_')
        except Exception:
            return url.replace('https://', '').replace('http://', '').split('/')[0]

    @staticmethod
    def _extract_meta(soup: BeautifulSoup, keys: List[str]) -> Optional[str]:
        for key in keys:
            # og: and twitter: meta
            if ':' in key:
                tag = soup.find('meta', property=key)
                if tag and tag.get('content'):
                    return tag['content'].strip()
            else:
                tag = soup.find('meta', attrs={'name': key})
                if tag and tag.get('content'):
                    return tag['content'].strip()
        return None

    @staticmethod
    def _extract_text(soup: BeautifulSoup, selectors: list) -> Optional[str]:
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        return None

    @staticmethod
    def _extract_number(soup: BeautifulSoup, selectors: list) -> Optional[float]:
        text = CollegeScraper._extract_text(soup, selectors)
        if text:
            try:
                return float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_percentage(soup: BeautifulSoup, selectors: list) -> Optional[float]:
        text = CollegeScraper._extract_text(soup, selectors)
        if text:
            try:
                num = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
                return num / 100 if num > 1 else num
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_programs(soup: BeautifulSoup) -> List[str]:
        """Look for common program element classes/lists."""
        programs = []
        program_selectors = [
            '.program', '.major', '[data-program]', 'li.program', '.programs li', '.majors li', '.degree-list li'
        ]

        for selector in program_selectors:
            elements = soup.select(selector)
            for elem in elements:
                program_text = elem.get_text(separator=' ', strip=True)
                if program_text:
                    programs.append(program_text)

        # De-duplicate and limit
        cleaned = []
        for p in programs:
            p_clean = re.sub(r'\s+', ' ', p).strip()
            if len(p_clean) > 2 and p_clean.lower() not in [c.lower() for c in cleaned]:
                cleaned.append(p_clean)
        return cleaned[:50]

    @staticmethod
    def _extract_programs_from_jsonld(soup: BeautifulSoup) -> List[str]:
        programs = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string or '{}')
            except Exception:
                continue

            # If top-level is a list, iterate
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                # Look for Course objects
                if item.get('@type') == 'Course' and item.get('name'):
                    programs.append(item.get('name').strip())
                # Look for educational offerings
                if item.get('name') and ('course' in item.get('@type', '').lower() or 'educ' in item.get('@type', '').lower()):
                    programs.append(item.get('name').strip())
                # Some sites embed items inside graph
                if '@graph' in item and isinstance(item['@graph'], list):
                    for node in item['@graph']:
                        if isinstance(node, dict) and node.get('@type') == 'Course' and node.get('name'):
                            programs.append(node.get('name').strip())

        # dedupe
        out = []
        for p in programs:
            if p and p.lower() not in [o.lower() for o in out]:
                out.append(p)
        return out

    @staticmethod
    def _extract_programs_by_headers(soup: BeautifulSoup) -> List[str]:
        """Find headings like 'Programs' or 'Majors' and extract following lists."""
        keywords = ['program', 'programs', 'major', 'majors', 'degree', 'degrees', 'undergraduate', 'graduate', 'academics']
        programs = []
        for header_tag in ['h2', 'h3', 'h4', 'h5']:
            for h in soup.find_all(header_tag):
                txt = h.get_text(' ', strip=True).lower()
                if any(k in txt for k in keywords):
                    # try next sibling lists
                    sib = h.find_next_sibling()
                    # collect from ul/li
                    if sib:
                        lis = sib.find_all('li')
                        for li in lis:
                            t = li.get_text(' ', strip=True)
                            if t:
                                programs.append(t)
                    # collect paragraphs under the section
                    parent = h.parent
                    if parent:
                        for li in parent.find_all('li'):
                            t = li.get_text(' ', strip=True)
                            if t:
                                programs.append(t)

        # dedupe and cleanup
        out = []
        for p in programs:
            p_clean = re.sub(r'\s+', ' ', p).strip()
            if len(p_clean) > 2 and p_clean.lower() not in [o.lower() for o in out]:
                out.append(p_clean)
        return out

    @staticmethod
    def _extract_programs_from_links(soup: BeautifulSoup) -> List[str]:
        programs = []
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            if 'program' in href or 'major' in href or 'degree' in href or 'academics' in href:
                txt = a.get_text(' ', strip=True)
                if txt and len(txt) > 2:
                    programs.append(txt)
        # dedupe
        out = []
        for p in programs:
            if p.lower() not in [o.lower() for o in out]:
                out.append(p)
        return out

    # domain-specific parsers (lightweight heuristics)
    def _parse_harvard_edu(self, soup: BeautifulSoup) -> List[str]:
        # Harvard often lists programs under elements with class 'programs-list' or 'field-list'
        programs = []
        for sel in ['.programs-list li', '.field-list li', '.academic-programs li', '.degree-list li']:
            for li in soup.select(sel):
                t = li.get_text(' ', strip=True)
                if t:
                    programs.append(t)
        return programs

    def _parse_stanford_edu(self, soup: BeautifulSoup) -> List[str]:
        programs = []
        for sel in ['.academics-list li', '.programs-list li', '.major-list li']:
            for li in soup.select(sel):
                t = li.get_text(' ', strip=True)
                if t:
                    programs.append(t)
        return programs

    def _parse_mit_edu(self, soup: BeautifulSoup) -> List[str]:
        programs = []
        for sel in ['.degree-list li', '.program-list li', '.department-list li']:
            for li in soup.select(sel):
                t = li.get_text(' ', strip=True)
                if t:
                    programs.append(t)
        return programs

    def _parse_berkeley_edu(self, soup: BeautifulSoup) -> List[str]:
        programs = []
        for sel in ['.programs li', '.majors li', '.degree-list li']:
            for li in soup.select(sel):
                t = li.get_text(' ', strip=True)
                if t:
                    programs.append(t)
        return programs

    def _parse_yale_edu(self, soup: BeautifulSoup) -> List[str]:
        programs = []
        for sel in ['.programs li', '.academics li', '.majors li']:
            for li in soup.select(sel):
                t = li.get_text(' ', strip=True)
                if t:
                    programs.append(t)
        return programs

    @staticmethod
    def _generate_college_id(url: str) -> str:
        """Generate unique ID from URL"""
        return url.replace('https://', '').replace('http://', '').replace('/', '_')
