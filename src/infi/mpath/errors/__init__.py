
class ClientBaseException(Exception):
    pass

class ConnectionError(ClientBaseException):
    pass

class TimeoutExpired(ConnectionError):
    pass
