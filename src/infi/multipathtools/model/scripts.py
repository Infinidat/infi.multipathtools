from __future__ import print_function

def print_examples():
    from .tests import MOCK_OUTPUT
    from . import get_list_of_multipath_devices_from_multipathd_output
    from json import dumps
    for output in MOCK_OUTPUT:
        maps_topology = output['show multipaths topology']
        paths_table = output['show paths']
        devices = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)
        print(dumps(devices, sort_keys=True, indent=4))
if __name__ == "__main__":
    print_examples()
