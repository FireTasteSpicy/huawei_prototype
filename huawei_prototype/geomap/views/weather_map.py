from django.shortcuts import render
import folium
import random
import logging
from dashboard.models import Weather, Camera
from django.contrib.auth.decorators import login_required

# Configure logging
logger = logging.getLogger(__name__)

# Singapore's coordinates
SINGAPORE_CENTER = [1.3521, 103.8198]

@login_required
def weather_map(request):
    """View for displaying weather information on a map."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)
    
    # Fetch latest weather data for each camera
    weather_data = Weather.objects.all().select_related('camera')
    
    # Add weather markers to the map
    for weather in weather_data:
        try:
            # Parse location from camera's location field
            lat, lng = map(float, weather.camera.location.split(','))
            
            # Choose icon and color based on conditions
            icon_name = "cloud"
            color = "lightblue"
            
            if "rain" in weather.conditions.lower():
                icon_name = "umbrella"
                color = "blue"
            elif "thunderstorm" in weather.conditions.lower():
                icon_name = "bolt"
                color = "purple"
            elif "sun" in weather.conditions.lower() or "clear" in weather.conditions.lower():
                icon_name = "sun-o"
                color = "orange"
            elif "fog" in weather.conditions.lower() or "mist" in weather.conditions.lower():
                icon_name = "low-vision"
                color = "gray"
            elif "cloud" in weather.conditions.lower():
                icon_name = "cloud"
                color = "lightgray"
            
            # Create popup content
            popup_content = f"""
            <div style="min-width: 200px;">
                <h5>Weather at {weather.camera.camera_name}</h5>
                <strong>Temperature:</strong> {weather.temperature}°C<br>
                <strong>Conditions:</strong> {weather.conditions}<br>
                <strong>Location:</strong> {weather.camera.road_name}<br>
                <strong>Time:</strong> {weather.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
            </div>
            """
            
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
            ).add_to(map_sg)
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            continue
    
    # If no weather data found, display cameras with demo weather
    if not weather_data:
        cameras = Camera.objects.all()
        
        # Weather conditions for demo
        demo_conditions = [
            {"temp": 32.5, "cond": "Sunny"},
            {"temp": 28.3, "cond": "Partly Cloudy"},
            {"temp": 27.1, "cond": "Light Rain"},
            {"temp": 30.8, "cond": "Clear"},
            {"temp": 29.4, "cond": "Cloudy"},
            {"temp": 26.7, "cond": "Thunderstorm"},
            {"temp": 28.9, "cond": "Hazy"},
        ]
        
        for camera in cameras:
            try:
                # Parse location
                lat, lng = map(float, camera.location.split(','))
                
                # Random weather condition
                weather = random.choice(demo_conditions)
                
                # Choose icon and color based on conditions
                icon_name = "cloud"
                color = "lightblue"
                
                if "rain" in weather["cond"].lower():
                    icon_name = "umbrella"
                    color = "blue"
                elif "thunderstorm" in weather["cond"].lower():
                    icon_name = "bolt" 
                    color = "purple"
                elif "sun" in weather["cond"].lower() or "clear" in weather["cond"].lower():
                    icon_name = "sun-o"
                    color = "orange"
                elif "fog" in weather["cond"].lower() or "mist" in weather["cond"].lower() or "hazy" in weather["cond"].lower():
                    icon_name = "low-vision"
                    color = "gray"
                elif "cloud" in weather["cond"].lower():
                    icon_name = "cloud"
                    color = "lightgray"
                
                # Create popup content
                popup_content = f"""
                <div style="min-width: 200px;">
                    <h5>Weather at {camera.camera_name}</h5>
                    <strong>Temperature:</strong> {weather["temp"]}°C<br>
                    <strong>Conditions:</strong> {weather["cond"]}<br>
                    <strong>Location:</strong> {camera.road_name}<br>
                    <em>(Demo data)</em>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
                ).add_to(map_sg)
            except Exception as e:
                logger.error(f"Error processing camera for demo weather: {e}")
                continue
        
        # If no cameras either, add some demo cameras with weather
        if not cameras:
            demo_cameras = [
                {"name": "ECP-01", "location": "1.3099,103.9053", "road": "East Coast Parkway"},
                {"name": "PIE-04", "location": "1.3347,103.7775", "road": "Pan Island Expressway"},
                {"name": "CTE-09", "location": "1.3545,103.8390", "road": "Central Expressway"},
                {"name": "AYE-02", "location": "1.3145,103.7650", "road": "Ayer Rajah Expressway"},
                {"name": "TPE-07", "location": "1.3800,103.9150", "road": "Tampines Expressway"},
            ]
            
            for camera in demo_cameras:
                try:
                    lat, lng = map(float, camera["location"].split(','))
                    weather = random.choice(demo_conditions)
                    
                    # Choose icon and color based on conditions
                    icon_name = "cloud"
                    color = "lightblue"
                    
                    if "rain" in weather["cond"].lower():
                        icon_name = "umbrella"
                        color = "blue"
                    elif "thunderstorm" in weather["cond"].lower():
                        icon_name = "bolt" 
                        color = "purple"
                    elif "sun" in weather["cond"].lower() or "clear" in weather["cond"].lower():
                        icon_name = "sun-o"
                        color = "orange"
                    elif "hazy" in weather["cond"].lower():
                        icon_name = "low-vision"
                        color = "gray"
                    elif "cloud" in weather["cond"].lower():
                        icon_name = "cloud"
                        color = "lightgray"
                    
                    # Create popup content
                    popup_content = f"""
                    <div style="min-width: 200px;">
                        <h5>Weather at {camera["name"]}</h5>
                        <strong>Temperature:</strong> {weather["temp"]}°C<br>
                        <strong>Conditions:</strong> {weather["cond"]}<br>
                        <strong>Location:</strong> {camera["road"]}<br>
                        <em>(Demo data)</em>
                    </div>
                    """
                    
                    folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
                    ).add_to(map_sg)
                except Exception as e:
                    logger.error(f"Error adding demo camera weather: {e}")
                    continue
    
    # Render map to HTML
    map_html = map_sg._repr_html_()
    
    return render(
        request,
        "geomap/weather_map.html",
        {
            "map_html": map_html,
            "title": "Live Weather Map",
            "description": "Current weather conditions across Singapore's traffic camera network."
        },
    )