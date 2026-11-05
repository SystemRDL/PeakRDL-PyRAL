import keyword

COMMON_RESERVED_WORDS = {
    "parent",
    "_dbapi",
    "_dbid",
    "name",
    "path",
    "address",
    "size",
    "_hwio",
    "_lookup_hwio",
    "children",
    "read",
    "write",
    "aread",
    "awrite",
    "detach_hwio",
    "attach_hwio",
    "_abc_impl",
}

GROUP_RESERVED_WORDS = COMMON_RESERVED_WORDS | {
    "read_list",
    "read_bytes",
    "write_list",
    "write_bytes",
    "aread_list",
    "aread_bytes",
    "awrite_list",
    "awrite_bytes",
}

REGISTER_RESERVED_WORDS = COMMON_RESERVED_WORDS | {
    "access_size",
    "read_fields",
    "write_fields",
    "change_fields",
    "aread_fields",
    "awrite_fields",
    "achange_fields",
}

def filter_group_item(s: str) -> str:
    if s in GROUP_RESERVED_WORDS:
        s += "_"
    return s

def filter_register_item(s: str) -> str:
    if s in REGISTER_RESERVED_WORDS:
        s += "_"
    return s

# Names that cannot be used as Enum members
ENUM_RESERVED_WORDS = {
    "mro",
}

def filter_enum_member(s: str) -> str:
    if s.startswith("_"):
        # Python's Enum reserves _sunder_ names, ignores __dunder__ names and
        # mangles __private names. Prefix so the member stays a plain name.
        s = "m" + s
    if keyword.iskeyword(s) or s in ENUM_RESERVED_WORDS:
        s += "_"
    return s
