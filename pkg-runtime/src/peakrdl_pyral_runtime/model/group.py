from typing import TYPE_CHECKING, Optional, Union

from .base import AddressableRALNode

if TYPE_CHECKING:
    from ..dbapi import DBAPI


class RALGroup(AddressableRALNode):
    """
    Represents an intermediate RAL hierarchy that may contain
    :class:`RALGroup` or :class:`RALRegister` members.
    """
    def __init__(self, parent: Optional["RALGroup"], dbapi: "DBAPI", dbid: int, name: str, address: int) -> None:
        super().__init__(parent, dbapi, dbid, name, address)
        self.parent: Optional["RALGroup"]


    def read(self, offset: int, accesswidth: int = 32) -> int:
        """
        Perform a read operation from an address offset relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset relative to this node's address to read. Resulting absolute
            address shall be aligned to the access width.
        accesswidth: int
            Access width in bits. Shall be 8, 16, 32, or 64.

        Returns
        -------
        int
            Read value
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read(addr, accesswidth, accesswidth)

    def read_list(self, offset: int, n_words: int, accesswidth: int = 32) -> list[int]:
        """
        Read a contiguous list of words relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        n_words: int
            Number of words to read.
        accesswidth: int
            Bit-width of the read access to use for each entry.
            Shall be 8, 16, 32, or 64.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read_list(addr, n_words, accesswidth)

    def read_bytes(self, offset: int, size: int) -> bytearray:
        """
        Read a buffer of bytes relative to this node's address.
        User shall make no assumptions on what underlying access width will be used.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        size: int
            Number of bytes to read

        Returns
        -------
        bytearray
            Read data
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read_bytes(addr, size)

    def write(self, offset: int, value: int, accesswidth: int = 32) -> None:
        """
        Perform a write operation to an address offset relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset relative to this node's address to write. Resulting absolute
            address shall be aligned to the access width.
        value: int
            Value to write
        accesswidth: int
            Access width in bits. Shall be 8, 16, 32, or 64.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write(addr, value, accesswidth, accesswidth)

    def write_list(self, offset: int, data: list[int], accesswidth: int = 32) -> None:
        """
        Write a contiguous list of words relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        data: list[int]
            List of words to write.
        accesswidth: int
            Bit-width of the write access to use for each entry.
            Shall be 8, 16, 32, or 64.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write_list(addr, data, accesswidth)

    def write_bytes(self, offset: int, data: Union[bytes, bytearray]) -> None:
        """
        Write a buffer of bytes relative to this node's address.
        User shall make no assumptions on what underlying access width will be used.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        data: bytes
            Buffer of data to write
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write_bytes(addr, data)
