Overview
========
Python client to the linx multipath-tools deamon
Usage
-----

```python
>>> from infi.multipathtools import MultipathClient
>>> client = MultipathClient()
```

Checking out the code
=====================

This project uses buildout and infi-projector, and git to generate setup.py and __version__.py.
In order to generate these, first get infi-projector:

    easy_install infi.projector

    and then run in the project directory:

        projector devenv build
