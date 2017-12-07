import binascii
from dnschaind.dnschain import exceptions
from dnschaind import get_data_chunks, estimate_chunks, int_to_ipv6


def query_validator(query):
    try:
        qa = len(query.arguments)
        if qa < 2:
            raise exceptions.MissingArgumentsException(query)
        elif qa == 2:
            assert all([16 == len(binascii.unhexlify(x.encode())) for x in query.arguments])
        elif qa == 3:
            assert all([16 == len(binascii.unhexlify(x.encode())) for x in query.arguments[:2]])
            assert int(query.arguments[3]) < 256
        else:
            raise exceptions.InvalidArgumentsException(query)
    except (AssertionError, binascii.Error, ValueError) as e:
        raise exceptions.InvalidArgumentsException(query) from e

QueryValidator = query_validator


def get_merkle_proof(tx, txs):
    return None


def get_response(query, txinfo):
    from dnschaind import Response
    response = Response()
    data = txinfo and get_merkle_proof(txinfo['txhash'], txinfo['blockparents'])
    if not data:
        return response
    chunk = get_data_chunks(data, chunk=None if len(query.arguments) == 2 else query.arguments[3])
    for answer in chunk:
        response.add_answer(query, answer, qtype=query.available_qtypes.TXT)
    if not len(query.arguments):
        response.add_answer(query, int_to_ipv6(estimate_chunks(data)), qtype=query.available_qtypes.AAAA)
    return response
