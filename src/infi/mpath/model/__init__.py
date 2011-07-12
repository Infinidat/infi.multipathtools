
from bunch import Bunch
from logging import debug

def get_bunch_from_multipathd_output(maps_topology, paths_table):
    result = dict()
    return result

def parse_paths_table(paths_table):
    from re import compile, MULTILINE, DOTALL
    HCTL = r'\d+:\d+:\d+:\d+'
    DEV = r'\w+'
    DEV_T = r'\d+:\d+'
    PRI = r'\d+'
    DM_ST = r'(?:\[\w+\])|(?:\w+)'
    CHK_ST = DM_ST
    NEXT_CHECK = '(?:[X\. /0-9]+)|orphan\s*|\[orphan\]\s*'
    PATH_PATTERN = r"^" + \
            ("(?P<hctl>%s)\s+(?P<dev>%s)\s+" % (HCTL, DEV)) + \
            (r"(?P<dev_t>%s)\s+(?P<pri>%s)\s+" % (DEV_T, PRI)) + \
            (r"(?P<dm_st>%s)\s*(?P<chk_st>%s)\s+" % (DM_ST, CHK_ST)) + \
             r"(?:\b|\B|\w+\s+)" + \
            (r"(?P<next_check>%s)$" % (NEXT_CHECK,))
    pattern = compile(PATH_PATTERN, MULTILINE | DOTALL)
    matches = []
    for match in pattern.finditer(paths_table):
        debug("match found: %s", match.groupdict())
        matches.append(dict((key, value.strip('[]')) for (key, value) in match.groupdict().items()))
    return matches
