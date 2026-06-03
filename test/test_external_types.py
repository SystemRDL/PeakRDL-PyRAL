from pyral_testutils.pyral_testcase import PyRALTestcase
from peakrdl_pyral_runtime import model as pyral

class TestExternalTypes(PyRALTestcase):
    def test_absolute_graft(self):
        self.export(
            [
                "rdl_src/tiny.rdl"
            ],
            output_lib_name="tinylib",
        )
        top = self.export(
            [
                "rdl_src/tiny.rdl",
                "rdl_src/grafted.rdl",
            ],
            external_types= {
                "tiny": "tinylib.tiny"
            },
            output_lib_name="toplib",
        )

        from toplib import grafted
        ral: pyral.RALGroup = grafted.get_ral()
        self.compare_rdl_with_ral(top, ral)

        self.assertEqual(ral._dbapi.origin_module_name, "toplib.grafted")
        self.assertEqual(ral.t0._dbapi.origin_module_name, "tinylib.tiny")
        self.assertEqual(ral.amap._dbapi.origin_module_name, "toplib.grafted")
        self.assertEqual(ral.amap.t1._dbapi.origin_module_name, "tinylib.tiny")

    def test_relative_graft(self):
        self.export(
            [
                "rdl_src/tiny.rdl"
            ],
            output_lib_name="mylib",
        )
        top = self.export(
            [
                "rdl_src/tiny.rdl",
                "rdl_src/grafted.rdl",
            ],
            external_types= {
                "tiny": ".tiny"
            },
            output_lib_name="mylib",
        )

        from mylib import grafted
        ral: pyral.RALGroup = grafted.get_ral()
        self.compare_rdl_with_ral(top, ral)

        self.assertEqual(ral._dbapi.origin_module_name, "mylib.grafted")
        self.assertEqual(ral.t0._dbapi.origin_module_name, "mylib.tiny")
        self.assertEqual(ral.amap._dbapi.origin_module_name, "mylib.grafted")
        self.assertEqual(ral.amap.t1._dbapi.origin_module_name, "mylib.tiny")
