from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from dashboard.models import (
    Camera, Weather, AccidentProbabilityScore,
    Incident, ResponseTime
)

class Command(BaseCommand):
    help = "Seed a full network: cameras along roads + weather, scores, incidents"

    def handle(self, *args, **options):
        now = timezone.now()

        # 1) Define your roads (start/end coords + code)
        roads = [
            {"code": "PIE", "start": [1.3380, 103.6914], "end": [1.3715, 103.9798]},
            {"code": "ECP", "start": [1.2936, 103.8771], "end": [1.3164, 103.9798]},
            {"code": "CTE", "start": [1.2855, 103.8380], "end": [1.3850, 103.8549]},
        ]

        total_cams = 0
        total_scores = 0
        total_incidents = 0

        for road in roads:
            start_lat, start_lng = road["start"]
            end_lat,   end_lng   = road["end"]
            code = road["code"]

            # 2) Create N cameras evenly spaced
            N = 15
            for i in range(N):
                ratio = i / float(N - 1)
                lat = start_lat + ratio * (end_lat - start_lat)
                lng = start_lng + ratio * (end_lng - start_lng)
                name = f"{code}-{i+1:02d}"
                obj, created = Camera.objects.get_or_create(
                    camera_name=name,
                    defaults={
                        "location": f"{lat:.6f},{lng:.6f}",
                        "road_name": f"{road['code']} Expressway",
                        "feed_url": f"https://example.com/feed/{name.lower()}.mp4"
                    }
                )
                total_cams += 1

                # 3) Weather at camera
                Weather.objects.create(
                    camera=obj,
                    temperature=round(random.uniform(25.0, 33.0), 1),
                    conditions=random.choice([
                        "Sunny", "Partly Cloudy", "Light Rain",
                        "Clear", "Cloudy", "Thunderstorm", "Hazy"
                    ]),
                    timestamp=now - timedelta(minutes=random.randint(1, 60))
                )

                # 4) AccidentProbabilityScore per camera
                score = random.uniform(0.2, 0.95)
                AccidentProbabilityScore.objects.create(
                    camera=obj,
                    accident_prob_score=score,
                    timestamp=now - timedelta(hours=random.uniform(0, 24)),
                    area_geometry=f"POINT({lat} {lng})"
                )
                total_scores += 1

                # 5) Random 0–3 incidents per camera
                for _ in range(random.randint(0, 3)):
                    itype, sev = random.choice([
                        ("Traffic Infraction", "low"),
                        ("Traffic Accident", "high"),
                        ("Vehicle Fire",   "medium"),
                    ])
                    ts = now - timedelta(hours=random.uniform(0, 24))
                    incident = Incident.objects.create(
                        camera=obj,
                        incident_type=itype,
                        severity=sev,
                        timestamp=ts
                    )
                    total_incidents += 1

                    # random response time (2–15 min)
                    resp = timedelta(seconds=random.randint(120, 900))
                    ResponseTime.objects.create(
                        incident=incident,
                        response_time=resp,
                        timestamp=ts + timedelta(minutes=1)
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {total_cams} cameras, "
            f"{total_scores} probability scores, "
            f"{total_incidents} incidents."
        ))
