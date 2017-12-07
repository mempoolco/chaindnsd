from dnslib import RR
from dnschaind import Query, TTL_1W
from dnschaind.dnschain import exceptions
from dnschaind.dnschain.exceptions import DomainException
from dnschaind.dnschain.zone import Zone


class Router:
    def __init__(self, domain, dns, ttl=TTL_1W):
        self._ttl = ttl
        self._domain = domain
        self._dns = dns
        self._zones = dict()
        self._resolver = None
        self._exceptions_handlers = dict()
        self._query_factory = None

    def set_query_factory(self, query_factory: callable):
        self._query_factory = query_factory
        return self

    def add_exception_handler(self, e, callback):
        self._exceptions_handlers[e] = callback
        return self

    def add_zone(self, zone: Zone):
        for _s in zone.subdomains:
            assert not self._zones.get(_s)
            self._zones[_s] = zone
        return self

    def resolve(self, request, handler):
        reply = request.reply()
        try:
            self._resolve(self._query_factory.get(request), reply, handler)
        except DomainException as e:
            # this must be improved
            if self._exceptions_handlers:
                for handler in self._exceptions_handlers:
                    if isinstance(e, handler):
                        self._exceptions_handlers[handler](e, request)
                return reply
            for zone in self._zones.values():
                for e, handler in zone.exceptions_handlers.items():
                    if isinstance(e, handler):
                        zone.exceptions_handlers[handler](e, request)
        return reply

    def _resolve(self, query: Query, reply, _):
        if query.domain != self._domain:
            raise exceptions.MissingDomainException()
        zone = self._zones.get(query.zone)
        if not zone:
            raise exceptions.MissingZoneException()
        response = zone.resolve(query)
        if not response:
            return
        for answer in response.answers:
            print(repr(answer))
            reply.add_answer(*RR.fromZone(answer, ttl=response.ttl))
