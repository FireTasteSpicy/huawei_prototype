from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from dashboard.models import *
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def dashboard(request):
    """Dashboard view showing summary statistics and recent notifications."""
    # Calculate time range for past 24 hours
    since = timezone.now() - timedelta(hours=24)

    # Query incidents in the past 24 hours
    # recent_incidents = Incident.objects.filter(timestamp__gte=since)
    # total_incidents = recent_incidents.count()
    # # total_infractions = recent_incidents.filter(incident_type__iexact='infraction').count()
    # total_infractions = recent_probs.filter(accident_prob_score__lt=0.4).count()
    recent_incidents = Incident.objects.filter(timestamp__gte=since)
    total_incidents = recent_incidents.count()

    # Calculate average emergency response time for incidents in past 24h
    avg_response_time = None
    if total_incidents > 0:
        # Get all response times for these incidents and compute average
        response_times = ResponseTime.objects.filter(incident__timestamp__gte=since)
        if response_times:
            avg_duration = sum([rt.response_time.total_seconds() for rt in response_times], 0.0) / response_times.count()
            avg_response_time = round(avg_duration/60.0, 1)  # in minutes, one decimal

    # Query accident probability scores in the past 24 hours
    recent_probs = AccidentProbabilityScore.objects.filter(timestamp__gte=since)
    low_risk_count = recent_probs.filter(accident_prob_score__lt=0.4).count()
    moderate_risk_count = recent_probs.filter(accident_prob_score__gte=0.4, accident_prob_score__lt=0.7).count()
    high_risk_count = recent_probs.filter(accident_prob_score__gte=0.7).count()

    total_infractions = low_risk_count
    # Count distinct areas (cameras) with moderate/high risk in past 24h
    moderate_risk_areas_count = recent_probs.filter(accident_prob_score__gte=0.4, accident_prob_score__lt=0.7) \
                                           .values('camera').distinct().count()
    high_risk_areas_count = recent_probs.filter(accident_prob_score__gte=0.7) \
                                       .values('camera').distinct().count()

    # Assemble notifications from past 24h (incidents or high-risk alerts)
    notifications = []
    # 1. Actual incidents as notifications
    for incident in recent_incidents:
       notifications.append({
           "message": f"{incident.incident_type.title()} on {incident.camera.road_name} "
                      f"(Severity: {incident.severity.title()})",
           "url": f"/cameras/view/{incident.camera.camera_id}/",
           "category": "incident",
           "timestamp": incident.timestamp
       })
    # 2. High or moderate risk threshold triggers as notifications
    threshold_alerts = recent_probs.filter(accident_prob_score__gte=0.6)
    for prob in threshold_alerts:
        score_pct = int(prob.accident_prob_score * 100)
        if prob.accident_prob_score >= 0.7:
            category = "threshold_triggered"
            msg = f"High risk threshold exceeded on {prob.camera.road_name} – accident probability {score_pct}%"
            url  = "/geomap/probability/?type=high%20risk"
        else:
            category = "threshold_triggered"
            msg = f"Moderate risk on {prob.camera.road_name} – accident probability {score_pct}%"
            url  = "/geomap/probability/?type=medium%20risk"

        notifications.append({
            "message": msg,
            "url": url,
            "category": category,
            "timestamp": prob.timestamp
        })

    # 3. If no notifications, use demo examples for display
    if not notifications:
        now = timezone.now()
        notifications = [
            {
                "message": "High risk threshold exceeded on PIE near Clementi Road – accident probability 83%",
                "url": "/geomap/probability/?type=high%20risk",
                "category": "threshold_triggered",
                "timestamp": now - timedelta(minutes=15)
            },
            {
                "message": "Traffic Accident on East Coast Parkway (Severity: High)",
                "url": "/cameras/view/1/",
                "category": "incident",
                "timestamp": now - timedelta(hours=1, minutes=5)
            },
            {
                "message": "System maintenance scheduled for tonight at 2:00 AM",
                "url": "#",
                "category": "message",
                "timestamp": now - timedelta(hours=2, minutes=30)
            },
            {
                "message": "Camera CTE-04 offline – maintenance required",
                "url": "/notifications/",
                "category": "alert",
                "timestamp": now - timedelta(hours=3, minutes=45)
            },
        ]

    context = {
        "total_incidents": total_incidents,
        "average_response_time": avg_response_time,  # in minutes (float or None)
        "total_infractions": total_infractions,
        "low_risk_count": low_risk_count,
        "moderate_risk_count": moderate_risk_count,
        "high_risk_count": high_risk_count,
        "moderate_risk_areas_count": moderate_risk_areas_count,
        "high_risk_areas_count": high_risk_areas_count,
        "notifications": notifications
    }
    return render(request, "dashboard/dashboard.html", context)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
