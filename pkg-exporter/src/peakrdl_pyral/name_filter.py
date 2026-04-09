GROUP_RESERVED_WORDS = {
    "parent",
    "_dbapi",
    "_dbid",
    "name",
    "path",
    "address",
    "_hwio",
    "_lookup_hwio",
    "children",
    "read",
    "read_list",
    "read_bytes",
    "write",
    "write_list",
    "write_bytes",
    "detach_hwio",
    "attach_hwio",
}

REGISTER_RESERVED_WORDS = {
    "parent",
    "_dbapi",
    "_dbid",
    "name",
    "path",
    "address",
    "_hwio",
    "_lookup_hwio",
    "children",
    "width",
    "accesswidth",
    "read",
    "read_fields",
    "write",
    "write_fields",
    "change_fields",
    "detach_hwio",
    "attach_hwio",
}

def filter_group_item(s: str) -> str:
    if s in GROUP_RESERVED_WORDS:
        s += "_"
    return s

def filter_register_item(s: str) -> str:
    if s in REGISTER_RESERVED_WORDS:
        s += "_"
    return s
