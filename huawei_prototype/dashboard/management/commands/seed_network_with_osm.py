from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

import osmnx as ox
import numpy as np
from shapely.ops import unary_union

from dashboard.models import (
    Camera, Weather, AccidentProbabilityScore,
    Incident, ResponseTime
)

class Command(BaseCommand):
    help = "Seed cameras + data along real expressway geometries via OSMnx"

    def handle(self, *args, **options):
        now = timezone.now()

        # 1) Define the expressways you want to sample by their OSM name and codes
        expressways = [
            {"name": "Pan Island Expressway", "code": "PIE"},
            {"name": "East Coast Parkway",  "code": "ECP"},
            {"name": "Central Expressway",   "code": "CTE"},
            {"name": "Ayer Rajah Expressway", "code": "AYE"},
            {"name": "Tampines Expressway",   "code": "TPE"},
            {"name": "Kallang-Paya Lebar Expressway", "code": "KPE"},
        ]

        # 2) Download Singapore’s drivable graph once
        self.stdout.write("Fetching Singapore road network…")
        G = ox.graph_from_place("Singapore", network_type="drive")
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

        total_cams = total_scores = total_incidents = 0

        for road in expressways:
            name = road["name"]
            code = road["code"]
            self.stdout.write(f"Processing {name}…")

            # Flexible, case-insensitive substring match on OSM name tag
            mask = edges["name"].apply(
                lambda x: (
                    any(name.lower() in n.lower() for n in x) if isinstance(x, list)
                    else (isinstance(x, str) and name.lower() in x.lower())
                )
            )
            selected = edges[mask]
            if selected.empty:
                self.stdout.write(self.style.WARNING(f"No OSM edges found for {name}."))
                continue

            # Merge into a single MultiLineString
            road_geom = unary_union(selected.geometry.values)
            length = road_geom.length  # meters

            # Place N cameras along the real geometry
            N = 20
            distances = np.linspace(0, length, N)

            for idx, dist in enumerate(distances, start=1):
                point = road_geom.interpolate(dist)
                lng, lat = point.x, point.y
                cam_name = f"{code}-{idx:02d}"

                cam, created = Camera.objects.get_or_create(
                    camera_name=cam_name,
                    defaults={
                        "location": f"{lat:.6f},{lng:.6f}",
                        "road_name": name,
                        "feed_url": f"https://example.com/feed/{cam_name.lower()}.mp4"
                    }
                )
                total_cams += 1

                # Seed weather
                Weather.objects.create(
                    camera=cam,
                    temperature=round(random.uniform(25.0, 33.0), 1),
                    conditions=random.choice([
                        "Sunny", "Partly Cloudy", "Light Rain",
                        "Clear", "Cloudy", "Thunderstorm", "Hazy"
                    ]),
                    timestamp=now - timedelta(minutes=random.randint(1, 60))
                )

                # Seed probability score
                score = random.uniform(0.2, 0.95)
                AccidentProbabilityScore.objects.create(
                    camera=cam,
                    accident_prob_score=score,
                    timestamp=now - timedelta(hours=random.uniform(0, 24)),
                    area_geometry=f"POINT({lat} {lng})"
                )
                total_scores += 1

                # Seed incidents + response times
                for _ in range(random.randint(0, 2)):
                    itype, severity = random.choice([
                        ("Traffic Infraction", "low"),
                        ("Traffic Accident",  "high"),
                        ("Vehicle Fire",      "medium"),
                    ])
                    ts = now - timedelta(hours=random.uniform(0, 24))
                    inc = Incident.objects.create(
                        camera=cam,
                        incident_type=itype,
                        severity=severity,
                        timestamp=ts
                    )
                    ResponseTime.objects.create(
                        incident=inc,
                        response_time=timedelta(seconds=random.randint(120, 900)),
                        timestamp=ts + timedelta(minutes=1)
                    )
                    total_incidents += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {total_cams} cameras, {total_scores} scores, {total_incidents} incidents."
        ))

