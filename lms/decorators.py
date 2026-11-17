from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login


def login_required_message(view_func):
    """Require authentication and explain the Login redirect to anonymous visitors."""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        messages.warning(request, "Login First to access the page")
        return redirect_to_login(request.get_full_path())

    return wrapped_view
