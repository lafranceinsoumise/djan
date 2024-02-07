import string
from hashlib import sha1
from importlib.resources import open_text, files

from django.utils.crypto import get_random_string
from django_redis import get_redis_connection

from djan.models import UniqueCounterMode

from urllib.parse import quote

SESSION_KEY = "djan.unique_counter.session_key"
VALID_KEY_CHARS = string.ascii_lowercase + string.digits
_script = None


def get_ip_address(request):
    return request.META["REMOTE_ADDR"]


def get_session_id(request):
    """return a unique session id"""
    # it would be better if we could use django internal session id; however it will not exist for new sessions
    # and there does not seem to be any simple way in the SessionStore public API to generate it
    # instead we generate an internal session key that is saved on the session.
    if SESSION_KEY not in request.session:
        request.session[SESSION_KEY] = get_random_string(
            32, allowed_chars=VALID_KEY_CHARS
        )
    return request.session[SESSION_KEY]


def get_normalized_query_params(request):
    query_params = request.GET
    # we sort the query params to guarantee unicity
    pairs = sorted((k, v) for k, l in query_params.lists() for v in l)
    hash = sha1()
    hash.update("&".join(f"{k}={quote(v)}" for k, v in pairs).encode())
    return hash.hexdigest()


unique_key_funcs = {
    UniqueCounterMode.IP: get_ip_address,
    UniqueCounterMode.SSID: get_session_id,
    UniqueCounterMode.QUERY_PARAMS: get_normalized_query_params,
}


def get_unique_key(redirection, request):
    return unique_key_funcs[redirection.unique_counter_mode](request)


def unique_should_be_counted(redirection, request):
    global _script

    if redirection.unique_counter_mode == UniqueCounterMode.NONE:
        return False

    filter_key = f"redirection:{redirection.id}"
    unique_key = get_unique_key(redirection, request)
    con = get_redis_connection()
    if _script is None:
        with (files("djan") / "unique_should_be_counted.lua").open("r") as fd:
            _script = con.register_script(fd.read())

    return _script(
        keys=(filter_key,),
        args=(unique_key,),
        client=con,
    )
