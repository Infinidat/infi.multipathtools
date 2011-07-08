
from ..client import BaseConnection
from ..client import MessageLength
from infi.exceptools import chain

class SimulatorError(Exception):
    pass

class SimulatorConnection(BaseConnection):
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

    def receive(self, expected_size):
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
    def __init__(self):
        super(Simulator, self).__init__()
        self._handled_messages = []

    def handle_incomming_message(self, message):
        self._handled_messages.append(message)
        if message == 'reconfigure':
            return 'ok\n'

class Singleton(object):
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = Simulator()
        return cls._instance
