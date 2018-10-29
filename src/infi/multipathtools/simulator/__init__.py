from __future__ import print_function
from ..connection import BaseConnection
from ..connection import MessageLength
from infi.exceptools import chain

#pylint: disable-msg=E1101

class SimulatorError(Exception):
    pass

class SimulatorConnection(BaseConnection):
    def __init__(self):
        self._connected = False
        self._response = None
        self._expecting_length = False
        self._expected_length = 0
        self._message_to_return = None
        self._sent_message_size = False

    def connect(self):
        self._connected = True
        self._response = None
        self._expecting_length = True
        self._expected_length = 0
        self._message_to_return = None
        self._sent_message_size = False

    def send(self, message):
        if self._expecting_length:
            self._expected_length = MessageLength.create_from_string(message).length
            self._expecting_length = False
        else:
            assert len(message) == self._expected_length
            self._message_to_return = Singleton().handle_incomming_message(message)

    def receive(self, expected_size): #pylint: disable-msg=W0613
        if not self._connected or not self._message_to_return:
            raise SimulatorError
        if not self._sent_message_size:
            self._sent_message_size = True
            instance = MessageLength()
            instance.length = len(self._message_to_return)
            return MessageLength.write_to_string(instance)
        else:
            return self._message_to_return

    def disconnect(self):
        self._connected = False

class Simulator(object):
    def __init__(self, conf_path):
        super(Simulator, self).__init__()
        self._handled_messages = []
        self._conf_path = conf_path
        self._write_sample_config_if_empty()
        self._load_configuration()
        self._load_devices()

    def _load_devices(self):
        from ..model import tests
        from ..model import get_list_of_multipath_devices_from_multipathd_output
        from mock import patch
        from six.moves import builtins
        output = tests.MOCK_OUTPUT[-1]
        maps_topology = output['show multipaths topology']
        paths_table = output['show paths']
        with patch.object(builtins, "open"):
            self._devices = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)

    def _write_sample_config_if_empty(self):
        from os.path import exists, join, sep, dirname
        if exists(self._conf_path) and open(self._conf_path).read() != '':
            return
        from ..config.tests import SAMPLE_FILEPATH
        with open(SAMPLE_FILEPATH) as sample_fd:
            sample_content = sample_fd.read()
        with open(self._conf_path, 'w') as conf_fd:
            conf_fd.write(sample_content)

    def _load_configuration(self):
        from ..config import Configuration
        with open(self._conf_path) as conf_fd:
            self._configuration = Configuration.from_multipathd_conf(conf_fd.read())

    def _path_change_state(self, path_id):
        for device in self._devices:
            for pathgroup in device.path_groups:
                for path in pathgroup.paths:
                    if path.id == path_id:
                        print('changing state of %s from %s' % (path_id, path.state))
                        path.state = 'failed' if path.state == 'active' else 'active'

    def handle_incomming_message(self, message):
        from ..model import tests
        # the "real" send and receieve functions deal with bytes which are actually ascii messages.
        # It's easier to deal with strings here by decoding input first and encoding output last
        message = message.decode("ascii").strip('\n')
        self._handled_messages.append(message)
        print(message)
        if message == 'show config':
            response = self._configuration.to_multipathd_conf()
        elif message == 'reconfigure':
            self._load_configuration()
            response = 'ok\n'
        elif message in ['show multipaths topology', 'show paths']:
            output = tests.MOCK_OUTPUT[-1]
            response = output[message]
        elif message.rsplit(' ', 1)[0] == 'fail path':
            path_id = message.rsplit(' ', 1)[1]
            self._path_change_state(path_id)
            response = 'ok\n'
        elif message.rsplit(' ', 1)[0] == 'reinstate path':
            path_id = message.rsplit(' ', 1)[1]
            self._path_change_state(path_id)
            response = 'ok\n'
        elif message.rsplit(' ', 1)[0] == '?':
            from ..model.tests import VERSION_OUTPUT
            response = VERSION_OUTPUT[0]
        else:
            raise AssertionError("Unknown message " + message)
        return response.encode("ascii")

#TODO load some multipaths to simualtor
#TODO support fail_path, reinstate_path

class Singleton(object):
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs): #pylint: disable-msg=W0613
        if not cls._instance:
            from tempfile import mkstemp
            from os import close
            fd, fpath = mkstemp()
            close(fd)
            cls._instance = Simulator(fpath)
        return cls._instance
