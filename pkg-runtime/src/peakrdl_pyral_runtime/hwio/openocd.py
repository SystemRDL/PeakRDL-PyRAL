import socket

from .base import HWIO

# All OpenOCD RPC messages are terminated with this token
RPC_TERM = b"\x1a"

SUFFIX_MAP = {
    1: "b",
    2: "h",
    4: "w",
    8: "d",
}

class OpenOCDHWIO(HWIO):
    def __init__(self, *, offset: int = 0) -> None:
        """
        HWIO Implementation that connects to an
        `OpenOCD Tcl RPC server <https://openocd.org/doc-release/html/Tcl-Scripting-API.html#Tcl-RPC-server>`_

        Prior to connecting, the OpenOCD debug server shall be active,
        connected to the target, and configured to ``swd`` transport mode.
        """
        super().__init__(offset)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)

    def connect(self, host: str = "localhost", port: int = 6666) -> None:
        """
        Connect to the Tcl RPC server.

        Parameters:
        -----------
        host: str
            Hostname or IP address of the server.
        port: int
            Port number of the server.
        """
        self._sock.connect((host, port))

        # Ensure any asynchronous Tcl RPC messages are disabled
        self._cmd("tcl_trace off")
        self._cmd("tcl_notifications off")

    def disconnect(self) -> None:
        """
        Disconnect from the server.
        """
        self._sock.close()

    def _cmd(self, cmd: str) -> str:
        # Send the command
        data = cmd.encode("utf-8") + RPC_TERM
        self._sock.sendall(data)

        # Get response
        data = bytearray()
        while True:
            chunk = self._sock.recv(4096)
            data.extend(chunk)
            if chunk.endswith(RPC_TERM):
                break

        # strip trailing RPC_TERM token
        data = data[:-1]
        return data.decode("utf-8").strip()

    def _read_impl(self, addr: int, size: int) -> int:
        suffix = SUFFIX_MAP[size]
        resp = self._cmd(f"md{suffix} phys {addr:#x}")
        return int(resp.partition(":")[2], 16)

    def _write_impl(self, addr: int, value: int, size: int) -> None:
        suffix = SUFFIX_MAP[size]
        self._cmd(f"mw{suffix} phys {addr:#x} {value:#x}")
