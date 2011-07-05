

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

    def start(self):
        raise NotImplementedError # pragma: no cover

    def reload(self):
        raise NotImplementedError # pragma: no cover

    def restart(self):
        raise NotImplementedError # pragma: no cover

class KernelModule(EntryPoint):
    def __init__(self, module_name):
        object.__init__(self)
        self.module_name = module_name

    def get_kernel_release(self):
        import platform
        (system, node, release, version, machine, processor) = platform.uname()
        return release

    def is_installed(self):
        import re
        from os.path import exists, sep, join
        with open(join(sep, 'lib', 'modules', self.get_kernel_release(), 'modules.dep')) as modules_dep:
            context = modules_dep.read()
        regex = re.compile('^[a-bA-b_0-9\/]*%s.ko:.*' % self.module_name)
        match = regex.match(context)
        return bool(match)

    def is_running(self):
        from os.path import exists, sep, join
        return exists(join(sep, 'sys', 'module', self.module_name))

    def _execute(self, command):
        from logging import debug
        from infi.execute import execute
        from infi.exceptools import chain
        debug('executing %s', command)
        try:
            subprocess = execute(command.split())
        except Exception, exception:
            # TODO mock this
            chain(ServiceFailedToStart)
        debug('waiting for it')
        debug('returncode = %s', subprocess.get_returncode())
        debug('stdout = %s', subprocess.get_stdout())
        debug('stderr = %s', subprocess.get_stderr())
        if subprocess.get_returncode() != 0:
            # TODO mock this
            raise ServiceFailedToStart(subprocess.get_stderr())

    def stop(self):
        self._execute('rmmod %s' % self.module_name)

    def start(self):
        self._execute('modprobe %s' % self.module_name)

    def reload(self):
        pass

    def restart(self):
        pass

class File(EntryPoint):
    def __init__(self, path):
        object.__init__(self)
        self.path = path

    def is_installed(self):
        from os.path import exists
        return exists(self.path)

    def is_running(self):
        return True

    def stop(self):
        pass

    def start(self):
        pass

    def reload(self):
        pass

    def restart(self):
        pass

class InitScript(EntryPoint):
    def __init__(self, script_name):
        object.__init__(self)
        self.script_name = script_name

    def is_installed(self):
        return EntryPoint.is_installed(self)

    def is_running(self):
        return EntryPoint.is_running(self)

    def stop(self):
        return EntryPoint.stop(self)

    def start(self):
        return EntryPoint.start(self)

    def reload(self):
        return EntryPoint.reload(self)

    def restart(self):
        return EntryPoint.restart(self)

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

    def restart(self):
        self.stop()
        self.start()

    def reload(self):
        for key, value in self.iter_components_by_order(True):
            value.reload()
