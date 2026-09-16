from typing import Callable, Optional, Awaitable, Any
from . import HWIO

class CallbackHWIO(HWIO):
    def __init__(
            self,
            read_cb: Optional[Callable[[int, int], int]] = None,
            write_cb: Optional[Callable[[int, int, int], None]] = None,
            aread_cb: Optional[Callable[[int, int], Awaitable[int]]] = None,
            awrite_cb: Optional[Callable[[int, int, int], Awaitable[None]]] = None,
            *, offset: int = 0,
        ) -> None:
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

        aread_cb: Async Callable
            Reference to async function that implements read operations from the hardware.
            See ``read_cb``.

        awrite_cb: Async Callable
            Reference to async function that implements write operations to the hardware.
            See ``write_cb``.

        offset: int
            Additional address offset to add to all HWIO transactions
        """
        super().__init__(offset)
        if read_cb:
            self._read_cb = read_cb
        else:
            self._read_cb = self._unimplemented_cb

        if write_cb:
            self._write_cb = write_cb
        else:
            self._write_cb = self._unimplemented_cb

        if aread_cb:
            self._aread_cb = aread_cb
        else:
            self._aread_cb = self._unimplemented_acb

        if awrite_cb:
            self._awrite_cb = awrite_cb
        else:
            self._awrite_cb = self._unimplemented_acb

    def _unimplemented_cb(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("HWIO does not implement this type of access")

    async def _unimplemented_acb(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("HWIO does not implement this type of access")

    def _read_impl(self, addr: int, size: int) -> int:
        return self._read_cb(addr, size)

    def _write_impl(self, addr: int, value: int, size: int) -> None:
        self._write_cb(addr, value, size)

    async def _aread_impl(self, addr: int, size: int) -> int:
        return await self._aread_cb(addr, size)

    async def _awrite_impl(self, addr: int, value: int, size: int) -> None:
        await self._awrite_cb(addr, value, size)
