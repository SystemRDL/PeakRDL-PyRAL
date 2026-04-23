Abstract HWIO Base Class
========================

All hardware i/o implementations extend from the :class:`~peakrdl_pyral_runtime.hwio.base.HWIO`
abstract base class.


Methods that **require** implementation
---------------------------------------
All HWIO shall implement the :meth:`~peakrdl_pyral_runtime.hwio.base.HWIO._read_impl`
and :meth:`~peakrdl_pyral_runtime.hwio.base.HWIO._write_impl` methods.

.. automethod:: peakrdl_pyral_runtime.hwio.base.HWIO._read_impl

.. automethod:: peakrdl_pyral_runtime.hwio.base.HWIO._write_impl


Methods that *may* be overridden
--------------------------------
If a HWIO interface is able to execute native block memory copy operations, it
is recommended to override the :meth:`~peakrdl_pyral_runtime.hwio.base.HWIO._read_bytes_impl` and
:meth:`~peakrdl_pyral_runtime.hwio.base.HWIO._write_bytes_impl` methods.

.. automethod:: peakrdl_pyral_runtime.hwio.base.HWIO._read_bytes_impl

.. automethod:: peakrdl_pyral_runtime.hwio.base.HWIO._write_bytes_impl


HWIO
----
Calling HWIO methods directly is seldom useful as you would usually interact
with the RAL API instead. Even so, bypassing the RAL is sometimes necessary, so
here is a reference to the public HWIO API.

.. autoclass:: peakrdl_pyral_runtime.hwio.base.HWIO
    :members:
