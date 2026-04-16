from typing import Union
from abc import ABC, abstractmethod

class HWIO(ABC):
    def __init__(self, offset: int = 0) -> None:
        self.offset = offset

    def read_list(self, offset: int, n_words: int, accesswidth: int = 32) -> list[int]:
        addr = self.offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        words = []
        for _ in range(n_words):
            words.append(self._read_impl(addr, bpw))
            addr += bpw
        return words

    def write_list(self, offset: int, data: list[int], accesswidth: int = 32) -> None:
        addr = self.offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        for word in data:
            self._write_impl(addr, word, bpw)
            addr += bpw

    def read(self, offset: int, regwidth: int, accesswidth: int) -> int:
        addr = self.offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        if regwidth == accesswidth:
            return self._read_impl(addr, bpw)
        else:
            # Is wide register. Read low-to-high address
            n_subwords = regwidth // accesswidth
            result = 0
            for i in range(n_subwords):
                subword = self._read_impl(addr + i * bpw, bpw)
                result |= subword << (i * accesswidth)
            return result

    def write(self, offset: int, data: int, regwidth: int, accesswidth: int) -> None:
        addr = self.offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        if regwidth == accesswidth:
            self._write_impl(addr, data, bpw)
        else:
            # Accessing a wide register. Issue multiple accesses
            n_subwords = regwidth // accesswidth
            mask = (1 << accesswidth) - 1
            for i in range(n_subwords):
                self._write_impl(addr + i * bpw, data & mask, bpw)
                data >>= accesswidth

    def read_bytes(self, offset: int, size: int) -> bytearray:
        addr = self.offset + offset
        return self._read_bytes_impl(addr, size)

    def write_bytes(self, offset: int, data: Union[bytes, bytearray]) -> None:
        addr = self.offset + offset
        self._write_bytes_impl(addr, data)

    #---------------------------------------------------------------------------

    @abstractmethod
    def _read_impl(self, addr: int, size: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def _write_impl(self, addr: int, data: int, size: int) -> None:
        raise NotImplementedError

    def _read_bytes_impl(self, addr: int, size: int) -> bytearray:
        data = bytearray()
        for _ in range(size):
            data.append(self._read_impl(addr, 1))
            addr += 1
        return data

    def _write_bytes_impl(self, addr: int, data: Union[bytes, bytearray]) -> None:
        for b in data:
            self._write_impl(addr, b, 1)
            addr += 1
