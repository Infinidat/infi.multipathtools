
from munch import Munch

class MultipathDevice(Munch):
    def __init__(self, id, device_name, dm_name):
        super(MultipathDevice, self).__init__()
        self.path_groups = []
        self.id = id
        self.device_name = device_name
        self.dm_name = dm_name
        with open("/sys/block/{}/dev".format(dm_name)) as fd:
            self.major_minor = tuple([int(number) for number in fd.read().split(':')])

class PathGroup(Munch):
    def __init__(self, state, priority):
        super(PathGroup, self).__init__()
        self.paths = []
        self.state = state # enabled, disabled, active, undef
        self.priority = int(priority)
        # TODO add support for service-time and queue-length that were recently added
        self.load_balancing_policy = 'round-robin'

class Path(Munch):
    def __init__(self, id, device_name, major_minor, state, priority, hctl):
        super(Path, self).__init__()
        self.id = id
        self.device_name = device_name
        self.major_minor = tuple([int(item) for item in major_minor.split(":")])
        self.state = state # active, failed, or undef
        self.priority = int(priority)
        self.hctl = tuple([int(item) for item in hctl.split(":")])

PATHGROUP_STATES = ['enabled', 'disabled', 'active', 'undef']
PATH_STATES = ['active', 'failed', 'undef']
