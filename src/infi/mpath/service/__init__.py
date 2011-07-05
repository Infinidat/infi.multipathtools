

class ServiceException(Exception):
    pass

class ServiceFailedToStop(ServiceException):
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

def is_module_name_listed_in_dep_file(module_name, content):
    import re
    regex = re.compile(r'^[A-Za-z0-9-_/]*/%s.ko:\w*$' % module_name, re.MULTILINE)
    match = regex.search(content)
    return True if match and match.group() else False

def get_list_of_live_modules():
    from os.path import join, sep
    with open(join(sep, 'proc', 'modules')) as modules:
        return [line.split()[0] for line in modules.readlines()]

class KernelModule(EntryPoint):
    def __init__(self, module_name):
        object.__init__(self)
        self.module_name = module_name

    def get_kernel_release(self):
        import platform
        (system, node, release, version, machine, processor) = platform.uname()
        return release

    def is_installed(self):
        from os.path import sep, join
        with open(join(sep, 'lib', 'modules', self.get_kernel_release(), 'modules.dep')) as modules_dep:
            content = modules_dep.read()
        return is_module_name_listed_in_dep_file(self.module_name, content)

    def is_running(self):
        return self.module_name in get_list_of_live_modules()

    def _execute(self, command):
        from logging import debug
        from infi.execute import execute
        debug('executing %s', command)
        try:
            subprocess = execute(command.split())
        except Exception, exception:
            from infi.exceptools import chain
            raise chain(ServiceException)
        debug('waiting for it')
        debug('returncode = %s', subprocess.get_returncode())
        debug('stdout = %s', subprocess.get_stdout())
        debug('stderr = %s', subprocess.get_stderr())
        if subprocess.get_returncode() != 0:
            raise ServiceException(subprocess.get_stderr())

    def stop(self):
        try:
            self._execute('rmmod %s' % self.module_name)
        except ServiceException:
            from infi.exceptools import chain
            raise chain(ServiceFailedToStop)

    def start(self):
        try:
            self._execute('modprobe %s' % self.module_name)
        except ServiceException:
            from infi.exceptools import chain
            raise chain(ServiceFailedToStart)

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
