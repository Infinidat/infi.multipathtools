
from bunch import Bunch
class MultipathDevice(Bunch):
    def __init__(self, id, device_name, minor):
        super(MultipathDevice, self).__init__()
        self.path_groups = []
        self.id = id
        self.device_name = device_name
        self.major_minor = '253:%s' % minor.replace('dm-', '')

class PathGroup(Bunch):
    def __init__(self, state, priority):
        super(PathGroup, self).__init__()
        self.paths = []
        self.state = state # enabled, disabled, active, undef
        self.priority = priority
        self.load_balancing_policy = 'round-robin'

class Path(Bunch):
    def __init__(self, id, device_name, major_minor, state, priority, hctl):
        super(Path, self).__init__()
        self.id = id
        self.device_name = device_name
        self.major_minor = major_minor
        self.state = state # active, failed, or undef
        self.priority = priority
        self.hctl = hctl
