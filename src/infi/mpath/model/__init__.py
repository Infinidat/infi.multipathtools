
from bunch import Bunch
from logging import debug
from re import compile, MULTILINE, DOTALL

HCTL = r'\d+:\d+:\d+:\d+'
DEV = r'\w+'
DEV_T = r'\d+:\d+'
PRI = r'\d+'
DM_ST = r'(?:\[\w+\])|(?:\w+)'
CHK_ST = DM_ST
NEXT_CHECK = '(?:[X\. /0-9]+)|orphan *|\[orphan\] *'


def parse_paths_table(paths_table):
    PATH_PATTERN = r"^" + \
            ("(?P<hctl>%s) +(?P<dev>%s) +" % (HCTL, DEV)) + \
            (r"(?P<dev_t>%s) +(?P<pri>%s) +" % (DEV_T, PRI)) + \
            (r"(?P<dm_st>%s) *(?P<chk_st>%s) +" % (DM_ST, CHK_ST)) + \
             r"(?:\b|\B|\w+ +)" + \
            (r"(?P<next_check>%s)$" % (NEXT_CHECK,))
    pattern = compile(PATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(paths_table):
        debug("match found: %s", match.groupdict())
        matches.append(dict((key, value.strip('[]')) for (key, value) in match.groupdict().items()))
    return matches

def parse_multipaths_topology(maps_topology):
    PATH_PATTERN = r" +.. (?:%s) +(?:%s) +(?:%s) +(?:%s) *(?:%s) *(?:\w +|\b|\B)$" % \
        (HCTL, DEV, DEV_T, DM_ST, CHK_ST)

    MULTIPATH_PATTERN = r"^" + \
        r"create: (?P<wwid>[a-z0-9]+) ?(?P<dm>dm-\w+) +" \
        r"(?P<vendor>\w+) *,(?P<product>\w+)(?P<rev>[^\n]*)\n" + \
        r"(?P<options>[^\n]+)\n" + \
        r"(?P<policy>[^\n]+)\n" + \
        ("(?P<paths>(?:%s)*)" % PATH_PATTERN)

    pattern = compile(MULTIPATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(maps_topology):
        debug("multipath found: %s", match.groupdict())
        groupdict = dict((key, value.strip(' []')) for (key, value) in match.groupdict().items())
        parse_paths_in_groupdict(groupdict)
        matches.append(groupdict)
    return matches

def parse_paths_in_groupdict(groupdict):
    PATH_PATTERN = r"(?P<hctl>%s) +(?P<dev>%s) +(?P<dev_t>%s)" % (HCTL, DEV, DEV_T)
    pattern = compile(PATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(groupdict['paths']):
        debug("path found: %s", match.groupdict())
        matches.append(dict((key, value.strip(' []')) for (key, value) in match.groupdict().items()))
    groupdict['paths'] = matches


def dict_by_attribute(attr_name, list_obj):
    result = dict()
    for item in list_obj:
        result[item[attr_name]] = item
    return result

def get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table):
    from ..dtypes import MultipathDevice, Path
    multipaths = parse_multipaths_topology(maps_topology)
    paths = parse_paths_table(paths_table)
    paths_by_mjmn = dict_by_attribute('dev_t', paths)
    result = []
    for mpath_dict in multipaths:
        multipath = MultipathDevice(mpath_dict['wwid'], mpath_dict['dm'])
        for path_dict in mpath_dict['paths']:
            path_info = paths_by_mjmn[path_dict['dev_t']]
            path = Path(path_info['dev'], path_info['dev'], path_info['dev_t'], path_info['dm_st'])
            multipath.paths.append(path)
        result.append(multipath)
    return result

def strip_ansi_colors(string):
    pattern = compile(r"\x1b\[[;\d]*[A-Za-z]", MULTILINE | DOTALL)
    return pattern.sub("", string)
