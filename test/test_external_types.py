from pyral_testutils.pyral_testcase import PyRALTestcase
from peakrdl_pyral_runtime import model as pyral

class TestExternalTypes(PyRALTestcase):
    def test_graft(self):
        self.export([
            "rdl_src/tiny.rdl"
        ])
        top = self.export(
            [
                "rdl_src/tiny.rdl",
                "rdl_src/grafted.rdl",
            ],
            external_types= {
                "tiny": "tiny"
            }
        )

        import grafted
        ral: pyral.RALGroup = grafted.get_ral()
        self.compare_rdl_with_ral(top, ral)

        self.assertEqual(ral._dbapi.origin_module_name, "grafted")
        self.assertEqual(ral.t0._dbapi.origin_module_name, "tiny")
        self.assertEqual(ral.amap._dbapi.origin_module_name, "grafted")
        self.assertEqual(ral.amap.t1._dbapi.origin_module_name, "tiny")
