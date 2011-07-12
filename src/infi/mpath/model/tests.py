
import unittest
import mock

MOCK_OUTPUT = {'v0.4.9':
               {'show multipaths topology': "\x1b[1mcreate: 36000402001f45eb566e79f6d00000000 dm-0 NEXSAN,SATABoy2\x1b[0m\nsize=3.7G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 4:0:0:10 sdc 8:32 active ready  running\n\x1b[1mcreate: 36000402001f45eb56424ca6800000000 dm-1 NEXSAN,SATABoy2\x1b[0m\nsize=466G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=0 status=active\n  `- 4:0:0:0  sdb 8:16 failed faulty running\n\x1b[1mcreate: 36000402001f45eb566e79fb700000000 dm-2 NEXSAN,SATABoy2\x1b[0m\nsize=5.6G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 4:0:0:11 sdd 8:48 active ready  running",
                'show paths': 'hcil     dev dev_t pri dm_st  chk_st dev_st  next_check     \n2:0:0:0  sda 8:0   1   undef  ready  running orphan         \n4:0:0:10 sdc 8:32  1   active ready  running XXXX...... 9/20\n4:0:0:0  sdb 8:16  1   failed faulty running X......... 2/20\n4:0:0:11 sdd 8:48  1   active ready  running XXXX...... 8/20'},
               'v0.4.8':
               {'show multipaths topology': 'create: 36000402001f45eb56424ca6800000000dm-0  NEXSAN  ,SATABoy2      \n[size=466G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:0  sdb 8:16  [active][ready]\ncreate: 36000402001f45eb566e79f6d00000000dm-1  NEXSAN  ,SATABoy2      \n[size=3.7G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:10 sdc 8:32  [active][ready]\ncreate: 36000402001f45eb566e79fb700000000dm-2  NEXSAN  ,SATABoy2      \n[size=5.6G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:11 sdd 8:48  [active][ready]',
                 'show paths': 'hcil     dev dev_t pri dm_st   chk_st  next_check      \n2:0:0:0  sda 8:0   1   [undef] [undef] [orphan]        \n5:0:0:0  sdb 8:16  1   [active][ready] .......... 1/20 \n5:0:0:10 sdc 8:32  1   [active][ready] XXXXXXX... 15/20\n5:0:0:11 sdd 8:48  1   [active][ready] XXXXXXXX.. 17/20'                 },
               'v0.4.7':
               {'show multipaths topology': 'create: 36000402001f45eb56424ca6800000000 dm-0  NEXSAN,SATABoy2\n[size=466G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 2:0:0:0  sdb 8:16  [active][ready]\ncreate: 36000402001f45eb566e79f6d00000000 dm-1  NEXSAN,SATABoy2\n[size=3.7G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][active]\n \\_ 2:0:0:10 sdc 8:32  [active][ready]\ncreate: 36000402001f45eb566e79fb700000000 dm-2  NEXSAN,SATABoy2\n[size=5.6G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 2:0:0:11 sdd 8:48  [active][ready]',
                'show paths': 'hcil     dev dev_t pri dm_st   chk_st  next_check     \n0:0:0:0  sda 8:0   1   [undef] [ready] [orphan]       \n2:0:0:0  sdb 8:16  1   [active][ready] XXXX...... 9/20\n2:0:0:10 sdc 8:32  1   [active][ready] X......... 2/20\n2:0:0:11 sdd 8:48  1   [active][ready] XXXX...... 9/20'
               }
               }

# TODO add a mock that has more than one path per multipath

from . import parse_paths_table, parse_multipaths_topology
from . import get_list_of_multipath_devices_from_multipathd_output
from ..dtypes import MultipathDevice, Path

class PathTableTestCase(unittest.TestCase):
    def test_parser__1(self):
        subject = MOCK_OUTPUT['v0.4.7']['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 4)
        # TODO add more asserts to verify content

    def test_parser__2(self):
        subject = MOCK_OUTPUT['v0.4.8']['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 4)
        # TODO add more asserts to verify content

    def test_parser__3(self):
        subject = MOCK_OUTPUT['v0.4.9']['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 4)
        # TODO add more asserts to verify content

class MultipathsTopologyTestCase(unittest.TestCase):
    def test_parser__1(self):
        subject = MOCK_OUTPUT['v0.4.7']['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 3)

class ModelTestCase(unittest.TestCase):
    def test_example__1(self):
        output = MOCK_OUTPUT['v0.4.7']
        maps_topology = output['show multipaths topology']
        paths_table = output['show paths']
        devices = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)
        self.assertEqual(len(devices), 3)
        [self.assertIsInstance(item, MultipathDevice) for item in devices]
        self.assertEquals([item.id for item in devices], ['36000402001f45eb56424ca6800000000',
                                                          '36000402001f45eb566e79f6d00000000',
                                                          '36000402001f45eb566e79fb700000000'])
        for device in devices:
            [self.assertIsInstance(item, Path) for item in device.paths]
            self.assertIn([path.id for path in device.paths], [['sdb'], ['sdc'], ['sdd']])
        # TODO add more asserts to verify content

    # TODO add more tests on the rest of hte examples
    # TODO add more tests on devices with more than one path