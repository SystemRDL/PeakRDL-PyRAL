from typing import TYPE_CHECKING

from .base import RALNode

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from .register import RALRegister

class RALField(RALNode):
    """
    Represents a single field in a register.
    """
    def __init__(self, parent: "RALRegister", dbapi: "DBAPI", dbid: int, name: str, offset: int, width: int) -> None:
        super().__init__(parent, dbapi, dbid, name)
        self.parent: "RALRegister"

        #: Bit-offset of this field
        self.offset = offset

        #: Bit-width of this field
        self.width = width

    def read(self) -> int:
        """
        Read the value of this field.

        This will implicitly perform a read of the parent register before returning the field's value.

        If you are reading multiple fields from the same register, it may be more
        efficient to use :meth:`RALRegister.read_fields()`
        """
        reg_value = self.parent.read()
        return (reg_value >> self.offset) & ((1 << self.width) - 1)

    def change(self, value: int) -> None:
        """
        Change the value of this field.

        This will implicitly perform a read and a write of the parent register.

        If you are changing multiple fields from the same register, it may be more
        efficient to use :meth:`RALRegister.change_fields()`

        Parameters
        ----------
        value: int
            Value to change the field to
        """
        reg_value = self.parent.read()
        mask = ((1 << self.width) - 1) << self.offset
        reg_value = (reg_value & ~mask) | ((value << self.offset) & mask)
        self.parent.write(reg_value)
