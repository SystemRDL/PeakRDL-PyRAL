from typing import Optional
from peakrdl_pyral_runtime.hwio.demo import DemoHWIO

class MockHWIO(DemoHWIO):
    def __init__(self, *, offset: int = 0) -> None:
        super().__init__(offset=offset)

        # List of: ("R/W", addr, size, data|None)
        self._xfer_log: list[tuple[str, int, int, Optional[int]]] = []

    def get_latest_xfers(self) -> list[tuple[str, int, int, Optional[int]]]:
        xfers = self._xfer_log
        self._xfer_log = []
        return xfers

    def _read_impl(self, addr: int, size: int) -> int:
        self._xfer_log.append(
            ("R", addr, size, None)
        )
        return super()._read_impl(addr, size)

    def _write_impl(self, addr: int, data: int, size: int) -> None:
        self._xfer_log.append(
            ("W", addr, size, data)
        )
        super()._write_impl(addr, data, size)

    async def _aread_impl(self, addr: int, size: int) -> int:
        self._xfer_log.append(
            ("aR", addr, size, None)
        )
        # DemoHWIO does not implement async methods.
        # Call sync version instead to avoid double-logging transactions
        return super()._read_impl(addr, size)

    async def _awrite_impl(self, addr: int, data: int, size: int) -> None:
        self._xfer_log.append(
            ("aW", addr, size, data)
        )
        # DemoHWIO does not implement async methods.
        # Call sync version instead to avoid double-logging transactions
        super()._write_impl(addr, data, size)
