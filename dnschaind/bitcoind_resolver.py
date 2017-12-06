#
# DNSChain
# github.com/dnschain
# MIT license 11/2017
# Author: twitter.com/khs9ne
#

from dnslib import RR
from dnschaind.bitcoind_client import BitcoinRPCClient, BitcoindException
from dnschaind.zones_factory import ZonesFactory


class ChainResolver:
    TTL_1Y = 31449600
    IN_TXT = 16

    def __init__(self, bitcoind: BitcoinRPCClient, domain: str, coin: str, zones_factory: ZonesFactory=None):
        self.bitcoind = bitcoind
        self.domain = domain
        self.coin = coin
        self.zones_factory = zones_factory
        self.actions = {
            'height': self._resolve_blockheight,
            'block': self._resolve_blockheaders,
            'txs': self._resolve_transactions,
            'tx': self._resolve_transaction
        }

    def _resolve_blockheight(self, record, _, reply):
        blockheight = int(record[0])
        try:
            blockhash = self.bitcoind.getblockhash(blockheight)
        except BitcoindException:
            return
        r = '{}.height.{}.{}'.format(blockheight, self.coin, self.domain)
        for zone in self.zones_factory().set_record(r).set_coin(self.coin).set_domain(self.domain)\
                .from_blockheight(blockheight, blockhash).zones():
            reply.add_answer(*RR.fromZone(zone, ttl=0))

    def _resolve_blockheaders(self, record, qtype, reply):
        blockhash = record[0]
        try:
            blockheader = self.bitcoind.getblockheader(blockhash, verbose=False)
        except BitcoindException:
            return
        r = '{}.block.{}.{}'.format(blockhash, self.coin, self.domain)
        for zone in self.zones_factory().set_record(r).set_coin(self.coin).set_domain(self.domain)\
                .set_qtype(qtype).from_hexblockheaders(blockhash, blockheader).zones():
            reply.add_answer(*RR.fromZone(zone, ttl=self.TTL_1Y))

    def _resolve_transactions(self, record, qtype, reply):
        blockhash = record[0]
        try:
            jsonblock = self.bitcoind.getblock(blockhash)
        except BitcoindException:
            return
        if record[1] == 'txs':
            r = '{}.txs.{}.{}'.format(blockhash, self.coin, self.domain)
            for zone in self.zones_factory().set_record(r).set_coin(self.coin).set_domain(self.domain).\
                    set_qtype(qtype).from_transactions(blockhash, jsonblock['tx']).to_block_transactions():
                reply.add_answer(*RR.fromZone(zone, ttl=self.TTL_1Y))
        else:
            r = '{}.{}.txs.{}.{}'.format(blockhash, record[1], self.coin, self.domain)
            print(r)
            for zone in self.zones_factory().set_record(r).set_coin(self.coin).set_domain(self.domain).\
                    set_qtype(qtype).from_transactions(blockhash, jsonblock['tx']).to_block_transactions_chunk():
                reply.add_answer(*RR.fromZone(zone, ttl=self.TTL_1Y))

    def _resolve_transaction(self, record, qtype, reply):
        txhash = record[0]
        pass

    def _resolve_pushtx(self, question, reply):
        # todo
        pass

    def _resolve_bestblock(self, record, _, reply):
        # todo
        pass

    def _resolve_question(self, question, reply):
        q = [x for x in str(question.qname).strip().split('.') if x]
        d = '{}.{}'.format(q[-2].lower(), q[-1].lower())
        if d != self.domain or q[-3].lower() != self.coin:
            print('OOPS: {}'.format(d))
            return
        try:
            print(q)
            self.actions[q[-4].lower()](q, question.qtype, reply)
        except KeyError as e:
            print('ooops'.format(e))

    def resolve(self, request, handler):
        reply = request.reply()
        for question in request.questions:
            self._resolve_question(question, reply)
        return reply
