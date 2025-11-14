# College Competition AI

An AI-powered system to analyze and compare your college with competitors. This tool scrapes college websites, extracts relevant data, and provides detailed competition analysis.

## Features

- **Web Scraping**: Automatically scrape college websites for key metrics
- **Data Storage**: SQLite database to store and organize college data
- **Competition Analysis**: Compare your college with competitors using multiple metrics
- **Similarity Scoring**: Calculate how similar competitors are to your college
- **Detailed Reports**: Generate comprehensive competition analysis reports
- **Strategic Recommendations**: Get actionable insights based on competition analysis
- **Multiple Export Formats**: Export reports as JSON or CSV

## Project Structure

```
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
- **🗺️ Real Maps Integration**: Visualize competitors on Google Maps, Apple Maps, or OpenStreetMap
- **Geographic Analysis**: Distance calculations and location-based competition insights
└── .env.example            # Environment variables template
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Archie-Robertson/Archie-s-College-App.git
cd Archie-s-College-App
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Update `.env` with your settings (optional):
```
DB_PATH=college_data.db
MY_COLLEGE_ID=my_college
OPENAI_API_KEY=your_key_here  # Optional for advanced AI features
USE_AI_ANALYSIS=True
```

## Usage

### Interactive CLI (Recommended)

```bash
python cli.py
```

This launches an interactive menu where you can:
- Setup your college data
- Add competitor colleges to analyze
- Generate competition reports
- View detailed analysis
- Export reports
- Get strategic recommendations

### Programmatic Usage

```python
from main import CollegeCompetitionAI

# Initialize the AI
ai = CollegeCompetitionAI()

# Setup your college
college_data = {
    'name': 'Your College',
    'location': 'City, State',
    'programs': ['CS', 'Engineering', 'Business'],
    'tuition': 50000,
    'enrollment': 15000,
    'acceptance_rate': 0.25,
    'avg_gpa': 3.8,
    'avg_sat': 1450,
    'avg_act': 33,
}
ai.setup_my_college(college_data)

# Analyze competitors
urls = ['https://college1.edu', 'https://college2.edu']
results = ai.analyze_competitors(urls)

# Generate report
report = ai.get_competition_report()
ai.print_report(report)
```

## Key Metrics

The system analyzes colleges using:

- **Academic Metrics**: GPA, SAT, ACT scores, acceptance rate
- **Size**: Enrollment numbers
- **Cost**: Tuition and fees
- **Programs**: Academic program overlap
- **Location**: Geographic information

## Competition Levels

Colleges are rated as:
- **HIGH**: Direct competitors with very similar metrics (>65% similarity)
- **MEDIUM**: Some overlapping characteristics (40-65% similarity)
- **LOW**: Limited direct competition (<40% similarity)

## Database Schema

### my_college
Stores data about your college
- Academic metrics (GPA, SAT, ACT, acceptance rate)
- Enrollment and tuition
- Programs offered
- Location and metadata

### competitor_colleges
Stores data about competitor colleges
- Same fields as my_college
- Source URL for reference
- Scraping timestamp

### comparison_results
Stores analysis results
- Similarity scores
- Competition level classification
- Detailed analysis text

## Similarity Scoring

The similarity score is calculated based on:
- Academic metrics (40% weight)
- Enrollment/Size (20% weight)
- Tuition/Cost (20% weight)
- Program overlap (20% weight)

Score ranges from 0 (no similarity) to 1 (identical).

## Web Scraping

The scraper supports common college website structures and looks for:
- College name and location
- Academic programs
- Admission statistics
- Enrollment numbers
- Tuition information

You can customize selectors in `scraper.py` for specific college websites.

## Error Handling

The system includes:
- Retry logic for failed scrapes
- Timeout handling for slow websites
- Data validation and error logging
- Graceful degradation for missing data

## Future Enhancements

- [ ] Support for more data sources (college databases, APIs)
- [ ] Advanced NLP analysis of college descriptions
- [ ] Trend analysis over time
- [ ] Student outcome data comparison
- [ ] Geographic competitor mapping
- [ ] API endpoint for external integration
- [ ] Web dashboard for visualization
- [ ] Automated reporting on schedule

## License

This project is part of Archie's College Application work.

## Contact

For questions or issues, please contact the developer.