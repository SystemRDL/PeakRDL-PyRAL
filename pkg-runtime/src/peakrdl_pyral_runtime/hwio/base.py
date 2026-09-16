from typing import Union
from abc import ABC, abstractmethod

class HWIO(ABC):
    def __init__(self, offset: int = 0) -> None:
        """
        Abstract base class for all Hardware I/O (HWIO) implementations.

        Parameters
        ----------
        offset: int
            Additional address offset to add to all HWIO transactions
        """
        self._offset = offset

    def read_list(self, offset: int, n_words: int, size: int = 4) -> list[int]:
        """
        Read a contiguous list of words from the hardware

        Parameters
        ----------
        offset: int
            Address offset.
        n_words: int
            Number of words to read.
        size: int
            Size of the read access in bytes to use for each entry.
            Shall be 1, 2, 4, or 8.

        Returns
        -------
        list[int]
            List of values read
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        words = []
        for _ in range(n_words):
            words.append(self._read_impl(addr, size))
            addr += size
        return words

    def write_list(self, offset: int, data: list[int], size: int = 4) -> None:
        """
        Write a contiguous list of words to the hardware

        Parameters
        ----------
        offset: int
            Address offset.
        data: list[int]
            List of words to write.
        size: int
            Size of the write access in bytes to use for each entry.
            Shall be 1, 2, 4, or 8.
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        for word in data:
            self._write_impl(addr, word, size)
            addr += size

    def read(self, offset: int, size: int = 4) -> int:
        """
        Read a single register.

        Parameters
        ----------
        offset: int
            Address offset
        size: int
            Size of the access in bytes.
            Shall be 1, 2, 4, or 8.

        Returns
        -------
        int
            Read value
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")
        return self._read_impl(addr, size)

    def write(self, offset: int, value: int, size: int = 4) -> None:
        """
        Write a single register.

        Parameters
        ----------
        offset: int
            Address offset
        data: int
            Value to write
        size: int
            Size of the access in bytes.
            Shall be 1, 2, 4, or 8.
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        self._write_impl(addr, value, size)

    def read_bytes(self, offset: int, size: int) -> bytearray:
        """
        Read a buffer of bytes from the device.
        User shall make no assumptions on what underlying access size will be used.

        Parameters
        ----------
        offset: int
            Address offset
        size: int
            Number of bytes to read

        Returns
        -------
        bytearray
            Read data
        """
        addr = self._offset + offset
        return self._read_bytes_impl(addr, size)

    def write_bytes(self, offset: int, data: Union[bytes, bytearray]) -> None:
        """
        Write a buffer of bytes to the device.
        User shall make no assumptions on what underlying access size will be used.

        Parameters
        ----------
        offset: int
            Address offset
        data: bytes
            Buffer of data to write
        """
        addr = self._offset + offset
        self._write_bytes_impl(addr, data)

    #---------------------------------------------------------------------------
    async def aread_list(self, offset: int, n_words: int, size: int = 4) -> list[int]:
        """
        Async equivalent of :meth:`read_list()`
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        words = []
        for _ in range(n_words):
            words.append(await self._aread_impl(addr, size))
            addr += size
        return words

    async def awrite_list(self, offset: int, data: list[int], size: int = 4) -> None:
        """
        Async equivalent of :meth:`write_list()`
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        for word in data:
            await self._awrite_impl(addr, word, size)
            addr += size

    async def aread(self, offset: int, size: int = 4) -> int:
        """
        Async equivalent of :meth:`read()`
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")
        return await self._aread_impl(addr, size)

    async def awrite(self, offset: int, value: int, size: int = 4) -> None:
        """
        Async equivalent of :meth:`write()`
        """
        addr = self._offset + offset
        if addr % size != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {size}-byte aligned")

        await self._awrite_impl(addr, value, size)

    async def aread_bytes(self, offset: int, size: int) -> bytearray:
        """
        Async equivalent of :meth:`read_bytes()`
        """
        addr = self._offset + offset
        return await self._aread_bytes_impl(addr, size)

    async def awrite_bytes(self, offset: int, data: Union[bytes, bytearray]) -> None:
        """
        Async equivalent of :meth:`write_bytes()`
        """
        addr = self._offset + offset
        await self._awrite_bytes_impl(addr, data)
    #---------------------------------------------------------------------------
    @abstractmethod
    def _read_impl(self, addr: int, size: int) -> int:
        """
        Implementation of a hardware read operation.
        Classes that extend :class:`HWIO` shall provide an implementation for
        this method.

        Callers will guarantee that ``addr`` is aligned to ``size``.

        Parameters
        ----------
        addr: int
            Address offset
        size: int
            Access size in bytes. Typical sizes are 1, 2, 4 or 8 bytes.
            If a given size is not supported, the implementation shall raise ``NotImplementedError``

        Returns
        -------
        int
            Read value
        """
        raise NotImplementedError

    @abstractmethod
    def _write_impl(self, addr: int, value: int, size: int) -> None:
        """
        Implementation of a hardware write operation.
        Classes that extend :class:`HWIO` shall provide an implementation for
        this method.

        Callers will guarantee that ``addr`` is aligned to ``size``.

        Parameters
        ----------
        addr: int
            Address offset
        value: int
            Value to write
        size: int
            Access size in bytes. Typical sizes are 1, 2, 4 or 8 bytes.
            If a given size is not supported, the implementation shall raise ``NotImplementedError``
        """
        raise NotImplementedError

    def _read_bytes_impl(self, addr: int, size: int) -> bytearray:
        """
        Implementation of a raw data read operation
        Classes that extend :class:`HWIO` may choose to provide an alternate
        implementation for this method if it proves to be more efficient.

        Parameters
        ----------
        offset: int
            Address offset
        size: int
            Number of bytes to read

        Returns
        -------
        bytearray
            Read data
        """
        data = bytearray()
        for _ in range(size):
            data.append(self._read_impl(addr, 1))
            addr += 1
        return data

    def _write_bytes_impl(self, addr: int, data: Union[bytes, bytearray]) -> None:
        """
        Implementation of a raw data write operation
        Classes that extend :class:`HWIO` may choose to provide an alternate
        implementation for this method if it proves to be more efficient.

        Parameters
        ----------
        offset: int
            Address offset
        data: bytes
            Buffer of data to write
        """
        for b in data:
            self._write_impl(addr, b, 1)
            addr += 1

    #---------------------------------------------------------------------------
    async def _aread_impl(self, addr: int, size: int) -> int:
        """
        Async equivalent of :meth:`_read_impl`.

        If a HWIO implementation does not define this, falls back to the sync
        variant.
        """
        return self._read_impl(addr, size)

    async def _awrite_impl(self, addr: int, value: int, size: int) -> None:
        """
        Async equivalent of :meth:`_write_impl`.

        If a HWIO implementation does not define this, falls back to the sync
        variant.
        """
        self._write_impl(addr, value, size)

    async def _aread_bytes_impl(self, addr: int, size: int) -> bytearray:
        """
        Async equivalent of :meth:`_read_bytes_impl`
        """
        data = bytearray()
        for _ in range(size):
            data.append(await self._aread_impl(addr, 1))
            addr += 1
        return data

    async def _awrite_bytes_impl(self, addr: int, data: Union[bytes, bytearray]) -> None:
        """
        Async equivalent of :meth:`_write_bytes_impl`
        """
        for b in data:
            await self._awrite_impl(addr, b, 1)
            addr += 1
