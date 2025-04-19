from django.shortcuts import render
import folium
from folium.plugins import HeatMap
import random
import logging
from dashboard.models import AccidentProbabilityScore, Camera

# Configure logging
logger = logging.getLogger(__name__)

# Singapore's coordinates
SINGAPORE_CENTER = [1.3521, 103.8198]

def probability_map(request):
    """View for displaying probability maps with risk scores from the database."""
    # Create a map centered on Singapore
    map_sg = folium.Map(location=SINGAPORE_CENTER, zoom_start=12)
    
    # Filter by risk level if specified
    risk_level = request.GET.get('type', 'all')
    
    # Define risk level categories
    def get_risk_level(score):
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    # Fetch probability scores from database
    probabilitys = AccidentProbabilityScore.objects.all().select_related('camera')
    
    # Prepare data for heatmap
    heat_data = []
    
    # Create markers for high-risk areas
    for probability in probabilitys:
        try:
            # Get camera location
            if not probability.camera or not probability.camera.location:
                continue
                
            lat, lng = map(float, probability.camera.location.split(','))
            
            # Calculate risk level
            score = probability.risk_score
            risk = get_risk_level(score)
            
            # Skip if filtered by risk level
            if risk_level != 'all' and risk_level != f"{risk}_risk":
                continue
                
            # Skip all markers if no markers is selected
            if risk_level == 'no markers':
                continue
                
            # Add to heatmap data (lat, lng, intensity)
            heat_data.append([lat, lng, score])
            
         # Add marker based on risk level and filter
            show_marker = False
            marker_color = "blue"  # Default color
            
            if score >= 0.7 and (risk_level == 'all' or risk_level == 'high risk'):
                show_marker = True
                marker_color = "red"
                risk_text = "High Risk Area"
            elif score >= 0.4 and score < 0.7 and (risk_level == 'all' or risk_level == 'medium risk'):
                show_marker = True
                marker_color = "orange"
                risk_text = "Medium Risk Area"
            elif score < 0.4 and (risk_level == 'all' or risk_level == 'low risk'):
                show_marker = True
                marker_color = "green"
                risk_text = "Low Risk Area"
            
            if show_marker:
                popup_content = f"""
                <div style="min-width: 200px;">
                    <h5>{risk_text}</h5>
                    <strong>Risk Score:</strong> {score:.2f}<br>
                    <strong>Location:</strong> {probability.camera.road_name}<br>
                    <strong>Camera:</strong> {probability.camera.camera_name}<br>
                    <strong>Probability Time:</strong> {probability.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                """
                
                radius = 6
                
                # Make markers even smaller when showing 'all' risk levels
                if risk_level == 'all':
                    radius = 4
                    
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=radius,
                    popup=folium.Popup(popup_content, max_width=300),
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7
                ).add_to(map_sg)
        except Exception as e:
            logger.error(f"Error processing probability {probability.accident_probability_score_id}: {e}")
            continue
    
    # If no data is found, generate demo data
    if not heat_data:
        # List of major roads in Singapore for demo data
        major_roads = [
            # PIE (Pan Island Expressway)
            {'start': [1.3380, 103.6914], 'end': [1.3715, 103.9798], 'name': 'PIE'},
            # ECP (East Coast Parkway)
            {'start': [1.2936, 103.8771], 'end': [1.3164, 103.9798], 'name': 'ECP'},
            # CTE (Central Expressway)
            {'start': [1.2855, 103.8380], 'end': [1.3850, 103.8549], 'name': 'CTE'},
            # Other major roads...
        ]
        
        # Generate demo heat data along roads
        for road in major_roads:
            num_points = random.randint(20, 40)
            start_lat, start_lon = road['start']
            end_lat, end_lon = road['end']
            
            for _ in range(num_points):
                ratio = random.random()
                lat = start_lat + ratio * (end_lat - start_lat)
                lon = start_lon + ratio * (end_lon - start_lon)
                lat += (random.random() - 0.5) * 0.003
                lon += (random.random() - 0.5) * 0.003
                
                # Higher intensity at interchanges
                if 'Expressway' in road['name'] or road['name'] in ['PIE', 'CTE', 'ECP']:
                    if ratio < 0.1 or ratio > 0.9:
                        intensity = random.uniform(0.7, 1.0)
                    else:
                        intensity = random.uniform(0.3, 0.7)
                else:
                    intensity = random.uniform(0.2, 0.8)
                    
                heat_data.append([lat, lon, intensity])
                
                # Skip all markers if no_markers selected
                if risk_level == 'no_markers':
                    continue
                # Add marker based on risk level and filter
                show_marker = False
                marker_color = "blue"  # Default color
                
                if intensity >= 0.7 and (risk_level == 'all' or risk_level == 'high risk'):
                    show_marker = True
                    marker_color = "red"
                    risk_text = "High Risk Area"
                elif intensity >= 0.4 and intensity < 0.7 and (risk_level == 'all' or risk_level == 'medium risk'):
                    show_marker = True
                    marker_color = "orange"
                    risk_text = "Medium Risk Area"
                elif intensity < 0.4 and (risk_level == 'all' or risk_level == 'low risk'):
                    show_marker = True
                    marker_color = "green"
                    risk_text = "Low Risk Area"
                
                if show_marker:
                    popup_content = f"""
                    <div style="min-width: 200px;">
                        <h5>{risk_text}</h5>
                        <strong>Risk Score:</strong> {intensity:.2f}<br>
                        <strong>Location:</strong> {road['name']}<br>
                        <em>(Demo data)</em>
                    </div>
                    """
                    
                    radius = 6
                    
                    # Make markers even smaller when showing 'all' risk levels
                    if risk_level == 'all':
                        radius = 4
                        
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        popup=folium.Popup(popup_content, max_width=300),
                        color='black',  # Black border
                        weight=0.5,                        
                        fill=True,
                        fill_color=marker_color,
                        fill_opacity=0.7
                    ).add_to(map_sg)
    
    # Add heatmap layer
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
    
    # Risk level filters for UI
    risk_types = ['all', 'high risk', 'medium risk', 'low risk', 'no markers']
        
    # Render map to HTML
    map_html = map_sg._repr_html_()
    
    return render(request, 'geomap/probability_map.html', {
        'map_html': map_html,
        'incident_types': risk_types,
        'selected_type': risk_level,
        'title': 'Risk Probability Map',
        'description': 'This map shows predicted risk levels based on historical data and AI analysis.'
    })