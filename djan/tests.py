from django.contrib.redirects.models import Redirect
from django.test import TestCase, override_settings


@override_settings(API_TOKEN="supertoken", SITE_ID=2)
class APITestCas(TestCase):
    def test_redirects(self):
        Redirect.objects.create(
            site_id=2, old_path="/test", new_path="https://example.com"
        )

        res = self.client.get("/test")
        self.assertRedirects(
            res, "https://example.com", status_code=301, fetch_redirect_response=False
        )

    def test_authenticate(self):
        res = self.client.post(
            "/api/shorten?token=passupertoken", data={"url": "http://example.com"}
        )
        self.assertEqual(res.status_code, 403)

    def test_create_redirects(self):
        res = self.client.post(
            "/api/shorten?token=supertoken", data={"url": "http://examplee.com"}
        )
        self.assertRegex(str(res.content), r"http://testserver/[a-zA-Z0-9]{5,6}")

        res = self.client.get(res.content.decode().replace("http://testserver", ""))
        self.assertRedirects(
            res, "http://examplee.com", status_code=301, fetch_redirect_response=False
        )
