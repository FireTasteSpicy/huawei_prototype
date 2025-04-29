# dashboard/management/commands/seed_road_demo_probs.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from dashboard.models import Camera, AccidentProbabilityScore

class Command(BaseCommand):
    help = "Seed AccidentProbabilityScore points along major expressways"

    def handle(self, *args, **options):
        now = timezone.now()

        major_roads = [
            {"code": "PIE", "start": [1.3380, 103.6914], "end": [1.3715, 103.9798]},
            {"code": "ECP", "start": [1.2936, 103.8771], "end": [1.3164, 103.9798]},
            {"code": "CTE", "start": [1.2855, 103.8380], "end": [1.3850, 103.8549]},
        ]

        total = 0
        for road in major_roads:
            # look up by camera_name prefix, e.g. "PIE-"
            cams = Camera.objects.filter(camera_name__startswith=f"{road['code']}-")
            if not cams.exists():
                self.stdout.write(self.style.WARNING(
                    f"No cameras found with camera_name starting '{road['code']}-', skipping."))
                continue

            cam = cams.first()
            s_lat, s_lng = road["start"]
            e_lat, e_lng = road["end"]

            for _ in range(random.randint(20, 40)):
                r = random.random()
                lat = s_lat + r*(e_lat - s_lat) + (random.random()-0.5)*0.003
                lng = s_lng + r*(e_lng - s_lng) + (random.random()-0.5)*0.003

                # weight severity near ends
                score = random.uniform(0.7,1.0) if (r<0.1 or r>0.9) else random.uniform(0.3,0.7)

                AccidentProbabilityScore.objects.create(
                    camera=cam,
                    accident_prob_score=score,
                    timestamp=now - timedelta(hours=random.uniform(0,24)),
                    area_geometry=f"POINT({lat} {lng})"
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {total} demo accident-probability points across expressways."))
