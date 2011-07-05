
import unittest
import mock

from contextlib import contextmanager, nested

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

class MockCompositeServiceTestCase(unittest.TestCase):
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
        self.assertIn(component, self.concrete.components.values())
        self.concrete.remove_component(component)
        self.assertNotIn(component, self.concrete.components.values())

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

class KernelModuleTestCase(unittest.TestCase):
    def setUp(self):
        if self.should_skip():
            raise unittest.SkipTest

    def tearDown(self):
        pass

    def should_skip(self):
        import platform
        (system, node, release, version, machine, processor) = platform.uname()
        return system.lower() != 'linux'

    def test_floppy_module_state(self):
        from . import KernelModule
        item = KernelModule('floppy')
        self.assertTrue(item.is_installed())
        self.assertTrue(item.is_running())

    def test_floppy_module_start(self):
        from . import KernelModule
        item = KernelModule('floppy')
        if item.is_running():
            item.stop()
        item.start()
        self.assertTrue(item.is_running())

    def test_floppy_module_stop(self):
        from . import KernelModule
        item = KernelModule('floppy')
        if not item.is_running():
            item.start()
        item.stop()
        self.assertFalse(item.is_running())

    def test__module_not_exists(self):
        from . import KernelModule
        item = KernelModule('thereisNoSuchModule')
        self.assertFalse(item.is_installed())

    def _get_module_in_use(self):
        from os.path import join, sep, exists
        with open(join(sep, 'proc', 'modules')) as modules:
            for line in modules.readlines():
                module_name, _, used_by_counter, _, _, _ = line.split()
                if used_by_counter:
                    return module_name
        return None

    def test__cannot_stop_module(self):
        from . import KernelModule, ServiceFailedToStop
        module_in_use = self._get_module_in_use()
        if module_in_use is None:
            raise unittest.SkipTest
        item = KernelModule(module_in_use)
        self.assertRaises(ServiceFailedToStop, item.stop)

class MockKernelModuleTestCase(KernelModuleTestCase):
    def setUp(self):
        KernelModuleTestCase.setUp(self)
        self._prepare_modules_dep_file()

    def tearDown(self):
        from os import close, remove
        fd, filename = self.tempfile
        fd.close()
        remove(filename)

    def should_skip(self):
        return False

    def _prepare_modules_dep_file(self):
        from os import fdopen
        from tempfile import mkstemp
        fd, filename = mkstemp()
        fd = fdopen(fd, 'w+b')
        fd.write('/legen/wait/for/it/dary.ko:\n')
        fd.write('/foo/bar/floppy.ko:\n')
        fd.write('/abra/kadabra.ko:\n')
        fd.seek(0)
        self.tempfile = fd, filename

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
    def mock_uname(self):
        with mock.patch("platform.uname") as uname:
            uname.return_value = ("Linux", "hostname", "2.6.something", "long text", "x64_64", '')
            yield uname

    @contextmanager
    def mock_open(self):
        fd, _ = self.tempfile
        with mock.patch("__builtin__.open") as _open:
            _open.return_value = mock.MagicMock(fd)
            _open.return_value.__enter__.return_value.read.return_value = fd.read()
            yield _open

    @contextmanager
    def mock_execute(self, return_value):
        with mock.patch("infi.execute.execute") as execute:
            execute.side_effect = self._execute_side_effect(return_value)
            yield execute

    def test_floppy_module_state(self):
        with nested(self.mock_uname(), self.mock_execute(0), self.mock_open()) as (_, _, _open):
            _open.return_value.__enter__.return_value.readlines.return_value = \
                    ['floppy 1234 0 - Live 0x00', 'ext3 4321 0 - Live 0x00']
            KernelModuleTestCase.test_floppy_module_state(self)
            self.assertEquals(_open.return_value.__enter__.return_value.read.call_count, 1)


    def test_floppy_module_start(self):
        with nested(self.mock_uname(), self.mock_execute(0), self.mock_open()) as (_, _, _open):
            return_values = [['ext3 4321 0 - Live 0x00'],
                             ['floppy 1234 0 - Live 0x00', 'ext3 4321 0 - Live 0x00']]
            return_values.reverse()

            def side_effect(*args, **kwargs):
                return return_values.pop()

            _open.return_value.__enter__.return_value.readlines.side_effect = side_effect
            KernelModuleTestCase.test_floppy_module_start(self)

    def test_floppy_module_stop(self):
        with nested(self.mock_uname(), self.mock_execute(0), self.mock_open()) as (_, _, _open):
            return_values = [['ext3 4321 0 - Live 0x00'],
                             ['floppy 1234 0 - Live 0x00', 'ext3 4321 0 - Live 0x00']]

            def side_effect(*args, **kwargs):
                return return_values.pop()

            _open.return_value.__enter__.return_value.readlines.side_effect = side_effect
            KernelModuleTestCase.test_floppy_module_stop(self)

    def test_module_listing(self):
        from . import is_module_name_listed_in_dep_file
        fd, filename = self.tempfile
        module_name, content = 'floppy', fd.read()
        self.assertTrue(is_module_name_listed_in_dep_file(module_name, content))

    def test__module_not_exists(self):
        with nested(self.mock_uname(), self.mock_execute(0), self.mock_open()):
            KernelModuleTestCase.test__module_not_exists(self)

    def _get_module_in_use(self):
        return 'floppy'

    def test__cannot_stop_module(self):
        with nested(self.mock_uname(), self.mock_execute(1), self.mock_open()):
            KernelModuleTestCase.test__cannot_stop_module(self)

class InitServiceTestCase(unittest.TestCase):
    pass

class CompositeServiceTestCase(unittest.TestCase):
    def test_get_composite(self):
        from . import get_multipath_composite
