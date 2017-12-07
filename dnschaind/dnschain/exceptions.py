class DomainException(Exception):
    pass


class InvalidQueryLengthException(DomainException):
    pass


class UnhandledQueryTypeException(DomainException):
    pass


class UnhandledQueryClassException(DomainException):
    pass


class MissingDomainException(DomainException):
    pass


class MissingQueryTypeException(DomainException):
    pass


class MissingZoneException(DomainException):
    pass


class MissingCommandException(DomainException):
    pass


class InvalidArgumentsException(DomainException):
    pass


class MissingArgumentsException(DomainException):
    pass


class RequestsFloodException(DomainException):
    pass
