"""Expose subscription info to all templates."""
from accounts.services.subscription_checker import get_profile, has_active_subscription


def subscription_context(request):
    if not request.user.is_authenticated:
        return {}
    profile = get_profile(request.user)
    return {
        "user_profile": profile,
        "subscription_active": has_active_subscription(request.user),
    }
