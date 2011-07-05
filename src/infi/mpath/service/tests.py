
import unittest
import mock

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

class CompositeServiceTestCase(unittest.TestCase):
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
    pass

class InitServiceTestCase(unittest.TestCase):
    pass
