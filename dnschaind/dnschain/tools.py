from base64 import b64encode
from functools import wraps

import binascii

import merkle

from dnschaind.dnschain.settings import MAX_QUERY_SIZE, MAX_TXT_SIZE
import hashlib


TTL_1S = 1
TTL_1H = 3600
TTL_1D = TTL_1H*24
TTL_1W = TTL_1D*7
TTL_1Y = TTL_1W*52
LOCALHOST = '127.0.0.1'


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
    res = int(len(data) / MAX_QUERY_SIZE)
    res += len(data) % MAX_QUERY_SIZE and 1 or 0
    return res


def _split(d, s):
    return [d[i:i + s] for i in range(0, len(d), s)]


def get_data_chunks(data, chunk=None):
    chunks = _split(data, MAX_QUERY_SIZE)
    if chunk is None:
        matrix = [_split(c, MAX_TXT_SIZE) for c in chunks]
        return matrix
    return _split(chunks[chunk], MAX_TXT_SIZE)


def int_to_ipv6(n: int):
    assert len(str(n)) < 28
    return '1000:' + ':'.join(_split('{}{}'.format('0' * (28 - len(str(n))), n), 4))


def hex_to_ipv6(data: str):
    ips = []
    prefix = '10'
    assert not len(data) % 28, len(data)
    chunks = _split(data, 28)
    for i, chunk in enumerate(chunks):
        ips.append('{}{:02}:{}'.format(prefix, i, ':'.join(_split(chunk, 4))))
    return ips


class dblsha256:
    def __init__(self, x):
        self.data = x

    def digest(self):
        return hashlib.sha256(hashlib.sha256(self.data).digest()).digest()

    def hexdigest(self):
        return binascii.hexlify(self.digest()).decode()


class SatoshiMerkleTree(merkle.MerkleTree):
    merkle.hash_function = dblsha256

    def _build(self, leaves):
        new, odd = [], None
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        for i in range(0, len(leaves), 2):
            newnode = merkle.Node(leaves[i].val + leaves[i + 1].val)
            newnode.l, newnode.r = leaves[i], leaves[i + 1]
            leaves[i].side, leaves[i + 1].side, leaves[i].p, leaves[i + 1].p = 'L', 'R', newnode, newnode
            leaves[i].sib, leaves[i + 1].sib = leaves[i + 1], leaves[i]
            new.append(newnode)
        return new


def check_merkle_proof(data, root, proof=None):
    proof = proof and [x for x in proof] or []
    d = {0: 'SELF', 1: 'R', 2: 'L'}
    if data:
        proof.append((data[:32], d[data[32]]))
        return check_merkle_proof(data[33:], root, proof=proof)
    return proof + [(binascii.unhexlify(root)[::-1], 'ROOT')]
