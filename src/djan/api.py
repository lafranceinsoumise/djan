import hmac
import secrets

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.forms import Form, URLField, IntegerField
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from djan.models import Redirection


class ShortenForm(Form):
    url = URLField(required=True, assume_scheme="https")
    length = IntegerField(max_value=4000, required=False)


def check_authorization_header(request):
    if not settings.API_TOKEN:
        raise PermissionDenied("No token configured")
    PREF = "Bearer "
    if (
        "Authorization" not in request.headers
        or request.headers["Authorization"][: len(PREF)] != PREF
    ):
        raise PermissionDenied("Authenticate using bearer token")

    token = request.headers["Authorization"][len(PREF) :].strip()
    if len(token) != len(settings.API_TOKEN) or hmac.compare_digest(
        request.GET.get("token"), settings.API_TOKEN
    ):
        raise PermissionDenied("Invalid token")


@require_POST
@csrf_exempt
def shorten_view(request):
    if settings.API_TOKEN and "token" in request.GET:
        if len(request.GET.get("token", "")) != len(
            settings.API_TOKEN
        ) or not hmac.compare_digest(request.GET.get("token"), settings.API_TOKEN):
            return HttpResponseForbidden("Token invalid")
    else:
        check_authorization_header(request)

    form = ShortenForm(request.POST)

    if form.is_valid():
        length = form.cleaned_data["length"] or 5
        random_string = secrets.token_urlsafe(length)[:length]
        site = get_current_site(request)
        redirect = Redirection.objects.create(
            site_id=site.id,
            destination_url=form.cleaned_data["url"],
            short_url=random_string,
        )

        return HttpResponse(request.build_absolute_uri(f"/{redirect.short_url}"))

    return HttpResponseBadRequest(
        "\n".join(
            str(field) + " : " + str(error)
            for field, errors in form.errors.items()
            for error in errors
        )
    )


def status_view(request):
    check_authorization_header(request)
    return JsonResponse({"status": "ok"})


def counter_view(request, short_url):
    check_authorization_header(request)

    redirection = get_object_or_404(
        Redirection, short_url=short_url, site=get_current_site(request)
    )
    return JsonResponse(
        {
            "short_url": redirection.short_url,
            "destination_url": redirection.destination_url,
            "http_status": redirection.http_status,
            "params_mode": redirection.params_mode,
            "unique_counter_mode": redirection.unique_counter_mode,
            "counter": redirection.counter,
            "unique_counter": redirection.unique_counter,
        }
    )
