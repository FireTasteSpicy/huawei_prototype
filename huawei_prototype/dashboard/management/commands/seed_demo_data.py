from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from dashboard.models import (
    Camera, Incident, ResponseTime,
    AccidentProbabilityScore, Weather
)

class Command(BaseCommand):
    help = "Seed all demo fallback data (cameras, incidents, probs, weather)"

    def handle(self, *args, **options):
        now = timezone.now()

        # ——— 1. Cameras ———
        demo_cameras = [
            {
                "camera_name": "ECP-01",
                "location": "1.3099,103.9053",
                "road_name": "East Coast Parkway",
                "feed_url": "https://example.com/feed/ecp01.mp4"
            },
            {
                "camera_name": "PIE-04",
                "location": "1.3347,103.7775",
                "road_name": "Pan Island Expressway",
                "feed_url": "https://example.com/feed/pie04.mp4"
            },
            {
                "camera_name": "CTE-09",
                "location": "1.3545,103.8390",
                "road_name": "Central Expressway",
                "feed_url": "https://example.com/feed/cte09.mp4"
            },
            {
                "camera_name": "AYE-02",
                "location": "1.3145,103.7650",
                "road_name": "Ayer Rajah Expressway",
                "feed_url": "https://example.com/feed/aye02.mp4"
            },
            {
                "camera_name": "TPE-07",
                "location": "1.3800,103.9150",
                "road_name": "Tampines Expressway",
                "feed_url": "https://example.com/feed/tpe07.mp4"
            },
        ]
        cameras = []
        for spec in demo_cameras:
            cam, created = Camera.objects.get_or_create(
                camera_name=spec["camera_name"],
                defaults={
                    "location": spec["location"],
                    "road_name": spec["road_name"],
                    "feed_url": spec["feed_url"]
                }
            )
            cameras.append(cam)

        # ——— 2. Incidents & ResponseTimes ———
        demo_incidents = [
            {
                "type": "Traffic Accident",
                "severity": "high",
                "camera": "ECP-01",
                "timestamp": "2025-04-13 14:25:30"
            },
            {
                "type": "Vehicle Fire",
                "severity": "medium",
                "camera": "PIE-04",
                "timestamp": "2025-04-13 15:10:45"
            },
            {
                "type": "Traffic Infraction",
                "severity": "low",
                "camera": "CTE-09",
                "timestamp": "2025-04-13 13:55:20"
            },
        ]
        for entry in demo_incidents:
            # ts = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
            # # localize to UTC
            # ts = ts.replace(tzinfo=timezone.utc)
            ts = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
            # make an aware datetime in your current timezone
            ts = timezone.make_aware(ts)
            cam = Camera.objects.get(camera_name=entry["camera"])
            inc = Incident.objects.create(
                incident_type=entry["type"],
                severity=entry["severity"],
                timestamp=ts,
                camera=cam
            )
            # fake a 5-minute response
            ResponseTime.objects.create(
                incident=inc,
                response_time=timedelta(minutes=5),
                timestamp=ts + timedelta(minutes=1)
            )

        # ——— 3. AccidentProbabilityScores ———
        # seed 3 fixed scores per camera (so heatmap + markers show)
        for cam in cameras:
            for score in [0.8, 0.5, 0.3]:
                AccidentProbabilityScore.objects.create(
                    camera=cam,
                    accident_prob_score=score,
                    timestamp=now - timedelta(hours=random.uniform(1, 23)),
                    area_geometry=cam.location
                )

        # ——— 4. Weather ———
        demo_conditions = [
            "Sunny", "Partly Cloudy", "Light Rain",
            "Clear", "Cloudy", "Thunderstorm", "Hazy"
        ]
        for cam in cameras:
            Weather.objects.create(
                camera=cam,
                temperature=round(random.uniform(25.0, 33.0), 1),
                conditions=random.choice(demo_conditions),
                timestamp=now - timedelta(minutes=random.randint(5, 60))
            )

        self.stdout.write(self.style.SUCCESS("Demo fallback data seeded successfully."))
