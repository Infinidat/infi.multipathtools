
from infi.exceptools import chain
from infi.instruct import Struct
from infi.instruct import UNInt32, UNInt64

from os.path import exists, sep, join, exists
from ctypes import c_size_t, sizeof

DEFAULT_PATHNAME_SOCKET = join(sep, 'var', 'run', 'multipathd.sock')
DEFAULT_ABSTRACT_SOCKET = "\x00/org/kernel/linux/storage/multipathd"

DEFAULT_TIMEOUT = 60
MAX_SIZE = 2 ** 8
HEADER_SIZE = sizeof(c_size_t)

from logging import getLogger
logger = getLogger(__name__)


try:
    from gevent import socket
except ImportError:
    import socket

class ClientBaseException(Exception):
    pass

from ..errors import ConnectionError, TimeoutExpired

class MessageLength(Struct):
    _fields_ = [(UNInt64 if HEADER_SIZE == 8 else UNInt32)("length"), ]

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
    def __init__(self, timeout=DEFAULT_TIMEOUT, address=None):
        super(UnixDomainSocket, self).__init__() #pragma: no cover
        self._timeout = timeout
        self._address = address if address is not None else \
                        DEFAULT_PATHNAME_SOCKET if exists(DEFAULT_PATHNAME_SOCKET) else \
                        DEFAULT_ABSTRACT_SOCKET
        self._socket = None

    def connect(self):
        try:
            socket_object = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            socket_object.connect(self._address)
            socket_object.settimeout(self._timeout)
        except socket.error as error:
            raise chain(ConnectionError("failed to connect to multipathd socket: {}".format(error.strerror)))
        except Exception as error:
            raise chain(ConnectionError("failed to connect to multipathd socket: {}".format(error)))
        self._socket = socket_object

    def send(self, message):
        try:
            bytes_sent = self._socket.send(message)
        except socket.timeout:
            logger.debug("Caught socket timeout: {!r}".format(self._socket.gettimeout()))
            raise chain(TimeoutExpired("multipathd is not responding"))
        except socket.error as error:
            raise chain(ConnectionError("multipathd socket error: {}".format(error.strerror)))

        if bytes_sent < len(message):
            self.send(message[bytes_sent:])

    def _receive(self, expected_length=MAX_SIZE):
        received_string = b''
        remaining_length = expected_length
        while remaining_length > 0:
            unit_length = MAX_SIZE if remaining_length > MAX_SIZE else remaining_length
            received_string += self._socket.recv(unit_length)
            remaining_length = expected_length - len(received_string)
        return received_string

    def receive(self, expected_length=MAX_SIZE):
        try:
            return self._receive(expected_length)
        except socket.timeout:
            logger.debug("Caught socket timeout: {!r}".format(self._socket.gettimeout()))
            raise chain(TimeoutExpired("multipathd is not responding"))
        except socket.error as error:
            raise chain(ConnectionError("multipathd connection error: {}".format(error.strerror)))

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
