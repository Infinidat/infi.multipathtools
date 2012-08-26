
from infi.exceptools import chain
from infi.instruct import Struct
from infi.instruct import ULInt32, ULInt64

from os.path import exists, sep, join
from ctypes import c_size_t, sizeof

DEFAULT_SOCKET = join(sep, 'var', 'run', 'multipathd.sock')
DEFAULT_TIMEOUT = 60
MAX_SIZE = 2 ** 8
HEADER_SIZE = sizeof(c_size_t)

from logging import getLogger
logger = getLogger(__name__)

class ClientBaseException(Exception):
    pass

from ..errors import ConnectionError, TimeoutExpired

class MessageLength(Struct):
    _fields_ = [(ULInt64 if HEADER_SIZE == 8 else ULInt32)("length"), ]

class BaseConnection(object):
    def __init__(self):
        super(BaseConnection, self).__init__() #pragma: no cover

    def connect(self):
        raise NotImplementedError #pragma: no cover

    def send(self, message):
        raise NotImplementedError #pragma: no cover

    def receive(self, message):
        raise NotImplementedError #pragma: no cover

    def disconnect(self):
        raise NotImplementedError #pragma: no cover

class UnixDomainSocket(BaseConnection):
    def __init__(self, timeout=DEFAULT_TIMEOUT, address=DEFAULT_SOCKET):
        super(UnixDomainSocket, self).__init__() #pragma: no cover
        self._timeout = timeout
        self._address = address
        self._socket = None

    def connect(self):
        import socket
        try:
            socket_object = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            socket_object.connect(self._address)
            socket_object.settimeout(self._timeout)
        except:
            raise chain(ConnectionError)
        self._socket = socket_object

    def send(self, message):
        from socket import timeout, error

        try:
            bytes_sent = self._socket.send(message)
        except timeout:
            logger.debug("Caught socket timeout: {!r}".format(self._socket.gettimeout()))
            raise chain(TimeoutExpired)
        except error:
            raise chain(ConnectionError)

        if bytes_sent < len(message):
            self.send(message[bytes_sent:])

    def _receive(self, expected_length=MAX_SIZE):
        received_string = ''
        remaining_length = expected_length
        while remaining_length > 0:
            unit_length = MAX_SIZE if remaining_length > MAX_SIZE else remaining_length
            received_string += self._socket.recv(unit_length)
            remaining_length = expected_length - len(received_string)
        return received_string

    def receive(self, expected_length=MAX_SIZE):
        from socket import timeout, error
        try:
            return self._receive(expected_length)
        except timeout:
            logger.debug("Caught socket timeout: {!r}".format(self._socket.gettimeout()))
            raise chain(TimeoutExpired)
        except error:
            raise chain(ConnectionError)

    def disconnect(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None

    def __repr__(self):
        try:
            msg = "<UnixDomainSocket(timeout={}, address={}, socket={})>"
            return msg.format(self._timeout, self._address, self._socket)
        except:
            return super(UnixDomainSocket, self).__repr__()
