import pytest
from django.contrib.auth.models import User
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def db_sessions(settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.db"


@pytest.fixture
def admin_user():
    return User.objects.create_superuser("admin", "admin@example.com", "password")


def login_password(client):
    return client.post(
        "/admin/account/login/",
        {
            "login_view-current_step": "auth",
            "auth-username": "admin",
            "auth-password": "password",
        },
    )


def test_admin_login_redirects_to_two_factor_login(client):
    res = client.get("/admin/login/?next=/admin/")
    assertRedirects(
        res, "/admin/account/login/?next=/admin/", fetch_redirect_response=False
    )


def test_login_without_device(client, admin_user):
    res = login_password(client)
    assertRedirects(res, "/admin/", fetch_redirect_response=False)
    assert client.get("/admin/").status_code == 200


def test_login_with_device(client, admin_user):
    device = TOTPDevice.objects.create(user=admin_user, name="default")

    res = login_password(client)
    assert res.status_code == 200
    assert "token-otp_token" in res.content.decode()
    assert client.get("/admin/").status_code == 302

    res = client.post(
        "/admin/account/login/",
        {"login_view-current_step": "token", "token-otp_token": "000000"},
    )
    assert res.status_code == 200
    assert client.get("/admin/").status_code == 302

    # un mauvais code déclenche le délai anti-bruteforce de django-otp
    device.refresh_from_db()
    device.throttle_reset()
    token = totp(device.bin_key, device.step, device.t0, device.digits, device.drift)
    res = client.post(
        "/admin/account/login/",
        {"login_view-current_step": "token", "token-otp_token": f"{token:06d}"},
    )
    assertRedirects(res, "/admin/", fetch_redirect_response=False)
    assert client.get("/admin/").status_code == 200


def test_setup_pages(client, admin_user):
    client.force_login(admin_user)
    assert client.get("/admin/account/two_factor/").status_code == 200
    assert client.get("/admin/account/two_factor/setup/").status_code == 200
    assert b"/admin/account/two_factor/" in client.get("/admin/").content
