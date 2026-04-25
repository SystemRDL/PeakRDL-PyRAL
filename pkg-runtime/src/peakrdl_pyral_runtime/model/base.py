from typing import TYPE_CHECKING, Optional, Union
from abc import ABC

# TODO: Add slots?

if TYPE_CHECKING:
    from ..dbapi import DBAPI
    from ..hwio.base import HWIO
    from .array import RALArray
    from .field import RALField
    from .group import RALGroup
    from .register import RALRegister

class RALNode(ABC):
    """
    Abstract base class for all nodes in a RAL
    """
    def __init__(self, parent: Optional["RALNode"], dbapi: "DBAPI", dbid: int, name: str) -> None:
        #: Parent RAL node
        self.parent = parent

        self._dbapi = dbapi
        self._dbid = dbid

        #: Node name. If the node is an array, the name will include any array suffixes.
        self.name: str = name

        #: Hierarchical path of this node
        self.path: str
        if parent:
            self.path = parent.path + "." + name
        else:
            self.path = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.path}>"


class AddressableRALNode(RALNode, ABC):
    """
    Abstract base class for all RAL nodes that can have an address.
    """
    def __init__(self, parent: Optional["AddressableRALNode"], dbapi: "DBAPI", dbid: int, name: str, address: int, size: int) -> None:
        super().__init__(parent, dbapi, dbid, name)
        self.parent: Optional["RALGroup"]

        #: Absolute address of this RAL node
        self.address = address

        #: Node's size in bytes
        self.size = size

        self._hwio: Optional["HWIO"] = self._dbapi.hwio_registry.attached_hwio.get(self.path)

    def __getattr__(self, name: str) -> Union["RALArray", "RALRegister", "RALGroup", "RALField"]:
        child = self._dbapi.get_child(self, name)
        if child is None:
            raise AttributeError(f"'{repr(self)}' has no attribute '{name}'")
        return child

    def children(self) -> list[Union["RALArray", "RALRegister", "RALGroup", "RALField"]]:
        """
        Returns a list of child RAL elements
        """
        return self._dbapi.get_children(self)

    def _lookup_hwio(self) -> tuple["HWIO", int]:
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
        raise LookupError("No HWIO was connected")

    def attach_hwio(self, hwio: "HWIO") -> None:
        """
        Attach a :class:`HWIO` interface to this node. All read/write operations
        to this node and its descendants will use the provided HWIO interface.

        If this is the root node of the RAL, transactions will include any
        additional address offset provided during RAL construction.

        If this is an internal node of the RAL, transactions will use an address
        relative to this node.
        """
        self._hwio = hwio
        self._dbapi.hwio_registry.attached_hwio[self.path] = hwio

    def detach_hwio(self) -> None:
        """
        Detach the HWIO interface from this node, if any.
        """
        self._hwio = None
        self._dbapi.hwio_registry.attached_hwio.pop(self.path, None)
