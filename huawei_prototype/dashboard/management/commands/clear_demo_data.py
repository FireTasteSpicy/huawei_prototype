from django.core.management.base import BaseCommand
from dashboard.models import (
    Camera, Incident, ResponseTime,
    AccidentProbabilityScore, Weather
)

class Command(BaseCommand):
    help = "Clear all demo fallback data (from seed_demo_data)"

    def handle(self, *args, **options):
        # Demo cameras you seeded
        demo_camera_names = [
            "ECP-01", "PIE-04", "CTE-09",
            "AYE-02", "TPE-07"
        ]
        # Delete response times & incidents tied to those cameras
        ResponseTime.objects.filter(
            incident__camera__camera_name__in=demo_camera_names
        ).delete()
        Incident.objects.filter(
            camera__camera_name__in=demo_camera_names
        ).delete()

        # Delete probability scores where area_geometry equals the camera.loc string
        AccidentProbabilityScore.objects.filter(
            camera__camera_name__in=demo_camera_names,
            area_geometry__in=[
                Camera.objects.get(camera_name=name).location
                for name in demo_camera_names
            ]
        ).delete()

        # Delete weather entries for those cameras
        Weather.objects.filter(
            camera__camera_name__in=demo_camera_names
        ).delete()

        # Finally, delete the demo cameras themselves
        Camera.objects.filter(
            camera_name__in=demo_camera_names
        ).delete()

        self.stdout.write(self.style.SUCCESS(
            "Demo fallback data cleared."
        ))
