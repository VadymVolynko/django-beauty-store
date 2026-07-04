from functools import wraps

from django.shortcuts import redirect

OWNER_SESSION_KEY = "owner_access"


def owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get(OWNER_SESSION_KEY):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
