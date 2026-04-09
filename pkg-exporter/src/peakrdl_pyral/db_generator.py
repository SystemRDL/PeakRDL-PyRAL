from typing import Union, Optional, Dict
import sqlite3
import os
import enum

from systemrdl.node import AddrmapNode, MemNode, RegfileNode
from systemrdl.node import RegNode, FieldNode

from . import __about__
from .name_filter import filter_group_item, filter_register_item

# DBAPI version denotes the underlying database content's compatibility with
# the runtime implementation. This value is incremented any time there is a
# compatibility-breaking change in this interface.
DBAPI_VERSION = "1"


class TypeID(enum.Enum):
    Group = 1
    Reg = 2
    Field = 3
    ExternalRef = 4


class DBGenerator:
    def __init__(self, db_path: str, external_types: Dict[str, str]) -> None:
        self._init_db(db_path)
        self.external_types = external_types

    def _init_db(self, db_path: str) -> None:
        # Create new sqlite DB
        if os.path.exists(db_path):
            os.remove(db_path)
        self.db = sqlite3.connect(db_path)

        cur = self.db.cursor()

        # Create table that contains version information
        cur.execute("""
            CREATE TABLE dbinfo(
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cur.execute("INSERT INTO dbinfo VALUES (?, ?)", ("version", __about__.__version__))
        cur.execute("INSERT INTO dbinfo VALUES (?, ?)", ("dbapi-version", DBAPI_VERSION))

        # Create main RAL database table
        cur.execute("""
            CREATE TABLE ral(
                dbid INTEGER PRIMARY KEY,
                parent_dbid INTEGER,
                type_id INTEGER,        -- See dbapi.TypeID
                name TEXT,              -- aka inst_name

                offset INTEGER,         -- [all] address offset / bit-offset for field
                dims TEXT,              -- [g,r] array dimensions. Comma-separated hex strings
                stride INTEGER,         -- [g,r] array stride
                size INTEGER,           -- [r,f] regwidth / fieldwidth
                accesswidth INTEGER     -- [r]
            )
        """)

        cur.execute("""
            CREATE TABLE external_refs(
                dbid INTEGER PRIMARY KEY,
                import_path TEXT
            )
        """)

        # Create index for faster child node lookups
        cur.execute("""
            CREATE UNIQUE INDEX idx_ral_parent_child
            ON ral (parent_dbid, name)
        """)

        cur.close()

    def generate_group(self, node: Union[AddrmapNode, MemNode, RegfileNode], parent_dbid: Optional[int] = None) -> None:
        this_dbid = self.add_group(node, parent_dbid)

        for child in node.children():
            if isinstance(child, (AddrmapNode, MemNode, RegfileNode)):
                if (
                    child.get_scope_path() == "" # Was declared in the root namespace
                    and (child.type_name in self.external_types) # Is marked as an external type
                ):
                    # Export this as an external reference
                    import_path = self.external_types[child.type_name]
                    self.add_external_group(child, this_dbid, import_path)
                else:
                    self.generate_group(child, this_dbid)
            elif isinstance(child, RegNode):
                self.generate_reg(child, this_dbid)


    def add_group(self, node: Union[AddrmapNode, MemNode, RegfileNode], parent_dbid: Optional[int]) -> int:
        if node.array_dimensions:
            dims = ",".join([hex(d) for d in node.array_dimensions])
            stride = node.array_stride
        else:
            dims = None
            stride = None

        cur = self.db.cursor()
        res = cur.execute("""
            INSERT INTO ral VALUES (
                NULL, -- dbid
                ?,    -- parent_dbid
                ?,    -- type_id
                ?,    -- name
                ?,    -- offset
                ?,    -- dims
                ?,    -- stride
                NULL, -- size
                NULL  -- accesswidth
            ) RETURNING dbid
        """, (
            parent_dbid,
            TypeID.Group.value,
            filter_group_item(node.inst_name),
            node.raw_address_offset,
            dims,
            stride,
        ))
        dbid = res.fetchone()[0]
        cur.close()
        return dbid

    def add_external_group(self, node: Union[AddrmapNode, MemNode, RegfileNode], parent_dbid: int, import_path: str) -> None:
        if node.array_dimensions:
            dims = ",".join([hex(d) for d in node.array_dimensions])
            stride = node.array_stride
        else:
            dims = None
            stride = None

        cur = self.db.cursor()
        res = cur.execute("""
            INSERT INTO ral VALUES (
                NULL, -- dbid
                ?,    -- parent_dbid
                ?,    -- type_id
                ?,    -- name
                ?,    -- offset
                ?,    -- dims
                ?,    -- stride
                NULL, -- size
                NULL  -- accesswidth
            ) RETURNING dbid
        """, (
            parent_dbid,
            TypeID.ExternalRef.value,
            filter_group_item(node.inst_name),
            node.raw_address_offset,
            dims,
            stride,
        ))
        dbid = res.fetchone()[0]

        cur.execute("""
            INSERT INTO external_refs VALUES (
                ?, -- dbid
                ?  -- import_path
            )
        """, (
            dbid,
            import_path,
        ))

        cur.close()

    def generate_reg(self, node: RegNode, parent_dbid: int) -> None:
        this_dbid = self.add_reg(node, parent_dbid)
        for child in node.fields():
            self.add_field(child, this_dbid)

    def add_reg(self, node: RegNode, parent_dbid: int) -> int:
        if node.array_dimensions:
            dims = ",".join([hex(d) for d in node.array_dimensions])
            stride = node.array_stride
        else:
            dims = None
            stride = None

        cur = self.db.cursor()
        res = cur.execute("""
            INSERT INTO ral VALUES (
                NULL, -- dbid
                ?,    -- parent_dbid
                ?,    -- type_id
                ?,    -- name
                ?,    -- offset
                ?,    -- dims
                ?,    -- stride
                ?,    -- size
                ?     -- accesswidth
            ) RETURNING dbid
        """, (
            parent_dbid,
            TypeID.Reg.value,
            filter_group_item(node.inst_name),
            node.raw_address_offset,
            dims,
            stride,
            node.get_property("regwidth"),
            node.get_property("accesswidth"),
        ))
        dbid = res.fetchone()[0]
        cur.close()
        return dbid

    def add_field(self, node: FieldNode, parent_dbid: int) -> None:
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO ral VALUES (
                NULL, -- dbid
                ?,    -- parent_dbid
                ?,    -- type_id
                ?,    -- name
                ?,    -- offset
                NULL, -- dims
                NULL, -- stride
                ?,    -- size
                NULL  -- accesswidth
            )
        """, (
            parent_dbid,
            TypeID.Field.value,
            filter_register_item(node.inst_name),
            node.low,
            node.width,
        ))
        cur.close()

    def finish(self) -> None:
        self.db.commit()
        self.db.close()
