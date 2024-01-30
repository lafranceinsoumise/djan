from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from .models import Redirection
from .unique_counter import unique_should_be_counted


def redirect_view(request, *args, short_url, **kwargs):
    site = get_current_site(request)
    redirection = get_object_or_404(Redirection, site=site, short_url=short_url)
    destination = redirection.get_full_destination(request.GET)
    updates = {"counter": F("counter") + 1}
    Redirection.objects.filter(id=redirection.id).update(**updates)

    return HttpResponseRedirect(destination, status=redirection.http_status)
