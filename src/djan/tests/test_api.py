import re

import pytest
from pytest_django.asserts import assertRedirects

from djan.models import Redirection, UniqueCounterMode, HttpStatus

pytestmark = pytest.mark.django_db


def test_redirects(client):
    Redirection.objects.create(
        site_id=1,
        short_url="test",
        destination_url="https://example.com",
        http_status=HttpStatus.FOUND,
        unique_counter_mode=UniqueCounterMode.NONE,
    )

    res = client.get("/test")
    assertRedirects(
        res,
        "https://example.com",
        status_code=HttpStatus.FOUND,
        fetch_redirect_response=False,
    )


def test_authenticate(client):
    res = client.post(
        "/api/shorten?token=passupertoken", data={"url": "http://example.com"}
    )
    assert res.status_code == 403


def test_create_redirects(client):
    res = client.post(
        "/api/shorten?token=supertoken", data={"url": "http://examplee.com"}
    )

    assert re.match(
        r"http://testserver/[a-zA-Z0-9_-]{5}", res.content.decode(res.charset)
    )

    res = client.get(res.content.decode().replace("http://testserver", ""))
    assertRedirects(
        res, "http://examplee.com", status_code=302, fetch_redirect_response=False
    )


def test_length_param(client):
    res = client.post(
        "/api/shorten?token=supertoken",
        data={"url": "http://examplee.com", "length": 10},
    )
    assert re.match(
        r"http://testserver/[a-zA-Z0-9_-]{10}", res.content.decode(res.charset)
    )
