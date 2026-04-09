from typing import TYPE_CHECKING, Optional, Tuple

# TODO: Add slots?

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from ..hwio import HWIO
    from .array import RALArray
    from .field import RALField
    from .group import RALGroup
    from .register import RALRegister

class RALNode:
    def __init__(self, parent: Optional["RALNode"], dbapi: "DBAPI", dbid: int, name: str) -> None:
        self.parent = parent
        self._dbapi = dbapi
        self._dbid = dbid
        self.name = name

        self.path: str
        if parent:
            self.path = parent.path + "." + name
        else:
            self.path = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.path}>"


class AddressableRALNode(RALNode):
    def __init__(self, parent: Optional["AddressableRALNode"], dbapi: "DBAPI", dbid: int, name: str, address: int) -> None:
        super().__init__(parent, dbapi, dbid, name)
        self.parent: Optional["RALGroup"]
        self.address = address
        self._hwio: Optional["HWIO"] = None

    def __getattr__(self, name: str) -> "RALArray | RALRegister | RALGroup | RALField":
        child = self._dbapi.get_child(self, name)
        if child is None:
            raise AttributeError(f"'{repr(self)}' has no attribute '{name}'")
        return child

    def children(self) -> list["RALArray | RALRegister | RALGroup | RALField"]:
        return self._dbapi.get_children(self)

    def _lookup_hwio(self) -> Tuple["HWIO", int]:
        # TODO: Implement HWIO object caching
        if self._hwio is not None:
            # This node has a HWIO bound to it
            if self.parent is None:
                # Is root node.
                # Do not include offset so that callers incorporate the full
                # offset in accesses
                hwio_addr_offset = 0
            else:
                # Pass along any address offset that was bound to this node
                # so that callers can derive the relative offset
                hwio_addr_offset = self.address
            return (self._hwio, hwio_addr_offset)

        # Recurse to parent
        if self.parent is not None:
            return self.parent._lookup_hwio()

        # Reached root without finding anything
        raise LookupError("No HWIF was connected")

    def attach_hwio(self, hwio: "HWIO") -> None:
        self._hwio = hwio

    def detach_hwio(self) -> None:
        self._hwio = None
