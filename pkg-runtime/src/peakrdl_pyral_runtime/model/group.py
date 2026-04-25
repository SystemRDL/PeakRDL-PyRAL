from typing import TYPE_CHECKING, Optional, Union

from .base import AddressableRALNode

if TYPE_CHECKING:
    from ..dbapi import DBAPI


class RALGroup(AddressableRALNode):
    """
    Represents an intermediate RAL hierarchy that may contain
    :class:`RALGroup` or :class:`RALRegister` members.
    """
    def __init__(self, parent: Optional["RALGroup"], dbapi: "DBAPI", dbid: int, name: str, address: int, size: int) -> None:
        super().__init__(parent, dbapi, dbid, name, address, size)
        self.parent: Optional["RALGroup"]


    def read(self, offset: int, size: int = 4) -> int:
        """
        Perform a read operation from an address offset relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset relative to this node's address to read. Resulting absolute
            address shall be aligned to the access size.
        size: int
            Size of the access in bytes.
            Shall be 1, 2, 4, or 8.

        Returns
        -------
        int
            Read value
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read(addr, size)

    def read_list(self, offset: int, n_words: int, size: int = 4) -> list[int]:
        """
        Read a contiguous list of words relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        n_words: int
            Number of words to read.
        size: int
            Size of the read access in bytes to use for each entry.
            Shall be 1, 2, 4, or 8.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        return hwio.read_list(addr, n_words, size)

    def read_bytes(self, offset: int, size: int) -> bytearray:
        """
        Read a buffer of bytes relative to this node's address.
        User shall make no assumptions on what underlying access size will be used.

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

    def write(self, offset: int, value: int, size: int = 4) -> None:
        """
        Perform a write operation to an address offset relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset relative to this node's address to write. Resulting absolute
            address shall be aligned to the access size.
        value: int
            Value to write
        size: int
            Size of the access in bytes.
            Shall be 1, 2, 4, or 8.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write(addr, value, size)

    def write_list(self, offset: int, data: list[int], size: int = 4) -> None:
        """
        Write a contiguous list of words relative to this node's address.

        Parameters
        ----------
        offset: int
            Offset from this node's address.
        data: list[int]
            List of words to write.
        size: int
            Size of the write access in bytes to use for each entry.
            Shall be 1, 2, 4, or 8.
        """
        hwio, hwio_addr_offset = self._lookup_hwio()
        addr = self.address - hwio_addr_offset + offset
        hwio.write_list(addr, data, size)

    def write_bytes(self, offset: int, data: Union[bytes, bytearray]) -> None:
        """
        Write a buffer of bytes relative to this node's address.
        User shall make no assumptions on what underlying access size will be used.

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
