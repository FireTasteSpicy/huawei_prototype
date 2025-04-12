from django.shortcuts import render
from dashboard.models import *
import folium
from folium.plugins import HeatMap
from django.http import HttpResponse
import random  # For demo data; replace with your actual data source

# Singapore's coordinates
SINGAPORE_CENTER = [1.3521, 103.8198]

def index(request):
    """Main view that provides links to both maps."""
    return render(request, 'geomap/index.html', {'active_page': 'index'})

def realtime_incident_map(request):
    """View for displaying real-time incidents on a map."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)
    
    # Demo data - replace with your actual data source
    incidents = [
        {"location": [1.3644, 103.9915], "type": "accident", "severity": "high", 
         "description": "Multi-vehicle collision"},
        {"location": [1.3099, 103.7775], "type": "fire", "severity": "medium", 
         "description": "Vehicle fire on expressway"},
        {"location": [1.3347, 103.8470], "type": "infraction", "severity": "low", 
         "description": "Illegal parking"},
        # Add more incidents as needed
    ]
    
    # Define icons for different incident types
    icons = {
        "accident": "ambulance",
        "fire": "fire",
        "infraction": "exclamation-triangle",
    }
    
    # Define colors for severity levels
    colors = {
        "high": "red",
        "medium": "orange",
        "low": "blue",
    }
    
    # Add incidents to the map
    for incident in incidents:
        folium.Marker(
            location=incident["location"],
            popup=f"{incident['description']} ({incident['severity']})",
            icon=folium.Icon(color=colors[incident["severity"]], icon=icons[incident["type"]], prefix='fa')
        ).add_to(map_sg)
    
    # Render map to HTML
    map_html = map_sg._repr_html_()
    
    return render(request, 'geomap/realtime_map.html', {
        'map': map_html,
        'active_page': 'realtime_map'
    })

def prediction_heatmap(request):
    """View for displaying incident prediction heatmap."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)
    
    # Filter by incident type if specified
    incident_type = request.GET.get('type', 'all')
    
    # Demo data - simulating major roads in Singapore
    # These are approximate coordinates of major roads/expressways
    major_roads = [
        # PIE (Pan Island Expressway) - East-West
        {'start': [1.3380, 103.6914], 'end': [1.3715, 103.9798], 'name': 'PIE'},
        # ECP (East Coast Parkway)
        {'start': [1.2936, 103.8771], 'end': [1.3164, 103.9798], 'name': 'ECP'},
        # CTE (Central Expressway) - North-South
        {'start': [1.2855, 103.8380], 'end': [1.3850, 103.8549], 'name': 'CTE'},
        # AYE (Ayer Rajah Expressway)
        {'start': [1.2934, 103.7818], 'end': [1.3211, 103.8475], 'name': 'AYE'},
        # BKE (Bukit Timah Expressway)
        {'start': [1.3697, 103.7698], 'end': [1.4202, 103.7698], 'name': 'BKE'},
        # KPE (Kallang-Paya Lebar Expressway)
        {'start': [1.3209, 103.8719], 'end': [1.3975, 103.9085], 'name': 'KPE'},
        # TPE (Tampines Expressway)
        {'start': [1.3715, 103.9574], 'end': [1.4202, 103.9085], 'name': 'TPE'},
        # Orchard Road
        {'start': [1.3024, 103.8318], 'end': [1.3072, 103.8369], 'name': 'Orchard Rd'},
        # Marina Coastal Expressway
        {'start': [1.2754, 103.8602], 'end': [1.2936, 103.8771], 'name': 'MCE'},
    ]
    
    # Generate points along these roads
    heat_data = []
    for road in major_roads:
        # Number of points to generate along this road
        num_points = random.randint(20, 40)
        
        start_lat, start_lon = road['start']
        end_lat, end_lon = road['end']
        
        for _ in range(num_points):
            # Generate a point somewhere along the road
            ratio = random.random()  # Position along the road (0 to 1)
            
            # Linear interpolation between start and end
            lat = start_lat + ratio * (end_lat - start_lat)
            lon = start_lon + ratio * (end_lon - start_lon)
            
            # Add some small random deviation to simulate width of road
            # and to avoid all points being in a perfect line
            lat += (random.random() - 0.5) * 0.003  # About 300m deviation
            lon += (random.random() - 0.5) * 0.003
            
            # Intensity based on road type and location
            # Expressways have higher intensity at interchanges (beginning/end)
            if 'Expressway' in road['name'] or road['name'] in ['PIE', 'CTE', 'ECP', 'AYE', 'BKE', 'KPE', 'TPE', 'MCE']:
                # Higher intensity near start/end (interchanges)
                if ratio < 0.1 or ratio > 0.9:
                    intensity = random.uniform(0.7, 1.0)
                else:
                    intensity = random.uniform(0.3, 0.7)
            else:
                # For other roads, more uniform distribution
                intensity = random.uniform(0.2, 0.8)
                
            heat_data.append([lat, lon, intensity])
    
    # Add some hotspots at key intersections
    hotspots = [
        # PIE/CTE interchange
        [1.3399, 103.8549, 1.0],
        # Orchard Road/Scotts Road
        [1.3047, 103.8318, 0.9],
        # Raffles Place
        [1.2830, 103.8513, 0.85],
        # Jurong East
        [1.3329, 103.7436, 0.8],
        # Changi Airport
        [1.3644, 103.9915, 0.75],
    ]
    heat_data.extend(hotspots)
    
    # Add heatmap layer to the map
    HeatMap(
        heat_data, 
        radius=15, 
        gradient={
            '0.1': 'green', 
            '0.5': 'yellow', 
            '0.7': 'orange', 
            '1.0': 'red'
        }
    ).add_to(map_sg)
    
    # Add incident type filter controls
    incident_types = ['all', 'collision', 'fire', 'self-accident', 'hit-and-run']
    
    # Render map to HTML
    map_html = map_sg._repr_html_()
    
    return render(request, 'geomap/prediction_heatmap.html', {
        'map': map_html,
        'incident_types': incident_types,
        'selected_type': incident_type,
        'active_page': 'prediction_heatmap'
    })