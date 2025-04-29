from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def map_home(request):
    """Main view that provides links to both maps."""
    return render(request, 'geomap/map_home.html')