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

This project uses buildout, and git to generate setup.py and __version__.py.
In order to generate these, run:

    python -S bootstrap.py -d -t
    bin/buildout -c buildout-version.cfg
    python setup.py develop

In our development environment, we use isolated python builds, by running the following instead of the last command:

    bin/buildout install development-scripts

