from django.http import QueryDict

from djan.models import Redirection, ParamsMode, UniqueCounterMode


def test_ignore_params_mode():
    redirection = Redirection(
        destination_url="http://www.example.com/?a=2&c=2",
        params_mode=ParamsMode.IGNORE,
        unique_counter_mode=UniqueCounterMode.NONE,
    )

    q = QueryDict()
    assert redirection.get_full_destination(q) == "http://www.example.com/?a=2&c=2"

    q = QueryDict("a=1&b=1")
    assert redirection.get_full_destination(q) == "http://www.example.com/?a=2&c=2"


def test_default_params_mode():
    redirection = Redirection(
        destination_url="http://www.example.com/?a=2&c=2",
        params_mode=ParamsMode.DEFAULT,
    )

    q = QueryDict()
    assert redirection.get_full_destination(q) == "http://www.example.com/?a=2&c=2"

    q = QueryDict("a=1&b=1")
    assert redirection.get_full_destination(q) == "http://www.example.com/?a=1&c=2&b=1"
