from enum import Enum
from dnschaind.dnschain import exceptions


class Qtype(Enum):
    A = 1
    TXT = 16
    AAAA = 28
    CNAME = 2


class Qclass(Enum):
    IN = 1


class Query:
    available_qtype = Qtype
    available_qclass = Qclass

    def __init__(self, request, domain, zone, command, arguments):
        self._request = request
        self._domain = domain
        self._zone = zone
        self._command = command
        self._arguments = arguments
        self._domainstr = '.'.join(self._domain)
        self._qtype = None
        self._qclass = None

    @property
    def domain(self):
        return self._domainstr

    @property
    def zone(self):
        return self._zone

    @property
    def command(self):
        return self._command

    @property
    def arguments(self):
        return self._arguments

    @property
    def fqdn(self):
        return str(self._request.q.qname)

    @property
    def qclass(self):
        self._qclass = self._qclass or Qclass(self._request.q.qclass)
        return self._qclass

    @property
    def qtype(self):
        self._qtype = self._qtype or Qtype(self._request.q.qtype)
        return self._qtype


def query_factory():

    class _QueryFactory:
        def __init__(self):
            self._dp = 0

        def add_domain(self, domain):
            self._dp = len(domain.strip().split('.'))

        def get(self, request):
            _question = [x.decode() for x in request.questions[0].qname.label]
            if not len(_question) > self._dp:
                raise exceptions.InvalidQueryLengthException()
            q = Query(
                request,
                domain=_question[-self._dp:],
                zone=_question[-self._dp - 1:-self._dp][0],
                command=_question[-self._dp - 2:-self._dp - 1][0],
                arguments=_question[:-self._dp - 2]
            )
            try:
                assert q.qtype
            except ValueError:
                raise exceptions.UnhandledQueryTypeException
            try:
                assert q.qclass
            except ValueError:
                raise exceptions.UnhandledQueryClassException
            return q

    return _QueryFactory()

QueryFactory = query_factory
