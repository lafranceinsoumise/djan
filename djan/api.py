import hmac
import secrets

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.forms import Form, URLField, IntegerField
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


class ShortenForm(Form):
    url = URLField(required=True)
    length = IntegerField(max_value=255, required=False)


@require_POST
@csrf_exempt
def shorten_view(request):
    if settings.API_TOKEN and (
        len(request.GET.get("token", "")) != len(settings.API_TOKEN)
        or not hmac.compare_digest(request.GET.get("token"), settings.API_TOKEN)
    ):
        return HttpResponseForbidden("Token invalid")

    form = ShortenForm(request.POST)

    if form.is_valid():
        length = form.cleaned_data["length"] or 5
        random_string = secrets.token_urlsafe(length)[:length]
        redirect, new = Redirect.objects.get_or_create(
            site_id=settings.SITE_ID,
            new_path=form.cleaned_data["url"],
            defaults={"old_path": "/" + random_string},
        )

        return HttpResponse(request.build_absolute_uri(redirect.old_path))

    return HttpResponseBadRequest(
        "\n".join(
            str(field) + " : " + str(error)
            for field, errors in form.errors.items()
            for error in errors
        )
    )
