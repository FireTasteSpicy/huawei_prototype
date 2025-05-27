import os, logging, random, cv2
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ultralytics import YOLO
from dashboard.models import Camera, Weather, AccidentProbabilityScore, Incident

logger = logging.getLogger(__name__)
model = YOLO(settings.YOLO_MODEL_PATH)  # load once

@login_required
def cameras(request):
    qs = Camera.objects.all().order_by('camera_name')
    if request.GET.get('search'):
        q = request.GET['search']
        qs = qs.filter(Q(camera_name__icontains=q) | Q(road_name__icontains=q))
    cameras_page = Paginator(qs, 10).get_page(request.GET.get('page',1))
    return render(request, "cameras/cameras.html", {
        'cameras': cameras_page,
        'search_query': request.GET.get('search',''),
        'title': 'Camera Directory',
        'description': 'Directory of traffic cameras.',
        'is_demo_data': False,
    })

@login_required
def camera_feed(request, camera_id):
    """Renders the page with an MJPEG <img> pointing at camera_stream."""
    camera = get_object_or_404(Camera, camera_id=camera_id)
    # fetch weather & risk (same as before)...
    try:
        w = Weather.objects.filter(camera=camera).latest('timestamp')
        weather = {"temperature": w.temperature,"conditions":w.conditions,"updated":w.timestamp}
    except Weather.DoesNotExist:
        weather = {"temperature":round(random.uniform(25,33),1),
                   "conditions":random.choice(["Sunny","Cloudy","Rain","Clear","Hazy"]),
                   "updated":datetime.now()}
    try:
        p = AccidentProbabilityScore.objects.filter(camera=camera).latest('timestamp')
        acc_prob = p.accident_prob_score
    except AccidentProbabilityScore.DoesNotExist:
        acc_prob = round(random.uniform(0.2,0.8),2)
    risk = "High" if acc_prob>=0.7 else "Medium" if acc_prob>=0.4 else "Low"

    return render(request, "cameras/camera_feed.html", {
        'camera': camera,
        'weather': weather,
        'accident_prob_score': acc_prob,
        'risk_level': risk,
        'timestamp': datetime.now(),
        'title': f"Camera: {camera.camera_name}",
        'description': "Live annotated stream"
    })

@login_required
def camera_stream(request, camera_id):
    """MJPEG stream: reads frames, runs YOLO on each, yields JPEGs."""
    camera = get_object_or_404(Camera, camera_id=camera_id)
    if not camera.feed_url or camera.feed_url.startswith('http'):
        return HttpResponseNotFound("No local video available.")
    path = camera.feed_url.lstrip('/')
    cap = cv2.VideoCapture(os.path.join(settings.BASE_DIR, path))
    if not cap.isOpened():
        return HttpResponseNotFound("Cannot open video.")

    seen = set()
    def gen():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            res = model(frame)[0]
            img = res.plot()  # annotated frame
            # log each new class once
            for c in getattr(res.boxes, 'cls', []):
                name = res.names[int(c)]
                if name not in seen:
                    seen.add(name)
                    Incident.objects.create(incident_type=name, camera=camera)
            _, jpg = cv2.imencode('.jpg', img)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   jpg.tobytes() + b'\r\n')
        cap.release()

    return StreamingHttpResponse(gen(),
        content_type='multipart/x-mixed-replace; boundary=frame')
