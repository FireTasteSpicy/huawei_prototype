from django.test import TestCase, Client
from django.urls import reverse
from dashboard.models import Camera, Weather, AccidentProbabilityScore
from datetime import datetime, timedelta


class CameraListViewTests(TestCase):
    """Tests for the camera listing view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.cameras_url = reverse("cameras")

        # Create test cameras
        self.camera1 = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01",
        )

        self.camera2 = Camera.objects.create(
            camera_id=2,
            camera_name="TEST-02",
            location="1.3347,103.7775",
            road_name="Test Road B",
            feed_url="https://example.com/test02",
        )

    def test_view_loads(self):
        """Test that the camera list view loads successfully."""
        response = self.client.get(self.cameras_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cameras/cameras.html")
        self.assertTrue("cameras" in response.context)
        self.assertEqual(len(response.context["cameras"]), 2)

    def test_search_by_name(self):
        """Test searching cameras by name."""
        response = self.client.get(f"{self.cameras_url}?search=TEST-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cameras"]), 1)
        self.assertEqual(response.context["cameras"][0].camera_name, "TEST-01")

    def test_search_by_road(self):
        """Test searching cameras by road name."""
        response = self.client.get(f"{self.cameras_url}?search=Road A")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cameras"]), 1)
        self.assertEqual(response.context["cameras"][0].road_name, "Test Road A")

    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(f"{self.cameras_url}?search=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["cameras"]), 0)
        self.assertContains(response, "No cameras found")

    def test_pagination(self):
        """Test pagination for cameras view."""
        # Create 11 additional cameras to have 13 total (requiring 2 pages)
        for i in range(3, 14):
            Camera.objects.create(
                camera_id=i,
                camera_name=f"TEST-{i:02d}",
                location="1.3099,103.9053",
                road_name=f"Test Road {i}",
                feed_url=f"https://example.com/test{i:02d}",
            )

        # Test first page
        response = self.client.get(self.cameras_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("cameras" in response.context)
        self.assertEqual(len(response.context["cameras"]), 10)  # 10 per page

        # Test second page
        response = self.client.get(f"{self.cameras_url}?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("cameras" in response.context)
        self.assertEqual(len(response.context["cameras"]), 3)  # remaining 3 cameras


class MockDataGenerationTests(TestCase):
    """Tests for mock data generation when no data exists."""

    def setUp(self):
        self.client = Client()
        self.cameras_url = reverse("cameras")
        # Ensure database is empty
        Camera.objects.all().delete()

    def test_mock_data_generation(self):
        """Test that mock data is generated when database is empty."""
        response = self.client.get(self.cameras_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("cameras" in response.context)
        self.assertTrue(len(response.context["cameras"]) > 0)
        self.assertTrue(response.context["is_demo_data"])

    def test_mock_data_search(self):
        """Test that mock data can be searched too."""
        # Search for "ECP" in demo data (should match ECP-01)
        response = self.client.get(f"{self.cameras_url}?search=ECP")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("cameras" in response.context)
        self.assertTrue(response.context["is_demo_data"])

        # At least one camera should contain "ECP" in demo data
        found_ecp = False
        for camera in response.context["cameras"]:
            if "ECP" in camera.camera_name:
                found_ecp = True
                break
        self.assertTrue(found_ecp)


class CameraFeedViewTests(TestCase):
    """Tests for the camera feed detail view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create test camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TEST-01",
            location="1.3099,103.9053",
            road_name="Test Road A",
            feed_url="https://example.com/test01",
        )

        # Create test weather data
        self.weather = Weather.objects.create(
            camera=self.camera,
            temperature=28.5,
            conditions="Sunny",
            timestamp=datetime.now() - timedelta(minutes=15),
        )

        # Create test risk data
        self.accident_probability = AccidentProbabilityScore.objects.create(
            camera=self.camera,
            area_geometry="POLYGON((0 0, 0 1, 1 1, 0 0))",  # Simple triangle
            accident_prob_score=0.75,  # High risk
            timestamp=datetime.now() - timedelta(minutes=10),
        )

        self.camera_feed_url = reverse("camera_feed", args=[1])
        self.nonexistent_camera_url = reverse("camera_feed", args=[999])

    def test_camera_feed_view_loads(self):
        """Test that the camera feed view loads successfully for existing camera."""
        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cameras/camera_feed.html")

        # Check that camera data is in context
        self.assertEqual(response.context["camera"], self.camera)

        # Check that associated data is present
        self.assertTrue("weather" in response.context)
        self.assertTrue("accident_prob_score" in response.context)
        self.assertTrue("risk_level" in response.context)
        self.assertEqual(
            response.context["risk_level"], "High"
        )  # Based on our 0.75 score

    def test_camera_feed_risk_levels(self):
        """Test that risk levels are correctly calculated based on probability score."""
        # Update to high risk (already set to 0.75 in setUp)
        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.context["risk_level"], "High")

        # Update to medium risk
        self.accident_probability.accident_prob_score = 0.5
        self.accident_probability.save()
        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.context["risk_level"], "Medium")

        # Update to low risk
        self.accident_probability.accident_prob_score = 0.3
        self.accident_probability.save()
        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.context["risk_level"], "Low")

    def test_nonexistent_camera(self):
        """Test that mock data is generated for nonexistent cameras."""
        response = self.client.get(self.nonexistent_camera_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_demo_data" in response.context)
        self.assertTrue(response.context["is_demo_data"])
        self.assertTrue("Camera 999" in response.context["title"])

    def test_weather_missing(self):
        """Test that mock weather data is generated when real data is missing."""
        # Delete the weather record
        self.weather.delete()

        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("weather" in response.context)
        self.assertTrue("temperature" in response.context["weather"])
        self.assertTrue("conditions" in response.context["weather"])

    def test_risk_missing(self):
        """Test that mock risk data is generated when real data is missing."""
        # Delete the accident probability record
        self.accident_probability.delete()

        response = self.client.get(self.camera_feed_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("accident_prob_score" in response.context)
        self.assertTrue("risk_level" in response.context)
        self.assertTrue(isinstance(response.context["accident_prob_score"], float))
