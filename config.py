"""Configuration settings for the College Competition AI"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database settings
DB_PATH = os.getenv('DB_PATH', 'college_data.db')
MY_COLLEGE_ID = os.getenv('MY_COLLEGE_ID', 'my_college')

# API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_AI_ANALYSIS = os.getenv('USE_AI_ANALYSIS', 'True').lower() == 'true'

# Web scraping settings
SCRAPING_TIMEOUT = 30
MAX_RETRIES = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Comparison thresholds
SIMILARITY_THRESHOLD = 0.75
COMPETITION_LEVEL_THRESHOLD = 0.6

# Colleges to analyze (can be expanded)
TARGET_COLLEGES = [
    'https://www.example.com/college1',
    'https://www.example.com/college2',
]
