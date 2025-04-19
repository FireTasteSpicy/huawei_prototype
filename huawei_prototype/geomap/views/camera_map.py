from dashboard.models import Camera
from django.shortcuts import render
import folium
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Singapore's coordinates
SINGAPORE_CENTER = [1.3521, 103.8198]

def camera_map(request):
    """View for displaying camera locations on a map."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)

    # Fetch cameras from database
    cameras_db = Camera.objects.all()

    # Add cameras to the map
    for camera in cameras_db:
        try:
            # Parse location from camera's location field (assuming format "lat,lng")
            lat, lng = map(float, camera.location.split(','))

            # Create popup content with button for feed URL
            popup_content = f"""
            <div style="min-width: 200px;">
                <h5>Camera: {camera.camera_name}</h5>
                <strong>ID:</strong> {camera.camera_id}<br>
                <strong>Location:</strong> {camera.location}<br>
                <strong>Road:</strong> {camera.road_name}<br>
                <div class="mt-2">
                    <a href="{camera.feed_url}" target="_blank" class="btn btn-primary btn-sm" style="color: white !important;">
                        <i class="fa fa-video-camera"></i> View Feed
                    </a>
                </div>
            </div>
            """

            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),  # Fixed width popup
                icon=folium.Icon(color="blue", icon="video-camera", prefix="fa"),
            ).add_to(map_sg)
        except Exception as e:
            logger.error(f"Error processing camera {camera.camera_id}: {e}")
            continue
    
    # If no cameras found, add demo data
    if not cameras_db:
        # Demo data
        demo_cameras = [
            {
                "id": 1,
                "name": "ECP-01",
                "location": "1.3099,103.9053",
                "road": "Duku Road",
                "feed": "https://example.com/feed/ecp01"
            },
            {
                "id": 2,
                "name": "PIE-04",
                "location": "1.3347,103.7775", 
                "road": "Clementi Road",
                "feed": "https://example.com/feed/pie04"
            },
            {
                "id": 3,
                "name": "CTE-09",
                "location": "1.3545,103.8390",
                "road": "Jalan Pintau",
                "feed": "https://example.com/feed/cte09"
            }
        ]
        
        for camera in demo_cameras:
            try:
                lat, lng = map(float, camera["location"].split(','))
                
                popup_content = f"""
                <div style="min-width: 200px;">
                    <h5>Camera: {camera["name"]}</h5>
                    <strong>ID:</strong> {camera["id"]}<br>
                    <strong>Location:</strong> {camera["location"]}<br>
                    <strong>Road:</strong> {camera["road"]}<br>
                    <div class="mt-2">
                        <a href="{camera["feed"]}" target="_blank" class="btn btn-primary btn-sm" style="color: white !important;">
                            <i class="fa fa-video-camera"></i> View Feed
                        </a>
                    </div>
                    <div><em>(Demo data)</em></div>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color="blue", icon="video-camera", prefix="fa"),
                ).add_to(map_sg)
            except Exception as e:
                logger.error(f"Error adding demo camera: {e}")
                continue

    # Render the map in the template
    map_html = map_sg._repr_html_()
    return render(request, "geomap/camera_map.html", {"map_html": map_html})