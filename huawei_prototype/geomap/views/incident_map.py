from django.shortcuts import render
import folium
from dashboard.models import Incident, Camera
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Singapore's coordinates
SINGAPORE_CENTER = [1.3521, 103.8198]

def incident_map(request):
    """View for displaying real-time incidents on a map."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)

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

    # Fetch incidents from database
    incidents_db = Incident.objects.all().select_related('camera')

    # Add incidents to the map from database
    for incident in incidents_db:
        try:
            # Parse location from camera's location field
            lat, lng = map(float, incident.camera.location.split(','))
            
            # Get corresponding icon (default to exclamation-triangle if not found)
            icon_name = icons.get(incident.incident_type.lower(), "exclamation-triangle")
            
            # Get color based on severity level
            color = colors.get(incident.severity, "blue")
            
            # Create popup content with bold headings
            popup_content = f"""
            <div style="min-width: 200px;">
                <h5>{incident.incident_type}</h5>
                <strong>Severity:</strong> {incident.severity.title()}<br>
                <strong>Location:</strong> {incident.camera.road_name}<br>
                <strong>Camera:</strong> {incident.camera.camera_name}<br>
                <strong>Time:</strong> {incident.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
            </div>
            """
            
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),  # Set fixed width
                icon=folium.Icon(
                    color=color,
                    icon=icon_name,
                    prefix="fa",
                ),
            ).add_to(map_sg)
        except Exception as e:
            logger.error(f"Error processing incident {incident.incident_id}: {e}")
            continue

    # ========== DEMO DATA ========== #
    # If no incidents found, add demo data
    if not incidents_db:
        # Demo data for empty database
        demo_incidents = [
            {
                "type": "Traffic Accident",
                "severity": "high",
                "location": "1.3644,103.9915",
                "road": "East Coast Parkway",
                "time": "2025-04-13 14:25:30"
            },
            {
                "type": "Vehicle Fire",
                "severity": "medium",
                "location": "1.3099,103.7775",
                "road": "Jurong West Avenue",
                "time": "2025-04-13 15:10:45"
            },
            {
                "type": "Traffic Infraction",
                "severity": "low",
                "location": "1.3347,103.8470",
                "road": "Orchard Road",
                "time": "2025-04-13 13:55:20"
            }
        ]
        
        for incident in demo_incidents:
            try:
                lat, lng = map(float, incident["location"].split(','))
                icon_name = icons.get(incident["type"].lower().split()[0], "exclamation-triangle")
                
                # Create wider popup with bold headings
                popup_content = f"""
                <div style="min-width: 200px;">
                    <h5>{incident['type']}</h5>
                    <strong>Severity:</strong> {incident['severity'].title()}<br>
                    <strong>Location:</strong> {incident['road']}<br>
                    <strong>Time:</strong> {incident['time']}<br>
                    <em>(Demo data)</em>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(popup_content, max_width=300),  # Set fixed width
                    icon=folium.Icon(
                        color=colors[incident["severity"]],
                        icon=icon_name,
                        prefix="fa",
                    ),
                ).add_to(map_sg)
            except Exception as e:
                logger.error(f"Error adding demo incident: {e}")

    # Render map to HTML
    map_html = map_sg._repr_html_()

    return render(
        request,
        "geomap/incident_map.html",
        {"map_html": map_html},
    )