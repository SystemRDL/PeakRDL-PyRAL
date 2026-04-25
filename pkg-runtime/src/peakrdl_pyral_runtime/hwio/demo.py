from collections import defaultdict

from .base import HWIO

class DemoHWIO(HWIO):
    def __init__(self, *, offset: int = 0) -> None:
        """
        Demonstration HWIO implementation for testing purposes that models a
        hardware I/O connection without requiring any hardware.

        Models the hardware as a blank RAM that is initialized to all 0's.

        Parameters
        ----------
        offset: int
            Additional address offset to add to all HWIO transactions
        """
        super().__init__(offset)
        self.mem: defaultdict[int, int] = defaultdict(int)

    def _read_impl(self, addr: int, size: int) -> int:
        value = 0
        for i in range(size):
            value |= (self.mem[addr + i] << (8 * i))
        return value

    def _write_impl(self, addr: int, value: int, size: int) -> None:
        for i in range(size):
            self.mem[addr + i] = value & 0xFF
            value >>= 8
