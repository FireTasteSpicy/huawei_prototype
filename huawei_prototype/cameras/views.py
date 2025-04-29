from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from dashboard.models import Camera, Weather, AccidentProbabilityScore
from django.db.models import Q
import logging
import random
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def cameras(request):
    """View for displaying and searching cameras."""
    
    # Get search query if exists
    search_query = request.GET.get('search', '')
    
    # Fetch cameras from database with optional filtering
    if search_query:
        cameras_list = Camera.objects.filter(
            Q(camera_name__icontains=search_query) | 
            Q(road_name__icontains=search_query)
        ).order_by('camera_name')
    else:
        cameras_list = Camera.objects.all().order_by('camera_name')
    
    # If no cameras found, add demo cameras
    if not cameras_list:
        logger.info("No cameras found, generating mock data")
        mock_cameras = []
        
        # Demo cameras data - similar to what's in camera_map.py
        demo_cameras = [
            {
                "camera_id": 1,
                "camera_name": "ECP-01",
                "location": "1.3099,103.9053",
                "road_name": "East Coast Parkway",
                "feed_url": "https://example.com/feed/ecp01"
            },
            {
                "camera_id": 2,
                "camera_name": "PIE-04",
                "location": "1.3347,103.7775",
                "road_name": "Pan Island Expressway",
                "feed_url": "https://example.com/feed/pie04"
            },
            {
                "camera_id": 3,
                "camera_name": "CTE-09",
                "location": "1.3545,103.8390",
                "road_name": "Central Expressway",
                "feed_url": "https://example.com/feed/cte09"
            },
            {
                "camera_id": 4,
                "camera_name": "AYE-02",
                "location": "1.3145,103.7650",
                "road_name": "Ayer Rajah Expressway",
                "feed_url": "https://example.com/feed/aye02"
            },
            {
                "camera_id": 5,
                "camera_name": "TPE-07",
                "location": "1.3800,103.9150",
                "road_name": "Tampines Expressway",
                "feed_url": "https://example.com/feed/tpe07"
            }
        ]
        
        try:
            # If search query exists, filter demo data too
            if search_query:
                demo_cameras = [c for c in demo_cameras if 
                                search_query.lower() in c["camera_name"].lower() or 
                                search_query.lower() in c["road_name"].lower()]
            
            # Create mock camera objects for display
            class MockCamera:
                def __init__(self, id, camera_name, location, road_name, feed_url):
                    self.camera_id = id
                    self.camera_name = camera_name
                    self.location = location
                    self.road_name = road_name
                    self.feed_url = feed_url
            
            # Create mock camera objects
            for camera in demo_cameras:
                mock_cameras.append(
                    MockCamera(
                        id=camera["camera_id"],
                        camera_name=camera["camera_name"],
                        location=camera["location"],
                        road_name=camera["road_name"],
                        feed_url=camera["feed_url"]
                    )
                )
            
            # For pagination
            paginator = Paginator(mock_cameras, 10)
            page = request.GET.get('page', 1)
            cameras = paginator.get_page(page)
            
            return render(
                request,
                "cameras/cameras.html",
                {
                    'cameras': cameras,
                    'search_query': search_query,
                    'title': 'Camera Directory',
                    'description': 'Directory of traffic cameras in the monitoring system.',
                    'is_demo_data': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating mock cameras: {e}")
            
            # Alternatively, create real cameras in the database
            for camera in demo_cameras:
                try:
                    Camera.objects.create(
                        camera_name=camera["camera_name"],
                        location=camera["location"],
                        road_name=camera["road_name"],
                        feed_url=camera["feed_url"]
                    )
                except Exception as e:
                    logger.error(f"Error creating camera in database: {e}")
            
            # Re-query the database after creating cameras
            if search_query:
                cameras_list = Camera.objects.filter(
                    Q(camera_name__icontains=search_query) | 
                    Q(road_name__icontains=search_query)
                ).order_by('camera_name')
            else:
                cameras_list = Camera.objects.all().order_by('camera_name')
    
    # Pagination (10 cameras per page)
    paginator = Paginator(cameras_list, 10)
    page = request.GET.get('page', 1)
    cameras = paginator.get_page(page)
    
    return render(
        request,
        "cameras/cameras.html",
        {
            'cameras': cameras,
            'search_query': search_query,
            'title': 'Camera Directory',
            'description': 'Directory of traffic cameras in the monitoring system.',
            'is_demo_data': not bool(cameras_list.exists() if hasattr(cameras_list, 'exists') else False)
        }
    )

# Keep your existing cameras function
@login_required
def camera_feed(request, camera_id):
    """View for displaying details of a specific camera."""
    
    try:
        # Try to get camera from database
        camera = get_object_or_404(Camera, camera_id=camera_id)
        
        # If feed_url is missing or invalid, use a fallback for demo purposes
        if not camera.feed_url or camera.feed_url.startswith('http://example.com') or camera.feed_url.startswith('https://example.com'):
            # For demo purposes, we'll use a placeholder
            camera.feed_url = ""  # Empty string will trigger the fallback in the template
        
        # Try to get latest associated data
        try:
            latest_weather = Weather.objects.filter(camera=camera).latest('timestamp')
            weather = {
                "temperature": latest_weather.temperature,
                "conditions": latest_weather.conditions,
                "updated": latest_weather.timestamp
            }
        except Weather.DoesNotExist:
            # Generate mock weather data
            weather_conditions = ["Sunny", "Partly Cloudy", "Light Rain", "Clear", "Cloudy", "Thunderstorm", "Hazy"]
            weather = {
                "temperature": round(random.uniform(25.0, 33.0), 1),
                "conditions": random.choice(weather_conditions),
                "updated": datetime.now() - timedelta(minutes=random.randint(5, 30))
            }
        
        try:
            latest_accident_probability = AccidentProbabilityScore.objects.filter(camera=camera).latest('timestamp')
            accident_prob_score = latest_accident_probability.accident_prob_score
        except AccidentProbabilityScore.DoesNotExist:
            # Generate mock accident_probability score
            accident_prob_score = round(random.uniform(0.2, 0.8), 2)
        
        # Determine accident_probability label
        if accident_prob_score >= 0.7:
            risk_level = "High"
        elif accident_prob_score >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return render(
            request,
            "cameras/camera_feed.html",
            {
                'camera': camera,
                'weather': weather,
                'accident_prob_score': accident_prob_score,
                'risk_level': risk_level,
                'timestamp': datetime.now(),
                'title': f'Camera: {camera.camera_name}',
                'description': f'Live feed and details for camera {camera.camera_name}'
            }
        )
    except Exception as e:
        logger.error(f"Error displaying camera detail: {e}")
        
        # Create mock camera if we can't find the real one
        mock_camera = {
            "camera_id": camera_id,
            "camera_name": f"Camera {camera_id}",
            "location": "1.3521, 103.8198",
            "road_name": "Demo Road",
            "feed_url": f"/cameras/view/{camera_id}/"
        }
        
        class MockCamera:
            def __init__(self, data):
                self.camera_id = data["camera_id"]
                self.camera_name = data["camera_name"]
                self.location = data["location"]
                self.road_name = data["road_name"]
                self.feed_url = data["feed_url"]
        
        # Generate mock weather and accident_probability data
        weather_conditions = ["Sunny", "Partly Cloudy", "Light Rain", "Clear", "Cloudy", "Thunderstorm", "Hazy"]
        weather = {
            "temperature": round(random.uniform(25.0, 33.0), 1),
            "conditions": random.choice(weather_conditions),
            "updated": datetime.now() - timedelta(minutes=random.randint(5, 30))
        }
        
        accident_prob_score = round(random.uniform(0.2, 0.8), 2)
        
        # Determine accident_probability label
        if accident_prob_score >= 0.7:
            risk_level = "High"
        elif accident_prob_score >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return render(
            request,
            "cameras/camera_feed.html",
            {
                'camera': MockCamera(mock_camera),
                'weather': weather,
                'accident_prob_score': accident_prob_score,
                'risk_level': risk_level,
                'timestamp': datetime.now(),
                'title': f'Camera {camera_id}',
                'description': 'Live feed and details for camera (Demo data)',
                'is_demo_data': True
            }
        )