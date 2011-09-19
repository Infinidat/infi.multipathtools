
import unittest
import mock
from logging import debug
from contextlib import contextmanager

from ctypes import sizeof, c_size_t

#pylint: disable-all

TEST_MESSAGE_TO_SEND = 'reconfigure'
TEST_MESSAGE_SIZE_TO_SEND = '\x0b' + '\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_SIZE_TO_RECEIVE = '\x04' + '\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_TO_RECEIVE = 'ok\n\x00'

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
        self.assertEquals(self.connection.receive(len(TEST_MESSAGE_SIZE_TO_RECEIVE)),
                          TEST_MESSAGE_SIZE_TO_RECEIVE)
        self.assertEquals(self.connection.receive(len(TEST_MESSAGE_TO_RECEIVE)),
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
        with mock.patch("socket.socket") as socket:
            socket.return_value = mock.Mock()
            socket.return_value.send.side_effect = send_mock
            yield socket

    def test_connect(self):
        from socket import AF_UNIX, SOCK_STREAM
        with self.mock_socket() as socket:
            super(MockUnixDomainSocketTestCase, self).test_connect()
        self.assertTrue(socket.called)
        self.assertEquals(socket.call_count, 1)
        self.assertEquals(socket.call_args[0], (AF_UNIX, SOCK_STREAM))

    def test_connect_and_disconnect(self):
        from socket import AF_UNIX, SOCK_STREAM
        with self.mock_socket() as socket:
            super(MockUnixDomainSocketTestCase, self).test_connect_and_disconnect()
        self.assertTrue(socket.called)
        self.assertEquals(socket.call_count, 1)
        self.assertEquals(socket.call_args[0], (AF_UNIX, SOCK_STREAM))
        self.assertEquals(socket.return_value.close.call_count, 1)

    def test_send_and_receive(self):
        with self.mock_socket() as socket:
            _recv_mock = recv_mock([TEST_MESSAGE_TO_RECEIVE, TEST_MESSAGE_SIZE_TO_RECEIVE])
            socket.return_value.recv.side_effect = _recv_mock
            super(MockUnixDomainSocketTestCase, self).test_send_and_receive()
        self.assertEquals(socket.return_value.send.call_count, 2)

    def _test_send_and_receive_long_messages(self):
        from . import MessageLength
        message_to_send = 'abcd' * 2048
        self.connection.connect()
        instance = MessageLength.create()
        instance.length = len(message_to_send)
        self.connection.send(MessageLength.instance_to_string(instance))
        self.connection.send(message_to_send)
        self.assertEquals(self.connection.receive(2048), 'a' * 2048)
        self.connection.disconnect()

    def test_send_and_receive_long_messages(self):
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
        self.assertEquals(socket.return_value.send.call_count, 18)
        self.assertEquals(socket.return_value.recv.call_count, 72)

    def test_connect__init_raises_exception(self):
        from socket import error
        from . import ConnectionError
        with self.mock_socket() as socket:
            socket.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_connect__connect_raises_exception(self):
        from socket import error
        from . import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.connect.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_connect__settimeout_raises_exception(self):
        from socket import error
        from . import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.settimeout.side_effect = error
            self.assertRaises(ConnectionError, self.connection.connect)

    def test_send__raises_error(self):
        from socket import error
        from . import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.send.side_effect = error
            self.connection.connect()
            self.assertRaises(ConnectionError, self.connection.send, *['foo'])

    def test_send__raises_timeout(self):
        from socket import timeout
        from . import TimeoutExpired
        with self.mock_socket() as socket:
            socket.return_value.send.side_effect = timeout
            self.connection.connect()
            self.assertRaises(TimeoutExpired, self.connection.send, *['foo'])

    def test_recv__raises_error(self):
        from socket import error
        from . import ConnectionError
        with self.mock_socket() as socket:
            socket.return_value.recv.side_effect = error
            self.connection.connect()
            self.assertRaises(ConnectionError, self.connection.receive, *[1])

    def test_recv__raises_timeout(self):
        from socket import timeout
        from . import TimeoutExpired
        with self.mock_socket() as socket:
            socket.return_value.recv.side_effect = timeout
            self.connection.connect()
            self.assertRaises(TimeoutExpired, self.connection.receive, *[1])

class MultipathClientTestCase(unittest.TestCase):
    def setUp(self):
        from platform import system
        from . import MultipathClient
        if system().lower() != 'linux':
            raise unittest.SkipTest
        super(MultipathClientTestCase, self).setUp()
        self.client = MultipathClient()

    def test_rescan(self):
        self.client.rescan()

    def test_is_running(self):
        self.assertTrue(self.client.is_running())

class MutipathClientSimulatorTestCase(MultipathClientTestCase):
    def setUp(self):
        from ..simulator import SimulatorConnection, Singleton
        from . import MultipathClient
        super(MultipathClientTestCase, self).setUp()
        self.client = MultipathClient(SimulatorConnection())
        self.simulator = Singleton()

    def test_rescan(self):
        MultipathClientTestCase.test_rescan(self)
        self.assertIn('reconfigure', self.simulator._handled_messages)
