#
# DNSChain
# github.com/dnschain
# MIT license 11/2017
# Author: twitter.com/khs9ne
#
import hashlib
from typing import List

import base64
import binascii


def ZonesFactory(cache=None):
    class _ZonesFactory:
        BLOCKHEIGHT = 1
        BLOCKHEADERS = 2
        HEXBLOCK = 3
        TRANSACTIONS = 4

        QTYPE_TXT = 16

        def __init__(self, cache=None):
            self.cache = cache
            self.qtype = None
            self.data_type = None
            self.blockheight = None
            self.blockhash = None
            self.hexblockheaders = None
            self.hexblock = None
            self.record = None
            self.coin = None
            self.domain = None
            self.transactions = None
            self.factories = {
                self.BLOCKHEIGHT: self.to_blockindex,
                self.BLOCKHEADERS: self.to_blockheaders,
                self.HEXBLOCK: NotImplementedError,
                self.TRANSACTIONS: self.to_block_transactions
            }

        def set_record(self, record):
            self.record = record
            return self

        def set_qtype(self, qtype):
            self.qtype = qtype
            return self

        def set_domain(self, domain):
            self.domain = domain
            return self

        def set_coin(self, coin):
            self.coin = coin
            return self

        def from_blockheight(self, blockheight: int, blockhash: str):
            assert not self.data_type
            self.blockheight = blockheight
            self.blockhash = blockhash
            self.data_type = self.BLOCKHEIGHT
            return self

        def from_hexblockheaders(self, blockhash: str, hexblockheaders: str):
            assert not self.data_type
            self.data_type = self.BLOCKHEADERS
            self.blockhash = blockhash
            self.hexblockheaders = hexblockheaders
            return self

        def from_hexblock(self, blockhash: str, hexblock: str):
            assert not self.data_type
            self.data_type = self.HEXBLOCK
            self.blockhash = blockhash
            self.hexblock = hexblock
            return self

        def from_transactions(self, blockhash: str, transactions: list):
            assert not self.data_type
            self.data_type = self.TRANSACTIONS
            self.blockhash = blockhash
            self.transactions = transactions
            return self

        def to_blockindex(self, disable_cache=False):
            assert self.blockheight is not None and self.coin and self.domain and self.blockhash and self.record
            stripped_leading_zeros_blockhash = self.blockhash[8:]
            zone = 'IN CNAME {}.block.{}.{}'.format(stripped_leading_zeros_blockhash, self.coin, self.domain)
            zones = [self.record + ' ' + zone]
            not disable_cache and self.cache and self.cache.cache_zone(self.record, self.qtype, zones)
            return zones

        def to_blockheaders(self, disable_cache=False):
            assert self.hexblockheaders and self.blockhash and self.coin
            zone = 'IN A 127.0.0.1'
            zones = [self.record + ' ' + zone]
            if self.qtype not in [self.QTYPE_TXT]:
                return zones
            b64headers = base64.b64encode(binascii.unhexlify(self.hexblockheaders)).decode()
            zones.append(
                self.record + ' ' + 'IN TXT {}'.format(b64headers)
            )
            not disable_cache and self.cache and self.cache.cache_zone(self.record, self.qtype, zones)
            return zones

        def _iterchunks(self, chunks, zones, h=0):
            if not chunks:
                return zones

            def int_to_ip(n: int):
                return '{}.{}'.format(int(n / 254), n % 254)

            def gettxt(a, b):
                return '{} IN TXT {}'.format(a, base64.b64encode(b).decode())

            def geta(a, n: int=None):
                return '{} IN A 127.0.{}'.format(a, n is not None and int_to_ip(n) or '0.1')

            if not h and len(chunks) > 1:
                record = '{}.txs.{}.{}'.format(self.blockhash, self.coin, self.domain)
                zones[record] = zones.get(record, [])
                zones[record].extend([geta(record, n=len(chunks))])
            elif h and len(chunks) > 1:
                record = '{}.{}.txs.{}.{}'.format(self.blockhash, h, self.coin, self.domain)
                zones[record] = zones.get(record, [])
                zones[record].extend([geta(record)])
            else:
                record = h and '{}.{}.txs.{}.{}'.format(self.blockhash, h, self.coin, self.domain) or \
                         '{}.txs.{}.{}'.format(self.blockhash, self.coin, self.domain)
                zones[record] = zones.get(record, [])
                zones[record].extend([geta(record)])
            zones[record].extend([gettxt(record, x) for x in chunks[0]])
            return self._iterchunks(chunks[1:], zones, h=h+1)

        @staticmethod
        def make_chunks(hexdata) -> List[List[bytes]]:
            print('data size: {}'.format(len(hexdata)/2))
            d = binascii.unhexlify(hexdata)
            QUERY_SIZE = 128
            TXT_SIZE = 64
            m0 = [d[i:i+QUERY_SIZE] for i in range(0, len(d), QUERY_SIZE)]
            return [[m[i:i+TXT_SIZE] for i in range(0, len(m), TXT_SIZE)] for m in m0]

        def to_block_transactions(self):
            assert self.transactions
            transactions_blob = ''.join(self.transactions)
            block_records = self._iterchunks(self.make_chunks(transactions_blob), {})
            self.cache and [self.cache.cache_zone(k, v) for k, v in block_records.values()]
            try:
                if 'txt' in self.record and self.qtype not in [self.QTYPE_TXT]:
                    return []
                return block_records[self.record]
            except KeyError as e:
                print('NOPE: {}'.format(e))
                return []

        def to_block_transactions_chunk(self):
            return self.to_block_transactions()

        def zones(self, disable_cache=False):
            response = self.factories[self.data_type](disable_cache=disable_cache)
            return response

    return _ZonesFactory(cache=cache)
