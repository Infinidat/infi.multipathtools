
#pylint: disable-msg=E1101

import time
from os.path import sep, join
from contextlib import contextmanager
from ..errors import ConnectionError

DEFAULT_CONF_FILE = join(sep, 'etc', 'multipath.conf')

from ..connection import MessageLength, UnixDomainSocket

class MultipathClient(object):
    """ Client to the multipath-tools daemon
    """

    def __init__(self, connection=None):
        super(MultipathClient, self).__init__() #pragma: no cover
        self._connection = connection or UnixDomainSocket()

    @contextmanager
    def _with_connection_open(self):
        try:
            self._connection.connect()
            yield
        finally:
            self._connection.disconnect()

    def is_running(self):
        try:
            with self._with_connection_open():
                pass
            return True
        except ConnectionError:
            pass
        return False

    def _get_message_size_as_string(self, message):
        instance = MessageLength()
        instance.length = len(message)
        return MessageLength.write_to_string(instance)

    def _get_expected_message_size_from_string(self, string):
        return MessageLength.create_from_string(string).length

    def _send_and_receive(self, message):
        from ..model import strip_ansi_colors
        message = "%s\n" % message
        with self._with_connection_open():
            self._connection.send(self._get_message_size_as_string(message))
            self._connection.send(message.encode("ascii"))
            stream = self._connection.receive(MessageLength.min_max_sizeof().max)
            expected_length = self._get_expected_message_size_from_string(stream)
            response = self._connection.receive(expected_length).decode("ascii")
            stripped_response = strip_ansi_colors(response.strip('\x00\n'))
            if stripped_response == 'timeout':
                time.sleep(1)
                return self._send_and_receive(message.rstrip('\n'))
            return stripped_response

    def rescan(self):
        result = self._send_and_receive("reconfigure")
        if result != 'ok':
            raise RuntimeError(result) #pragma: no-cover

    def get_multipathd_conf(self):
        """ retreive multipathd.conf
        """
        from ..config import Configuration
        return Configuration.from_multipathd_conf(self._send_and_receive("show config"))

    def write_to_multipathd_conf(self, value, filepath=DEFAULT_CONF_FILE):
        """ save configuration to multipathd.conf file
        in order for the configuration to take affect, call reload()
        """
        from ..config import Configuration
        assert isinstance(value, Configuration)
        with open(filepath, 'w') as fd:
            fd.write(value.to_multipathd_conf())

    def get_list_of_multipath_devices(self):
        """ returns a list of mulipath devices and their attributes, as seen from multipathd
        """
        from ..model import get_list_of_multipath_devices_from_multipathd_output
        maps_topology = self._send_and_receive("show multipaths topology")
        paths_table = self._send_and_receive("show paths")
        result = get_list_of_multipath_devices_from_multipathd_output(maps_topology, paths_table)
        return result

    def fail_path(self, path_id):
        result = self._send_and_receive("fail path %s" % path_id)
        if result != 'ok':
            raise RuntimeError(result) #pragma: no-cover

    def reinstate_path(self, path_id):
        result = self._send_and_receive("reinstate path %s" % path_id)
        if result != 'ok': #pragma: no-cover
            raise RuntimeError(result) #pragma: no-cover

    def get_version(self):
        from ..model import parse_multipath_tools_version
        result = self._send_and_receive("?")
        version_string = parse_multipath_tools_version(result)
        return [int(item) for item in version_string.split(".")]

__all__ = ('MultipathClient')
