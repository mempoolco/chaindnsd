from dnschaind.dnschain import exceptions
from dnschaind import hex_to_ipv6


def query_validator(query):
    try:
        qa = len(query.arguments)
        if qa != 1:
            raise exceptions.MissingArgumentsException(query)
        assert int(query.arguments[0]) >= 0
    except (AssertionError, ValueError) as e:
        raise exceptions.InvalidArgumentsException(query) from e

QueryValidator = query_validator


def get_response(query, blockhash):
    from dnschaind import Response
    response = Response()
    ips = hex_to_ipv6(blockhash[8:])
    for ip in ips:
        response.add_answer(query, ip, qtype=query.available_qtype.AAAA)
    return response
