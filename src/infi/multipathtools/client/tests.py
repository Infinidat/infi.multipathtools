
import unittest
import mock
from contextlib import contextmanager
from logging import getLogger

loger = getLogger(__name__)

from ctypes import sizeof, c_size_t

#pylint: disable-all

TEST_MESSAGE_TO_SEND = 'reconfigure'
TEST_MESSAGE_SIZE_TO_SEND = '\x0b' + '\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_SIZE_TO_RECEIVE = '\x04' + '\x00' * (sizeof(c_size_t) - 1)
TEST_MESSAGE_TO_RECEIVE = 'ok\n\x00'

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

    def test_get_config(self):
        from ..config import Configuration
        config = self.client.get_multipathd_conf()
        self.assertIsInstance(config, Configuration)

    def test_write_config(self):
        config = self.client.get_multipathd_conf()
        self.client.write_to_multipathd_conf(config)

    def test_get_devices(self):
        from six.moves import builtins
        with mock.patch.object(builtins, "open"):
            devices = self.client.get_list_of_multipath_devices()

    def test_disable_and_reinstante_paths(self):
        raise unittest.SkipTest
        from time import sleep
        devices = self.client.get_list_of_multipath_devices()
        path_id = devices[0].path_groups[0].paths[0].id
        self.client.fail_path(path_id)
        sleep(1)
        devices = self.client.get_list_of_multipath_devices()
        path = devices[0].path_groups[0].paths[0]
        self.assertEqual(path.id, path_id)
        self.assertEqual(path.state, 'failed')
        self.client.reinstate_path(path.id)
        sleep(1)
        devices = self.client.get_list_of_multipath_devices()
        path = devices[0].path_groups[0].paths[0]
        self.assertEqual(path.id, path_id)
        self.assertEqual(path.state, 'active')

class MutipathClientSimulatorTestCase(MultipathClientTestCase):
    def setUp(self):
        from ..simulator import SimulatorConnection, Singleton
        from . import MultipathClient
        super(MultipathClientTestCase, self).setUp()
        self.client = MultipathClient(SimulatorConnection())
        self.simulator = Singleton()

    def test_rescan(self):
        super(MutipathClientSimulatorTestCase, self).test_rescan()
        self.assertIn('reconfigure', self.simulator._handled_messages)

    def test_get_config(self):
        super(MutipathClientSimulatorTestCase, self).test_get_config()
        self.assertIn('show config', self.simulator._handled_messages)

    def test_write_config(self):
        config = self.client.get_multipathd_conf()
        self.client.write_to_multipathd_conf(config, self.simulator._conf_path)

    def test_disable_and_reinstante_paths(self):
        raise unittest.SkipTest

    def test_get_version(self):
        actual = self.client.get_version()
        expected = [0, 4, 8]
        self.assertEqual(actual, expected)
