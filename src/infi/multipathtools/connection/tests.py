
import unittest
import mock
import os

try:
    from gevent import socket
except ImportError:
    import socket

socket_module = socket
from contextlib import contextmanager

from ctypes import sizeof, c_size_t

#pylint: disable-all

TEST_MESSAGE_TO_SEND = b'reconfigure'
TEST_MESSAGE_SIZE_TO_SEND = b'\x0b' + b'\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_SIZE_TO_RECEIVE = b'\x04' + b'\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_TO_RECEIVE = b'ok\n\x00'

class ConnectionTestCase(unittest.TestCase):
    def _get_connection_object(self):
        raise unittest.SkipTest

    def setUp(self):
        self.connection = self._get_connection_object()

    def test_connect(self):
        self.connection.connect()

    def test_connect_and_disconnect(self):
        self.connection.connect()
        self.connection.disconnect()

    def test_send_and_receive(self):
        self.connection.connect()
        self.connection.send(TEST_MESSAGE_SIZE_TO_SEND)
        self.connection.send(TEST_MESSAGE_TO_SEND)
        self.assertEqual(self.connection.receive(len(TEST_MESSAGE_SIZE_TO_RECEIVE)),
                          TEST_MESSAGE_SIZE_TO_RECEIVE)
        self.assertEqual(self.connection.receive(len(TEST_MESSAGE_TO_RECEIVE)),
                          TEST_MESSAGE_TO_RECEIVE)
        self.connection.disconnect()

class UnixDomainSocketTestCase(ConnectionTestCase):
    def _get_connection_object(self):
        from . import  UnixDomainSocket
        return UnixDomainSocket()

    def setUp(self):
        from platform import system
        if system().lower() != 'linux':
            raise unittest.SkipTest
        super(UnixDomainSocketTestCase, self).setUp()

def send_mock(*args, **kwargs):
    message = kwargs.get('string', args[0])
    return len(message)

def recv_mock(items_to_return):
    items = [item for item in items_to_return]
    def side_effect(*args, **kwargs):
        return items.pop()
    return side_effect

class MockUnixDomainSocketTestCase(UnixDomainSocketTestCase):
    def setUp(self):
        with mock.patch("platform.system") as system:
            system.return_value = 'Linux'
            super(UnixDomainSocketTestCase, self).setUp()

    @contextmanager
    def mock_socket(self):
        with mock.patch("infi.multipathtools.connection.socket.socket") as socket:
            socket.return_value = mock.Mock()
            socket.return_value.send.side_effect = send_mock
            yield socket

    def test_connect(self):
        with self.mock_socket() as socket:
            super(MockUnixDomainSocketTestCase, self).test_connect()
        self.assertTrue(socket.called)
        self.assertEqual(socket.call_count, 1)
        self.assertEqual(socket.call_args[0], (socket_module.AF_UNIX, socket_module.SOCK_STREAM))

    def test_connect_and_disconnect(self):
        with self.mock_socket() as socket:
            super(MockUnixDomainSocketTestCase, self).test_connect_and_disconnect()
        self.assertTrue(socket.called)
        self.assertEqual(socket.call_count, 1)
        self.assertEqual(socket.call_args[0], (socket_module.AF_UNIX, socket_module.SOCK_STREAM))
        self.assertEqual(socket.return_value.close.call_count, 1)

    def test_send_and_receive(self):
        with self.mock_socket() as socket:
            _recv_mock = recv_mock([TEST_MESSAGE_TO_RECEIVE, TEST_MESSAGE_SIZE_TO_RECEIVE])
            socket.return_value.recv.side_effect = _recv_mock
            super(MockUnixDomainSocketTestCase, self).test_send_and_receive()
        self.assertEqual(socket.return_value.send.call_count, 2)

    def _test_send_and_receive_long_messages(self):
        from . import MessageLength
        message_to_send = 'abcd' * 2048
        self.connection.connect()
        instance = MessageLength()
        instance.length = len(message_to_send)
        self.connection.send(MessageLength.write_to_string(instance))
        self.connection.send(message_to_send)
        self.assertEqual(self.connection.receive(2048), 'a' * 2048)
        self.connection.disconnect()

    def test_send_and_receive_long_messages(self):
        raise unittest.SkipTest
        def send_mock(*args, **kwargs):
            message = kwargs.get('string', args[0])
            return 1 if len(message) == 1 else len(message) / 2

        def recv_mock(*args, **kwargs):
            expected_size = kwargs.get('bufsize', args[0])
            return 'a' * (1 if expected_size == 1 else expected_size / 2)

        with self.mock_socket() as socket:
            socket.return_value.send.side_effect = send_mock
            socket.return_value.recv.side_effect = recv_mock
            self._test_send_and_receive_long_messages()
        self.assertEqual(socket.return_value.send.call_count, 18)
        self.assertEqual(socket.return_value.recv.call_count, 23)

    def test_connect__init_raises_exception(self):
        from socket import error
        from ..errors import ConnectionError
        with self.mock_socket() as socket:
            socket.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_connect__connect_raises_exception(self):
        from socket import error
        from ..errors import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.connect.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_connect__settimeout_raises_exception(self):
        from socket import error
        from ..errors import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.settimeout.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_send__raises_error(self):
        from socket import error
        from ..errors import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.send.side_effect = error
            self.connection.connect()
            self.assertRaises(ConnectionError, self.connection.send, *['foo'])

    def test_send__raises_timeout(self):
        from socket import timeout
        from ..errors import TimeoutExpired
        with self.mock_socket() as socket:
            socket.return_value.send.side_effect = timeout
            self.connection.connect()
            self.assertRaises(TimeoutExpired, self.connection.send, *['foo'])

    def test_recv__raises_error(self):
        from socket import error
        from ..errors import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.recv.side_effect = error
            self.connection.connect()
            self.assertRaises(ConnectionError, self.connection.receive, *[1])

    def test_recv__raises_timeout(self):
        from socket import timeout
        from ..errors import TimeoutExpired
        with self.mock_socket() as socket:
            socket.return_value.recv.side_effect = timeout
            self.connection.connect()
            self.assertRaises(TimeoutExpired, self.connection.receive, *[1])

    def _get_random_socket_path(self):
        import string
        import random
        N = 10
        return '/tmp/' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))

    def _get_socket_filepath(self):
        filepath = None
        while filepath is None or os.path.exists(filepath):
            filepath = self._get_random_socket_path()
        return filepath

    def _setup_unix_domain_socket(self):
        filepath = self._get_socket_filepath()
        sock = socket.socket(socket_module.AF_UNIX, socket_module.SOCK_STREAM)
        sock.bind(filepath)
        sock.listen(1)
        sock.setblocking(0)
        _ = sock.accept
        self.addCleanup(lambda: sock.close())
        return sock, filepath

    def test_receive__no_premature_timeout(self):
        from . import UnixDomainSocket
        from ..errors import TimeoutExpired
        from time import time
        server_side_socket, socket_filepath = self._setup_unix_domain_socket()
        self.assertTrue(os.path.exists(socket_filepath))
        client_side_socket = UnixDomainSocket(address=socket_filepath, timeout=5)
        client_side_socket.connect()
        before = time()
        with self.assertRaises(TimeoutExpired):
            client_side_socket.receive()
        after = time()
        self.assertGreater(after-before, 3)

    def test_repr(self):
        from . import UnixDomainSocket
        string = repr(UnixDomainSocket())
