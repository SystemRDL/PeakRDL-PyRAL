.. _ug-hier-hwio:

Hierarchical HWIO
=================

In some applications, it may not be practical to attach an entire RAL to a single
root-level HWIO. What if each of your subsystems are individually mapped to
`UIO Device files <https://www.kernel.org/doc/html/latest/driver-api/uio-howto.html>`_?

Consider the example SoC from the prior tutorial (:ref:`ug-grafting`), and we want
to map each individual RAL node to a UIO device file as follows:

* ``my_soc.awesome_A`` --> ``/dev/uio0``
* ``my_soc.awesome_B`` --> ``/dev/uio1``
* ``my_soc.splendid_X`` --> ``/dev/uio2``
* ``my_soc.splendid_Y`` --> ``/dev/uio3``

Not a problem! A RAL can accept multiple simultaneous HWIO connections on
different hierarchical nodes.

.. code-block:: python

    from peakrdl_pyral_runtime.hwio.mmap import MMapFileHWIO
    from my_soc_ral import my_soc

    # Create each HWIO
    uio0 = MMapFileHWIO("/dev/uio0")
    uio1 = MMapFileHWIO("/dev/uio1")
    uio2 = MMapFileHWIO("/dev/uio2")
    uio3 = MMapFileHWIO("/dev/uio3")

    # Create the RAL
    ral = my_soc.get_ral()

    # Attach HWIO to the respective components
    ral.awesome_A.attach_hwio(uio0)
    ral.awesome_B.attach_hwio(uio1)
    ral.splendid_X.attach_hwio(uio2)
    ral.splendid_Y.attach_hwio(uio3)
