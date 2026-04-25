from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Generator, Union

from . import HWIO

class MirroredHWIOWrapper(HWIO):
    def __init__(self, hwio: HWIO) -> None:
        """
        Wrapping HWIO implementations with the ``MirroredHWIOWrapper`` class
        provide a mechanism to maintain a mirrored state of hardware's memory
        map.

        This can be useful when interfacing with devices that have costly access
        times. For example, rather than reading from the hardware when
        performing a read-modify-write operation, one could use this mirror to
        retain the assumed state of the register being modified.

        Any HWIO interface can be mirrored by wrapping it in this class as
        follows:

        .. code-block:: python

            my_hwio = MirroredHWIOWrapper(OpenOCDHWIO())

        By default, behavior is as follows:

        Read operations
            * Perform a read using the ``hwio`` class provided to this wrapper.
            * Update the mirrored state with the value read
            * Return the value

        Write operations
            * Update the mirrored state with the value provided
            * Write the value using the ``hwio`` class provided to this wrapper.

        The above behavior can be augmented using the :meth:`read_from_mirror`
        and :meth:`write_to_mirror_only` context managers.

        .. important::

            The mirroring mechanism this class implements makes no attempt to
            model the hardware's register map behavior beyond what is described
            above. Be careful when mirroring hardware registers that have
            access side-effects such as read-clear, write-1-to-clear, volatile
            fields, etc.

            Any advanced modeling of the hardware is out of scope for this
            project.
        """
        super().__init__()

        #: Reference to the original HWIO class being wrapped.
        self.hwio = hwio

        # If True, reads from the mirror instead of the actual HWIO
        self._read_from_mirror = False

        # If false, only writes to the mirror (instead of both)
        self._write_to_hwio = True

        self._mirror_mem: defaultdict[int, int] = defaultdict(int)

    @contextmanager
    def read_from_mirror(self) -> Generator[None, Any, None]:
        """
        Provides a context manager where, when entered, will redirect any read
        operations that target this HWIO to pull values from the mirrored state
        rather than the actual hardware.

        .. code-block:: python

            x = ral.my_reg.read() # Returns value read from the hardware

            with my_hwio.read_from_mirror():
                x = ral.my_reg.read() # Returns value from the mirror instead of hardware
        """
        prev_state = self._read_from_mirror
        self._read_from_mirror = True
        yield
        self._read_from_mirror = prev_state

    @contextmanager
    def write_to_mirror_only(self) -> Generator[None, Any, None]:
        """
        Provides a context manager where, when entered, will skip writes to the
        hardware and only update the mirrored state.

        .. code-block:: python

            ral.my_reg.write(123) # Writes value to both the hardware and mirror

            with my_hwio.write_to_mirror_only():
                ral.my_reg.write(123) # Writes value to mirror only
        """
        prev_state = self._write_to_hwio
        self._write_to_hwio = False
        yield
        self._write_to_hwio = prev_state

    def _read_impl(self, addr: int, size: int) -> int:
        if self._read_from_mirror:
            # Do not read from the actual hardware. Pull value from the mirror
            value = 0
            for i in range(size):
                value |= (self._mirror_mem[addr + i] << (8 * i))
        else:
            # Pass-through to the actual HWIO
            value = self.hwio._read_impl(addr, size)

            # Update mirrored state
            v = value
            for i in range(size):
                self._mirror_mem[addr + i] = v & 0xFF
                v >>= 8
        return value

    def _write_impl(self, addr: int, value: int, size: int) -> None:
        # Always update the mirror when writing
        v = value
        for i in range(size):
            self._mirror_mem[addr + i] = v & 0xFF
            v >>= 8

        if self._write_to_hwio:
            self.hwio._write_impl(addr, value, size)

    def _read_bytes_impl(self, addr: int, size: int) -> bytearray:
        # Explicitly intercept this in case the HWIO layer overrides this
        if self._read_from_mirror:
            data = bytearray()
            for _ in range(size):
                data.append(self._mirror_mem[addr])
                addr += 1
        else:
            data = self.hwio._read_bytes_impl(addr, size)

            # Update mirrored state
            for i, b in enumerate(data):
                self._mirror_mem[addr + i] = b
        return data

    def _write_bytes_impl(self, addr: int, data: Union[bytes, bytearray]) -> None:
        # Explicitly intercept this in case the HWIO layer overrides this
        for i, b in enumerate(data):
            self._mirror_mem[addr + i] = b

        if self._write_to_hwio:
            self.hwio._write_bytes_impl(addr, data)
