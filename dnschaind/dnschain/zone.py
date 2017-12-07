from dnschaind import TTL_1W, Qtype
from dnschaind.dnschain import exceptions


class Zone:
    def __init__(self, *subdomains, ttl=TTL_1W):
        self._subdomains = set(subdomains) or set()
        self._ttl = ttl
        self._resolvers = {v: {} for v in Qtype}
        self._exceptions_handlers = {}

    def add_exception_handler(self, e, callback):
        self._exceptions_handlers[e] = callback
        return self

    @classmethod
    def create(cls, *subdomains):
        return cls(*subdomains)

    @property
    def exceptions_handlers(self) -> dict:
        return self._exceptions_handlers

    @property
    def subdomains(self):
        return self._subdomains

    def add_resolver(self, command: str, resolver: callable, qtypes: list=list(), ttl=None):
        for qtype in qtypes:
            self._resolvers[qtype][command] = [resolver, ttl]
        return self

    def resolve(self, query):
        resolvers = self._resolvers.get(query.qtype, [])
        if not resolvers:
            raise exceptions.MissingQueryTypeException()
        resolver = resolvers.get(query.command)
        if not resolver:
            raise exceptions.MissingZoneException()
        response = resolver[0](query)
        if response:
            response.ttl = response.force_ttl or resolver[1] if resolver[1] is not None else self._ttl
        return response
