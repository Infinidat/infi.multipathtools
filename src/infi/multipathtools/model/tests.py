
from infi import unittest
from six.moves import builtins
import mock

#pylint: disable-all

MOCK_OUTPUT = [
               {'show multipaths topology': "create: 36000402001f45eb566e79f6d00000000 dm-0 NEXSAN,SATABoy2\nsize=3.7G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 4:0:0:10 sdc 8:32 active ready  running\ncreate: 36000402001f45eb56424ca6800000000 dm-1 NEXSAN,SATABoy2\nsize=466G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=0 status=active\n  `- 4:0:0:0  sdb 8:16 failed faulty running\ncreate: 36000402001f45eb566e79fb700000000 dm-2 NEXSAN,SATABoy2\nsize=5.6G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 4:0:0:11 sdd 8:48 active ready  running",
                'show paths': 'hcil     dev dev_t pri dm_st  chk_st dev_st  next_check     \n2:0:0:0  sda 8:0   1   undef  ready  running orphan         \n4:0:0:10 sdc 8:32  1   active ready  running XXXX...... 9/20\n4:0:0:0  sdb 8:16  1   failed faulty running X......... 2/20\n4:0:0:11 sdd 8:48  1   active ready  running XXXX...... 8/20'
                },
               {'show multipaths topology': 'create: 36000402001f45eb56424ca6800000000dm-0  NEXSAN  ,SATABoy2      \n[size=466G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:0  sdb 8:16  [active][ready]\ncreate: 36000402001f45eb566e79f6d00000000dm-1  NEXSAN  ,SATABoy2      \n[size=3.7G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:10 sdc 8:32  [active][ready]\ncreate: 36000402001f45eb566e79fb700000000dm-2  NEXSAN  ,SATABoy2      \n[size=5.6G][features=0       ][hwhandler=0        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 5:0:0:11 sdd 8:48  [active][ready]',
                 'show paths': 'hcil     dev dev_t pri dm_st   chk_st  next_check      \n2:0:0:0  sda 8:0   1   [undef] [undef] [orphan]        \n5:0:0:0  sdb 8:16  1   [active][ready] .......... 1/20 \n5:0:0:10 sdc 8:32  1   [active][ready] XXXXXXX... 15/20\n5:0:0:11 sdd 8:48  1   [active][ready] XXXXXXXX.. 17/20'
                },
               {'show multipaths topology': 'create: 36000402001f45eb56424ca6800000000 dm-0  NEXSAN,SATABoy2\n[size=466G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 2:0:0:0  sdb 8:16  [active][ready]\ncreate: 36000402001f45eb566e79f6d00000000 dm-1  NEXSAN,SATABoy2\n[size=3.7G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][active]\n \\_ 2:0:0:10 sdc 8:32  [active][ready]\ncreate: 36000402001f45eb566e79fb700000000 dm-2  NEXSAN,SATABoy2\n[size=5.6G][features=0       ][hwhandler=0        ][rw        ]\n\\_ round-robin 0 [prio=0][enabled]\n \\_ 2:0:0:11 sdd 8:48  [active][ready]',
                'show paths': 'hcil     dev dev_t pri dm_st   chk_st  next_check     \n0:0:0:0  sda 8:0   1   [undef] [ready] [orphan]       \n2:0:0:0  sdb 8:16  1   [active][ready] XXXX...... 9/20\n2:0:0:10 sdc 8:32  1   [active][ready] X......... 2/20\n2:0:0:11 sdd 8:48  1   [active][ready] XXXX...... 9/20'
                },
               {'show multipaths topology': "mpatha (35742b0f006800000) dm-0 INFINID,Infinidat A01\nsize=10G features='0' hwhandler='0' wp=rw\n|-+- policy='round-robin 0' prio=1 status=active\n| `- 3:0:0:1 sdb 8:16 active ready running\n`-+- policy='round-robin 0' prio=1 status=enabled\n  `- 2:0:0:1 sdc 8:32 active ready running\nmpathb (36000402001f45eb565889a4b00000000) dm-2 NEXSAN,SATABoy2\nsize=47G features='0' hwhandler='0' wp=rw\n|-+- policy='round-robin 0' prio=1 status=active\n| `- 2:0:1:0 sdd 8:48 active ready running\n`-+- policy='round-robin 0' prio=1 status=enabled\n  `- 3:0:1:1 sdf 8:80 active ready running\nmpathc (36000402001f45eb565a24ae100000000) dm-3 NEXSAN,SATABoy2\nsize=466G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 3:0:1:0 sde 8:64 active ready running",
                'show paths': 'hcil    dev dev_t pri dm_st  chk_st dev_st  next_check      \n4:0:0:0 sda 8:0   1   undef  ready  running orphan          \n3:0:0:1 sdb 8:16  1   active ready  running XXXXXXX... 14/20\n2:0:0:1 sdc 8:32  1   active ready  running XXXXXXXX.. 16/20\n2:0:1:0 sdd 8:48  1   active ready  running XXXXXXXX.. 16/20\n3:0:1:0 sde 8:64  1   active ready  running XXXXXXX... 14/20\n3:0:1:1 sdf 8:80  1   active ready  running XXXXXX.... 13/20'
                },
               {'show multipaths topology': "mpatha (35742b0f006800000) dm-0 INFINID,Infinidat A01\nsize=10G features='0' hwhandler='0' wp=rw\n|-+- policy='round-robin 0' prio=1 status=active\n| `- 3:0:0:1 sdb 8:16 active ready running\n`-+- policy='round-robin 0' prio=1 status=enabled\n  `- 2:0:0:1 sdc 8:32 active ready running\nmpathb (36000402001f45eb565889a4b00000000) dm-2 NEXSAN,SATABoy2\nsize=47G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  |- 2:0:1:0 sdd 8:48 active ready running\n  `- 3:0:1:1 sdf 8:80 active ready running\nmpathc (36000402001f45eb565a24ae100000000) dm-3 NEXSAN,SATABoy2\nsize=466G features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=1 status=active\n  `- 3:0:1:0 sde 8:64 active ready running",
                'show paths': 'hcil    dev dev_t pri dm_st  chk_st dev_st  next_check      \n4:0:0:0 sda 8:0   1   undef  ready  running orphan          \n3:0:0:1 sdb 8:16  1   active ready  running XXXXXXXX.. 16/20\n2:0:0:1 sdc 8:32  1   active ready  running XXXXXXX... 15/20\n2:0:1:0 sdd 8:48  1   active ready  running XXXX...... 9/20 \n3:0:1:0 sde 8:64  1   active ready  running XXXXXXXXXX 20/20\n3:0:1:1 sdf 8:80  1   active ready  running XXXXX..... 10/20'
                },
               {'show multipaths topology': "mpaths (36742b0f0000004450000000000058bf2) dm-1 NFINIDAT,InfiniBox\nsize=954M features='0' hwhandler='0' wp=rw\n`-+- policy='round-robin 0' prio=50 status=active\n  |- 0:0:0:2  sdg 8:96  active ready       running\n  |- 0:0:1:2  sdh 8:112 active i/o pending running\n  |- 0:0:11:2 sdi 8:128 active i/o pending running\n  |- 0:0:21:2 sdj 8:144 active ready       running\n  `- 0:0:22:2 sdk 8:160 active ready       running",
                'show paths': 'hcil     dev dev_t pri dm_st  chk_st      dev_st  next_check\n0:0:0:1  sdb 8:16  50  active i/o pending running XXXXXXXXX. 9/10\n0:0:1:1  sdc 8:32  50  active ready       running XX........ 1/5\n0:0:11:1 sdd 8:48  50  active ready       running XXXXXXXXXX 10/10'
               }
               ]


from . import parse_paths_table, parse_multipaths_topology, strip_ansi_colors
from . import get_list_of_multipath_devices_from_multipathd_output
from ..dtypes import MultipathDevice, Path, PathGroup

class PathTableTestCase(unittest.TestCase):

    def _assert_lists(self, a, b):
        a.sort()
        b.sort()
        self.assertEqual(a, b)

    def _validate_example(self, matches):
        self.assertEqual(len(matches), 4)
        for hctl in [match['hctl'] for match in matches]:
            self.assertTrue(len(hctl.split(':')), 4)
            self.assertTrue([item.isdigit() for item in hctl.split(':')],
                            [True, ] * 4)
        self._assert_lists([match['dev'] for match in matches],
                         ['sda', 'sdc', 'sdb', 'sdd'])
        self._assert_lists([match['dev_t'] for match in matches],
                         ['8:0', '8:32', '8:16', '8:48'])
        for item in [match['dm_st'] for match in matches]:
            self.assertIn(item, ['active', 'undef', 'failed'])
        for item in [match['chk_st'] for match in matches]:
            self.assertIn(item, ['active', 'undef', 'failed', 'ready', 'faulty'])

    def test_parser__1(self):
        subject = MOCK_OUTPUT[0]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self._validate_example(matches)

    def test_parser__2(self):
        subject = MOCK_OUTPUT[1]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 4)
        self._validate_example(matches)

    def test_parser__3(self):
        subject = MOCK_OUTPUT[2]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 4)
        self._validate_example(matches)

    def test_parser__4(self):
        subject = MOCK_OUTPUT[3]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 6)

    def test_parser__5(self):
        subject = MOCK_OUTPUT[4]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 6)

    def test_parser__6(self):
        subject = MOCK_OUTPUT[5]['show paths']
        matches = [match for match in parse_paths_table(subject)]
        self.assertEqual(len(matches), 3)


class MultipathsTopologyTestCase(unittest.TestCase):
    def _validate_example(self, matches):
        self.assertEqual(len(matches), 3)
        self.assertEqual([len(match['path_groups']) for match in matches],
                         [1] * 3)
        self.assertEqual([len(match['path_groups'][0]['paths']) for match in matches],
                         [1] * 3)

    def test_parser__1(self):
        subject = MOCK_OUTPUT[0]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self._validate_example(matches)

    def test_parser__2(self):
        subject = MOCK_OUTPUT[1]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 3)

    def test_parser__3(self):
        subject = MOCK_OUTPUT[2]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 3)

    def test_parser__4(self):
        subject = MOCK_OUTPUT[3]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 3)

    def test_parser__5(self):
        subject = MOCK_OUTPUT[4]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 3)

    def test_parser__6(self):
        subject = MOCK_OUTPUT[5]['show multipaths topology']
        matches = [match for match in parse_multipaths_topology(subject)]
        self.assertEqual(len(matches), 1)
        self.assertEqual(len(matches[0]['path_groups'][0]['paths']), 5)

class ModelTestCase(unittest.TestCase):
    def _get_devices_from_example_by_index(self, index):
        output = MOCK_OUTPUT[index]
        maps_topology = output['show multipaths topology']
        paths_table = output['show paths']
        with mock.patch.object(builtins, "open") as open:
            devices = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)
        self.assertEqual(len(devices), 3)
        return devices

    def test_example__1(self):
        devices = self._get_devices_from_example_by_index(0)
        actual = devices[0]
        with mock.patch.object(builtins, "open") as open:
            expected = MultipathDevice('36000402001f45eb566e79f6d00000000',
                                       '36000402001f45eb566e79f6d00000000',
                                       'dm-0')
        expected.path_groups.append(PathGroup('active', '1'))
        expected.path_groups[0].paths.append(Path('sdc', 'sdc', '8:32', 'active', '1', '4:0:0:10'))
        self.assertEqual(actual, expected)

    def test_example__4(self):
        devices = self._get_devices_from_example_by_index(3)
        self.assertEqual(len(devices), 3)
        actual = devices[0]
        with mock.patch.object(builtins, "open") as open:
            expected = MultipathDevice('35742b0f006800000',
                                       'mpatha',
                                       'dm-0')
        expected.path_groups.append(PathGroup('active', '1'))
        expected.path_groups.append(PathGroup('enabled', '1'))
        expected.path_groups[0].paths.append(Path('sdb', 'sdb', '8:16', 'active', '1',
                                                  '3:0:0:1'))
        expected.path_groups[1].paths.append(Path('sdc', 'sdc', '8:32', 'active', '1',
                                                  '2:0:0:1'))
        self.assertEqual(actual, expected)
        self.assertEqual(actual.path_groups[0].paths[0].hctl, (3, 0, 0, 1))

    def test_example__5(self):
        devices = self._get_devices_from_example_by_index(4)
        self.assertEqual(len(devices), 3)
        actual = devices[1]
        with mock.patch.object(builtins, "open") as open:
            expected = MultipathDevice('36000402001f45eb565889a4b00000000',
                                       'mpathb',
                                       'dm-2')
        expected.path_groups.append(PathGroup('active', '1'))
        expected.path_groups[0].paths.append(Path('sdd', 'sdd', '8:48', 'active', '1', '2:0:1:0'))
        expected.path_groups[0].paths.append(Path('sdf', 'sdf', '8:80', 'active', '1', '3:0:1:1'))
        self.assertEqual(actual, expected)

class AnsiColorsTestCase(unittest.TestCase):
    def test_strip(self):
        subject = "\n".join(["\x1b[1mcreate: 36000402001f45eb566e79f6d00000000 dm-0 NEXSAN,SATABoy2\x1b[0m"] * 4)
        expected = "\n".join(["create: 36000402001f45eb566e79f6d00000000 dm-0 NEXSAN,SATABoy2"] * 4)
        actual = strip_ansi_colors(subject)
        self.assertEqual(actual, expected)

VERSION_OUTPUT = ["""multipath-tools v0.4.8 (08/02, 2007)
CLI commands reference:
 list|show paths
 list|show maps|multipaths
 list|show maps|multipaths status
 list|show maps|multipaths stats
 list|show maps|multipaths topology
 list|show topology""",

 """multipath-tools v0.4.9 (04/04, 2009)
CLI commands reference:
 list|show paths
 list|show paths format $format
 list|show status""",

 """fail
multipath-tools v0.4.7 (03/12, 2006)
CLI commands reference:
 list|show paths
 list|show maps|multipaths
 list|show maps|multipaths status
 list|show maps|multipaths stats"""]

class ParseVersionTestCase(unittest.TestCase):
    @unittest.parameters.iterate("output", VERSION_OUTPUT)
    def test_parse_version(self, output):
        from . import parse_multipath_tools_version
        actual = parse_multipath_tools_version(output)
        expected = ["0.4.8", "0.4.9", "0.4.7"]
        self.assertIn(actual, expected)
