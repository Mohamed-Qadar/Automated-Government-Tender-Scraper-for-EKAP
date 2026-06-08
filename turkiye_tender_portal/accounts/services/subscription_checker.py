"""Subscription business logic, isolated from views for testability."""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone


def get_profile(user):
    """Return the related UserProfile or None."""
    return getattr(user, "profile", None)


def has_active_subscription(user) -> bool:
    """Whether the user may access paid features."""
    if user.is_superuser:
        return True
    profile = get_profile(user)
    if profile is None:
        return False
    profile.mark_expired_if_due()
    return profile.is_subscription_active


def activate_subscription(profile, days: int = 30, package_name: str = "") -> None:
    """Manually activate/extend a subscription (used by admin actions)."""
    from accounts.models import UserProfile

    today = timezone.localdate()
    start = profile.subscription_start_date or today
    # Extend from the later of today or the current end date.
    base = profile.subscription_end_date
    if base is None or base < today:
        base = today
    profile.subscription_status = UserProfile.STATUS_ACTIVE
    profile.subscription_start_date = start
    profile.subscription_end_date = base + timedelta(days=days)
    if package_name:
        profile.package_name = package_name
    profile.save()


def suspend_subscription(profile) -> None:
    from accounts.models import UserProfile

    profile.subscription_status = UserProfile.STATUS_SUSPENDED
    profile.save(update_fields=["subscription_status", "updated_at"])
