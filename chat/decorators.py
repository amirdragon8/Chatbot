from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from functools import wraps

from django.urls import reverse

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "You need to log in to access this page.")
                return redirect('authentification:signin')  # Redirect to login page
            if request.user.role != required_role:
                messages.error(request, "Access denied. You do not have permission to access this page.")
                return redirect('authentification:index')  # Redirect to main page
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def unauthenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Redirect authenticated users to a main page
            messages.error(request, "Access denied. You already have user account.")
            return redirect('authentification:index')  # Redirect to main page
        return view_func(request, *args, **kwargs)
    
    return wrapper
