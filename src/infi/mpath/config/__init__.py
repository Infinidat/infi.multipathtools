from logging import debug

DEV_NONE = 0
DEV_DEVT = 1
DEV_DEVNODE = 2
DEV_DEVMAP = 3

from bunch import Bunch

def bunch_to_multipath_conf(bunch):
    self = bunch
    strings = []
    for key, value in self.items():
        if value is None:
            continue
        debug("%s, %s", key, value)
        strings.append(' '.join([key, value]))
    return '\n'.join(strings)

def populate_bunch_from_multipath_conf_string(instance, string):
    from re import compile, DOTALL, MULTILINE
    re_flags = DOTALL | MULTILINE
    key_value_pattern = compile(KEY_VALUE_PATTERN, re_flags)

    for match in key_value_pattern.finditer(string):
        key, value = match.groupdict()['key'], match.groupdict()['value']
        setattr(instance, key, value)

# taken from multipath-tools/libmultipath/dict.c

class HardwareEntry(Bunch):
    def __init__(self, *args, **kwargs):
        super(HardwareEntry, self).__init__(*args, **kwargs)
        for item in ['vendor', 'product', 'revision', 'product_blacklist',
                     'path_grouping_policy', 'getuid_callout', 'path_checker',
                     'alias_prefix', 'features', 'hardware_handler', 'prio',
                     'prio_args,' 'failback', 'rr_weight', 'no_path_retry',
                     'rr_min_io', 'rr_min_io_rq', 'pg_gtimeout', 'flush_on_last_del',
                     'fast_io_fail_tmo', 'dev_loss_tmo']:
            setattr(self, item, None)

class MultipathEntry(Bunch):
    def __init__(self, *args, **kwargs):
        super(MultipathEntry, self).__init__(*args, **kwargs)
        for item in ['wwid', 'alias', 'path_grouping_policy', 'path_selector',
                     'failback', 'rr_weight', 'no_path_retry', 'rr_min_io',
                     'rr_min_io_rq', 'pg_timeout', 'flush_on_last_del',
                     'mode', 'uid', 'gid']:
            setattr(self, item, None)

class ConfigurationAttributes(Bunch):
    def __init__(self, *args, **kwargs):
        super(ConfigurationAttributes, self).__init__(*args, **kwargs)
        for item in ['verbosity', 'polling_interval', 'udev_dir', 'multipath_dir',
                     'path_selector', 'path_grouping_policy', 'getuid_callout',
                     'prio', 'prio_args', 'features', 'path_checker', 'alias_prefix',
                     'failback' , 'rr_min_io', 'rr_min_io_rq', 'max_fds', 'no_path_retry',
                     'queue_without_daemon', 'checker_timeout', 'pg_timeout',
                     'flish_on_last_del', 'user_friendly_names', 'mode', 'uid', 'gid',
                     'fast_io_fail_tmo' , 'dev_loss_tmo']:
            setattr(self, item, None)

class RuleList(object):
    def __init__(self):
        super(RuleList, self).__init__()
        self.device = []
        self.devnode = []
        self.wwid = []

    def to_multipathd_conf(self):
        strings = []
        for devnode in self.devnode:
            strings.append('devnode %s' % devnode)
        for device in self.device:
            strings.append('device {')
            strings.extend(['\t%s' % line for line in bunch_to_multipath_conf(device).splitlines()])
            strings.append('}')
        for wwid in self.wwid:
            strings.append('wwid %s' % wwid)
        return '\n'.join(strings)

    @classmethod
    def from_multipathd_conf(cls, string):
        from re import compile, DOTALL, MULTILINE
        re_flags = DOTALL | MULTILINE
        rulelist_pattern = compile(RULELIST_PATTERN, re_flags)

        instance = cls()

        for match in rulelist_pattern.finditer(string):
            key, value = match.groupdict()['key'], match.groupdict()['value']
            if key == 'devnode':
                instance.devnode.append(value)
            elif key == 'wwid':
                instance.wwid.append(value)
            elif key == 'device':
                device = Device()
                populate_bunch_from_multipath_conf_string(device, value.strip("{}"))
                instance.device.append(device)
            else:
                raise AssertionError("key %s is invalid", key) # pragma: no cover
        return instance

class Device(Bunch):
    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)
        for item in ['vendor', 'product']:
            setattr(self, item, None)

KEY_VALUE_PATTERN = \
    r"^\t*(?P<key>[A-Za-z0-9_]+) (?P<value>[^{}\n]+)$"

DEVICE_PATTERN = \
    r"^\t*(?P<key>device|multipath) {(?P<value>[^{}]*)}$"

RULELIST_PATTERN = \
    r"^\t*(?P<key>[A-Za-z0-9_]+) (?P<value>(?:[^{}\n]+)|({[^{}].*}))$"

MULTIPATH_CONF_PATTERN = \
    r"^(?P<name>defaults|blacklist_exceptions|blacklist|devices|multipaths)" + \
    " {\n*(?P<content>(:?%s)*|(:?%s)*|(:?%s)*|(:?%s)*)\n*}" % \
        (r'\s', # empty content
         r"^[^{}]*$\n", # key-value pairs
         r"^\t*(?:device|multipath) {[^{}]*}$\n", # devices
         r"(?:^[^{}]*$\n)|(?:^\t*(?:device|multipath) {[^{}]*}$\n)", # both
         )

class Configuration(object):
    def __init__(self):
        super(Configuration, self).__init__()
        self.attributes = ConfigurationAttributes()
        self.multipath_items = []
        self.hardware_items = []
        self.blacklist = RuleList()
        self.whitelist = RuleList()

    def to_multipathd_conf(self):
        strings = []
        strings.append('defaults {')
        strings.extend(['\t%s' % line for line in bunch_to_multipath_conf(self.attributes).splitlines()])
        strings.append('}')
        strings.append('blacklist {')
        strings.extend(['\t%s' % line for line in self.blacklist.to_multipathd_conf().splitlines()])
        strings.append('}')
        strings.append('blacklist_exceptions {')
        strings.extend(['\t%s' % line for line in self.whitelist.to_multipathd_conf().splitlines()])
        strings.append('}')
        strings.append('devices {')
        for device in self.hardware_items:
            strings.append('\tdevice {')
            strings.extend(['\t\t%s' % line for line in bunch_to_multipath_conf(device).splitlines()])
            strings.append('\t}')
        strings.append('}')
        strings.append('multipaths {')
        for multipath in self.multipath_items:
            strings.append('\tmultipath {')
            strings.extend(['\t\t%s' % line for line in bunch_to_multipath_conf(multipath).splitlines()])
            strings.append('\t}')
        strings.append('}')
        return '\n'.join(strings)

    @classmethod
    def from_multipathd_conf(cls, string):
        from re import compile, DOTALL, MULTILINE
        re_flags = DOTALL | MULTILINE
        pattern = compile(MULTIPATH_CONF_PATTERN, re_flags)
        device_pattern = compile(DEVICE_PATTERN, re_flags)
        instance = cls()

        def populate_list(list, base_class, content):
            for match in device_pattern.finditer(content):
                key, value = match.groupdict()['key'], match.groupdict()['value']
                entry = base_class()
                populate_bunch_from_multipath_conf_string(entry, value)
                list.append(entry)

        for section in pattern.finditer(string):
            name, content = section.groupdict()['name'], section.groupdict()['content']
            if name == 'defaults':
                populate_bunch_from_multipath_conf_string(instance.attributes, content)
            elif name == 'blacklist':
                instance.blacklist = RuleList.from_multipathd_conf(content)
            elif name == 'blacklist_exceptions':
                instance.whitelist = RuleList.from_multipathd_conf(content)
            elif name == 'devices':
                populate_list(instance.hardware_items, HardwareEntry, content)
            elif name == 'multipaths':
                populate_list(instance.multipath_items, MultipathEntry, content)

        return instance
