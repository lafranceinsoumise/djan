import pytest
from django.contrib.auth.models import User
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from pytest_django.asserts import assertContains, assertRedirects

pytestmark = pytest.mark.django_db

LOGIN_URL = "/admin/login/?next=/admin/"


@pytest.fixture(autouse=True)
def db_sessions(settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.db"


@pytest.fixture
def admin_user():
    return User.objects.create_superuser("admin", "admin@example.com", "password")


def code(device):
    return f"{totp(device.bin_key, device.step, device.t0, device.digits, device.drift):06d}"


def test_login_without_device(client, admin_user):
    res = client.post(LOGIN_URL, {"username": "admin", "password": "password"})
    assertRedirects(res, "/admin/", fetch_redirect_response=False)
    assert client.get("/admin/").status_code == 200


def test_login_with_device(client, admin_user):
    device = TOTPDevice.objects.create(user=admin_user, name="default")

    res = client.post(LOGIN_URL, {"username": "admin", "password": "password"})
    assertContains(res, "double authentification est activée")
    assert client.get("/admin/").status_code == 302

    res = client.post(
        LOGIN_URL, {"username": "admin", "password": "password", "otp_token": "000000"}
    )
    assertContains(res, "Code invalide")
    assert client.get("/admin/").status_code == 302

    # un mauvais code déclenche le délai anti-bruteforce de django-otp
    device.refresh_from_db()
    device.throttle_reset()
    res = client.post(
        LOGIN_URL,
        {"username": "admin", "password": "password", "otp_token": code(device)},
    )
    assertRedirects(res, "/admin/", fetch_redirect_response=False)
    assert client.session["otp_device_id"] == device.persistent_id


def test_enable_and_disable(client, admin_user):
    client.force_login(admin_user)
    assert b"/admin/2fa/" in client.get("/admin/").content
    assertContains(client.get("/admin/2fa/"), "<svg")

    device = TOTPDevice.objects.get(user=admin_user, confirmed=False)
    res = client.post("/admin/2fa/", {"otp_token": code(device)})
    assertRedirects(res, "/admin/2fa/", fetch_redirect_response=False)
    device.refresh_from_db()
    assert device.confirmed

    device.last_t = -1
    device.save()
    res = client.post("/admin/2fa/", {"otp_token": code(device)})
    assertRedirects(res, "/admin/2fa/", fetch_redirect_response=False)
    assert not TOTPDevice.objects.filter(user=admin_user).exists()
