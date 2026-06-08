"""Auto-create a UserProfile (with trial subscription) for every new user."""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    from .models import UserProfile

    today = timezone.localdate()
    trial_days = getattr(settings, "DEFAULT_TRIAL_DAYS", 14)
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            "subscription_status": UserProfile.STATUS_TRIAL,
            "subscription_start_date": today,
            "subscription_end_date": today + timedelta(days=trial_days),
            "package_name": "Deneme",
        },
    )
