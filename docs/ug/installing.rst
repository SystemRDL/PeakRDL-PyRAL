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


Installing the runtime without PyPI
------------------------------------
Targets that cannot reach PyPI (embedded devices, air-gapped networks) can still
install ``peakrdl-pyral-runtime`` from wheels you fetch ahead of time.

On a machine with network access, download the wheel as follows:

.. code-block:: bash

    mkdir wheels
    python3 -m pip download peakrdl-pyral-runtime -d wheels

Since the runtime is implemented in pure Python, the weel is implicitly
platform-independent.

Copy the ``wheels/`` directory to the device, then install from disk without
contacting an index:

.. code-block:: bash

   python3 -m pip install --no-index --find-links=wheels peakrdl-pyral-runtime


.. note::
    For custom OS images, it is often preferable to install the runtime wheel
    during image build so the package included on the rootfs.
