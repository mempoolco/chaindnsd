from dnslib.server import DNSServer

from chaindnsd import exceptions, QueryFactory
from chaindnsd.chaindns import settings
from chaindnsd.chaindns.router import Router
from chaindnsd.zones.routes import zone

query_factory = QueryFactory()
query_factory.add_domain(settings.DOMAIN['domain'])

app = Router(
    settings.DOMAIN['domain'],
    settings.DOMAIN['dns_auth'],
    ttl=settings.DOMAIN['ttl']
)

app.set_query_factory(query_factory).add_zone(zone)


def error_missing_domain(exception, request):
    print('MISSING DOMAIN HANDLER')
    print(exception)


def error_missing_zone(exception, request):
    print('MISSING ZONE HANDLER')
    print(exception)


app.add_exception_handler(exceptions.MissingDomainException, error_missing_domain)
app.add_exception_handler(exceptions.MissingZoneException, error_missing_zone)

server = DNSServer(app, port=settings.LISTEN_PORT, address=settings.LISTEN_HOST, tcp=False)
