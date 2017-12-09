from chaindnsd.chaindns import exceptions
from chaindnsd import hex_to_ipv6


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
    from chaindnsd import Response
    response = Response()
    if query.qtype is query.available_qtype.AAAA:
        ips = hex_to_ipv6(blockhash[8:])
        for ip in ips:
            response.add_answer(query, ip, qtype=query.available_qtype.AAAA)
    elif query.qtype in (query.available_qtype.A, query.available_qtype.CNAME):
        data = blockhash[8:] + '.block.' + query.zone + '.' + query.domain
        response.add_answer(query, data, qtype=query.available_qtype.CNAME)
    return response
