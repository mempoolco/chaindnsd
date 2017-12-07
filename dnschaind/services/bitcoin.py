from dnschaind.clients.bitcoind import BitcoinRPCClient
from dnschaind.dnschain import settings


class BitcoinService():
    def __init__(self, bitcoin_client):
        self.bitcoin = bitcoin_client

    def getblockhash(self, height: int):
        blockhash = self.bitcoin.get_block_hash(height)
        return blockhash and {
            'hash': blockhash,
            'age': self.bitcoin.get_best_height() - height
        }

    def getblock(self, blockhash: str):
        pass

    def gettxinfo(self, txid: str, blockparents=None):
        pass

    def getbestheight(self):
        pass


def get_instance():
    bitcoind_client = BitcoinRPCClient(
        settings.BITCOIND_USER,
        settings.BITCOIND_PASS,
        settings.BITCOIND_HOSTNAME,
    )
    instance = BitcoinService(bitcoind_client)
    return instance

INSTANCE = get_instance()
