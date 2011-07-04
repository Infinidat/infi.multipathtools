

class ServiceException(Exception):
    pass

class ServiceFailedToStart(ServiceException):
    pass

class EntryPoint(object):
    """ This base class is for stuff that needs to exists for multipath to work
    """
    def __init__(self):
        object.__init__(self)

    def is_installed(self):
        raise NotImplementedError # pragma: no cover

    def is_running(self):
        raise NotImplementedError # pragma: no cover

    def stop(self):
        raise NotImplementedError # pragma: no cover

    def reload(self):
        if not self.is_running(): # pragma: no cover
            self.stop()           # pragma: no cover
        self.start()              # pragma: no cover

    def restart(self):
        self.reload()             # pragma: no cover


class KernelModule(object):
    def __init__(self, module_name):
        object.__init__(self)
        self.module_name = module_name

class File(object):
    def __init__(self, path):
        object.__init__(self)
        self.path = path

class CompositeEntryPoint(EntryPoint):
    def __init__(self):
        EntryPoint.__init__(self)
        self.components = {}

    def add_component(self, component, load_order):
        assert(isinstance(component, EntryPoint))
        assert(isinstance(load_order, int))

        if component in self.components.values():
            return
        self.components[load_order] = component

    def remove_component(self, component):
        assert(isinstance(component, EntryPoint))

        if component not in self.components.values():
            return

        for key, value in self.components.items():
            if value is component:
                self.components.pop(key)

    def iter_components_by_order(self, increasing_order=True):
        keys = self.components.keys()
        keys.sort()
        if not increasing_order:
            keys.reverse()
        for key in keys:
            yield key, self.components[key]

    def is_installed(self):
        for component in self.components.values():
            if not component.is_installed():
                return False
        return True

    def is_running(self):
        for component in self.components.values():
            if not component.is_running():
                return False
        return True

    def stop(self):
        for key, value in self.iter_components_by_order(False):
            if value.is_running():
                value.stop()

    def start(self):
        for key, value in self.iter_components_by_order(True):
            if not value.is_running():
                value.start()
