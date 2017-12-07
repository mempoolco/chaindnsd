import binascii

from dnschaind.dnschain import exceptions
from dnschaind import add_checksum, base64encode, int_to_ipv6


def query_validator(query):
    try:
        qa = len(query.arguments)
        if qa != 1:
            raise exceptions.MissingArgumentsException(query)
        assert len(query.arguments[0]) == 56
        binascii.unhexlify(query.arguments[0])
    except (AssertionError, ValueError, binascii.Error) as e:
        raise exceptions.InvalidArgumentsException(query) from e

QueryValidator = query_validator


def get_response(query, blockheader, blockheight):
    from dnschaind import Response
    response = Response()
    data = base64encode(add_checksum(binascii.unhexlify(blockheader)))
    response.add_answer(query, data, qtype=query.available_qtype.TXT)
    blockheight is not None and response.add_answer(query, int_to_ipv6(blockheight), qtype=query.available_qtype.AAAA)
    return response
