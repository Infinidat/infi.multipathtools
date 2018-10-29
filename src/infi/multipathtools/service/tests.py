
#pylint: disable-all

import unittest
import mock

from contextlib import contextmanager
from time import sleep
from six.moves import builtins
from . import EntryPoint

class MockEntryPoint(EntryPoint):
    def __init__(self):
        EntryPoint.__init__(self)
        self._running = False
        self._installed = True

    def is_installed(self):
        return self._installed

    def is_running(self):
        return self._running

    def stop(self):
        self._running = False

    def start(self):
        self._running = True

    def restart(self):
        pass

    def reload(self):
        pass

class TestCase(unittest.TestCase):
    def setUp(self):
        if self.should_skip():
            raise unittest.SkipTest

    def tearDown(self):
        pass

    def should_skip(self):
        return True

    def _execute_side_effect(self, return_value):
        execute = mock.Mock()
        execute.wait = mock.Mock()
        execute.get_returncode = mock.Mock()
        execute.get_returncode.return_value = return_value
        execute.get_stdout = mock.Mock()
        execute.get_stdout.return_value = ''
        execute.get_stderr = mock.Mock()
        execute.get_stderr.return_value = ''

        def side_effect(*args, **kwargs):
            return execute

        return side_effect

    @contextmanager
    def mock_execute(self, return_value):
        with mock.patch("infi.execute.execute") as execute:
            execute.side_effect = self._execute_side_effect(return_value)
            yield execute

class CompositeServiceTestCase(TestCase):
    def test_get_composite(self):
        from . import get_multipath_composite
        composite = get_multipath_composite()
        self.assertTrue(composite.is_installed())

class FileTestCase(unittest.TestCase):
    def setUp(self):
        from tempfile import mkstemp
        from os import close
        fd, self.tempfile = mkstemp()
        close(fd)

    def test_file_that_does_not_exist(self):
        from . import File
        item = File('abracadabra')
        self.assertFalse(item.is_installed())

    def test_file_that_exists(self):
        from . import File
        item = File(self.tempfile)
        self.assertTrue(item.is_installed())
        self.assertTrue(item.is_running())
        item.stop()
        item.start()
        item.reload()
        item.restart()

    def tearDown(self):
        from os import remove
        remove(self.tempfile)

class InitServiceTestCase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self._choose_service()

    def _choose_service(self):
        from os.path import exists, sep, join
        for item in ['ssh', 'sshd']:
            if exists(join(sep, 'etc', 'init.d', item)):
                self.service_name = item
                return
        raise unittest.SkipTest

    def test_get_list_of_running_processes(self):
        from . import get_list_of_running_processes
        actual = get_list_of_running_processes()
        self.assertGreater(len(actual), 0)

    def test_is_installed__service_does_not_exist(self):
        from . import InitScript
        item = InitScript("foo")
        self.assertFalse(item.is_installed())

    def test_is_installed(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        self.assertTrue(item.is_installed())

    def test_is_running(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        self.assertTrue(item.is_running())

    def test_start(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        if not item.is_running():
            item.stop()
        item.start()
        self.assertTrue(item.is_running())

    def test_stop(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        if item.is_running():
            item.start()
        item.stop()
        self.assertFalse(item.is_running())
        item.start()

    def test_restart(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        item.restart()

    def test_reload(self):
        from . import InitScript
        item = InitScript(self.service_name, 'sshd')
        item.reload()

class KernelModuleTestCase(TestCase):
    def _get_module_in_use(self):
        from os.path import join, sep, exists
        with open(join(sep, 'proc', 'modules')) as modules:
            for line in modules.readlines():
                module_name, _, used_by_counter, _, _, _ = line.split()
                if int(used_by_counter):
                    return module_name
        return None

    def test_is_installed(self):
        from . import KernelModule
        item = KernelModule('floppy')
        self.assertTrue(item.is_installed())

    def test_is_installed__no_such_module(self):
        from . import KernelModule
        item = KernelModule('thereisNoSuchModule')
        self.assertFalse(item.is_installed())

    def test_start(self):
        from . import KernelModule
        item = KernelModule('floppy')
        if item.is_running():
            item.stop()
        item.start()
        self.assertTrue(item.is_running())

    def test_stop(self):
        from . import KernelModule
        item = KernelModule('floppy')
        if not item.is_running():
            item.start()
        item.stop()
        self.assertFalse(item.is_running())
        item.start()

    def test_stop__module_in_use(self):
        from . import KernelModule, ServiceFailedToStop
        from logging import getLogger
        debug = getLogger(__name__).debug
        module_in_use = self._get_module_in_use()
        debug("module is use: %s", module_in_use)
        if module_in_use is None:
            raise unittest.SkipTest
        item = KernelModule(module_in_use)
        self.assertRaises(ServiceFailedToStop, item.stop)

class MockInitServiceTestCase(InitServiceTestCase):
    def should_skip(self):
        return False

    def _choose_service(self):
        self.service_name = 'foo'

    @contextmanager
    def mock_exists(self):
        from os.path import sep
        def side_effect(*args, **kwargs):
            path = args[0]
            return '20' in path.split(sep)

        with mock.patch("os.path.exists") as exists:
            exists.side_effect = side_effect
            yield exists

    @contextmanager
    def mock_open(self):
        with mock.patch.object(builtins, "open") as _open:
            _open.return_value = mock.MagicMock()
            _open.return_value.__enter__.return_value.read.return_value = '20\n'
            yield _open

    def test_get_list_of_running_processes(self):
        from os.path import join, sep
        with mock.patch("os.listdir") as listdir, \
             mock.patch("os.readlink") as readlink, \
             self.mock_exists():
            listdir.return_value = ['10', 'a', '20', 'b', '30', 'c']
            readlink.return_value = join(sep, 'sbin', 'foo')
            InitServiceTestCase.test_get_list_of_running_processes(self)

    def test_is_installed(self):
        with mock.patch("os.path.exists") as exists:
            exists.return_value = True
            InitServiceTestCase.test_is_installed(self)

    def test_is_running(self):
        with mock.patch("os.listdir") as listdir, \
             mock.patch("os.path.exists") as exists, \
             self.mock_open():
            listdir.return_value = ['10', 'a', '20', 'b', '30', 'c']
            exists.return_value = True
            InitServiceTestCase.test_is_running(self)

    def test_start(self):
        with mock.patch("os.listdir") as listdir, \
             mock.patch("os.path.exists") as exists, \
             self.mock_open(), \
             self.mock_execute(0):
            listdir.return_value = ['10', 'a', '20', 'b', '30', 'c']
            exists.return_value = True
            InitServiceTestCase.test_start(self)

    def test_stop(self):
        with mock.patch("os.listdir") as listdir, \
             mock.patch("os.path.exists") as exists, \
             self.mock_open(), \
             self.mock_execute(0):
            listdir.return_value = ['10', 'a', '20', 'b', '30', 'c']
            exists.return_value = False
            InitServiceTestCase.test_stop(self)
            exists.return_value = True
            listdir.return_value = ['10', 'a', 'b', '30', 'c']
            InitServiceTestCase.test_stop(self)

    def test_restart(self):
        pass

    def test_reload(self):
        pass

class MockKernelModuleTestCase(KernelModuleTestCase):
    def setUp(self):
        KernelModuleTestCase.setUp(self)
        self._prepare_modules_dep_file()

    def tearDown(self):
        from os import close, remove
        fd, filename = self.tempfile
        fd.close()
        remove(filename)
        KernelModuleTestCase.tearDown(self)

    def should_skip(self):
        return False

    def _prepare_modules_dep_file(self):
        from os import fdopen
        from tempfile import mkstemp
        fd, filename = mkstemp()
        fd = fdopen(fd, 'w+')
        fd.write('/legen/wait/for/it/dary.ko:\n')
        fd.write('/foo/bar/floppy.ko:\n')
        fd.write('/abra/kadabra.ko:\n')
        fd.seek(0)
        self.tempfile = fd, filename

    def _get_module_in_use(self):
        return 'floppy'

    @contextmanager
    def mock_uname(self):
        with mock.patch("platform.uname") as uname:
            uname.return_value = ("Linux", "hostname", "2.6.something", "long text", "x64_64", '')
            yield uname

    @contextmanager
    def mock_open(self):
        fd, _ = self.tempfile
        with mock.patch.object(builtins, "open") as _open:
            _open.return_value = mock.MagicMock(fd)
            _open.return_value.__enter__.return_value.read.return_value = fd.read()
            _open.return_value.__enter__.return_value.readlines.return_value = []
            yield _open

    def test_is_installed(self):
        with self.mock_uname(), self.mock_execute(0), self.mock_open() as _open:
            _open.return_value.__enter__.return_value.readlines.return_value = \
                    ["/a/b/c/floppy.ko: a\n/foo/a.ko:"]
            KernelModuleTestCase.test_is_installed(self)
            self.assertEqual(_open.return_value.__enter__.return_value.read.call_count, 1)


    def test_start(self):
        with self.mock_uname(), self.mock_execute(0), self.mock_open() as _open:
            return_values = [['ext3 4321 0 - Live 0x00'],
                             ['floppy 1234 0 - Live 0x00', 'ext3 4321 0 - Live 0x00']]
            return_values.reverse()

            def side_effect(*args, **kwargs):
                return return_values.pop()

            _open.return_value.__enter__.return_value.readlines.side_effect = side_effect
            KernelModuleTestCase.test_start(self)

    def test_stop(self):
        with self.mock_uname(), self.mock_execute(0), self.mock_open() as _open:
            return_values = [['ext3 4321 0 - Live 0x00'],
                             ['floppy 1234 0 - Live 0x00', 'ext3 4321 0 - Live 0x00']]

            def side_effect(*args, **kwargs):
                return return_values.pop()

            _open.return_value.__enter__.return_value.readlines.side_effect = side_effect
            KernelModuleTestCase.test_stop(self)

    def test_is_installed__no_such_module(self):
        with self.mock_uname(), self.mock_execute(0), self.mock_open():
            KernelModuleTestCase.test_is_installed__no_such_module(self)

    def test_stop__module_in_use(self):
        with self.mock_uname(), self.mock_execute(1), self.mock_open():
            KernelModuleTestCase.test_stop__module_in_use(self)

class SimpleCompositeServiceTestCase(unittest.TestCase):
    def setUp(self):
        from . import CompositeEntryPoint
        self.concrete = CompositeEntryPoint()
        self.concrete.add_component(MockEntryPoint(), 1)
        self.concrete.add_component(MockEntryPoint(), 5)
        self.concrete.add_component(MockEntryPoint(), 10)

    def test_stop_start(self):
        self.concrete.start()
        self.concrete.stop()

    def test_restart(self):
        self.concrete.restart()

    def test_reload(self):
        self.concrete.reload()

    def test_is_running(self):
        self.concrete.stop()
        self.assertFalse(self.concrete.is_running())
        self.concrete.start()
        self.assertTrue(self.concrete.is_running())

    def test_is_installed(self):
        self.assertTrue(self.concrete.is_installed())
        for key, value in self.concrete.iter_components_by_order():
            value._installed = False
        self.assertFalse(self.concrete.is_installed())

    def test_remove_componet(self):
        for key, value in self.concrete.iter_components_by_order():
            self.concrete.remove_component(value)
        self.concrete.remove_component(EntryPoint())

    def test_add_component(self):
        component = MockEntryPoint()
        self.concrete.add_component(component, 100)
        self.concrete.add_component(component, 100)
        self.assertIn(component, list(self.concrete.components.values()))
        self.concrete.remove_component(component)
        self.assertNotIn(component, list(self.concrete.components.values()))
