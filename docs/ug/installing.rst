Installation Details
====================

PeakRDL-PyRAL is distributed as two separate packages. Depending on your
use-case, you may not need to install both of them every time.

``peakrdl-pyral[cli]``
    This package implements the RAL exporter tool for converting a SystemRDL
    design into a RAL API for your application.

    Since most users prefer to use the `PeakRDL command-line tool <https://peakrdl.readthedocs.io>`_, it is
    recommended to install this using the optional ``cli`` dependency to ensure
    the correct version is installed.

``peakrdl-pyral-runtime``
    The exported RAL requires additional runtime files to be installed on the
    system that will run the RAL & application. This runtime package provides this.

.. todo::
    Add instructions on how to install the runtime on a device that cannot fetch from pypi

    - pip download command for a specific platform
    - copy wheels over
    - install within the device
    - Mention that installing the runtime as part of the rootfs may be preferred
