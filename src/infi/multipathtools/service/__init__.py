

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

def get_list_of_live_modules():
    from os.path import join, sep
    with open(join(sep, 'proc', 'modules')) as modules:
        return [line.split()[0] for line in modules.readlines()]

def execute(command):
    from logging import getLogger
    log = getLogger(__name__)
    debug = log.debug
    from infi.execute import execute as _execute
    debug('executing %s', command)
    try:
        subprocess = _execute(command.split())
    except:
        from infi.exceptools import chain
        raise chain(ServiceException)
    debug('waiting for it')
    subprocess.wait()
    debug('returncode = %s', subprocess.get_returncode())
    debug('stdout = %s', subprocess.get_stdout())
    debug('stderr = %s', subprocess.get_stderr())
    if subprocess.get_returncode() != 0:
        raise ServiceException(subprocess.get_stderr())

def get_kernel_release():
    import platform
    (_, _, release, _, _, _) = platform.uname()
    return release

def get_modules_list():
    from os.path import sep, join
    modules = []
    with open(join(sep, 'lib', 'modules', get_kernel_release(), 'modules.dep'), "r") as modules_dep:
        content = modules_dep.read()
        for line in content.splitlines():
            module_path, _ = line.split(':', 1)
            module_name = module_path.split(sep)[-1].split(".")[0]
            modules.append(module_name)
    return modules

class KernelModule(EntryPoint):
    def __init__(self, module_name):
        super(KernelModule, self).__init__()
        self.module_name = module_name

    def is_installed(self):
        return self.module_name in get_modules_list()

    def is_running(self):
        return self.module_name in get_list_of_live_modules()

    def stop(self):
        try:
            execute('rmmod %s' % self.module_name)
        except ServiceException:
            from infi.exceptools import chain
            raise chain(ServiceFailedToStop)

    def start(self):
        try:
            execute('modprobe %s' % self.module_name)
        except ServiceException:
            from infi.exceptools import chain
            raise chain(ServiceFailedToStart)

    def reload(self):
        pass # pragma: no cover

    def restart(self):
        pass # pragma: no cover

class File(EntryPoint):
    def __init__(self, path):
        super(File, self).__init__()
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

def get_list_of_running_processes():
    from os import listdir, readlink
    from os.path import exists, join, sep

    processes = []
    for item in listdir(join(sep, 'proc')):
        if not item.isdigit():
            continue
        if not exists(join(sep, 'proc', item, 'exe')):
            continue
        executable = readlink(join(sep, 'proc', item, 'exe')).split(sep)[-1]
        processes.append(executable)
    return processes

class InitScript(EntryPoint):
    def __init__(self, script_name, process_name=None):
        super(InitScript, self).__init__()
        self.script_name = script_name
        self.process_name = process_name if process_name is not None else script_name

    def is_installed(self):
        from os.path import exists
        return exists(self._get_script_path())

    def is_running(self):
        from os import listdir
        from os.path import exists, join, sep
        from logging import getLogger
        logger = getLogger(__name__)
        debug = logger.debug
        pid_file = join(sep, 'var', 'run', '%s.pid' % self.process_name)
        if not exists(pid_file):
            debug("did not found pid file %s", pid_file)
            return False
        with open(pid_file, 'r') as fd:
            pid = fd.read().splitlines()[0].strip()
            pid_running = pid in listdir(join(sep, 'proc'))
            debug("is pid %s listed under /proc? %s", pid, pid_running)
            return pid_running

    def _get_script_path(self):
        from os.path import sep, join
        return join(sep, 'etc', 'init.d', self.script_name)

    def _execute(self, command):
        execute("%s %s" % (self._get_script_path(), command))

    def stop(self):
        self._execute('stop')

    def start(self):
        self._execute('start')

    def reload(self):
        self._execute('reload')

    def restart(self):
        self._execute('restart')

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

        for key, value in list(self.components.items()):
            if value is component:
                self.components.pop(key)

    def iter_components_by_order(self, increasing_order=True):
        keys = list(self.components.keys())
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
        for _, value in self.iter_components_by_order(False):
            if value.is_running():
                value.stop()

    def start(self):
        for _, value in self.iter_components_by_order(True):
            if not value.is_running():
                value.start()

    def restart(self):
        self.stop()
        self.start()

    def reload(self):
        for _, value in self.iter_components_by_order(True):
            value.reload()

def get_multipath_composite():
    composite = CompositeEntryPoint()
    for item in ['multipath', 'dm-multipath']:
        component = KernelModule(item)
        if component.is_installed():
            break
    composite.add_component(component, 10)
    for item in ['multipathd', 'multipath-tools']:
        component = InitScript(item, 'multipathd')
        if component.is_installed():
            break
    composite.add_component(component, 20)
    return composite
