from chaindnsd.clients.bitcoind import BitcoinRPCClient
from chaindnsd.chaindns import settings


class BitcoinService:
    def __init__(self, bitcoin_client):
        self.bitcoin = bitcoin_client

    def getblockhash(self, height: int):
        blockhash = self.bitcoin.get_block_hash(height)
        return blockhash and {
            'hash': blockhash,
            'age': self.bitcoin.get_best_height() - height
        }

    def getblockheader(self, blockhash: str):
        return self.bitcoin.get_block_header(blockhash, verbose=False)

    def getblock(self, blockhash: str):
        return self.bitcoin.getblock(blockhash)

    def gettxinfo(self, txid: str, blockparents=None):
        res = {'txid': None}
        transaction = self.bitcoin.get_raw_transaction(txid, verbose=True)
        print(transaction.keys())
        if not transaction:
            return res
        res['txid'] = transaction['txid']
        if blockparents and transaction.get('blockhash') is not None:
            res['blockparents'] = self.bitcoin.getblock(transaction['blockhash'])['tx']
        return res

    def getbestheight(self):
        pass

    def getmempoolentry(self, txid):
        return self.bitcoin.getmempoolentry(txid)

    def getrawtransaction(self, txid, verbose=True):
        return self.bitcoin.get_raw_transaction(txid, verbose=verbose)


def get_instance():
    bitcoind_client = BitcoinRPCClient(
        settings.BITCOIND_USER,
        settings.BITCOIND_PASS,
        settings.BITCOIND_HOSTNAME,
    )
    instance = BitcoinService(bitcoind_client)
    return instance

INSTANCE = get_instance()
