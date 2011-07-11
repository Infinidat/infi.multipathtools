
import logging
from infi.exceptools import chain
from os.path import exists, sep, join

#pylint: disable-msg=E1101

DEFAULT_SOCKET = join(sep, 'var', 'run', 'multipathd.sock')
DEFAULT_TIMEOUT = 3
MAX_SIZE = 2 ** 8

class ClientBaseException(Exception):
    pass

class ConnectionError(ClientBaseException):
    pass

class TimeoutExpired(ConnectionError):
    pass

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
        logging.debug("sending %s", repr(message))

        try:
            bytes_sent = self._socket.send(message)
        except timeout:
            raise chain(TimeoutExpired)
        except error:
            raise chain(ConnectionError)

        if bytes_sent < len(message):
            self.send(message[bytes_sent:])

    def receive(self, expected_length=MAX_SIZE):
        from socket import timeout, error
        if expected_length > MAX_SIZE:
            return self.receive(MAX_SIZE) + self.receive(expected_length - MAX_SIZE)
        try:
            received_string = self._socket.recv(expected_length)
            if len(received_string) < expected_length:
                received_string += self.receive(expected_length - len(received_string))
            return received_string
        except timeout:
            raise chain(TimeoutExpired)
        except error:
            raise chain(ConnectionError)

    def disconnect(self):
        self._socket.close()

from contextlib import contextmanager, nested
from logging import debug, exception

from infi.instruct import Struct
from infi.instruct import ULInt32, ULInt64
from ctypes import c_size_t, sizeof

HEADER_SIZE = sizeof(c_size_t)

class MessageLength(Struct):
    _fields_ = [(ULInt64 if HEADER_SIZE == 8 else ULInt32)("length"), ]

class MultipathClient(object):
    def __init__(self, connection=UnixDomainSocket()):
        super(MultipathClient, self).__init__() #pragma: no cover
        self._connection = connection

    @contextmanager
    def _with_connection_open(self):
        try:
            self._connection.connect()
            yield
        finally:
            self._connection.disconnect()

    def _get_message_size_as_string(self, message):
        instance = MessageLength.create()
        instance.length = len(message)
        return MessageLength.instance_to_string(instance)

    def _get_expected_message_size_from_string(self, string):
        return MessageLength.create_instance_from_string(string).length

    def _strip_ansi_colors(self, string):
        # TODO implement this
        return string

    def _send_and_receive(self, message):
        with self._with_connection_open():
            self._connection.send(self._get_message_size_as_string(message))
            self._connection.send(message)
            stream = self._connection.receive(MessageLength.sizeof())
            expected_length = self._get_expected_message_size_from_string(stream)
            response = self._connection.receive(expected_length)
            return self._strip_ansi_colors(response.strip('\x00\n'))

    def rescan(self):
        result = self._send_and_receive("reconfigure")
        if result != 'ok':
            raise RuntimeError(result) # TODO test this
