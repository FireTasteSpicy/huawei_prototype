from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# User Authentication
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

# Camera Model
class Camera(models.Model):
    camera_id = models.AutoField(primary_key=True)
    camera_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)  # Coordinates as string, or consider using GeoDjango
    road_name = models.CharField(max_length=255)
    feed_url = models.URLField(max_length=255)
    
    def __str__(self):
        return self.camera_name

# Incident Model
class Incident(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    incident_id = models.AutoField(primary_key=True)
    incident_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text='Incident severity level'
    )
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='incidents')
    
    def __str__(self):
        return f"{self.incident_type} at {self.timestamp}"

# Response Time Model
class ResponseTime(models.Model):
    response_time_id = models.AutoField(primary_key=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='response_times')
    response_time = models.DurationField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response time: {self.response_time} for incident {self.incident_id}"

# Weather Model
class Weather(models.Model):
    weather_id = models.AutoField(primary_key=True)
    temperature = models.FloatField()
    conditions = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='weather_data')
    
    def __str__(self):
        return f"{self.conditions} at {self.temperature}°C"

# KPI Snapshot Model
class KPISnapshot(models.Model):
    kpi_snapshot_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_incidents = models.IntegerField(default=0)
    average_response_time = models.DurationField(null=True, blank=True)
    total_infractions = models.IntegerField(default=0)
    moderate_severity_count = models.IntegerField(default=0)
    high_severity_count = models.IntegerField(default=0)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='kpi_snapshots')
    
    def __str__(self):
        return f"KPI Snapshot at {self.timestamp}"

# Notification Model
class Notification(models.Model):
    CATEGORY_CHOICES = [
        ('threshold_triggered', 'Threshold Triggered'),
        ('message', 'Message'),
        ('alert', 'Alert'),
    ]
    
    notification_id = models.AutoField(primary_key=True)
    message = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    read_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    def __str__(self):
        return f"{self.category}: {self.message[:30]}..."

# Accident Probability Score Model
class AccidentProbabilityScore(models.Model):
    accident_prob_score_id = models.AutoField(primary_key=True)
    area_geometry = models.TextField()  # Consider using GeoDjango for proper geometry support
    accident_prob_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='accident_probabilitys')
    
    def __str__(self):
        return f"Risk score: {self.accident_prob_score} at {self.timestamp}"