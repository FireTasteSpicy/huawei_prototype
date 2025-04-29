from django.core.management.base import BaseCommand
from django.db.models import Q
from dashboard.models import Camera, Weather, AccidentProbabilityScore, Incident, ResponseTime

class Command(BaseCommand):
    help = "Clear all cameras and related data seeded by seed_network_with_osm"

    def handle(self, *args, **options):
        # Include every expressway code you seed
        prefixes = ["PIE-", "ECP-", "CTE-", "AYE-", "TPE-", "KPE-"]
        cam_filter = Q()
        for p in prefixes:
            cam_filter |= Q(camera_name__startswith=p)

        cams = Camera.objects.filter(cam_filter)

        # Delete in FK-safe order
        ResponseTime.objects.filter(incident__camera__in=cams).delete()
        Incident.objects.filter(camera__in=cams).delete()
        AccidentProbabilityScore.objects.filter(camera__in=cams).delete()
        Weather.objects.filter(camera__in=cams).delete()
        deleted_count, _ = cams.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Cleared {deleted_count} seeded cameras and all related data."
        ))
