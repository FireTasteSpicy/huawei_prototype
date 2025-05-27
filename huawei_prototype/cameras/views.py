from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from dashboard.models import Camera, Weather, AccidentProbabilityScore, Incident
from django.db.models import Q
import logging, random, os
from datetime import datetime, timedelta
from django.conf import settings
from ultralytics import YOLO
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@login_required
def cameras(request):
    """List & search cameras (no demo-seeding if you already have data)."""
    search_query = request.GET.get('search', '')
    qs = Camera.objects.all()
    if search_query:
        qs = qs.filter(
            Q(camera_name__icontains=search_query) |
            Q(road_name__icontains=search_query)
        )
    qs = qs.order_by('camera_name')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    cameras_page = paginator.get_page(page)
    return render(request, "cameras/cameras.html", {
        'cameras': cameras_page,
        'search_query': search_query,
        'title': 'Camera Directory',
        'description': 'Directory of traffic cameras in the monitoring system.',
        'is_demo_data': False,
    })

@login_required
def camera_feed(request, camera_id):
    """Display & annotate a video clip via YOLOv8, log incidents."""
    camera = get_object_or_404(Camera, camera_id=camera_id)
    # blank out placeholder feeds
    if not camera.feed_url or camera.feed_url.startswith('http'):
        camera.feed_url = ''

    # weather
    try:
        w = Weather.objects.filter(camera=camera).latest('timestamp')
        weather = {"temperature": w.temperature, "conditions": w.conditions, "updated": w.timestamp}
    except Weather.DoesNotExist:
        weather = {"temperature": round(random.uniform(25.0,33.0),1),
                   "conditions": random.choice(["Sunny","Cloudy","Rain","Clear","Hazy"]),
                   "updated": datetime.now()}

    # accident prob
    try:
        p = AccidentProbabilityScore.objects.filter(camera=camera).latest('timestamp')
        acc_prob = p.accident_prob_score
    except AccidentProbabilityScore.DoesNotExist:
        acc_prob = round(random.uniform(0.2,0.8),2)
    risk = "High" if acc_prob>=0.7 else "Medium" if acc_prob>=0.4 else "Low"

    # YOLOv8 annotation (batch)
    if camera.feed_url:
        src = camera.feed_url.lstrip('/')
        video_path = os.path.join(settings.BASE_DIR, src)
        if os.path.exists(video_path):
            try:
                model = YOLO(settings.YOLO_MODEL_PATH)
                out_dir = os.path.join(settings.MEDIA_ROOT, "annotated")
                os.makedirs(out_dir, exist_ok=True)
                results = model.predict(
                    source=video_path,
                    conf=0.5,
                    save=True,
                    project=out_dir,
                    name=f"camera_{camera.camera_id}",
                    save_txt=False
                )
                out_video = os.path.join(out_dir, f"camera_{camera.camera_id}", os.path.basename(video_path))
                if os.path.exists(out_video):
                    camera.feed_url = settings.MEDIA_URL + f"annotated/camera_{camera.camera_id}/" + os.path.basename(video_path)
                # log incidents
                seen = set()
                for res in results:
                    for cls in getattr(res.boxes, "cls", []):
                        name = res.names[int(cls)]
                        seen.add(name)
                for itype in seen:
                    Incident.objects.create(incident_type=itype, camera=camera)
            except Exception as e:
                logger.error(f"YOLO inference error: {e}")

    return render(request, "cameras/camera_feed.html", {
        'camera': camera,
        'weather': weather,
        'accident_prob_score': acc_prob,
        'risk_level': risk,
        'timestamp': datetime.now(),
        'title': f"Camera: {camera.camera_name}",
        'description': f"Live feed and details for camera {camera.camera_name}"
    })
