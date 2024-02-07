from hashlib import sha1
from typing import NamedTuple

from django.http import QueryDict

from djan.unique_counter import get_session_id, get_normalized_query_params


class PseudoRequest(NamedTuple):
    session: dict = {}
    meta: dict = {}
    GET: QueryDict = QueryDict()


def test_get_session_id():
    r = PseudoRequest()

    # should generate session key
    unique_key = get_session_id(r)

    # should be the same the next time
    assert unique_key == get_session_id(r)


def test_get_normalized_query_params():
    r = PseudoRequest(GET=QueryDict("b=1&a=2&c=3&a=1"))

    unique_key = get_normalized_query_params(r)

    # unique key should be the sha of properly ordonned params
    h = sha1(b"a=1&a=2&b=1&c=3").hexdigest()

    assert unique_key == h
