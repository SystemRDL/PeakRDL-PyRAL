#!/usr/bin/env python3

import os
import timeit

from systemrdl.compiler import RDLCompiler
from peakrdl_pyral.exporter import PyRALExporter
from peakrdl_pyral_runtime.hwio.demo import DemoHWIO

this_dir = os.path.normpath(os.path.dirname(__file__))

# Generate a RAL
rdlc = RDLCompiler()
rdlc.compile_file(os.path.join(this_dir, "../rdl_src/structural.rdl"))
root = rdlc.elaborate()
e = PyRALExporter()
e.export(root.top, this_dir)


# Prepare ral
import structural
ral = structural.get_ral()
hwio = DemoHWIO()
ral.attach_hwio(hwio)

def test_func():
    ral.sub2[4].sub[0].r1.read()

result = timeit.timeit("test_func()", globals=globals(), number=100_000)
print(result)
