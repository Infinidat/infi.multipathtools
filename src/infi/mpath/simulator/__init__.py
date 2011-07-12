
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
            self._expected_length = MessageLength.create_instance_from_string(message).length
            self._expecting_length = False
        else:
            assert len(message) == self._expected_length
            self._message_to_return = Singleton().handle_incomming_message(message)

    def receive(self, expected_size): #pylint: disable-msg=W0613
        if not self._connected or not self._message_to_return:
            raise SimulatorError
        if not self._sent_message_size:
            self._sent_message_size = True
            instance = MessageLength.create()
            instance.length = len(self._message_to_return)
            return MessageLength.instance_to_string(instance)
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

    def handle_incomming_message(self, message):
        self._handled_messages.append(message)
        if message == 'reconfigure':
            self._load_configuration()
            return 'ok\n'
        if message == 'show config':
            return self._configuration.to_multipathd_conf()

    def __del__(self):
        from os import remove
        try:
            remove(self._conf_path)
        except:
            pass
        super(Simulator, self).__del__()

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
