from typing import TYPE_CHECKING, Any, Union, overload
from collections.abc import Sequence

if TYPE_CHECKING:
    import sqlite3
    from .group import RALGroup
    from .register import RALRegister
    from .field import RALField
    from ..dbapi import DBAPI

    RALChild = Union["RALArray", RALRegister, RALGroup, RALField]

class RALArray(Sequence):
    def __init__(self, parent: "RALGroup", dbapi: "DBAPI", resolved_dims: list[int], dims: list[int], row: "sqlite3.Row") -> None:
        self._parent = parent
        self._dbapi = dbapi
        self._resolved_dims = resolved_dims
        self._this_dim_idx = len(resolved_dims)
        self._dims = dims
        self._row = row

    def __repr__(self) -> str:
        type_id = self._row["type_id"]
        if type_id == self._dbapi.TypeID.Reg.value:
            obj_name = "RALRegister"
        elif type_id == self._dbapi.TypeID.Group.value:
            obj_name = "RALGroup"
        else:
            raise RuntimeError(f"Unexpected type_id {type_id}")

        suffix = "".join([f"[{d}]" for d in self._resolved_dims])
        suffix += "[]" * (len(self._dims) - len(self._resolved_dims))
        return f"<RALArray of {obj_name}: {self._parent.path}.{self._row['name']}{suffix}>"

    @overload
    def __getitem__(self, subscript: int) -> "RALChild": ...

    @overload
    def __getitem__(self, subscript: slice) -> list["RALChild"]: ...

    def __getitem__(self, subscript: Any) -> Union["RALChild", list["RALChild"]]:
        dim = self._dims[self._this_dim_idx]

        if isinstance(subscript, slice):
            # Slice selects a range of items
            start: int = subscript.start or 0
            stop: int
            if subscript.stop is None:
                stop = dim
            else:
                stop = subscript.stop
            step: int = subscript.step or 1
            if start < 0:
                start += dim
            if stop < 0:
                stop += dim

            # For slices, silently clamp start/stop to range of array.
            # This is consistent with Python's behavior for lists
            start = max(start, 0)
            stop = min(stop, dim)
            return [self[i] for i in range(start, stop, step)]
        elif not isinstance(subscript, int):
            raise TypeError("array indices must be integers or slices")


        # Handle negative subscripts that index from end of array
        if subscript < 0:
            subscript += dim

        if subscript >= dim or subscript < 0:
            raise IndexError("array index out of range")

        # Update known dimensions
        resolved_dims = self._resolved_dims.copy()
        resolved_dims.append(subscript)

        if len(resolved_dims) != len(self._dims):
            # Multi-dimensional array still has unresolved dimensions
            # Create another array
            return RALArray(
                self._parent,
                self._dbapi,
                resolved_dims,
                self._dims,
                self._row,
            )

        # All dimensions are known. Create the actual node
        flat_idx = 0
        for i, current_idx in enumerate(resolved_dims):
            sz = 1
            for j in range(i + 1, len(self._dims)):
                sz *= self._dims[j]
            flat_idx += sz * current_idx
        array_offset = flat_idx * self._row["stride"]

        array_suffix = "".join([f"[{d}]" for d in resolved_dims])
        return self._dbapi.build_node(self._parent, self._row, array_suffix, array_offset)

    def __len__(self) -> int:
        return self._dims[self._this_dim_idx]
