from typing import Union
import enum
import sqlite3
from collections import OrderedDict
import importlib
import weakref

from .model import RALRegister, RALField, RALGroup, RALArray, RegValue
from .model import AddressableRALNode
from .hwio.base import HWIO

class HWIORegistry:
    """
    Since RAL nodes are dynamically re-created, a registry is needed to keep track
    of any HWIO interfaces that were bound to any internal RAL nodes.
    When a RAL node is re-created, it will check if a HWIO interface was bound
    to it, and will re-attach it
    """
    def __init__(self) -> None:
        # {node_path: HWIO}
        self.attached_hwio: dict[str, HWIO] = {}

class DBAPI:
    """
    Implements the mechanisms to query the RAL database and construct RAL nodes
    from the database definition.

    Go away! This is a **private** API! RAL users shall not use this directly
    as it may change between runtime versions!
    """

    # DBAPI version denotes the underlying database content's compatibility with
    # the runtime implementation. This value is incremented any time there is a
    # compatibility-breaking change in this interface.
    DBAPI_VERSION = "2"

    class TypeID(enum.Enum):
        Group = 1
        Reg = 2
        Field = 3
        ExternalRef = 4

    def __init__(self, path: str, origin_module_name: str) -> None:
        self.origin_module_name = origin_module_name
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row

        self.hwio_registry = HWIORegistry()

        # Check DBAPI version to make sure it is compatible
        cur = self.db.cursor()
        cur.execute("SELECT value FROM dbinfo WHERE key='dbapi-version'")
        version = cur.fetchone()
        if version is None:
            raise ValueError("Invalid RAL DB")
        if version[0] != self.DBAPI_VERSION:
            raise ValueError(f"RAL/Runtime version mismatch. RAL dbapi version = {version[0]}; runtime dbapi version = {self.DBAPI_VERSION}")
        cur.close()

        # Close the DB connection when this DBAPI gets garbage collected
        weakref.finalize(self, self.db.close)


    def get_root(self, offset: int = 0) -> RALGroup:
        """
        Get the root node of a RAL DB
        """
        # Fetch row from DB. Root node always has a dbid of 1
        cur = self.db.cursor()
        cur.execute("SELECT * FROM ral WHERE dbid=1")
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Not found")
        cur.close()

        # Root node is always a non-array group
        return RALGroup(
            None,
            self,
            row["dbid"],
            row["name"],
            offset,
            row["size"],
        )

    def get_ref_dbapi(self, ref_dbid: int) -> "DBAPI":
        """
        Get the DBAPI object that implements an external reference to this DBAPI
        """
        # Get ref's import path
        cur = self.db.cursor()
        cur.execute("SELECT import_path FROM external_refs WHERE dbid=?", (ref_dbid,))
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Not found")
        cur.close()

        import_path = row["import_path"]
        try:
            ref_module = importlib.import_module(import_path, self.origin_module_name)
        except ImportError as exc:
            raise ImportError(
                f"Failed to import grafted PyRAL module '{import_path}' while resolving an "
                f"external reference from RAL package '{self.origin_module_name}. "
                "Ensure the module is installed and importable, and that PeakRDL "
                "--graft-type path provided is correct."
            ) from exc

        get_dbapi = getattr(ref_module, "_get_dbapi", None)
        if get_dbapi is None:
            raise RuntimeError(
                f"Grafted module '{import_path} (imported for RAL '{self.origin_module_name}) "
                "does not define _get_dbapi(); expected a PeakRDL-PyRAL generated module."
            )
        new_dbapi: DBAPI = get_dbapi()

        # Child DBAPIs all share a common HWIO registry. Graft it in
        new_dbapi.hwio_registry = self.hwio_registry

        return new_dbapi

    def get_child(self, parent: AddressableRALNode, child_name: str) -> Union[None, RALArray, RALRegister, RALGroup, RALField]:
        """
        Get a single child of a node by name
        """
        # Fetch row from DB
        cur = self.db.cursor()
        cur.execute(
            "SELECT * FROM ral WHERE parent_dbid=? AND name=?",
            (
                parent._dbid, child_name
            )
        )
        row = cur.fetchone()
        if row is None:
            return None
        cur.close()

        return self.build_child(parent, row)

    def get_children(self, parent: AddressableRALNode) -> list[Union[RALArray, RALRegister, RALGroup, RALField]]:
        """
        Get all the children of a node
        """
        cur = self.db.cursor()
        cur.execute(
            "SELECT * FROM ral WHERE parent_dbid=? ORDER BY offset ASC",
            (parent._dbid,),
        )
        rows = cur.fetchall()
        cur.close()
        return [self.build_child(parent, row) for row in rows]

    def regvalue_from_int(self, parent_reg_dbid: int, reg_value: int) -> RegValue:
        """
        Convert a raw integer value to a field-aware RegValue
        """
        # Get all the fields of the register
        cur = self.db.cursor()
        cur.execute(
            "SELECT name, offset, size FROM ral WHERE parent_dbid=? ORDER BY offset ASC",
            (parent_reg_dbid,),
        )
        rows = cur.fetchall()
        cur.close()

        # Build the field spec
        spec = OrderedDict()
        for row in rows:
            spec[row["name"]] = (row["offset"], row["size"])

        return RegValue(reg_value, spec)

    def build_child(self, parent: AddressableRALNode, row: sqlite3.Row) -> Union[RALArray, RALRegister, RALGroup, RALField]:
        """
        Given an sqlite row, build the child RAL node.
        - If the row defines an external reference, resolve it.
        - If the row defines an array node, defer construction of the node and
          instead return an array that wraps it.
        """
        if row["type_id"] == self.TypeID.ExternalRef.value:
            # Is an external reference. Load the reference's DBAPI
            dbapi = self.get_ref_dbapi(row["dbid"])
            # Patch the row data ahead of object creation
            new_row = dict(row) # Cast to a mutable dict so it can be transformed
            new_row["type_id"] = self.TypeID.Group.value
            new_row["dbid"] = 1 # Is root node
            row = new_row # type: ignore # lets pretend this is still a sqlite3.Row
        else:
            dbapi = self

        # Construct the object
        if row["dims"] is not None:
            # Is an array. Defer creation of the node and instead wrap it in an array
            # Arrays only exist as children of groups
            assert isinstance(parent, RALGroup)
            dims = [int(s, 16) for s in row["dims"].split(",")]
            return RALArray(parent, dbapi, [], dims, row)
        else:
            # Is not an array
            return dbapi.build_node(parent, row)

    def build_node(self, parent: AddressableRALNode, row: sqlite3.Row, array_suffix: str = "", array_offset: int = 0) -> Union[RALRegister, RALGroup, RALField]:
        """
        Factory function to build a RAL node once all its attributes are known
        """
        type_id = row["type_id"]
        name = row["name"] + array_suffix

        if type_id == self.TypeID.Reg.value:
            assert isinstance(parent, RALGroup)
            return RALRegister(
                parent,
                self,
                row["dbid"],
                name,
                parent.address + row["offset"] + array_offset,
                row["size"],
                row["access_size"],
            )
        elif type_id == self.TypeID.Group.value:
            assert isinstance(parent, RALGroup)
            return RALGroup(
                parent,
                self,
                row["dbid"],
                name,
                parent.address + row["offset"] + array_offset,
                row["size"],
            )
        elif type_id == self.TypeID.Field.value:
            assert isinstance(parent, RALRegister)
            return RALField(
                parent,
                self,
                row["dbid"],
                name,
                row["offset"],
                row["size"],
            )
        else:
            raise RuntimeError(f"Unexpected type_id {type_id}")
