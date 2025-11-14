"""Database management for college data storage and retrieval"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from config import DB_PATH, MY_COLLEGE_ID

class CollegeDatabase:
    """Manages college data in SQLite database"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # My college data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS my_college (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT,
                programs TEXT,
                tuition REAL,
                enrollment INTEGER,
                acceptance_rate REAL,
                avg_gpa REAL,
                avg_sat REAL,
                avg_act REAL,
                metadata TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Competitor colleges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_colleges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                college_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                latitude REAL,
                longitude REAL,
                programs TEXT,
                tuition REAL,
                enrollment INTEGER,
                acceptance_rate REAL,
                avg_gpa REAL,
                avg_sat REAL,
                avg_act REAL,
                source_url TEXT,
                metadata TEXT,
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Comparison results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparison_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id TEXT NOT NULL,
                similarity_score REAL,
                competition_level TEXT,
                analysis TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitor_colleges(college_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_my_college(self, college_data: Dict):
        """Add or update my college data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO my_college 
            (id, name, location, programs, tuition, enrollment, acceptance_rate, 
             avg_gpa, avg_sat, avg_act, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            MY_COLLEGE_ID,
            college_data.get('name'),
            college_data.get('location'),
            json.dumps(college_data.get('programs', [])),
            college_data.get('tuition'),
            college_data.get('enrollment'),
            college_data.get('acceptance_rate'),
            college_data.get('avg_gpa'),
            college_data.get('avg_sat'),
            college_data.get('avg_act'),
            json.dumps(college_data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def add_competitor(self, college_data: Dict):
        """Add or update competitor college data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO competitor_colleges 
            (college_id, name, location, latitude, longitude, programs, tuition, enrollment, 
             acceptance_rate, avg_gpa, avg_sat, avg_act, source_url, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            college_data.get('college_id'),
            college_data.get('name'),
            college_data.get('location'),
            college_data.get('latitude'),
            college_data.get('longitude'),
            json.dumps(college_data.get('programs', [])),
            college_data.get('tuition'),
            college_data.get('enrollment'),
            college_data.get('acceptance_rate'),
            college_data.get('avg_gpa'),
            college_data.get('avg_sat'),
            college_data.get('avg_act'),
            college_data.get('source_url'),
            json.dumps(college_data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def get_my_college(self) -> Optional[Dict]:
        """Get my college data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM my_college WHERE id = ?', (MY_COLLEGE_ID,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_dict(row, 'my_college')
    
    def get_all_competitors(self) -> List[Dict]:
        """Get all competitor colleges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM competitor_colleges')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row, 'competitor_colleges') for row in rows]
    
    def save_comparison(self, competitor_id: str, similarity_score: float, 
                       competition_level: str, analysis: str):
        """Save comparison results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comparison_results 
            (competitor_id, similarity_score, competition_level, analysis)
            VALUES (?, ?, ?, ?)
        ''', (competitor_id, similarity_score, competition_level, analysis))
        
        conn.commit()
        conn.close()
    
    def get_comparisons(self) -> List[Dict]:
        """Get all comparison results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cr.*, cc.name as competitor_name 
            FROM comparison_results cr
            JOIN competitor_colleges cc ON cr.competitor_id = cc.college_id
            ORDER BY cr.similarity_score DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    
    @staticmethod
    def _row_to_dict(row, table_name):
        """Convert database row to dictionary"""
        if table_name == 'my_college':
            return {
                'id': row[0],
                'name': row[1],
                'location': row[2],
                'programs': json.loads(row[3]),
                'tuition': row[4],
                'enrollment': row[5],
                'acceptance_rate': row[6],
                'avg_gpa': row[7],
                'avg_sat': row[8],
                'avg_act': row[9],
                'metadata': json.loads(row[10])
            }
        elif table_name == 'competitor_colleges':
            return {
                'college_id': row[1],
                'name': row[2],
                'location': row[3],
                'latitude': row[4],
                'longitude': row[5],
                'programs': json.loads(row[6]),
                'tuition': row[7],
                'enrollment': row[8],
                'acceptance_rate': row[9],
                'avg_gpa': row[10],
                'avg_sat': row[11],
                'avg_act': row[12],
                'source_url': row[13],
                'metadata': json.loads(row[14])
            }
        return dict(row)
