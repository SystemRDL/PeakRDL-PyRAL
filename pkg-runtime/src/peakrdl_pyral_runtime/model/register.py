from typing import TYPE_CHECKING
from collections.abc import Iterator
from contextlib import contextmanager

from .base import AddressableRALNode
from .regvalue import RegValue

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from .group import RALGroup


class RALRegister(AddressableRALNode):
    def __init__(self, parent: "RALGroup", dbapi: "DBAPI", dbid: int, name: str, address: int, width: int, accesswidth: int) -> None:
        super().__init__(parent, dbapi, dbid, name, address)
        self.parent: "RALGroup"
        self.width = width
        self.accesswidth = accesswidth

    def read(self) -> int:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset
        return hwio.read(addr, self.width, self.accesswidth)

    def write(self, value: int) -> None:
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset
        hwio.write(addr, value, self.width, self.accesswidth)

    def read_fields(self) -> RegValue:
        value = self.read()
        return self._dbapi.regvalue_from_int(self._dbid, value)

    @contextmanager
    def write_fields(self) -> Iterator[RegValue]:
        rv = self._dbapi.regvalue_from_int(self._dbid, 0)
        yield rv
        self.write(int(rv))

    @contextmanager
    def change_fields(self) -> Iterator[RegValue]:
        value = self.read()
        rv = self._dbapi.regvalue_from_int(self._dbid, value)
        yield rv
        self.write(int(rv))
