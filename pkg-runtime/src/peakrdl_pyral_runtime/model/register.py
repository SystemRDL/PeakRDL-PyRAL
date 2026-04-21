from typing import TYPE_CHECKING
from collections.abc import Iterator
from contextlib import contextmanager

from .base import AddressableRALNode
from .regvalue import RegValue

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from .group import RALGroup


class RALRegister(AddressableRALNode):
    """
    Represents a register.
    """
    def __init__(self, parent: "RALGroup", dbapi: "DBAPI", dbid: int, name: str, address: int, width: int, accesswidth: int) -> None:
        super().__init__(parent, dbapi, dbid, name, address)
        self.parent: "RALGroup"

        #: Register's width in bits
        self.width = width

        #: Register's access width in bits
        self.accesswidth = accesswidth

    def read(self) -> int:
        """
        Read the register's value
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset
        return hwio.read(addr, self.width, self.accesswidth)

    def write(self, value: int) -> None:
        """
        Write a value to the register

        Parameters
        ----------
        value: int
            Value to write
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset
        hwio.write(addr, value, self.width, self.accesswidth)

    def read_fields(self) -> RegValue:
        """
        Read the register's value and return it as a structured :class:`RegValue` object.

        This allows you to access individual fields by-name:

        .. code-block:: python

            r = my_reg.read_fields()
            print(r.field_1)
            print(r.field_2)
            print(r.field_3)
        """
        value = self.read()
        return self._dbapi.regvalue_from_int(self._dbid, value)

    @contextmanager
    def write_fields(self) -> Iterator[RegValue]:
        """
        Provides a context manager to write a register's value by-field.
        This operation triggers a write operation to the register after
        exiting the ``with`` context body.

        Any fields that are not explicitly set will be written with a value of 0.

        .. code-block:: python

            with my_reg.write_fields() as r:
                r.field_1 = 123
                # r.field_2 = 0 (implied)
                r.field_3 = 456

        """
        rv = self._dbapi.regvalue_from_int(self._dbid, 0)
        yield rv
        self.write(int(rv))

    @contextmanager
    def change_fields(self) -> Iterator[RegValue]:
        """
        Provides a context manager to modify the value of a register's fields.
        This operations triggers a read operation prior to entering the ``with``
        context body, and a write operation once exiting.

        Any fields that are not explicitly set will remain unchanged.

        .. code-block:: python

            with my_reg.change_fields() as r:
                r.field_1 = 1
                r.field_2 += 5 # increment by 5
                # r.field_3 (remains unchanged)
        """
        value = self.read()
        rv = self._dbapi.regvalue_from_int(self._dbid, value)
        yield rv
        self.write(int(rv))
