from django.shortcuts import render

def map_home(request):
    """Main view that provides links to both maps."""
    return render(request, 'geomap/map_home.html')