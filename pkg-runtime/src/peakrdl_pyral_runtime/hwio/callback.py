from typing import Callable
from . import HWIO

class CallbackHWIO(HWIO):
    def __init__(self, read_cb: Callable[[int, int], int], write_cb: Callable[[int, int, int], None], *, offset: int = 0) -> None:
        """
        Generic HWIO implementation that allows users to provide externally defined
        read/methods as callbacks.

        Parameters
        ----------
        read_cb: Callable
            Reference to function that implements read operations from the hardware.

            Function shall match the following prototype:

            .. code-block:: python

                def read_cb(addr: int, size: int) -> int: ...

        write_cb: Callable
            Reference to function that implements write operations to the hardware.

            Function shall match the following prototype:

            .. code-block:: python

                def write_cb(addr: int, value: int, size: int) -> None: ...

        offset: int
            Additional address offset to add to all HWIO transactions
        """
        super().__init__(offset)
        self._read_cb = read_cb
        self._write_cb = write_cb

    def _read_impl(self, addr: int, size: int) -> int:
        return self._read_cb(addr, size)

    def _write_impl(self, addr: int, value: int, size: int) -> None:
        self._write_cb(addr, value, size)
