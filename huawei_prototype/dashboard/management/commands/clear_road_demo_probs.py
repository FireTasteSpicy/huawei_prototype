# dashboard/management/commands/clear_road_demo_probs.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from dashboard.models import AccidentProbabilityScore

class Command(BaseCommand):
    help = "Clear AccidentProbabilityScore points seeded by seed_road_demo_probs"

    def handle(self, *args, **options):
        # Build a Q filter for camera_name starting with each code
        codes = ["PIE-", "ECP-", "CTE-"]
        q_filter = Q(camera__camera_name__startswith=codes[0]) \
                | Q(camera__camera_name__startswith=codes[1]) \
                | Q(camera__camera_name__startswith=codes[2])

        qs = AccidentProbabilityScore.objects.filter(q_filter)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Cleared {count} road-pattern probability points."
        ))
