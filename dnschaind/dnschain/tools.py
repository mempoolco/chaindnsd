from base64 import b64encode
from functools import wraps
from dnschaind.dnschain.settings import MAX_QUERY_SIZE, MAX_TXT_SIZE
import hashlib


TTL_1S = 1
TTL_1H = 3600
TTL_1D = TTL_1H*24
TTL_1W = TTL_1D*7
TTL_1Y = TTL_1W*52


def validate(validator):
    def decorator(func):
        @wraps(func)
        def func_wrapper(query):
            validator(query)
            return func(query)
        return func_wrapper
    return decorator


def create_zone(*a, ttl=None):
    from dnschaind.dnschain.zone import Zone
    return Zone(*a, ttl=ttl)


def add_checksum(data):
    checksum = hashlib.sha256(data).digest()[:2]
    return data + checksum


def base64encode(data: bytes):
    return b64encode(data).decode().strip()


def estimate_chunks(data):
    res = int(data / MAX_QUERY_SIZE)
    res += data % MAX_QUERY_SIZE and 1 or 0
    return res


def _split(d, s):
    return [d[i:i + s] for i in range(0, len(d), s)]


def get_data_chunks(data, chunk=None):
    chunks = _split(data, MAX_QUERY_SIZE)
    if chunk is None:
        matrix = [_split(c, MAX_TXT_SIZE) for c in chunks]
        return matrix
    return _split(chunks[chunk], MAX_TXT_SIZE)


def int_to_ipv4(n: int):
    assert n < 254**2
    return '127.0.{}.{}'.format(int(n / 254), n % 254)


def hex_to_ipv6(data: str):
    ips = []
    prefix = '10'
    assert not len(data) % 28, len(data)
    chunks = _split(data, 28)
    for i, chunk in enumerate(chunks):
        ips.append('{}{:02}:{}'.format(prefix, i, ':'.join(_split(chunk, 4))))
    return ips
