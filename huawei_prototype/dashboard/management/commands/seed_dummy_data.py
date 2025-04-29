from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from dashboard.models import Camera, Incident, ResponseTime, AccidentProbabilityScore

class Command(BaseCommand):
    help = "Seed dummy data for cameras, incidents, response times, and probability scores"

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Ensure some cameras exist
        camera_specs = [
            {"camera_name": "ECP-01", "location": "1.3099,103.9053", "road_name": "East Coast Pkwy"},
            {"camera_name": "PIE-04", "location": "1.3347,103.7775", "road_name": "Pan Island Expwy"},
            {"camera_name": "CTE-09", "location": "1.3545,103.8390", "road_name": "Central Expwy"},
        ]
        cameras = []
        for spec in camera_specs:
            cam, _ = Camera.objects.get_or_create(
                camera_name=spec["camera_name"],
                defaults={
                    "location": spec["location"],
                    "road_name": spec["road_name"],
                    "feed_url": "https://example.com/feed/{}.mp4".format(spec["camera_name"].lower())
                }
            )
            cameras.append(cam)

        # 2. Create incidents & response times in past 24h
        for cam in cameras:
            for i, (itype, severity) in enumerate([
                ("Infraction", "low"),
                ("Traffic Accident", "high"),
                ("Vehicle Fire", "medium"),
            ]):
                ts = now - timedelta(hours=random.uniform(0, 24))
                incident = Incident.objects.create(
                    incident_type=itype,
                    severity=severity,
                    timestamp=ts,
                    camera=cam
                )
                # random response time between 2 and 15 minutes
                resp_secs = random.randint(120, 900)
                ResponseTime.objects.create(
                    incident=incident,
                    response_time=timedelta(seconds=resp_secs),
                    timestamp=ts + timedelta(minutes=1)
                )

        # 3. Create probability scores in past 24h
        for cam in cameras:
            for _ in range(3):
                ts = now - timedelta(hours=random.uniform(0, 24))
                AccidentProbabilityScore.objects.create(
                    camera=cam,
                    accident_prob_score=random.uniform(0.2, 0.95),
                    timestamp=ts,
                    area_geometry="POINT({} {})".format(*map(str, map(float, cam.location.split(','))))
                )

        self.stdout.write(self.style.SUCCESS("Dummy data seeded successfully."))
