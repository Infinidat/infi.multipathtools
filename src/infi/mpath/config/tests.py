
from unittest import TestCase, SkipTest
from mock import patch, Mock, MagicMock

#pylint: disable-all

EMPTY_CONFIGURATION = """
defaults {
}
blacklist {
}
blacklist_exceptions {
}
devices {
}
multipaths {
}
""".strip('\n')

EMPTY_CONFIGURATION__EMPTY_CHILDREN = """
defaults {
}
blacklist {
    device {
    }
}
blacklist_exceptions {
    device {
    }
}
devices {
    device {
    }
}
multipaths {
    multipath {
    }
}
""".strip('\n').replace('    ', '\t')

KEY_VALUE_ITEMS = """
a 1
b "hello 1"
foo legen...|wait.for\wit|[^dary]
""".strip('\n').replace('    ', '\t')

class OutputTests(TestCase):
    def test_output__empty_configuration(self):
        from . import Configuration
        config = Configuration()
        self.assertEquals(config.to_multipathd_conf(), EMPTY_CONFIGURATION)

    def test_output__empty_configuration__everything_is_none(self):
        from . import Configuration, Device, MultipathEntry, HardwareEntry
        config = Configuration()
        config.blacklist.device.append(Device())
        config.whitelist.device.append(Device())
        config.hardware_items.append(HardwareEntry())
        config.multipath_items.append(MultipathEntry())
        self.assertEquals(config.to_multipathd_conf(), EMPTY_CONFIGURATION__EMPTY_CHILDREN)

from re import compile, DOTALL, MULTILINE
from . import KEY_VALUE_PATTERN, MULTIPATH_CONF_PATTERN

from os.path import exists, join, sep, abspath, dirname
SAMPLE_FILEPATH = abspath(join(dirname(__file__), "sample.txt"))


class InputTests(TestCase):
    def test_empty_configuration(self):
        from . import Configuration
        config = Configuration.from_multipathd_conf(EMPTY_CONFIGURATION)

    def test_regex__empty_configuration(self):
        pattern = compile(MULTIPATH_CONF_PATTERN, DOTALL | MULTILINE)
        matches = [match.groupdict() for match in pattern.finditer(EMPTY_CONFIGURATION)]
        sections = [dict['name'] for dict in matches]
        self.assertIn('defaults', sections)
        self.assertIn('blacklist', sections)
        self.assertIn('blacklist_exceptions', sections)
        self.assertIn('devices', sections)
        self.assertIn('multipaths', sections)

    def test_regex__key_value_pattern(self):
        pattern = compile(KEY_VALUE_PATTERN, DOTALL | MULTILINE)
        result = pattern.search("key value")
        self.assertEquals(result.groupdict()['key'], 'key')
        self.assertEquals(result.groupdict()['value'], 'value')
        result = pattern.search(r"regex ^this|is|[a][^complicated](regex).*/")
        self.assertEquals(result.groupdict()['key'], 'regex')
        self.assertEquals(result.groupdict()['value'], '^this|is|[a][^complicated](regex).*/')

    def test_regex__multiple_key_values(self):
        pattern = compile(KEY_VALUE_PATTERN, DOTALL | MULTILINE)
        iterator = pattern.finditer(KEY_VALUE_ITEMS)

        expected_keys = ['a', 'b', 'foo']
        expected_values = ['1', '"hello 1"', "legen...|wait.for\wit|[^dary]"]
        for match in iterator:
            self.assertEquals(len(match.groupdict().keys()), 2)
            self.assertIn(match.groupdict()['key'], expected_keys)
            self.assertIn(match.groupdict()['value'], expected_values)

    def test_populate_bunch(self):
        from . import populate_bunch_from_multipath_conf_string
        from bunch import Bunch
        string = """
            foo bar
            high lower
            1 0
            """.replace('    ', '\t')
        instance = Bunch()
        populate_bunch_from_multipath_conf_string(instance, string)
        self.assertEquals(instance.foo, 'bar')
        self.assertEquals(instance.high, 'lower')
        self.assertEquals(instance['1'], '0')

    def test_rulelist_from_string(self):
        from . import RuleList
        string = """
        devnode ^something%N
        devnode else$
        wwid 010203040506
        device {
            product someProduct
            vendor someVendor
        }
        """.replace('    ', '\t')
        instance = RuleList.from_multipathd_conf(string)
        self.assertEqual(len(instance.device), 1)
        self.assertEqual(len(instance.devnode), 2)
        self.assertEqual(len(instance.wwid), 1)
        self.assertEquals(instance.device[0].product, 'someProduct')
        self.assertEquals(instance.device[0].vendor , 'someVendor')
        self.assertEquals(instance.devnode, ['^something%N', 'else$'])
        self.assertEquals(instance.wwid, ['010203040506', ])


    def test_regex__sample_configuration(self):
        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)

        pattern = compile(MULTIPATH_CONF_PATTERN, DOTALL | MULTILINE)
        matches = [match.groupdict() for match in pattern.finditer(sample_config_string)]
        sections = [dict['name'] for dict in matches]
        self.assertIn('defaults', sections)
        self.assertIn('blacklist', sections)
        self.assertIn('blacklist_exceptions', sections)
        self.assertIn('devices', sections)
        self.assertIn('multipaths', sections)

    def test_sample_configuration(self):
        from . import Configuration

        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)

        config = Configuration.from_multipathd_conf(sample_config_string)
        self.assertEqual(config.attributes.udev_dir, '/dev')
        self.assertEqual(config.attributes.polling_interval, '10')
        self.assertEquals(config.attributes.uid, '0')
        self.assertEqual(config.blacklist.wwid, ['26353900f02796769'])
        self.assertIn('"^dcssblk[0-9]*"', config.blacklist.devnode)
        self.assertEqual(config.blacklist.device[0].product, "MSA[15]00")
        self.assertIn('"IBM.75000000092461.4d00.36"', config.whitelist.wwid)
        self.assertEqual(len(config.multipath_items), 2)
        self.assertEqual(config.multipath_items[0].wwid, "3600508b4000156d700012000000b0000")
        self.assertEqual(config.multipath_items[0].failback, "manual")
        self.assertEqual(len(config.hardware_items), 2)
        self.assertEqual(config.hardware_items[1].path_grouping_policy, "multibus")

class InOut(TestCase):
    def test_sample_configuration(self):
        from . import Configuration

        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)
        config = Configuration.from_multipathd_conf(sample_config_string)
        self.assertEqual(config.to_multipathd_conf(), sample_config_string)
