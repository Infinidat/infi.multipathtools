
#pylint: disable-msg=E1101

from os.path import sep, join
from contextlib import contextmanager

DEFAULT_CONF_FILE = join(sep, 'etc', 'multipath.conf')

from ..connection import MessageLength, UnixDomainSocket

class MultipathClient(object):
    def __init__(self, connection=UnixDomainSocket()):
        super(MultipathClient, self).__init__() #pragma: no cover
        self._connection = connection

    @contextmanager
    def _with_connection_open(self):
        try:
            self._connection.connect()
            yield
        finally:
            self._connection.disconnect()

    def _get_message_size_as_string(self, message):
        instance = MessageLength.create()
        instance.length = len(message)
        return MessageLength.instance_to_string(instance)

    def _get_expected_message_size_from_string(self, string):
        return MessageLength.create_instance_from_string(string).length

    def _strip_ansi_colors(self, string):
        # TODO implement this
        return string

    def _send_and_receive(self, message):
        message = "%s\n" % message
        with self._with_connection_open():
            self._connection.send(self._get_message_size_as_string(message))
            self._connection.send(message)
            stream = self._connection.receive(MessageLength.sizeof())
            expected_length = self._get_expected_message_size_from_string(stream)
            response = self._connection.receive(expected_length)
            return self._strip_ansi_colors(response.strip('\x00\n'))

    def rescan(self):
        result = self._send_and_receive("reconfigure")
        if result != 'ok':
            raise RuntimeError(result) # TODO test this

    def get_multipathd_conf(self):
        from ..config import Configuration
        return Configuration.from_multipathd_conf(self._send_and_receive("show config"))

    def write_to_multipathd_conf(self, value, filepath=DEFAULT_CONF_FILE):
        from ..config import Configuration
        assert isinstance(value, Configuration)
        with open(filepath, 'w') as fd:
            fd.write(value.to_multipathd_conf())

    def _get_multipath_information(self):
        from model import get_bunch_from_multipathd_output
        maps_topology = self._send_and_receive("show multipaths topology")
        paths_table = self._send_and_receive("show paths")
        result = get_bunch_from_multipathd_output(maps_topology, paths_table)
        return result

    def get_paths(self):
        return self._get_multipath_information().paths

    def get_multipaths(self):
        return self._get_multipath_information().multipaths

    def fail_path(self, path):
        raise NotImplementedError

    def reinstate_path(self, path):
        raise NotImplementedError


__all__ = ('MultipathClient')
