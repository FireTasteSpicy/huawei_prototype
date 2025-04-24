from django.test import TestCase, Client
from django.urls import reverse
from dashboard.models import Camera, Incident, Weather, AccidentProbabilityScore

class MapHomeViewTests(TestCase):
    """Tests for the map home view."""
    
    def setUp(self):
        self.client = Client()
        self.map_home_url = reverse('geomap')
        
    def test_map_home_loads(self):
        """Test that the map home view loads successfully."""
        response = self.client.get(self.map_home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geomap/map_home.html')
        
        # Check for links to other maps
        self.assertContains(response, reverse('camera_map'))
        self.assertContains(response, reverse('incident_map'))
        self.assertContains(response, reverse('probability_map'))
        self.assertContains(response, reverse('weather_map'))


class CameraMapViewTests(TestCase):
    """Tests for the camera map view."""
    
    def setUp(self):
        self.client = Client()
        self.camera_map_url = reverse('camera_map')
        
        # Create test cameras
        self.camera1 = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-CAM-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01"
        )
        
        self.camera2 = Camera.objects.create(
            camera_id=2,
            camera_name="TEST-CAM-02",
            location="1.3347,103.7775",
            road_name="Test Road B",
            feed_url="https://example.com/test02"
        )
        
    def test_camera_map_with_cameras(self):
        """Test the camera map view with existing cameras."""
        response = self.client.get(self.camera_map_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geomap/camera_map.html')
        
        # Check for camera data in the map HTML
        map_html = response.context['map_html']
        self.assertIn("TEST-CAM-01", map_html)
        self.assertIn("TEST-CAM-02", map_html)
        self.assertIn("Test Road A", map_html)
        self.assertIn("Test Road B", map_html)
        
        # Check for correct coordinates
        self.assertIn("1.3099", map_html)
        self.assertIn("103.9053", map_html)
        
        # Check for feed links
        self.assertIn('/cameras/view/1/', map_html)
        self.assertIn('/cameras/view/2/', map_html)
    
    def test_camera_map_no_cameras(self):
        """Test the camera map view with no cameras (demo data)."""
        # Delete all cameras
        Camera.objects.all().delete()
        
        response = self.client.get(self.camera_map_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for demo data in the map HTML
        map_html = response.context['map_html']
        self.assertIn("ECP-01", map_html)
        self.assertIn("PIE-04", map_html)
        self.assertIn("Demo data", map_html)


class IncidentMapViewTests(TestCase):
    """Tests for the incident map view."""
    
    def setUp(self):
        self.client = Client()
        self.incident_map_url = reverse('incident_map')
        
        # Create a test camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-CAM-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01"
        )
        
        # Create test incidents
        self.incident1 = Incident.objects.create(
            incident_type="Traffic Accident",
            severity="high",
            camera=self.camera
        )
        
        self.incident2 = Incident.objects.create(
            incident_type="Vehicle Fire",
            severity="medium",
            camera=self.camera
        )
        
    def test_incident_map_with_incidents(self):
        """Test the incident map view with existing incidents."""
        response = self.client.get(self.incident_map_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geomap/incident_map.html')
        
        # Check for incident data in the map HTML
        map_html = response.context['map_html']
        self.assertIn("Traffic Accident", map_html)
        self.assertIn("Vehicle Fire", map_html)
        self.assertIn("Test Road A", map_html)
        
        # Check for severity levels
        self.assertIn("high", map_html.lower())
        self.assertIn("medium", map_html.lower())
        
        # Check for the correct coordinates
        self.assertIn("1.3099", map_html)
        self.assertIn("103.9053", map_html)
    
    def test_incident_map_no_incidents(self):
        """Test the incident map view with no incidents (demo data)."""
        # Delete all incidents
        Incident.objects.all().delete()
        
        response = self.client.get(self.incident_map_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for demo data in the map HTML
        map_html = response.context['map_html']
        self.assertIn("Traffic Accident", map_html)
        self.assertIn("Demo data", map_html)
        
        # Verify all severity levels in demo data
        self.assertIn("high", map_html.lower())
        self.assertIn("medium", map_html.lower())
        self.assertIn("low", map_html.lower())


class ProbabilityMapViewTests(TestCase):
    """Tests for the probability map view."""
    
    def setUp(self):
        self.client = Client()
        self.probability_map_url = reverse('probability_map')
        
        # Create a test camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-CAM-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01"
        )
        
        # Create test probability scores of different risk levels
        self.high_risk = AccidentProbabilityScore.objects.create(
            area_geometry="POINT(1.3099 103.9053)",
            accident_prob_score=0.85,  # High risk
            camera=self.camera
        )
        
        self.medium_risk = AccidentProbabilityScore.objects.create(
            area_geometry="POINT(1.3099 103.9053)",
            accident_prob_score=0.55,  # Medium risk
            camera=self.camera
        )
        
        self.low_risk = AccidentProbabilityScore.objects.create(
            area_geometry="POINT(1.3099 103.9053)",
            accident_prob_score=0.25,  # Low risk
            camera=self.camera
        )
        
    def test_probability_map_all_risks(self):
        """Test the probability map with 'all' filter."""
        response = self.client.get(self.probability_map_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geomap/probability_map.html')
        
        # Check that context contains expected variables
        self.assertEqual(response.context['selected_type'], 'all')
        self.assertIn('map_html', response.context)
        
        # Check that all risk levels are in the HTML
        map_html = response.context['map_html']
        self.assertIn("High Risk Area", map_html)
        self.assertIn("Medium Risk Area", map_html)
        self.assertIn("Low Risk Area", map_html)
        self.assertIn("0.85", map_html)  # High risk score
        self.assertIn("0.55", map_html)  # Medium risk score
        self.assertIn("0.25", map_html)  # Low risk score
    
    def test_probability_map_high_risk_filter(self):
        """Test the probability map filtered to high risk only."""
        response = self.client.get(f"{self.probability_map_url}?type=high%20risk")
        self.assertEqual(response.status_code, 200)
        
        # Check that context contains expected variables
        self.assertEqual(response.context['selected_type'], 'high risk')
        
        # Check that only high risk is in the HTML
        map_html = response.context['map_html']
        self.assertIn("High Risk Area", map_html)
        self.assertNotIn("Medium Risk Area", map_html)
        self.assertNotIn("Low Risk Area", map_html)
        self.assertIn("0.85", map_html)  # High risk score
        self.assertNotIn("0.55", map_html)  # Medium risk score
        self.assertNotIn("0.25", map_html)  # Low risk score
    
    def test_probability_map_no_markers_filter(self):
        """Test the probability map with no markers filter."""
        response = self.client.get(f"{self.probability_map_url}?type=no%20markers")
        self.assertEqual(response.status_code, 200)
        
        # Check that context contains expected variables
        self.assertEqual(response.context['selected_type'], 'no markers')
        
        # Check that risk areas aren't in the HTML
        map_html = response.context['map_html']
        self.assertNotIn("High Risk Area", map_html)
        self.assertNotIn("Medium Risk Area", map_html)
        self.assertNotIn("Low Risk Area", map_html)
    
    def test_probability_map_no_data(self):
        """Test the probability map with no data (demo data)."""
        # Delete all probability scores
        AccidentProbabilityScore.objects.all().delete()
        
        response = self.client.get(self.probability_map_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for demo data indicator
        map_html = response.context['map_html']
        self.assertIn("Demo data", map_html)
        
        # Check that all risk levels are in the demo data
        self.assertIn("High Risk Area", map_html)
        self.assertIn("Medium Risk Area", map_html)
        self.assertIn("Low Risk Area", map_html)


class WeatherMapViewTests(TestCase):
    """Tests for the weather map view."""
    
    def setUp(self):
        self.client = Client()
        self.weather_map_url = reverse('weather_map')
        
        # Create test cameras
        self.camera1 = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-CAM-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01"
        )
        
        self.camera2 = Camera.objects.create(
            camera_id=2,
            camera_name="TEST-CAM-02",
            location="1.3347,103.7775",
            road_name="Test Road B",
            feed_url="https://example.com/test02"
        )
        
        # Create weather data for different conditions
        self.sunny_weather = Weather.objects.create(
            temperature=32.5,
            conditions="Sunny",
            camera=self.camera1
        )
        
        self.rainy_weather = Weather.objects.create(
            temperature=26.7,
            conditions="Light Rain",
            camera=self.camera2
        )
        
    def test_weather_map_with_weather_data(self):
        """Test the weather map with existing weather data."""
        response = self.client.get(self.weather_map_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'geomap/weather_map.html')
        
        # Check for weather data in the map HTML
        map_html = response.context['map_html']
        self.assertIn("32.5°C", map_html)
        self.assertIn("26.7°C", map_html)
        self.assertIn("Sunny", map_html)
        self.assertIn("Light Rain", map_html)
        self.assertIn("TEST-CAM-01", map_html)
        self.assertIn("TEST-CAM-02", map_html)
        
        # Check for proper coordinates
        self.assertIn("1.3099", map_html)
        self.assertIn("103.9053", map_html)
        self.assertIn("1.3347", map_html)
        self.assertIn("103.7775", map_html)
    
    def test_weather_map_no_weather_data_but_cameras(self):
        """Test the weather map with no weather data but existing cameras."""
        # Delete weather data but keep cameras
        Weather.objects.all().delete()
        
        response = self.client.get(self.weather_map_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for camera data with demo weather in the map HTML
        map_html = response.context['map_html']
        self.assertIn("TEST-CAM-01", map_html)
        self.assertIn("TEST-CAM-02", map_html)
        self.assertIn("°C", map_html)  # Temperature symbol
        self.assertIn("Demo data", map_html)
    
    def test_weather_map_no_data(self):
        """Test the weather map with no data at all (complete demo)."""
        # Delete all cameras and weather data
        Weather.objects.all().delete()
        Camera.objects.all().delete()
        
        response = self.client.get(self.weather_map_url)
        self.assertEqual(response.status_code, 200)
        
        # Check for demo data
        map_html = response.context['map_html']
        self.assertIn("ECP-01", map_html)
        self.assertIn("PIE-04", map_html)
        self.assertIn("°C", map_html)  # Temperature symbol
        self.assertIn("Demo data", map_html)


class MapIntegrationTests(TestCase):
    """Integration tests for maps working together."""
    
    def setUp(self):
        self.client = Client()
        
        # Create a test camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-CAM-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01"
        )
        
        # Create related data for this camera
        self.incident = Incident.objects.create(
            incident_type="Traffic Accident",
            severity="high",
            camera=self.camera
        )
        
        self.weather = Weather.objects.create(
            temperature=28.5,
            conditions="Sunny",
            camera=self.camera
        )
        
        self.risk_score = AccidentProbabilityScore.objects.create(
            area_geometry="POINT(1.3099 103.9053)",
            accident_prob_score=0.85,
            camera=self.camera
        )
    
    def test_camera_appears_on_all_maps(self):
        """Test that a camera appears consistently on all maps."""
        # Check camera map
        camera_response = self.client.get(reverse('camera_map'))
        self.assertIn("TEST-CAM-01", camera_response.context['map_html'])
        
        # Check incident map
        incident_response = self.client.get(reverse('incident_map'))
        self.assertIn("TEST-CAM-01", incident_response.context['map_html'])
        self.assertIn("Traffic Accident", incident_response.context['map_html'])
        
        # Check weather map
        weather_response = self.client.get(reverse('weather_map'))
        self.assertIn("TEST-CAM-01", weather_response.context['map_html'])
        self.assertIn("28.5°C", weather_response.context['map_html'])
        self.assertIn("Sunny", weather_response.context['map_html'])
        
        # Check probability map
        probability_response = self.client.get(reverse('probability_map'))
        self.assertIn("TEST-CAM-01", probability_response.context['map_html'])
        self.assertIn("0.85", probability_response.context['map_html'])