from typing import TYPE_CHECKING, Optional

from .base import AddressableRALNode

if TYPE_CHECKING:
    from ..dbapi import DBAPI


class RALGroup(AddressableRALNode):
    def __init__(self, parent: Optional["RALGroup"], dbapi: "DBAPI", dbid: int, name: str, address: int) -> None:
        super().__init__(parent, dbapi, dbid, name, address)
        self.parent: Optional["RALGroup"]


    def read(self, offset: int, accesswidth: int = 32) -> int:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read(addr, accesswidth, accesswidth)

    def read_list(self, offset: int, n_words: int, accesswidth: int = 32) -> list[int]:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read_list(addr, n_words, accesswidth)

    def read_bytes(self, offset: int, size: int) -> bytearray:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read_bytes(addr, size)

    def write(self, offset: int, value: int, accesswidth: int = 32) -> None:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write(addr, value, accesswidth, accesswidth)

    def write_list(self, offset: int, data: list[int], accesswidth: int = 32) -> None:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write_list(addr, data, accesswidth)

    def write_bytes(self, offset: int, data: bytes|bytearray) -> None:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write_bytes(addr, data)
