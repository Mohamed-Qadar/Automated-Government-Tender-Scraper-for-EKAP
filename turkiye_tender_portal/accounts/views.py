from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.services.subscription_checker import get_profile


@login_required
def subscription_expired(request):
    """Shown when a logged-in user has no active subscription."""
    profile = get_profile(request.user)
    return render(
        request,
        "tenders/subscription_expired.html",
        {"profile": profile},
    )
