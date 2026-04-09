from typing import TYPE_CHECKING

from peakrdl.plugins.exporter import ExporterSubcommandPlugin

from .exporter import PyRALExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode

class Exporter(ExporterSubcommandPlugin):
    short_desc = "Generate a Python register abstraction layer"

    def add_exporter_arguments(self, arg_group: 'argparse._ActionsContainer') -> None:
        pass

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        x = PyRALExporter()
        x.export(
            top_node,
            options.output,
        )
