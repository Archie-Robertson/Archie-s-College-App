"""Utility functions for the College Competition AI"""
import json
from typing import Dict, List
import pandas as pd
from datetime import datetime

class ReportGenerator:
    """Generate reports in various formats"""
    
    @staticmethod
    def export_to_json(data: Dict, filename: str = 'competition_report.json'):
        """Export report to JSON"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return filename
    
    @staticmethod
    def export_to_csv(comparisons: List, filename: str = 'competitors.csv'):
        """Export comparisons to CSV"""
        df = pd.DataFrame(comparisons, columns=[
            'id', 'competitor_id', 'similarity_score', 
            'competition_level', 'analysis', 'created_date', 'competitor_name'
        ])
        df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def create_summary_table(report: Dict) -> str:
        """Create a formatted summary table"""
        summary = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    COMPETITION ANALYSIS SUMMARY                    ║
╠════════════════════════════════════════════════════════════════════╣
║ Total Competitors Analyzed: {report['total_competitors_analyzed']:>43} ║
║ High Competition Colleges:  {report['competition_summary']['high_competition']:>43} ║
║ Medium Competition Colleges:{report['competition_summary']['medium_competition']:>42} ║
║ Low Competition Colleges:   {report['competition_summary']['low_competition']:>43} ║
╚════════════════════════════════════════════════════════════════════╝
"""
        return summary


class DataProcessor:
    """Process and transform college data"""
    
    @staticmethod
    def normalize_metrics(value: float, min_val: float, max_val: float) -> float:
        """Normalize a value to 0-1 range"""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    @staticmethod
    def calculate_average_metrics(colleges: List[Dict]) -> Dict:
        """Calculate average metrics across colleges"""
        if not colleges:
            return {}
        
        metrics = {}
        metric_keys = ['tuition', 'enrollment', 'acceptance_rate', 'avg_gpa', 'avg_sat', 'avg_act']
        
        for key in metric_keys:
            values = [c.get(key) for c in colleges if c.get(key) is not None]
            if values:
                metrics[f'avg_{key}'] = sum(values) / len(values)
        
        return metrics
    
    @staticmethod
    def identify_outliers(colleges: List[Dict], metric: str, std_deviations: float = 2) -> List[str]:
        """Identify colleges that are outliers for a given metric"""
        values = [c.get(metric) for c in colleges if c.get(metric) is not None]
        
        if not values or len(values) < 2:
            return []
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        threshold = mean + (std_deviations * std_dev)
        
        return [
            c.get('name') for c in colleges 
            if c.get(metric) is not None and c.get(metric) > threshold
        ]


class StrategyRecommender:
    """Recommend strategies based on competition analysis"""
    
    @staticmethod
    def recommend_actions(report: Dict) -> List[str]:
        """Recommend strategic actions based on competition"""
        recommendations = []
        
        high_comp_count = report['competition_summary']['high_competition']
        
        if high_comp_count >= 5:
            recommendations.append(
                "High competition detected! Differentiate by highlighting unique programs and strengths."
            )
        
        if high_comp_count < 3:
            recommendations.append(
                "Limited direct competition. Focus on market expansion and growth opportunities."
            )
        
        avg_metrics = DataProcessor.calculate_average_metrics(
            [c['college_name'] for c in report.get('all_comparisons', [])]
        )
        
        recommendations.append(
            "Monitor top 5 competitors closely and analyze their strategic moves quarterly."
        )
        
        recommendations.append(
            "Conduct student satisfaction and outcome surveys compared to competitors."
        )
        
        return recommendations
