"""Geographic mapping for college competitors"""
import logging
from typing import Dict, List, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoMapper:
    """Maps colleges geographically and visualizes competition"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="college_ai_mapper")
        self.location_cache = {}
    
    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a location"""
        if not location:
            return None
        
        # Check cache first
        if location in self.location_cache:
            return self.location_cache[location]
        
        try:
            time.sleep(0.1)  # Rate limiting for Nominatim
            result = self.geocoder.geocode(location, timeout=5)
            if result:
                coords = (result.latitude, result.longitude)
                self.location_cache[location] = coords
                logger.info(f"Located {location}: {coords}")
                return coords
            else:
                logger.warning(f"Could not geocode: {location}")
                self.location_cache[location] = None
                return None
        except GeocoderTimedOut:
            logger.warning(f"Geocoding timeout for {location}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error for {location}: {e}")
            return None
    
    def calculate_distance(self, coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in miles"""
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 3959  # Earth's radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def categorize_by_distance(self, competitors_with_coords: List[Dict], 
                               my_college_coords: Tuple[float, float]) -> Dict:
        """Categorize competitors by geographic distance"""
        categories = {
            'local': [],        # < 50 miles
            'regional': [],     # 50-250 miles
            'national': []      # > 250 miles
        }
        
        for comp in competitors_with_coords:
            if not comp.get('coordinates'):
                continue
            
            distance = self.calculate_distance(my_college_coords, comp['coordinates'])
            comp['distance_miles'] = distance
            
            if distance < 50:
                categories['local'].append(comp)
            elif distance < 250:
                categories['regional'].append(comp)
            else:
                categories['national'].append(comp)
        
        return categories
    
    def generate_ascii_map(self, comparisons: List[Dict], 
                          my_college_coords: Tuple[float, float]) -> str:
        """Generate ASCII map showing competitors"""
        map_text = """
╔══════════════════════════════════════════════════════════════╗
║          GEOGRAPHIC COMPETITION MAP (ASCII)                  ║
╚══════════════════════════════════════════════════════════════╝

Legend:
🎓 = Your College
🔴 = HIGH competition (same programs)
🟡 = MEDIUM competition (some programs)
🟠 = LOW competition (few programs)

Note: Map uses simplified geographic positioning
"""
        return map_text
    
    def generate_html_map(self, comparisons: List[Dict], 
                         my_college_coords: Tuple[float, float],
                         my_college_name: str,
                         map_type: str = 'google') -> str:
        """Generate HTML map for competitors using Google Maps, Apple Maps, or Folium
        
        Args:
            comparisons: List of competitor colleges with coordinates
            my_college_coords: Latitude, longitude tuple for your college
            my_college_name: Name of your college
            map_type: 'google', 'apple', or 'folium'
        
        Returns:
            HTML string or URL to open in browser
        """
        if map_type.lower() == 'google':
            return self._generate_google_maps(comparisons, my_college_coords, my_college_name)
        elif map_type.lower() == 'apple':
            return self._generate_apple_maps(comparisons, my_college_coords, my_college_name)
        else:
            return self._generate_folium_map(comparisons, my_college_coords, my_college_name)
    
    def _generate_google_maps(self, comparisons: List[Dict], 
                             my_college_coords: Tuple[float, float],
                             my_college_name: str) -> str:
        """Generate Google Maps URL with markers"""
        lat, lon = my_college_coords
        
        # Start with your college as the center
        markers = f"markers=color:blue%7Clabel:HOME%7C{lat},{lon}"
        
        # Add competitors with color coding
        color_map = {
            'HIGH': 'red',
            'MEDIUM': 'orange',
            'LOW': 'yellow',
            'NONE': 'gray'
        }
        
        for idx, comp in enumerate(comparisons):
            if not comp.get('coordinates'):
                continue
            
            comp_lat, comp_lon = comp['coordinates']
            color = color_map.get(comp.get('competition_level'), 'gray')
            
            # Add marker for each competitor
            markers += f"&markers=color:{color}%7Clabel:{idx+1}%7C{comp_lat},{comp_lon}"
        
        # Create Google Maps URL
        zoom = 6
        size = "1280x720"
        url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom}&size={size}&{markers}&key=YOUR_API_KEY"
        
        # If no API key, generate interactive map URL instead
        interactive_url = f"https://www.google.com/maps/place/{lat},{lon}/"
        
        # Generate HTML that opens Google Maps
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>College Competition Map - Google Maps</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #1f2937; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .map-container {{ margin-bottom: 30px; }}
        .map-frame {{ width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 8px; }}
        .info {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .legend {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; }}
        .color-box {{ width: 20px; height: 20px; border-radius: 50%; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📍 College Competition Map</h1>
            <p>Your College: <strong>{my_college_name}</strong></p>
            <p>Location: {lat:.4f}°N, {lon:.4f}°E</p>
        </div>
        
        <div class="info">
            <h3>Legend</h3>
            <div class="legend">
                <div class="legend-item">
                    <div class="color-box" style="background: #4285f4;"></div>
                    <span>Your College</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #ea4335;"></div>
                    <span>HIGH Competition</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #fbbc04;"></div>
                    <span>MEDIUM Competition</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #34a853;"></div>
                    <span>LOW Competition</span>
                </div>
            </div>
        </div>
        
        <div class="map-container">
            <h3>Click button below to open interactive map in Google Maps</h3>
            <a href="{interactive_url}" target="_blank" style="
                display: inline-block;
                background: #1f2937;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                margin-bottom: 20px;
            ">
                📍 Open in Google Maps
            </a>
            <p><em>Note: Interactive map will open in a new tab with full zoom and pan controls</em></p>
        </div>
        
        <div class="info">
            <h3>Competitors ({len([c for c in comparisons if c.get('coordinates')])})</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #e5e7eb;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">College Name</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Competition</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Distance</th>
                    <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Match</th>
                </tr>
"""
        
        for comp in sorted([c for c in comparisons if c.get('distance_miles')], 
                          key=lambda x: x['distance_miles']):
            level = comp.get('competition_level', 'UNKNOWN')
            distance = comp.get('distance_miles', 0)
            similarity = comp.get('similarity_score', 0)
            comp_lat, comp_lon = comp['coordinates']
            
            color_map = {
                'HIGH': '#ea4335',
                'MEDIUM': '#fbbc04',
                'LOW': '#34a853',
                'NONE': '#9ca3af'
            }
            
            html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">
                        <a href="https://www.google.com/maps/place/{comp_lat},{comp_lon}/" 
                           target="_blank" style="color: #1f73e6; text-decoration: none;">
                            {comp.get('name')}
                        </a>
                    </td>
                    <td style="padding: 10px; border: 1px solid #ddd;">
                        <span style="background: {color_map.get(level, '#9ca3af')}; color: white; 
                                   padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            {level}
                        </span>
                    </td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{distance:.1f} mi</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{similarity:.0%}</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="info">
            <p style="font-size: 12px; color: #666;">
                💡 <strong>Tip:</strong> Once opened in Google Maps, you can:
                <ul>
                    <li>Search for more competitors</li>
                    <li>Get directions between colleges</li>
                    <li>View satellite/street view</li>
                    <li>Save locations for later</li>
                    <li>Check travel time between competitors</li>
                </ul>
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_apple_maps(self, comparisons: List[Dict], 
                            my_college_coords: Tuple[float, float],
                            my_college_name: str) -> str:
        """Generate Apple Maps URL with markers"""
        lat, lon = my_college_coords
        
        # Generate Apple Maps URL
        apple_maps_url = f"maps://?address={my_college_name}&ll={lat},{lon}"
        
        # Fallback to web version
        web_url = f"https://maps.apple.com/?ll={lat},{lon}&q={my_college_name.replace(' ', '+')}"
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>College Competition Map - Apple Maps</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; 
                margin: 20px; background: #f5f5f7; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #ffffff; color: #000; padding: 20px; border-radius: 12px; 
                  margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .info {{ background: #ffffff; padding: 20px; border-radius: 12px; 
                margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .legend {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; }}
        .color-box {{ width: 24px; height: 24px; border-radius: 50%; }}
        a.button {{
            display: inline-block;
            background: #0071e3;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            margin: 10px 10px 10px 0;
        }}
        a.button:hover {{ background: #0077ed; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e5ea; }}
        th {{ background: #f5f5f7; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ College Competition Map - Apple Maps</h1>
            <p>Your College: <strong>{my_college_name}</strong></p>
            <p>Location: {lat:.4f}°N, {lon:.4f}°E</p>
        </div>
        
        <div class="info">
            <h3>🧭 Open in Apple Maps</h3>
            <p>Click the button below to view competitors in Apple Maps:</p>
            <a href="{web_url}" target="_blank" class="button">
                📍 Open in Apple Maps
            </a>
            <p><small>For iOS devices, use the native Maps app for the best experience.</small></p>
        </div>
        
        <div class="info">
            <h3>📊 Legend</h3>
            <div class="legend">
                <div class="legend-item">
                    <div class="color-box" style="background: #0071e3;"></div>
                    <span>Your College</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #ff3b30;"></div>
                    <span>HIGH Competition</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #ff9500;"></div>
                    <span>MEDIUM Competition</span>
                </div>
                <div class="legend-item">
                    <div class="color-box" style="background: #34c759;"></div>
                    <span>LOW Competition</span>
                </div>
            </div>
        </div>
        
        <div class="info">
            <h3>🎓 Competitors ({len([c for c in comparisons if c.get('coordinates')])})</h3>
            <table>
                <tr>
                    <th>College</th>
                    <th>Competition</th>
                    <th>Distance</th>
                    <th>Match</th>
                </tr>
"""
        
        for comp in sorted([c for c in comparisons if c.get('distance_miles')], 
                          key=lambda x: x['distance_miles']):
            level = comp.get('competition_level', 'UNKNOWN')
            distance = comp.get('distance_miles', 0)
            similarity = comp.get('similarity_score', 0)
            comp_lat, comp_lon = comp['coordinates']
            comp_name = comp.get('name', 'Unknown')
            
            # Apple Maps URL for specific location
            comp_map_url = f"https://maps.apple.com/?ll={comp_lat},{comp_lon}&q={comp_name.replace(' ', '+')}"
            
            color_map = {
                'HIGH': '#ff3b30',
                'MEDIUM': '#ff9500',
                'LOW': '#34c759',
                'NONE': '#8e8e93'
            }
            
            html += f"""
                <tr>
                    <td><a href="{comp_map_url}" target="_blank" style="color: #0071e3; text-decoration: none;">
                        {comp_name}</a></td>
                    <td><span style="background: {color_map.get(level)}; color: white; 
                               padding: 4px 8px; border-radius: 4px; font-size: 12px;">{level}</span></td>
                    <td>{distance:.1f} mi</td>
                    <td>{similarity:.0%}</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="info">
            <h3>💡 Tips</h3>
            <ul>
                <li>On iPhone: Tap a location to get directions and see it on the map</li>
                <li>On Mac: Use Apple Maps' 3D view and Flyover feature</li>
                <li>Save locations for offline access</li>
                <li>Use "Directions" to plan visits between competitor colleges</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_folium_map(self, comparisons: List[Dict], 
                            my_college_coords: Tuple[float, float],
                            my_college_name: str) -> str:
        """Generate Folium/OpenStreetMap map (fallback)"""
        try:
            import folium
        except ImportError:
            logger.warning("Folium not installed. Install with: pip install folium")
            return self._generate_fallback_map(comparisons, my_college_coords, my_college_name)
        
        # Create map centered on your college
        map_obj = folium.Map(
            location=list(my_college_coords),
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add your college marker
        folium.Marker(
            location=list(my_college_coords),
            popup=my_college_name,
            tooltip="Your College",
            icon=folium.Icon(color='blue', icon='graduation-cap')
        ).add_to(map_obj)
        
        # Add competitor markers
        for comp in comparisons:
            if not comp.get('coordinates'):
                continue
            
            # Color based on competition level
            color_map = {
                'HIGH': 'red',
                'MEDIUM': 'orange',
                'LOW': 'yellow',
                'NONE': 'gray'
            }
            color = color_map.get(comp.get('competition_level'), 'gray')
            
            distance = comp.get('distance_miles', 0)
            popup_text = f"""
            <b>{comp.get('name')}</b><br>
            Level: {comp.get('competition_level')}<br>
            Similarity: {comp.get('similarity_score', 0):.1%}<br>
            Distance: {distance:.1f} miles
            """
            
            folium.Marker(
                location=list(comp['coordinates']),
                popup=folium.Popup(popup_text, max_width=200),
                tooltip=comp.get('name'),
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(map_obj)
        
        return map_obj._repr_html_()
    
    def _generate_fallback_map(self, comparisons: List[Dict], 
                              my_college_coords: Tuple[float, float],
                              my_college_name: str) -> str:
        """Generate fallback text-based map"""
        map_text = f"""
╔══════════════════════════════════════════════════════════════╗
║     GEOGRAPHIC COMPETITION VISUALIZATION (Text Format)      ║
╚══════════════════════════════════════════════════════════════╝

Your College: {my_college_name}
Location: {my_college_coords[0]:.4f}°N, {my_college_coords[1]:.4f}°E

COMPETITORS BY PROXIMITY:
"""
        
        # Sort by distance
        sorted_comps = sorted(
            [c for c in comparisons if c.get('distance_miles')],
            key=lambda x: x['distance_miles']
        )
        
        for comp in sorted_comps[:20]:  # Top 20 closest
            distance = comp['distance_miles']
            level = comp.get('competition_level', 'UNKNOWN')
            similarity = comp.get('similarity_score', 0)
            
            # Direction indicator
            if distance < 50:
                location_type = "LOCAL ⭐"
            elif distance < 250:
                location_type = "REGIONAL 📍"
            else:
                location_type = "NATIONAL 🗺️"
            
            # Color indicator
            level_indicator = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟠',
                'NONE': '⚪'
            }.get(level, '?')
            
            map_text += f"""
{level_indicator} {comp.get('name', 'Unknown')}
   Distance: {distance:.1f} miles [{location_type}]
   Level: {level} | Match: {similarity:.0%}
"""
        
        return map_text
    
    def generate_distance_report(self, comparisons: List[Dict],
                                my_college_coords: Tuple[float, float]) -> str:
        """Generate report on geographic distribution of competitors"""
        report = """
╔══════════════════════════════════════════════════════════════╗
║        GEOGRAPHIC COMPETITION ANALYSIS                       ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        # Categorize by distance
        categories = self.categorize_by_distance(comparisons, my_college_coords)
        
        total_competitors = sum(len(v) for v in categories.values())
        
        report += f"\nTotal Competitors Mapped: {total_competitors}\n\n"
        
        # Local competitors
        report += f"LOCAL COMPETITORS (< 50 miles): {len(categories['local'])}\n"
        for comp in sorted(categories['local'], key=lambda x: x.get('distance_miles', 0)):
            report += f"  ✓ {comp.get('name')} - {comp.get('distance_miles', 0):.1f} miles\n"
        
        # Regional competitors
        report += f"\nREGIONAL COMPETITORS (50-250 miles): {len(categories['regional'])}\n"
        for comp in sorted(categories['regional'], key=lambda x: x.get('distance_miles', 0))[:10]:
            report += f"  ✓ {comp.get('name')} - {comp.get('distance_miles', 0):.1f} miles\n"
        
        # National competitors
        report += f"\nNATIONAL COMPETITORS (> 250 miles): {len(categories['national'])}\n"
        for comp in sorted(categories['national'], key=lambda x: x.get('distance_miles', 0))[:5]:
            report += f"  ✓ {comp.get('name')} - {comp.get('distance_miles', 0):.1f} miles\n"
        
        return report
