from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks if the user has a specific role.
    Usage: @role_required(['ADMIN', 'CONTRACTOR'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role in allowed_roles or request.user.role == 'ADMIN':
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator
