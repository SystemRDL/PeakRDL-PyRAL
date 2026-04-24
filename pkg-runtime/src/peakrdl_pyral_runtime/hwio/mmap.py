from typing import Type, Union, Optional
import mmap
import os
import weakref
from ctypes import c_uint8, c_uint16, c_uint32, c_uint64

from .base import HWIO

CTYPE_MAP: dict[int, Type[Union[c_uint8, c_uint16, c_uint32, c_uint64]]] = {
    1: c_uint8,
    2: c_uint16,
    4: c_uint32,
    8: c_uint64,
}

class _MMapHWIO(HWIO):
    def __init__(self, path: str, offset: int, size: int) -> None:
        # Adjust the start of the mmap window to align with a page boundary
        page_offset = offset % mmap.PAGESIZE
        offset -= page_offset
        size += page_offset

        # Let superclass HWIO handle the additional page offset
        super().__init__(page_offset)

        # Open the mmap
        self._f = os.open(path, os.O_RDWR | os.O_SYNC)
        self._mm = mmap.mmap(
            self._f, size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE,
            offset=offset,
        )

        # Close mmap when this object is garbage collected
        weakref.finalize(self, self._close)

    def _close(self) -> None:
        self._mm.close()
        os.close(self._f)

    def _read_impl(self, addr: int, size: int) -> int:
        ct = CTYPE_MAP[size]
        return ct.from_buffer(self._mm, addr).value

    def _write_impl(self, addr: int, data: int, size: int) -> None:
        ct = CTYPE_MAP[size]
        ct.from_buffer(self._mm, addr).value = data

    def _read_bytes_impl(self, addr: int, size: int) -> bytearray:
        self._mm.seek(addr)
        return bytearray(self._mm.read())

    def _write_bytes_impl(self, addr: int, data: Union[bytes, bytearray]) -> None:
        self._mm.seek(addr)
        self._mm.write(data)


class MMapMemHWIO(_MMapHWIO):
    def __init__(self, offset: int, size: int) -> None:
        """
        HWIO implementation that directly maps an address space to the system's
        physical memory map using the ``/dev/mem`` device.

        Parameters
        ----------
        offset: int
            Additional address offset of the region to map
        size: int
            Size of the region to map map.
        """
        super().__init__("/dev/mem", offset, size)


class MMapFileHWIO(_MMapHWIO):
    def __init__(self, path: str, *, offset: int = 0, size: Optional[int] = None) -> None:
        """
        HWIO implementation that directly maps an address space to a file-backed
        memory map on the host device, such as a UIO device.

        Parameters
        ----------
        path: str
            Path to the device file.
        offset: int
            Additional address offset to add to all HWIO transactions
        size: int|None
            Explicit size of the memory map. If None, the size is derived based
            on the advertised size of the file.
        """
        if size is None:
            size = os.stat(path).st_size
        super().__init__(path, offset, size)
