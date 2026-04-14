from typing import Optional, Dict
import os
import textwrap

from systemrdl.node import AddrmapNode

from .db_generator import DBGenerator
from .type_stub_generator import TypeStubGenerator

class PyRALExporter:
    def export(self, top_node: AddrmapNode, output_dir: str, external_types: Optional[Dict[str, str]] = None) -> None:
        if external_types is None:
            external_types = {}

        ral_name = top_node.inst_name
        db_path = os.path.join(output_dir, f"{ral_name}.db")
        pyi_path = os.path.join(output_dir, f"{ral_name}_stubs.pyi")

        db_generator = DBGenerator(db_path, external_types)
        db_generator.generate_group(top_node)
        db_generator.finish()

        ts_gen = TypeStubGenerator(pyi_path, external_types)
        ts_gen.generate(top_node)

        self._write_py_module(output_dir, ral_name)

    def _write_py_module(self, output_dir: str, ral_name: str) -> None:
        py_path = os.path.join(output_dir, f"{ral_name}.py")

        if os.path.exists(os.path.join(output_dir, "__init__.py")):
            # Use relative import
            stubs_import_prefix = "."
        else:
            # Use absolute import
            stubs_import_prefix = ""

        content = f"""
        import os
        from typing import TYPE_CHECKING

        from peakrdl_pyral_runtime.dbapi import DBAPI

        if TYPE_CHECKING:
            from {stubs_import_prefix}{ral_name}_stubs import {ral_name}_Group

        def _get_dbapi() -> DBAPI:
            this_dir = os.path.dirname(os.path.realpath(__file__))
            db_path = os.path.join(this_dir, "{ral_name}.db")
            dbapi = DBAPI(db_path, __name__)
            return dbapi

        def get_ral(offset: int = 0) -> "{ral_name}_Group":
            dbapi = _get_dbapi()
            root = dbapi.get_root(offset)
            return root # type: ignore[return-value]
        """
        content = textwrap.dedent(content).lstrip()

        with open(py_path, "w", encoding="utf-8") as f:
            f.write(content)
