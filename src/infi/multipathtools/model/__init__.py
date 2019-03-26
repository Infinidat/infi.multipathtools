
from munch import Munch
from re import compile, MULTILINE, DOTALL

from logging import getLogger
logger = getLogger(__name__)

HCTL = r'\d+:\d+:\d+:\d+'
DEV = r'\w+'
DEV_T = r'\d+:\d+'
PRI = r'[-]?\d+'
DM_ST = '(?:active|failed|undef|\[active\]|\[failed\]|\[undef\])'
CHK_ST = '(?:ready|faulty|shaky|ghost|i/o pending|i/o timeout|undef|\[ready\]|\[faulty\]|\[shaky\]|\[ghost\]|i/o \[pending\]|i/o \[timeout\]|\[undef\])'
DEV_ST = r'(?:\b|\B|\w+ +|running|offline|\[running\]|\[offline\])'
NEXT_CHECK = '(?:[X\. /0-9]+)|orphan *|\[orphan\] *'


def parse_paths_table(paths_table):
    PATH_PATTERN = r"^" + \
            ("(?P<hctl>%s) +(?P<dev>%s) +" % (HCTL, DEV)) + \
            (r"(?P<dev_t>%s) +(?P<pri>%s) +" % (DEV_T, PRI)) + \
            (r"(?P<dm_st>%s) *(?P<chk_st>%s) +(?P<dev_st>%s) ?" % (DM_ST, CHK_ST, DEV_ST)) + \
            (r"(?P<next_check>%s)$" % (NEXT_CHECK,))
    pattern = compile(PATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(paths_table):
        logger.debug("match found: %s", match.groupdict())
        matches.append(dict((key, value.strip('[]')) for (key, value) in match.groupdict().items()))
    return matches


def parse_multipaths_topology(maps_topology):
    MULTIPATH_PATTERN = r"^" + \
        r"(?:(?P<action>[^:]*): +|\b|\B)" + \
        r"(?:(?P<alias>[A-Za-z0-9_-]+) +|\b|\B)" + \
        r"(?P<wwid>[A-Za-z0-9_\(\) ]+) *" + \
        r"(?P<dm>dm-\w+) +" \
        r"(?P<vendor>\w+) *,(?P<product>\w+)(?P<rev>.*)\n" + \
        r"(?P<options>.+)\n" + \
        r"(?P<path_groups>(?:(?:.*[\|`\\].*\n?)*))"
    pattern = compile(MULTIPATH_PATTERN, MULTILINE)
    matches = []
    for match in pattern.finditer(maps_topology):
        logger.debug("multipath found: %s", match.groupdict())
        multipath_dict = dict((key, value.strip(' ()[]') if value is not None else value) \
                              for (key, value) in match.groupdict().items())
        parse_path_groups_in_multipath_dict(multipath_dict)
        matches.append(multipath_dict)
    return matches

def parse_path_groups_in_multipath_dict(multipath_dict):
    PATH_GROUP_PATTERN = r"^" + \
        r"[^\n]*" + \
        r"\[?prio=(?P<prio>\d+)\]?" + \
        r" *" + \
        r"(?:status=|\b|\B)" + \
        r"\[?(?P<state>\w+)\]?" + \
        r" *\n" + \
        r"(?P<paths>(?:(?:.*:.*\n?)*))"
    pattern = compile(PATH_GROUP_PATTERN, MULTILINE)
    matches = []
    for match in pattern.finditer(multipath_dict['path_groups']):
        logger.debug("pathgroup found: %s", match.groupdict())
        pathgroup_dict = dict((key, value.strip(' ()[]') if value is not None else value) for (key, value) in match.groupdict().items())
        parse_paths_in_pathgroup_dict(pathgroup_dict)
        matches.append(pathgroup_dict)
    multipath_dict['path_groups'] = matches

def parse_paths_in_pathgroup_dict(pathgroup_dict):
    PATH_PATTERN = r"(?P<hctl>%s) +(?P<dev>%s) +(?P<dev_t>%s)" % (HCTL, DEV, DEV_T)
    pattern = compile(PATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(pathgroup_dict['paths']):
        logger.debug("path found: %s", match.groupdict())
        matches.append(dict((key, value.strip(' []')) for (key, value) in match.groupdict().items()))
    pathgroup_dict['paths'] = matches

def dict_by_attribute(attr_name, list_obj):
    result = dict()
    for item in list_obj:
        result[item[attr_name]] = item
    return result

def get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table):
    from ..dtypes import MultipathDevice, Path, PathGroup
    multipaths = parse_multipaths_topology(maps_topology)
    paths = parse_paths_table(paths_table)
    paths_by_mjmn = dict_by_attribute('dev_t', paths)
    result = []
    logger.debug("multipaths = %s", multipaths)
    for mpath_dict in multipaths:
        try:
            multipath = MultipathDevice(mpath_dict['wwid'], mpath_dict['alias'] or mpath_dict['wwid'], mpath_dict['dm'])
        except IOError as err:
            logger.error("MultipathDevice disappeared: {}".format(err))
            continue
        for pathgroup_dict in mpath_dict['path_groups']:
            path_group = PathGroup(pathgroup_dict['state'], pathgroup_dict['prio'])
            for path_dict in pathgroup_dict['paths']:
                mjmn = path_dict['dev_t']
                if mjmn not in paths_by_mjmn.keys():
                    logger.debug("There is no path for major:minor {}, only for {}".format(mjmn, paths_by_mjmn))
                    continue
                path_info = paths_by_mjmn[mjmn]
                path = Path(path_info['dev'], path_info['dev'], path_info['dev_t'],
                            path_info['dm_st'], path_info['pri'], path_info['hctl'])
                path_group.paths.append(path)
            multipath.path_groups.append(path_group)
        result.append(multipath)
    return result

def strip_ansi_colors(string):
    pattern = compile(r"\x1b\[[;\d]*[A-Za-z]", MULTILINE | DOTALL)
    return pattern.sub("", string)

def parse_multipath_tools_version(string):
    pattern = compile(r"^multipath-tools v(?P<version>[0-9\.]+)", MULTILINE)
    match = pattern.search(string)
    return match.groupdict()['version']
