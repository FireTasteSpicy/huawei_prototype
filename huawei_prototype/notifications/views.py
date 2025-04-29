from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from dashboard.models import Notification, User
from datetime import datetime, timedelta
import logging
import random
from django.contrib.auth.decorators import login_required

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def notifications(request):
    """View for displaying and managing user notifications."""
    
    # Handle marking notifications as read/unread
    if request.GET.get('mark_read'):
        try:
            notification_id = int(request.GET.get('mark_read'))
            notification = Notification.objects.get(notification_id=notification_id)
            notification.read_status = True
            notification.save()
            logger.info(f"Notification {notification_id} marked as read")
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
    
    if request.GET.get('mark_unread'):
        try:
            notification_id = int(request.GET.get('mark_unread'))
            notification = Notification.objects.get(notification_id=notification_id)
            notification.read_status = False
            notification.save()
            logger.info(f"Notification {notification_id} marked as unread")
        except Exception as e:
            logger.error(f"Error marking notification as unread: {e}")
    
    # Filter notifications by status
    status_filter = request.GET.get('status', 'all')
    
    # Get current user (you'll need to implement user authentication)
    # For now, just get all notifications
    if status_filter == 'unread':
        notifications_list = Notification.objects.filter(read_status=False).order_by('-timestamp')
    elif status_filter == 'read':
        notifications_list = Notification.objects.filter(read_status=True).order_by('-timestamp')
    else:  # 'all'
        notifications_list = Notification.objects.all().order_by('-timestamp')
    
    # If no notifications found, create mock data
    if not notifications_list:
        logger.info("No notifications found, generating mock data")
        mock_notifications = []
        
        # Try to get a demo user or create one
        try:
            demo_user = User.objects.first()
            if not demo_user:
                demo_user = User.objects.create(
                    username="demo_user",
                    password="not_a_real_password",
                    email="demo@example.com"
                )
        except Exception as e:
            logger.error(f"Error getting/creating demo user: {e}")
            # Create a simple data structure for mock notifications without DB
            class MockNotification:
                def __init__(self, id, message, category, read_status, timestamp):
                    self.notification_id = id
                    self.message = message
                    self.category = category
                    self.read_status = read_status
                    self.timestamp = timestamp
            
            # Demo notification templates
            mock_data = [
                # Threshold alerts
                {
                    "message": "High risk threshold exceeded on PIE near Clementi Road - accident probability 83%",
                    "category": "threshold_triggered",
                    "read_status": False,
                    "timestamp": datetime.now() - timedelta(minutes=17)
                },
                {
                    "message": "Moderate risk detected on ECP near Marine Parade - accident probability 62%",
                    "category": "threshold_triggered",
                    "read_status": True,
                    "timestamp": datetime.now() - timedelta(hours=3)
                },
                # System alerts
                {
                    "message": "Camera CTE-04 offline - maintenance required",
                    "category": "alert",
                    "read_status": False,
                    "timestamp": datetime.now() - timedelta(hours=1)
                },
                {
                    "message": "Weather station at Changi reporting severe conditions",
                    "category": "alert",
                    "read_status": False,
                    "timestamp": datetime.now() - timedelta(minutes=45)
                },
                # Regular messages
                {
                    "message": "System maintenance scheduled for tonight at 2:00 AM",
                    "category": "message",
                    "read_status": True,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "message": "Weekly traffic report summary generated and available for download",
                    "category": "message",
                    "read_status": True,
                    "timestamp": datetime.now() - timedelta(days=2)
                },
                {
                    "message": "New camera TPE-09 added to monitoring network",
                    "category": "message",
                    "read_status": False,
                    "timestamp": datetime.now() - timedelta(hours=5)
                }
            ]
            
            # Create mock notifications
            for i, data in enumerate(mock_data):
                mock_notifications.append(
                    MockNotification(
                        id=i+1,
                        message=data["message"],
                        category=data["category"],
                        read_status=data["category"] != "threshold_triggered" and random.random() > 0.3,
                        timestamp=data["timestamp"]
                    )
                )
            
            # Filter mock data based on status filter
            if status_filter == 'unread':
                mock_notifications = [n for n in mock_notifications if not n.read_status]
            elif status_filter == 'read':
                mock_notifications = [n for n in mock_notifications if n.read_status]
            
            # For pagination
            paginator = Paginator(mock_notifications, 10)
            page = request.GET.get('page', 1)
            notifications = paginator.get_page(page)
            
            # Status types for filter UI
            status_types = ['all', 'unread', 'read']
            
            return render(
                request,
                "notifications/notifications.html",
                {
                    'notifications': notifications,
                    'status_types': status_types,
                    'selected_status': status_filter,
                    'title': 'Notifications',
                    'description': 'System notifications and alerts.',
                    'is_demo_data': True
                }
            )
            
        # Create real mock notifications in the database
        mock_data = [
            # Threshold alerts
            {
                "message": "High risk threshold exceeded on PIE near Clementi Road - accident probability 83%",
                "category": "threshold_triggered",
                "read_status": False,
                "timestamp": datetime.now() - timedelta(minutes=17)
            },
            {
                "message": "Moderate risk detected on ECP near Marine Parade - accident probability 62%",
                "category": "threshold_triggered", 
                "read_status": True,
                "timestamp": datetime.now() - timedelta(hours=3)
            },
            # System alerts
            {
                "message": "Camera CTE-04 offline - maintenance required",
                "category": "alert",
                "read_status": False,
                "timestamp": datetime.now() - timedelta(hours=1)
            },
            {
                "message": "Weather station at Changi reporting severe conditions",
                "category": "alert",
                "read_status": False,
                "timestamp": datetime.now() - timedelta(minutes=45)
            },
            # Regular messages
            {
                "message": "System maintenance scheduled for tonight at 2:00 AM",
                "category": "message",
                "read_status": True,
                "timestamp": datetime.now() - timedelta(days=1)
            },
            {
                "message": "Weekly traffic report summary generated and available for download",
                "category": "message",
                "read_status": True,
                "timestamp": datetime.now() - timedelta(days=2)
            },
            {
                "message": "New camera TPE-09 added to monitoring network",
                "category": "message",
                "read_status": False,
                "timestamp": datetime.now() - timedelta(hours=5)
            }
        ]
        
        # Create notifications in the database
        for data in mock_data:
            try:
                notification = Notification.objects.create(
                    message=data["message"],
                    category=data["category"],
                    read_status=data["read_status"],
                    user=demo_user
                )
                # Override auto timestamp for demo purposes
                notification.timestamp = data["timestamp"]
                notification.save(update_fields=['timestamp'])
                mock_notifications.append(notification)
            except Exception as e:
                logger.error(f"Error creating mock notification: {e}")
        
        # Re-query based on filter to get the mock data
        if status_filter == 'unread':
            notifications_list = Notification.objects.filter(read_status=False).order_by('-timestamp')
        elif status_filter == 'read':
            notifications_list = Notification.objects.filter(read_status=True).order_by('-timestamp')
        else:  # 'all'
            notifications_list = Notification.objects.all().order_by('-timestamp')
    
    # Pagination (10 notifications per page)
    paginator = Paginator(notifications_list, 10)
    page = request.GET.get('page', 1)
    notifications = paginator.get_page(page)
    
    # Status types for filter UI
    status_types = ['all', 'unread', 'read']
    
    return render(
        request,
        "notifications/notifications.html",
        {
            'notifications': notifications,
            'status_types': status_types,
            'selected_status': status_filter,
            'title': 'Notifications',
            'description': 'System notifications and alerts.',
            'is_demo_data': not bool(notifications_list.exists() if hasattr(notifications_list, 'exists') else notifications_list)
        }
    )