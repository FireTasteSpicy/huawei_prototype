from django.core.management.base import BaseCommand
from dashboard.models import Camera, Weather, AccidentProbabilityScore, Incident, ResponseTime

class Command(BaseCommand):
    help = "Clear all seeded network data: cameras, weather, scores, incidents, response times"

    def handle(self, *args, **options):
        # Delete in order to respect FK constraints
        ResponseTime.objects.all().delete()
        Incident.objects.all().delete()
        AccidentProbabilityScore.objects.all().delete()
        Weather.objects.all().delete()
        Camera.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            "Cleared full network data (cameras, weather, scores, incidents, response times)."
        ))
