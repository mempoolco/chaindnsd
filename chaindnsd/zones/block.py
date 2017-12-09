import binascii

from chaindnsd.chaindns import exceptions
from chaindnsd import LOCALHOST


def query_validator(query):
    try:
        if len(query.arguments) != 1:
            raise exceptions.MissingArgumentsException(query)
        assert len(binascii.unhexlify(query.arguments[0])) == 28
    except (AssertionError, ValueError, binascii.Error) as e:
        raise exceptions.InvalidArgumentsException(query) from e

QueryValidator = query_validator


def get_response(query, _):
    from chaindnsd import Response
    response = Response()
    if query.qtype is query.available_qtype.A:
        response.add_answer(query, LOCALHOST, qtype=query.available_qtype.A)
    return response
