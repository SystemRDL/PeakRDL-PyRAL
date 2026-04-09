import enum
import sqlite3
from collections import OrderedDict
import importlib
import weakref

from .model import RALRegister, RALField, RALGroup, RALArray, RegValue
from .model import AddressableRALNode

class DBAPI:
    # DBAPI version denotes the underlying database content's compatibility with
    # the runtime implementation. This value is incremented any time there is a
    # compatibility-breaking change in this interface.
    DBAPI_VERSION = "1"

    class TypeID(enum.Enum):
        Group = 1
        Reg = 2
        Field = 3
        ExternalRef = 4

    def __init__(self, path: str, origin_module_name: str) -> None:
        self.origin_module_name = origin_module_name
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row

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
        # Fetch row from DB
        cur = self.db.cursor()
        cur.execute("SELECT * FROM ral WHERE dbid=1")
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Not found")
        cur.close()

        return RALGroup(
            None,
            self,
            row["dbid"],
            row["name"],
            offset,
        )

    def get_ref_dbapi(self, ref_dbid: int) -> "DBAPI":
        # Get ref's import path
        cur = self.db.cursor()
        cur.execute("SELECT import_path FROM external_refs WHERE dbid=?", (ref_dbid,))
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Not found")
        cur.close()

        import_path = row["import_path"]
        # TODO: Make sure import errors result in a helpful error.
        #   Ensure it tells the user what is wrong
        ref_module = importlib.import_module(import_path, self.origin_module_name)
        new_dbapi: DBAPI = ref_module._get_dbapi()
        return new_dbapi

    def get_child(self, parent: AddressableRALNode, child_name: str) -> None | RALArray | RALRegister | RALGroup | RALField:
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

    def get_children(self, parent: AddressableRALNode) -> list[RALArray | RALRegister | RALGroup | RALField]:
        cur = self.db.cursor()
        cur.execute(
            "SELECT * FROM ral WHERE parent_dbid=? ORDER BY offset ASC",
            (parent._dbid,),
        )
        rows = cur.fetchall()
        cur.close()
        return [self.build_child(parent, row) for row in rows]

    def regvalue_from_int(self, parent_reg_dbid: int, reg_value: int) -> RegValue:
        cur = self.db.cursor()
        cur.execute(
            "SELECT name, offset, size FROM ral WHERE parent_dbid=? ORDER BY offset ASC",
            (parent_reg_dbid,),
        )
        rows = cur.fetchall()
        cur.close()

        spec = OrderedDict()
        for row in rows:
            spec[row["name"]] = (row["offset"], row["size"])

        return RegValue(reg_value, spec)

    def build_child(self, parent: AddressableRALNode, row: sqlite3.Row) -> RALArray | RALRegister | RALGroup | RALField:
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
            # Is an array
            # Arrays only exist as children of groups
            assert isinstance(parent, RALGroup)
            dims = [int(s, 16) for s in row["dims"].split(",")]
            return RALArray(parent, dbapi, [], dims, row)
        else:
            # Is not an array
            return dbapi.build_node(parent, row)

    def build_node(self, parent: AddressableRALNode, row: sqlite3.Row, array_suffix: str = "", array_offset: int = 0) -> RALRegister | RALGroup | RALField:
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
                row["accesswidth"],
            )
        elif type_id == self.TypeID.Group.value:
            assert isinstance(parent, RALGroup)
            return RALGroup(
                parent,
                self,
                row["dbid"],
                name,
                parent.address + row["offset"] + array_offset,
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
