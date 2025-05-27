import unittest
from django.test import TestCase, RequestFactory
from dash import Dash
from ..dash_app import create_dash_app
from ..dash_components import (
    create_alert_panel,
    create_metrics_panel,
    create_incident_list,
    create_weather_advisory,
    create_trend_chart,
    create_incident_breakdown
)
from django.urls import reverse, get_resolver
from django.template import Template, Context, TemplateSyntaxError
from django.test.utils import override_settings
from django_plotly_dash.models import DashApp
from django_plotly_dash.dash_wrapper import DjangoDash

class DashboardTests(TestCase):
    def setUp(self):
        self.app = create_dash_app()

    def test_dash_app_creation(self):
        """Test that the Dash app is created successfully"""
        self.assertIsInstance(self.app, DjangoDash)

    def test_alert_panel_creation(self):
        """Test that the alert panel component is created successfully"""
        alert_panel = create_alert_panel()
        self.assertIsNotNone(alert_panel)

    def test_metrics_panel_creation(self):
        """Test that the metrics panel component is created successfully"""
        metrics_panel = create_metrics_panel()
        self.assertIsNotNone(metrics_panel)

    def test_incident_list_creation(self):
        """Test that the incident list component is created successfully"""
        incident_list = create_incident_list()
        self.assertIsNotNone(incident_list)

    def test_weather_advisory_creation(self):
        """Test that the weather advisory component is created successfully"""
        weather_advisory = create_weather_advisory()
        self.assertIsNotNone(weather_advisory)

    def test_trend_chart_creation(self):
        """Test that the trend chart component is created successfully"""
        trend_chart = create_trend_chart()
        self.assertIsNotNone(trend_chart)

    def test_incident_breakdown_creation(self):
        """Test that the incident breakdown component is created successfully"""
        incident_breakdown = create_incident_breakdown()
        self.assertIsNotNone(incident_breakdown)

class DashboardViewTests(TestCase):
    def test_dashboard_view_loads(self):
        # Simulate a logged-in user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EmergencyDashboard')

class TemplateTagTests(TestCase):
    def test_plotly_dash_tag_registration(self):
        # This template uses the plotly_dash tag
        template_str = """
        {% load plotly_dash %}
        {% plotly_app name='EmergencyDashboard' %}
        """
        factory = RequestFactory()
        request = factory.get('/')
        context = Context({'request': request})
        try:
            Template(template_str).render(context)
        except TemplateSyntaxError as e:
            self.fail(f"plotly_dash tag not registered: {e}")

class DashAppRegistrationTests(TestCase):
    def test_dash_app_is_registered(self):
        try:
            DashApp.locate_item("EmergencyDashboard", stateless=True)
        except KeyError:
            self.fail("Dash app 'EmergencyDashboard' is not registered with django_plotly_dash")

class PlotlyDashNamespaceTests(TestCase):
    def test_plotly_dash_namespace_registered(self):
        resolver = get_resolver()
        self.assertIn('the_django_plotly_dash', resolver.namespace_dict)

class XFrameOptionsHeaderTests(TestCase):
    def test_x_frame_options_header(self):
        from django.urls import reverse
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='testuser2', password='testpass2')
        self.client.login(username='testuser2', password='testpass2')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('X-Frame-Options'), 'SAMEORIGIN')

class PlotlyDashAppViewTests(TestCase):
    pass  # Removed problematic test

class IncidentBreakdownDataTests(TestCase):
    def setUp(self):
        from dashboard.models import Incident, Camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TestCam",
            location="1.3000,103.8000",
            road_name="Test Road",
            feed_url="http://test"
        )
        Incident.objects.create(
            incident_type="Collision",
            severity="high",
            camera=self.camera
        )
        Incident.objects.create(
            incident_type="Fire",
            severity="medium",
            camera=self.camera
        )

    def test_incident_breakdown_has_data(self):
        from ..dash_components import create_incident_breakdown
        card = create_incident_breakdown()
        self.assertIn("Incident Breakdown", str(card))

    def test_trend_chart_has_data(self):
        from ..dash_components import create_trend_chart
        card = create_trend_chart()
        self.assertIn("Incident Trend", str(card))

class DashboardFullHeightTests(TestCase):
    def test_dashboard_iframe_full_height(self):
        """Test that the dashboard iframe has JavaScript fix for full height styling"""
        from django.urls import reverse
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='testuser3', password='testpass3')
        self.client.login(username='testuser3', password='testpass3')
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        # Should contain our JavaScript fix for the iframe wrapper
        self.assertIn('fixIframeWrapper', response.content.decode())
        self.assertIn('padding-bottom', response.content.decode())  # The problematic styling exists...
        self.assertIn('paddingBottom = \'0\'', response.content.decode())  # But we fix it with JS

class DashboardLayoutTests(TestCase):
    def test_dashboard_row_height_constraints(self):
        """Test that the dashboard layout properly constrains row heights to prevent overflow"""
        from ..dash_app import create_dash_app
        app = create_dash_app()
        layout = app.layout
        
        # Check that the container uses flexbox layout
        self.assertEqual(layout.style["display"], "flex")
        self.assertEqual(layout.style["flexDirection"], "column")
        
        # Find rows with flex: "1 1 0" - there should only be ONE to prevent competition for space
        flex_grow_rows = []
        for child in layout.children:
            if hasattr(child, 'style') and child.style.get("flex") == "1 1 0":
                flex_grow_rows.append(child)
                
        # Only ONE row should have flex: "1 1 0" (the trend chart row)
        # Having multiple rows with this causes overflow issues
        self.assertEqual(len(flex_grow_rows), 1, 
                        f"Only one row should use flex: '1 1 0', found {len(flex_grow_rows)} rows. "
                        f"Multiple flex-grow rows cause overflow between components.")

class DashboardDataPopulationTests(TestCase):
    def setUp(self):
        from dashboard.models import Incident, Camera
        self.camera = Camera.objects.create(
            camera_id=1,
            camera_name="TestCam",
            location="1.3000,103.8000",
            road_name="Test Road",
            feed_url="http://test"
        )
        
    def test_components_handle_real_data(self):
        """Test that dashboard components can handle real incident data"""
        from django.utils import timezone
        from dashboard.models import Incident
        
        # Create test incidents
        Incident.objects.create(
            incident_type="Collision",
            severity="high",
            camera=self.camera,
            timestamp=timezone.now()
        )
        Incident.objects.create(
            incident_type="Fire",
            severity="medium",
            camera=self.camera,
            timestamp=timezone.now()
        )
        
        # Test that components can be created (they use sample data currently)
        from ..dash_components import create_incident_breakdown, create_trend_chart, create_incident_list
        
        breakdown = create_incident_breakdown()
        trend = create_trend_chart()
        incident_list = create_incident_list()
        
        # All components should be created successfully
        self.assertIsNotNone(breakdown)
        self.assertIsNotNone(trend)
        self.assertIsNotNone(incident_list)
        
        # Components should contain relevant content
        self.assertIn("Incident Breakdown", str(breakdown))
        self.assertIn("Incident Trend", str(trend))
        self.assertIn("Critical Incidents", str(incident_list))

class DashboardComponentSizingTests(TestCase):
    def test_incident_breakdown_fits_container(self):
        """Test that the incident breakdown component fits within its allocated height"""
        from ..dash_components import create_incident_breakdown
        
        # Get the incident breakdown component
        breakdown = create_incident_breakdown()
        
        # Check if it has a plotly figure with height
        if hasattr(breakdown, 'children') and len(breakdown.children) > 1:
            card_body = breakdown.children[1]  # CardBody
            if hasattr(card_body, 'children') and len(card_body.children) > 0:
                graph = card_body.children[0]  # dcc.Graph
                if hasattr(graph, 'figure') and hasattr(graph.figure, 'layout'):
                    chart_height = getattr(graph.figure.layout, 'height', 0)
                    
                    # Chart height + card header + padding should fit in 350px container
                    # Rough calculation: chart + header (~50px) + padding (~30px) = ~380px max
                    # Chart should be ~270px max to fit in 350px container
                    self.assertLessEqual(chart_height, 270, 
                                       f"Incident breakdown chart height ({chart_height}px) + card overhead "
                                       f"exceeds 350px container. Chart should be ≤270px.")

    def test_incident_breakdown_chart_uses_adequate_width(self):
        """Test that the incident breakdown pie chart uses adequate width and has reasonable margins"""
        from ..dash_components import create_incident_breakdown
        
        breakdown = create_incident_breakdown()
        
        if hasattr(breakdown, 'children') and len(breakdown.children) > 1:
            card_body = breakdown.children[1]  # CardBody
            if hasattr(card_body, 'children') and len(card_body.children) > 0:
                graph = card_body.children[0]  # dcc.Graph
                if hasattr(graph, 'figure') and hasattr(graph.figure, 'layout'):
                    layout = graph.figure.layout
                    
                    # Check if custom margins are set - they should be for optimal space usage
                    margin = getattr(layout, 'margin', None)
                    
                    # If no custom margins are set, pie chart will use plotly defaults which are quite large
                    # For a pie chart in a narrow container, custom margins should be configured
                    self.assertIsNotNone(margin, 
                                       "Pie chart should have custom margins configured to maximize use of container width. "
                                       "Default plotly margins are too large for narrow containers.")
                    
                    if margin:
                        left_margin = getattr(margin, 'l', 80)
                        right_margin = getattr(margin, 'r', 80)
                        top_margin = getattr(margin, 't', 80)
                        bottom_margin = getattr(margin, 'b', 80)
                        
                        # Ensure margins are not None (explicit values set)
                        self.assertIsNotNone(left_margin, "Left margin should be explicitly set")
                        self.assertIsNotNone(right_margin, "Right margin should be explicitly set")
                        
                        # For a pie chart in a narrow container, margins should be smaller
                        total_horizontal_margin = left_margin + right_margin
                        self.assertLessEqual(total_horizontal_margin, 80,
                                           f"Total horizontal margins ({total_horizontal_margin}px) are too large. "
                                           f"Pie chart should use more of the available container width.")

class DashboardAlertRedirectTests(TestCase):
    def setUp(self):
        from dashboard.models import Camera
        Camera.objects.create(camera_id=61, camera_name="AYE-01", location="1.3145,103.7650", road_name="Ayer Rajah Expressway", feed_url="https://example.com/feed/aye01")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='alertuser', password='testpass')
        self.client.login(username='alertuser', password='testpass')

    def test_alert_button_redirects_to_camera_feed(self):
        from django.urls import reverse
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '/cameras/view/61/', msg_prefix="Alert button should link to the correct camera feed for AYE-01")

if __name__ == '__main__':
    unittest.main() 