import sys
sys.path.insert(0, '.')
sys.setrecursionlimit(4096)

from dnslib.server import DNSServer
from dnschaind.bitcoind_client import BitcoinRPCClient
from dnschaind.bitcoind_resolver import ChainResolver
from dnschaind.zones_factory import ZonesFactory

from dnschaind import settings


if __name__ == '__main__':
    bitcoind_client = BitcoinRPCClient(
        settings.BITCOIND_USER,
        settings.BITCOIND_PASS,
        settings.BITCOIND_HOSTNAME,
    )

    resolver = ChainResolver(bitcoind_client, settings.DOMAIN, settings.COIN, ZonesFactory)
    server = DNSServer(resolver, port=settings.LISTEN_PORT, address=settings.LISTEN_HOST, tcp=False)
    server.start()
