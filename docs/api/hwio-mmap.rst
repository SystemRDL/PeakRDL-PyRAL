MMap'ed HWIO
============

There are two common ways of mmap-ing to an address region:

* If you have a device file that maps to your peripheral
  (like a `UIO Device <https://www.kernel.org/doc/html/latest/driver-api/uio-howto.html>`_),
  use :class:`~peakrdl_pyral_runtime.hwio.mmap.MMapFileHWIO`
* If you want to manually map to a sub-region of ``/dev/mem`` using a physical address and region size,
  use :class:`~peakrdl_pyral_runtime.hwio.mmap.MMapMemHWIO`


MMapFileHWIO
------------

.. autoclass:: peakrdl_pyral_runtime.hwio.mmap.MMapFileHWIO
    :members:


MMapMemHWIO
-----------

.. autoclass:: peakrdl_pyral_runtime.hwio.mmap.MMapMemHWIO
    :members:
