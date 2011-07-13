
def print_examples():
    from .tests import MOCK_OUTPUT
    from . import get_list_of_multipath_devices_from_multipathd_output

    for output in MOCK_OUTPUT:
        maps_topology = output['show multipaths topology']
        paths_table = output['show paths']
        devices = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)
        print devices

if __name__ == "__main__":
    print_examples()
