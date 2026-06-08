"""Access-control decorators: login + active subscription required."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.services.subscription_checker import has_active_subscription


def subscription_required(view_func):
    """Require an authenticated user with an active subscription.

    Superusers always pass. Authenticated users without an active
    subscription are redirected to the subscription-expired page.
    Anonymous users are sent to the login page.
    """

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if has_active_subscription(request.user):
            return view_func(request, *args, **kwargs)
        return redirect("subscription_expired")

    return _wrapped
