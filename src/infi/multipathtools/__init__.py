__import__("pkg_resources").declare_namespace(__name__)

""" Python bindings to Linux multipath-tools

The multipath-tools package for Linux includes a user-space monitoring tool
for the mulipath plug-in of device-mapper.
The monitor tool can be executed by two processes:
* multipath, which is executed on demand
* multipath-tools, which runs as a daemon

The two processes are independent.
Unlike what you'd expect, the 'multipath' program does not get/set properties
from the daemon's run-time configuration, it works directly with sysfs and device-mapper.

So, running 'multipath -ll' doesn't really give you the view that the daemon has,
nor does what the kernel plug-in has; it does shows you the information from sysfs,
it doesn't mean that the daemon is aware of the latest image.
Nor does 'multipath' update the daemon's configuration. That is also why this command is
some-what resources-intensive and time-consuming.

That is why we choose to do our bindings with the daemon only.
There are several advantages for this:
* We do not issue out-of-scope commands
* We always keep the daemon up-to-date
* The daemon unsures the validity of the configuration, so we don't need to worry about that

However, the communcation with the daemon is not documented and well-defined.
If you'll real the soruce-code of multipathd, you'll see it supports a ascii-based message
passing betweeen he daemon and a cleitn, which is 'multipathd -k', 
and the communication is over a unix domain socket.
This is not ideal, but its not worse than parsing the output of multipath -l.


"""

from .client import MultipathClient
from .dtypes import PATH_STATES, PATHGROUP_STATES
