"""AI-powered analysis for college competition"""
import json
import logging
from typing import Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import USE_AI_ANALYSIS, SIMILARITY_THRESHOLD, COMPETITION_LEVEL_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitionAnalyzer:
    """Analyzes competition between colleges"""
    
    def __init__(self):
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.competition_threshold = COMPETITION_LEVEL_THRESHOLD
    
    def compare_colleges(self, my_college: Dict, competitor: Dict) -> Tuple[float, str, str]:
        """
        Compare my college with a competitor college
        
        Returns:
            (similarity_score, competition_level, analysis_text)
        """
        similarity_score = self._calculate_similarity(my_college, competitor)
        competition_level = self._determine_competition_level(similarity_score, my_college, competitor)
        analysis = self._generate_analysis(my_college, competitor, similarity_score, competition_level)
        
        return similarity_score, competition_level, analysis
    
    def _calculate_similarity(self, college1: Dict, college2: Dict) -> float:
        """Calculate similarity score based primarily on course/program overlap (0-1)"""
        # PRIMARY: Program overlap similarity (70% weight)
        program_similarity = self._compare_programs(college1, college2)
        
        # SECONDARY: Academic metrics for similar programs (20% weight)
        academic_metrics = ['avg_gpa', 'avg_sat', 'avg_act', 'acceptance_rate']
        academic_similarity = self._compare_metrics(college1, college2, academic_metrics)
        
        # TERTIARY: Size/enrollment similarity (10% weight)
        enrollment_similarity = self._compare_single_metric(
            college1.get('enrollment'), 
            college2.get('enrollment')
        )
        
        # Calculate weighted similarity (ONLY count if program overlap exists)
        if program_similarity < 0.1:  # Very low program overlap
            return 0.0  # Not a real competitor
        
        return (program_similarity * 0.70) + (academic_similarity * 0.20) + (enrollment_similarity * 0.10)
    
    @staticmethod
    def _compare_metrics(college1: Dict, college2: Dict, metrics: list) -> float:
        """Compare multiple metrics between colleges"""
        valid_scores = []
        
        for metric in metrics:
            val1 = college1.get(metric)
            val2 = college2.get(metric)
            
            if val1 is not None and val2 is not None:
                similarity = CompetitionAnalyzer._compare_single_metric(val1, val2)
                valid_scores.append(similarity)
        
        return np.mean(valid_scores) if valid_scores else 0.5
    
    @staticmethod
    def _compare_single_metric(val1, val2) -> float:
        """Compare two metric values (0-1)"""
        if val1 is None or val2 is None:
            return 0.5
        
        if val1 == 0 and val2 == 0:
            return 1.0
        
        max_val = max(abs(val1), abs(val2))
        if max_val == 0:
            return 1.0
        
        difference = abs(val1 - val2) / max_val
        return max(0, 1 - difference)
    
    @staticmethod
    def _compare_programs(college1: Dict, college2: Dict) -> float:
        """Compare program overlap between colleges"""
        programs1 = set(college1.get('programs', []))
        programs2 = set(college2.get('programs', []))
        
        if not programs1 or not programs2:
            return 0.5
        
        overlap = len(programs1.intersection(programs2))
        total = len(programs1.union(programs2))
        
        return overlap / total if total > 0 else 0.5
    
    def _determine_competition_level(self, similarity_score: float, my_college: Dict, 
                                     competitor: Dict) -> str:
        """Determine competition level based primarily on program overlap"""
        program_overlap = self._compare_programs(my_college, competitor)
        
        # Classification based on program overlap and overall similarity
        if program_overlap > 0.6 and similarity_score > 0.65:
            return "HIGH"  # Direct competitor in same programs
        elif program_overlap > 0.3 and similarity_score > 0.45:
            return "MEDIUM"  # Some program overlap
        elif program_overlap > 0.1:
            return "LOW"  # Minimal program overlap
        else:
            return "NONE"  # No relevant program overlap
    
    def _generate_analysis(self, my_college: Dict, competitor: Dict, 
                          similarity_score: float, competition_level: str) -> str:
        """Generate detailed analysis text"""
        analysis = f"""
Competition Analysis:
- Similarity Score: {similarity_score:.2%}
- Competition Level: {competition_level}

My College: {my_college.get('name')}
Competitor: {competitor.get('name')}

Academic Metrics Comparison:
- Acceptance Rate: {my_college.get('acceptance_rate', 'N/A')} vs {competitor.get('acceptance_rate', 'N/A')}
- Avg GPA: {my_college.get('avg_gpa', 'N/A')} vs {competitor.get('avg_gpa', 'N/A')}
- Avg SAT: {my_college.get('avg_sat', 'N/A')} vs {competitor.get('avg_sat', 'N/A')}
- Avg ACT: {my_college.get('avg_act', 'N/A')} vs {competitor.get('avg_act', 'N/A')}

Size & Cost:
- Enrollment: {my_college.get('enrollment', 'N/A')} vs {competitor.get('enrollment', 'N/A')}
- Tuition: ${my_college.get('tuition', 'N/A')} vs ${competitor.get('tuition', 'N/A')}

Location:
- {my_college.get('location', 'N/A')} vs {competitor.get('location', 'N/A')}

Key Insights:
"""
        
        # Add specific insights based on metrics
        if competition_level == "HIGH":
            analysis += "- This college is a direct competitor with similar metrics\n"
            analysis += "- Target similar student demographics and marketing strategies\n"
        elif competition_level == "MEDIUM":
            analysis += "- This college has some overlapping characteristics\n"
            analysis += "- Monitor their programs and offerings\n"
        else:
            analysis += "- Limited direct competition\n"
            analysis += "- Different positioning in the market\n"
        
        # Program analysis - PRIMARY FOCUS
        programs1 = set(my_college.get('programs', []))
        programs2 = set(competitor.get('programs', []))
        overlap = programs1.intersection(programs2)
        unique_to_competitor = programs2 - programs1
        
        if overlap:
            analysis += f"\n=== SHARED PROGRAMS ===\n{', '.join(list(overlap)[:5])}\n"
        
        if unique_to_competitor:
            analysis += f"\n=== THEIR UNIQUE PROGRAMS ===\n{', '.join(list(unique_to_competitor)[:5])}\n"
        
        # Program overlap percentage
        overlap_pct = (len(overlap) / len(programs2) * 100) if programs2 else 0
        analysis += f"\nProgram Overlap: {overlap_pct:.1f}% of their programs\n"
        
        if competition_level == "NONE":
            analysis += "\n⚠️  No significant program overlap - Not a direct competitor\n"
        
        return analysis
    
    def rank_competitors(self, comparisons: list) -> list:
        """Rank competitors by competition level and similarity"""
        return sorted(comparisons, key=lambda x: (
            {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x[1], 0),
            x[0]
        ), reverse=True)
