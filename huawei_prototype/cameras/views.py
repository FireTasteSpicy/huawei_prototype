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
    camera = get_object_or_404(Camera, camera_id=camera_id)
    if not camera.feed_url or camera.feed_url.startswith('http'):
        return HttpResponseNotFound("No local video.")
    cap = cv2.VideoCapture(os.path.join(settings.BASE_DIR, camera.feed_url.lstrip('/')))
    if not cap.isOpened():
        return HttpResponseNotFound("Cannot open video.")

    # Define how each class maps to severity
    severity_map = {
        "Multiple collision": "high",
        "Vehicle fire":       "high",
        "Vehicular accident": "medium",
        "Reckless driving":   "medium",
        "Tailgating":         "medium",
        "Self-accident":      "medium",
    }

    # Ranking for selecting the "worst" class in an event
    severity_ranking = [
        "Multiple collision",
        "Vehicle fire",
        "Vehicular accident",
        "Reckless driving",
        "Tailgating",
        "Self-accident",
    ]

    in_event = False
    event_buffer = set()
    no_det_count = 0
    no_det_threshold = 5

    def gen():
        nonlocal in_event, event_buffer, no_det_count

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            res = model(frame)[0]
            img = res.plot()

            frame_classes = [res.names[int(c)] for c in getattr(res.boxes, "cls", [])]

            if frame_classes:
                if not in_event:
                    in_event = True
                    event_buffer.clear()
                    no_det_count = 0
                event_buffer.update(frame_classes)
                no_det_count = 0
            else:
                if in_event:
                    no_det_count += 1
                    if no_det_count >= no_det_threshold:
                        # Event ended → choose highest‐severity class
                        chosen = min(event_buffer, key=lambda x: severity_ranking.index(x))
                        sev = severity_map.get(chosen, "medium")
                        Incident.objects.create(
                            incident_type=chosen,
                            severity=sev,
                            camera=camera
                        )
                        in_event = False
                        event_buffer.clear()
                        no_det_count = 0

            success, jpeg = cv2.imencode('.jpg', img)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() +
                       b'\r\n')

        # Flush any open event at end of video
        if in_event and event_buffer:
            chosen = min(event_buffer, key=lambda x: severity_ranking.index(x))
            sev = severity_map.get(chosen, "medium")
            Incident.objects.create(
                incident_type=chosen,
                severity=sev,
                camera=camera
            )
        cap.release()

    return StreamingHttpResponse(
        gen(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
