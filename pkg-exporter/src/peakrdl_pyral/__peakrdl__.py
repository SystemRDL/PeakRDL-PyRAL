from typing import TYPE_CHECKING
import re

from peakrdl.plugins.exporter import ExporterSubcommandPlugin

from .exporter import PyRALExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode

class Exporter(ExporterSubcommandPlugin):
    short_desc = "Generate a Python register abstraction layer"

    def add_exporter_arguments(self, arg_group: 'argparse._ActionsContainer') -> None:
        arg_group.add_argument(
            "--graft-type",
            dest="graft_types",
            metavar="TYPE_NAME=IMPORT_PATH",
            action="append",
            default=[],
            help="Graft all occurrences of an RDL type to an existing PyRAL module"
        )

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        # Parse graft_types
        graft_types: dict[str, str] = {}
        for graft_type_arg in options.graft_types:
            m = re.fullmatch(r"(\w+)=([\.\w]+)", graft_type_arg)
            if not m:
                raise ValueError(f"Invalid graft type argument: {graft_type_arg}")

            type_name = m.group(1)
            import_path = m.group(2)
            graft_types[type_name] = import_path

        x = PyRALExporter()
        x.export(
            top_node,
            options.output,
            graft_types
        )
