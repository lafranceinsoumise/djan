from django.contrib.sites.models import Site
from django.db import models
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from urllib.parse import urlparse, urlunparse


class HttpStatus(models.IntegerChoices):
    MOVED_PERMANENTLY = 301, _("Moved permanently (301)")
    FOUND = 302, _("Found (302)")
    SEE_OTHER = 303, _("See other (303)")
    TEMPORARY_REDIRECT = 307, _("Temporary redirect (307)")
    PERMANENT_REDIRECT = 308, _("Permanent redirect (308)")


class ParamsMode(models.TextChoices):
    IGNORE = "IGNORE", _(
        "Ignore params in source URL, use only params in destination URL"
    )
    DEFAULT = "DEFAULT", _(
        "Params in source URL overwrite values defined in destination URL"
    )
    ADD = "ADD", _(
        "Params in source URL append to but do not replace values defined in destination URL"
    )


class UniqueCounterMode(models.TextChoices):
    NONE = "NONE", _("Do not count unique views")
    IP = "IP", _("Count by unique IP")
    SSID = "SSID", _("Count by unique SSID")
    QUERY_PARAMS = "QUERY_PARAMS", _("Count by unique query parameters")


class Redirection(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    short_url = models.CharField(
        verbose_name=_("Short URL fragment"),
        max_length=2000,
        help_text=_(
            "The source URL, without the domain name, and without the initial slash. It must not contain any question"
            "mark or hash sign."
        ),
    )
    destination_url = models.URLField(
        verbose_name=_("Destination URL"),
        max_length=4000,
        help_text=_("The complete destination URL. Must be an absolute URL."),
    )

    http_status = models.IntegerField(
        verbose_name=_("HTTP Status"),
        choices=HttpStatus.choices,
        default=HttpStatus.FOUND,
    )

    params_mode = models.CharField(
        verbose_name=_("Parameters handling mode"),
        max_length=10,
        help_text=_("How should query parameters be handled."),
        choices=ParamsMode.choices,
        default=ParamsMode.DEFAULT,
    )

    unique_counter_mode = models.CharField(
        verbose_name=_("Unique counter mode"),
        max_length=15,
        choices=UniqueCounterMode.choices,
        default=UniqueCounterMode.SSID,
        help_text=_(
            "From what properties of requests should the unique counter be computed"
        ),
    )

    counter = models.IntegerField(verbose_name=_("Counter"), default=0, editable=False)

    unique_counter = models.IntegerField(
        verbose_name=_("Unique counter"), default=0, editable=False
    )

    class Meta:
        unique_together = ("site", "short_url")

    def get_full_destination(self, source_query_dict):
        if self.params_mode == ParamsMode.IGNORE:
            return self.destination_url

        parsed = urlparse(self.destination_url)
        dest_query_dict = QueryDict(parsed.query, mutable=True)

        if self.params_mode == ParamsMode.DEFAULT:
            dict.update(dest_query_dict, source_query_dict)
        else:
            # self.params_mode == ParamsMode.ADD
            dest_query_dict.update(source_query_dict)

        parsed = parsed._replace(query=dest_query_dict.urlencode())
        return urlunparse(parsed)
