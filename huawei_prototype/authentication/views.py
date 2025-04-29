from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    """Login view – uses Django's built-in authentication."""
    if request.user.is_authenticated:
        return redirect('dashboard')  # already logged in, go to dashboard
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next page if specified, otherwise dashboard
            next_page = request.POST.get('next') or request.GET.get('next')
            return redirect(next_page if next_page else 'dashboard')
        else:
            # Invalid credentials, re-render login with error
            return render(request, 'authentication/login.html', {
                'error': 'Invalid username or password',
                'next': request.GET.get('next', '')
            })
    else:
        # GET request: render login form
        return render(request, 'authentication/login.html', {
            'next': request.GET.get('next', '')
        })

@login_required
def logout_view(request):
    """Logout the user and redirect to login page."""
    logout(request)
    return redirect('login')
