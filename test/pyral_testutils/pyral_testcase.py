from unittest import TestCase
from typing import Optional, Dict
import inspect
import os
import sys
import shutil
import pathlib

from peakrdl_pyral.exporter import PyRALExporter
from peakrdl_pyral_runtime import model as pyral
from systemrdl.compiler import RDLCompiler
from systemrdl.node import AddrmapNode, AddressableNode, FieldNode, SignalNode

class PyRALTestcase(TestCase):

    def get_testcase_dir(self) -> str:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        return class_dir

    def get_run_dir(self) -> str:
        this_dir = self.get_testcase_dir()
        run_dir = os.path.join(this_dir, "testdata.out", self.__class__.__name__)
        return run_dir

    def prepare_run_dir(self) -> None:
        run_dir = self.get_run_dir()
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        pathlib.Path(run_dir).mkdir(parents=True, exist_ok=True)

    def export(self, src_files: list[str], external_types: Optional[Dict[str, str]] = None) -> AddrmapNode:
        this_dir = self.get_testcase_dir()
        rdlc = RDLCompiler()
        for file in src_files:
            file = os.path.join(this_dir, file)
            rdlc.compile_file(file)
        root = rdlc.elaborate()

        e = PyRALExporter()
        e.export(root.top, self.get_run_dir(), external_types)

        return root.top

    def setUp(self) -> None:
        self.prepare_run_dir()
        sys.path.append(self.get_run_dir())

    def tearDown(self):
        sys.path.pop()


    def compare_rdl_with_ral(self, rdl_node: AddrmapNode, ral: pyral.RALGroup) -> None:
        # Compare the compiler's RDL hierarchy with the generated RAL
        for node in rdl_node.descendants(unroll=True):
            if isinstance(node, SignalNode):
                continue
            # Traverse the RAL to reach the same node
            path_segments = node.get_path_segments(array_suffix="/{index:d}")
            path_segments = path_segments[1:] # prune off the root node segment
            ral_node = ral
            for segment in path_segments:
                subsegs = segment.split("/")
                child_name = subsegs[0]
                array_indexes = [int(dim) for dim in subsegs[1:]]
                ral_node = getattr(ral_node, child_name)
                for dim in array_indexes:
                    ral_node = ral_node[dim]

            # Compare RAL against compiler model
            assert isinstance(ral_node, pyral.RALNode)
            self.assertEqual(node.get_path_segment(), ral_node.name)
            self.assertEqual(node.get_path(), ral_node.path)
            self.assertEqual(node.parent.get_path(), ral_node.parent.path)
            if isinstance(node, AddressableNode):
                assert isinstance(ral_node, pyral.AddressableRALNode)
                self.assertEqual(node.absolute_address, ral_node.address)
            elif isinstance(node, FieldNode):
                assert isinstance(ral_node, pyral.RALField)
                self.assertEqual(node.low, ral_node.offset)
                self.assertEqual(node.width, ral_node.width)
