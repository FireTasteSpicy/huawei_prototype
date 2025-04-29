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

        # 1) Define the expressways you want to sample by their OSM name
        expressways = [
            "Pan Island Expressway",
            "East Coast Parkway",
            "Central Expressway",
        ]

        # 2) Download Singapore’s drivable graph once
        self.stdout.write("Fetching Singapore road network…")
        G = ox.graph_from_place("Singapore", network_type="drive")
        # Convert edges to GeoDataFrame
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

        total_cams = total_scores = total_incidents = 0

        for road_name in expressways:
            self.stdout.write(f"Processing {road_name}…")
            # Filter edges whose 'name' contains our road_name
            mask = edges["name"].apply(
                lambda x: any(road_name == n for n in x) if isinstance(x, list)
                else (road_name == x)
            )
            selected = edges[mask]
            if selected.empty:
                self.stdout.write(self.style.WARNING(f"No OSM edges found for {road_name}."))
                continue

            # Merge into a single MultiLineString
            road_geom = unary_union(selected.geometry.values)
            length = road_geom.length  # in meters (approx.)

            # 3) Choose how many cameras you want along it
            N = 20
            distances = np.linspace(0, length, N)

            for idx, dist in enumerate(distances):
                # interpolate point along the line
                point = road_geom.interpolate(dist)
                lng, lat = point.x, point.y  # shapely gives x=lon, y=lat
                cam_name = f"{road_name.split()[0][:3].upper()}-{idx+1:02d}"

                # Create or get camera
                cam, created = Camera.objects.get_or_create(
                    camera_name=cam_name,
                    defaults={
                        "location": f"{lat:.6f},{lng:.6f}",
                        "road_name": road_name,
                        "feed_url": f"https://example.com/feed/{cam_name.lower()}.mp4"
                    }
                )
                total_cams += 1

                # Seed one weather reading
                Weather.objects.create(
                    camera=cam,
                    temperature=round(random.uniform(25.0, 33.0), 1),
                    conditions=random.choice([
                        "Sunny", "Partly Cloudy", "Light Rain",
                        "Clear", "Cloudy", "Thunderstorm", "Hazy"
                    ]),
                    timestamp=now - timedelta(minutes=random.randint(1, 60))
                )

                # Seed one probability score
                score = random.uniform(0.2, 0.95)
                AccidentProbabilityScore.objects.create(
                    camera=cam,
                    accident_prob_score=score,
                    timestamp=now - timedelta(hours=random.uniform(0, 24)),
                    area_geometry=f"POINT({lat} {lng})"
                )
                total_scores += 1

                # Seed 0–2 incidents + response times
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
            f"Seed complete: {total_cams} cameras, "
            f"{total_scores} scores, {total_incidents} incidents."
        ))
