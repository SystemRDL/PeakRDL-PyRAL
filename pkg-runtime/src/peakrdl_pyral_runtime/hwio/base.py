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

    def read_list(self, offset: int, n_words: int, accesswidth: int = 32) -> list[int]:
        """
        Read a contiguous list of words from the hardware

        Parameters
        ----------
        offset: int
            Address offset.
        n_words: int
            Number of words to read.
        accesswidth: int
            Bit-width of the read access to use for each entry.
            Shall be 8, 16, 32, or 64.

        Returns
        -------
        list[int]
            List of values read
        """
        addr = self._offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        words = []
        for _ in range(n_words):
            words.append(self._read_impl(addr, bpw))
            addr += bpw
        return words

    def write_list(self, offset: int, data: list[int], accesswidth: int = 32) -> None:
        """
        Write a contiguous list of words to the hardware

        Parameters
        ----------
        offset: int
            Address offset.
        data: list[int]
            List of words to write.
        accesswidth: int
            Bit-width of the write access to use for each entry.
            Shall be 8, 16, 32, or 64.
        """
        addr = self._offset + offset
        bpw = accesswidth // 8
        if addr % bpw != 0:
            raise ValueError(f"Access at address 0x{addr:x} is not {accesswidth}-bit aligned")

        for word in data:
            self._write_impl(addr, word, bpw)
            addr += bpw

    def read(self, offset: int, regwidth: int, accesswidth: int) -> int:
        """
        Read a single register.

        If regwidth > accesswidth, then the read operation will be performed as
        multiple sequential sub-word reads.

        Parameters
        ----------
        offset: int
            Address offset
        regwidth: int
            Register width in bits. Shall be 8, 16, 32, or 64.
        accesswidth: int
            Access width in bits. Shall be 8, 16, 32, or 64.

        Returns
        -------
        int
            Read value
        """
        addr = self._offset + offset
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
        """
        Write a single register.

        If regwidth > accesswidth, then the write operation will be performed as
        multiple sequential sub-word writes.

        Parameters
        ----------
        offset: int
            Address offset
        data: int
            Value to write
        regwidth: int
            Register width. Shall be 8, 16, 32, or 64.
        accesswidth: int
            Access width. Shall be 8, 16, 32, or 64.
        """
        addr = self._offset + offset
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
        """
        Read a buffer of bytes from the device.
        User shall make no assumptions on what underlying access width will be used.

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
        User shall make no assumptions on what underlying access width will be used.

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
    def _write_impl(self, addr: int, data: int, size: int) -> None:
        """
        Implementation of a hardware write operation.
        Classes that extend :class:`HWIO` shall provide an implementation for
        this method.

        Callers will guarantee that ``addr`` is aligned to ``size``.

        Parameters
        ----------
        addr: int
            Address offset
        data: int
            Data to write
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
