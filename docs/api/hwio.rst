.. _api-hwio:

HWIO
====

The PyRAL runtime library provides several built-in HWIO classes that you can use

.. list-table:: Frozen Delights!
    :header-rows: 1

    *   - Class
        - Description

    *   - :class:`~peakrdl_pyral_runtime.hwio.base.HWIO`
        - Abstract base class for all HWIO implementations.
          If you want to build your own HWIO, extend from this.

    *   - :class:`~peakrdl_pyral_runtime.hwio.demo.DemoHWIO`
        - Demonstration HWIO implementation for testing purposes.
          Does not require any actual hardware.

    *   - :class:`~peakrdl_pyral_runtime.hwio.callback.CallbackHWIO`
        - Pass your own existing read/write methods to this callback wrapper.

    *   - :class:`~peakrdl_pyral_runtime.hwio.mmap.MMapFileHWIO`
        - If you have a device file that maps to your peripheral
          (like a `UIO Device <https://www.kernel.org/doc/html/latest/driver-api/uio-howto.html>`_)

    *   - :class:`~peakrdl_pyral_runtime.hwio.mmap.MMapMemHWIO`
        - If you want to manually map to a sub-region of ``/dev/mem`` using a
          physical address and region size


.. toctree::
    :hidden:

    hwio-base
    hwio-demo
    hwio-callback
    hwio-mmap
