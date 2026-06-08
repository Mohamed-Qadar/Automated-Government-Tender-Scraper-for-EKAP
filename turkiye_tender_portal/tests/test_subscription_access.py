from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class SubscriptionAccessTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def _make_user(self, username, status, days=10):
        user = User.objects.create_user(username=username, password="pass12345")
        profile = user.profile  # auto-created by signal
        profile.subscription_status = status
        profile.subscription_start_date = self.today
        profile.subscription_end_date = self.today + timedelta(days=days)
        profile.save()
        return user

    def test_unauthenticated_user_redirected_to_login(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp.url)

    def test_active_user_can_access_dashboard(self):
        self._make_user("active1", "active")
        self.client.login(username="active1", password="pass12345")
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_active_user_can_access_tender_list(self):
        self._make_user("active2", "active")
        self.client.login(username="active2", password="pass12345")
        resp = self.client.get(reverse("tender_list"))
        self.assertEqual(resp.status_code, 200)

    def test_expired_user_redirected_from_dashboard(self):
        self._make_user("expired1", "active", days=-5)  # ended in the past
        self.client.login(username="expired1", password="pass12345")
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("subscription_expired"), resp.url)

    def test_expired_user_cannot_export_excel(self):
        self._make_user("expired2", "expired", days=-1)
        self.client.login(username="expired2", password="pass12345")
        resp = self.client.get(reverse("export_excel"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("subscription_expired"), resp.url)

    def test_superuser_always_allowed(self):
        User.objects.create_superuser("admin1", "a@a.com", "pass12345")
        self.client.login(username="admin1", password="pass12345")
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
