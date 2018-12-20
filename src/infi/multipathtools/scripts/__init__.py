from __future__ import print_function

def print_config():
    from ..client import MultipathClient
    client = MultipathClient()
    print(client._send_and_receive("show config"))

def print_maps():
    from ..client import MultipathClient
    client = MultipathClient()
    print(client._send_and_receive("show multipaths topology"))
    print(client._send_and_receive("show paths"))
