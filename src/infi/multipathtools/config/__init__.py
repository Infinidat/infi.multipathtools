from infi.pyutils.lazy import cached_function
from logging import getLogger
logger = getLogger(__name__)

DEV_NONE = 0
DEV_DEVT = 1
DEV_DEVNODE = 2
DEV_DEVMAP = 3

from munch import Munch

def munch_to_multipath_conf(munch):
    self = munch
    strings = []
    for key, value in self.items():
        if value is None:
            continue
        logger.debug("%s, %s", key, value)
        strings.append(' '.join([key, value]))
    return '\n'.join(strings)

def populate_munch_from_multipath_conf_string(instance, string):
    from re import compile, DOTALL, MULTILINE #pylint: disable-msg=W0622
    re_flags = DOTALL | MULTILINE
    key_value_pattern = compile(KEY_VALUE_PATTERN, re_flags)

    for match in key_value_pattern.finditer(string):
        key, value = match.groupdict()['key'], match.groupdict()['value']
        setattr(instance, key, value)

# taken from multipath-tools/libmultipath/dict.c

def is_parameter_supported_by_libmultipath(keyword):
    from glob import glob
    from os import path
    return any([read_shared_library(shared_library).find(keyword.encode("ascii"))
                for shared_library in glob(path.sep + path.join("lib*", "*libmultipath.so*"))])

@cached_function
def read_shared_library(shared_library):
    with open(shared_library, "rb") as fd:
        return fd.read()

@cached_function
def get_supported_keywords_for_hardware_entry():
    return [item for item in ['vendor', 'product', 'revision', 'product_blacklist',
                              'path_grouping_policy', 'getuid_callout', 'path_checker',
                              'alias_prefix', 'features', 'hardware_handler', 'prio',
                              'prio_args,' 'failback', 'rr_weight', 'no_path_retry',
                              'rr_min_io', 'rr_min_io_rq', 'pg_gtimeout', 'flush_on_last_del',
                              'fast_io_fail_tmo', 'dev_loss_tmo']
            if is_parameter_supported_by_libmultipath(item)]

class HardwareEntry(Munch):
    def __init__(self, *args, **kwargs): #pylint: disable-msg=W0613
        for item in get_supported_keywords_for_hardware_entry():
           setattr(self, item, None)

@cached_function
def get_supported_keywords_for_multipath_entry():
    return [item for item in ['wwid', 'alias', 'path_grouping_policy', 'path_selector',
                              'failback', 'rr_weight', 'no_path_retry', 'rr_min_io',
                              'rr_min_io_rq', 'pg_timeout', 'flush_on_last_del',
                              'mode', 'uid', 'gid']
            if is_parameter_supported_by_libmultipath(item)]

class MultipathEntry(Munch):
    def __init__(self, *args, **kwargs): #pylint: disable-msg=W0613
        for item in get_supported_keywords_for_multipath_entry():
           setattr(self, item, None)

@cached_function
def get_supported_keywords_for_configuration():
    return [item for item in ['verbosity', 'polling_interval', 'udev_dir', 'multipath_dir',
                              'path_selector', 'path_grouping_policy', 'getuid_callout',
                              'prio', 'prio_args', 'features', 'path_checker', 'alias_prefix',
                              'failback' , 'rr_min_io', 'rr_min_io_rq', 'max_fds', 'no_path_retry',
                              'queue_without_daemon', 'checker_timeout', 'pg_timeout',
                              'flush_on_last_del', 'user_friendly_names', 'mode', 'uid', 'gid',
                              'fast_io_fail_tmo' , 'dev_loss_tmo']
            if is_parameter_supported_by_libmultipath(item)]

class ConfigurationAttributes(Munch):
    def __init__(self, *args, **kwargs): #pylint: disable-msg=W0613
        for item in get_supported_keywords_for_configuration():
           setattr(self, item, None)

class RuleList(object):
    """ container for {black,white}list configuration:

    devnode    a list of the the regular experssions
    device     a list of the device declarations
    wwid       a list of the WWIDs being included
    property   a list of the properties included

    """
    def __init__(self):
        super(RuleList, self).__init__()
        self.device = []
        self.devnode = []
        self.wwid = []
        self.property = []

    def to_multipathd_conf(self):
        strings = []
        for devnode in self.devnode:
            strings.append('devnode %s' % devnode)
        for device in self.device:
            strings.append('device {')
            strings.extend(['\t%s' % line for line in munch_to_multipath_conf(device).splitlines()])
            strings.append('}')
        for wwid in self.wwid:
            strings.append('wwid %s' % wwid)
        if self.property:
            strings.append('property "(%s)"' % '|'.join(self.property))
        return '\n'.join(strings)

    @classmethod
    def from_multipathd_conf(cls, string):
        from re import compile, DOTALL, MULTILINE #pylint: disable-msg=W0622
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
                populate_munch_from_multipath_conf_string(device, value.strip("{}"))
                instance.device.append(device)
            elif key == 'property':
                instance.property.extend(value.strip('"()"').split("|"))
            else:
                raise AssertionError("key %s is invalid", key) # pragma: no cover
        return instance

class Device(Munch):
    def __init__(self, *args, **kwargs): #pylint: disable-msg=W0613
        for item in ['vendor', 'product']:
            setattr(self, item, None)

KEY_VALUE_PATTERN = \
    r"^\t*(?P<key>[A-Za-z0-9_]+) (?P<value>[^{}\n]+)$"

DEVICE_PATTERN = \
    r"^\t*(?P<key>device|multipath) {(?P<value>[^{}]*)}$"

RULELIST_PATTERN = \
    r"^\t*(?P<key>[A-Za-z0-9_]+) (?P<value>(?:[^{}\n]+)|({[^{}].*?}))$"

MULTIPATH_CONF_PATTERN = \
    r"^(?P<name>defaults|blacklist_exceptions|blacklist|devices|multipaths)" + \
    " {\n*(?P<content>(:?%s)*|(:?%s)*|(:?%s)*|\b|\B)\n*}\n*" % \
        (r"^[^{}\n]*$\n", # key-value pairs
         r"^\t*(?:device|multipath) {[^{}]*}$\n", # devices
         r"(?:^[^{}]*$\n)|(?:^\t*(?:device|multipath) {[^{}]*}$\n)", # both
         )

"""
        (r"^[^{}]*$\n", # key-value pairs
         r"^\t*(?:device|multipath) {[^{}]*}$\n", # devices
         r"(?:^[^{}]*$\n)|(?:^\t*(?:device|multipath) {[^{}]*}$\n)", # both
         )
"""
class Configuration(object):
    """ container for multipathd.conf

    the pupose of the class (and module) is to hold the configuration of multipathd.conf
    it provides a munch-like interface to all the configuration, where the keys are the option names as defined
    in multipath.conf.annotated.
    all values are stored as strings.

    The configuration contains several elements:

    devices        a list of devices, the devices {} section of multipath.conf
    multipaths     a list of mulltipath(es), the multipaths section of multipath.conf
    blacklist      the blacklist section of multipath.conf
    whitelist      the blacklist_exceptions section of multipath.conf

    This class also provides two-way translation to/from the syntax of multipath.conf.
    See the help of to_multipathd_conf and from_multipathd_conf
    """

    def __init__(self):
        super(Configuration, self).__init__()
        self.attributes = ConfigurationAttributes()
        self.devices = []
        self.multipaths = []
        self.blacklist = RuleList()
        self.whitelist = RuleList()

    def to_multipathd_conf(self):
        """ return a string representation of configuration is the syntax of multipath.conf
        unused values are not written to the configuration file
        """
        strings = []
        strings.append('defaults {')
        strings.extend(['\t%s' % line for line in munch_to_multipath_conf(self.attributes).splitlines()])
        strings.append('}')
        strings.append('blacklist {')
        strings.extend(['\t%s' % line for line in self.blacklist.to_multipathd_conf().splitlines()])
        strings.append('}')
        strings.append('blacklist_exceptions {')
        strings.extend(['\t%s' % line for line in self.whitelist.to_multipathd_conf().splitlines()])
        strings.append('}')
        strings.append('devices {')
        for device in self.devices:
            strings.append('\tdevice {')
            strings.extend(['\t\t%s' % line for line in munch_to_multipath_conf(device).splitlines()])
            strings.append('\t}')
        strings.append('}')
        strings.append('multipaths {')
        for multipath in self.multipaths:
            strings.append('\tmultipath {')
            strings.extend(['\t\t%s' % line for line in munch_to_multipath_conf(multipath).splitlines()])
            strings.append('\t}')
        strings.append('}')
        strings.append('') # add \n at the end
        return '\n'.join(strings)

    @classmethod
    def from_multipathd_conf(cls, show_config_output):
        """ this class method takes the multipathd configuration, as taken from multipathd -k; show config
        and returns an instance with all the configuration parsed out of the input

        this method may fail parsing the configuration if it was read directly from the configuration file,
        since it makes some assumpsions that are always valid when looking at the output of 'show config' command.
        For exmaple:
        * identations are with tab characters, and not spaces
        * between and key and value, only one space character exists
        """
        from re import compile, DOTALL, MULTILINE #pylint: disable-msg=W0622
        re_flags = DOTALL | MULTILINE
        pattern = compile(MULTIPATH_CONF_PATTERN, re_flags)
        device_pattern = compile(DEVICE_PATTERN, re_flags)
        instance = cls()

        def populate_list(list, base_class, content): #pylint: disable-msg=W0622
            for match in device_pattern.finditer(content):
                _, value = match.groupdict()['key'], match.groupdict()['value']
                entry = base_class()
                populate_munch_from_multipath_conf_string(entry, value)
                list.append(entry)

        for section in pattern.finditer(show_config_output):
            name, content = section.groupdict()['name'], section.groupdict()['content']
            if name == 'defaults':
                populate_munch_from_multipath_conf_string(instance.attributes, content)
            elif name == 'blacklist':
                instance.blacklist = RuleList.from_multipathd_conf(content)
            elif name == 'blacklist_exceptions':
                instance.whitelist = RuleList.from_multipathd_conf(content)
            elif name == 'devices':
                populate_list(instance.devices, HardwareEntry, content)
            elif name == 'multipaths':
                populate_list(instance.multipaths, MultipathEntry, content)

        return instance

