from collections import defaultdict

from .base import HWIO

class DemoHWIO(HWIO):
    def __init__(self, offset: int = 0) -> None:
        super().__init__(offset)
        self.mem: defaultdict[int, int] = defaultdict(int)

    def _read_impl(self, addr: int, size: int) -> int:
        value = 0
        for i in range(size):
            value |= (self.mem[addr + i] << (8 * i))
        return value

    def _write_impl(self, addr: int, data: int, size: int) -> None:
        for i in range(size):
            self.mem[addr + i] = data & 0xFF
            data >>= 8
