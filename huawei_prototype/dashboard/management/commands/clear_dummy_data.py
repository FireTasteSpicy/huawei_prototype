# dashboard/management/commands/clear_dummy_data.py
from django.core.management.base import BaseCommand
from dashboard.models import Incident, ResponseTime, AccidentProbabilityScore, Camera

class Command(BaseCommand):
    help = "Clear out all dummy data"

    def handle(self, *args, **options):
        ResponseTime.objects.all().delete()
        Incident.objects.all().delete()
        AccidentProbabilityScore.objects.all().delete()
        # If you want to remove demo cameras too:
        Camera.objects.filter(camera_name__in=["ECP-01","PIE-04","CTE-09"]).delete()
        self.stdout.write(self.style.SUCCESS("Dummy data cleared."))
