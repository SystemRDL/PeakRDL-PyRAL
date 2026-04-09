from typing import TYPE_CHECKING

from .base import RALNode

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from .register import RALRegister

class RALField(RALNode):
    def __init__(self, parent: "RALRegister", dbapi: "DBAPI", dbid: int, name: str, offset: int, width: int) -> None:
        super().__init__(parent, dbapi, dbid, name)
        self.parent: "RALRegister"
        self.offset = offset
        self.width = width

    def read(self) -> int:
        reg_value = self.parent.read()
        return (reg_value >> self.offset) & ((1 << self.width) - 1)

    def change(self, value: int) -> None:
        reg_value = self.parent.read()
        mask = ((1 << self.width) - 1) << self.offset
        reg_value = (reg_value & ~mask) | ((value << self.offset) & mask)
        self.parent.write(reg_value)
