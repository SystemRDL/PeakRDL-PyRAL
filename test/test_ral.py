from pyral_testutils.pyral_testcase import PyRALTestcase
from peakrdl_pyral_runtime import model as pyral
from systemrdl.node import AddressableNode, FieldNode

class TestRAL(PyRALTestcase):
    def test_structure(self) -> None:
        top = self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral = structural.get_ral()

        self.compare_rdl_with_ral(top, ral)

    def test_node_features(self):
        self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral: pyral.RALGroup = structural.get_ral()

        child_names = [repr(child) for child in ral.children()]
        self.assertListEqual(
            child_names,
            [
                "<RALRegister: structural.r0>",
                "<RALArray of RALRegister: structural.r1[][][]>",
                "<RALGroup: structural.sub1>",
                "<RALArray of RALGroup: structural.sub2[]>",
            ]
        )

        with self.assertRaises(AttributeError):
            ral.does_not_exist

    def test_arrays(self):
        self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral: pyral.RALGroup = structural.get_ral()

        self.assertEqual(len(ral.sub2), 8)
        self.assertEqual(len(list(ral.sub2)), 8)
        self.assertEqual(ral.sub2[0].name, "sub2[0]")
        self.assertEqual(ral.sub2[4].name, "sub2[4]")
        self.assertEqual(ral.sub2[-1].name, "sub2[7]")
        self.assertEqual(ral.sub2[-2].name, "sub2[6]")
        with self.assertRaises(IndexError):
            ral.sub2[8]
        self.assertListEqual(
            [g.name for g in ral.sub2[1:6]],
            [
                "sub2[1]",
                "sub2[2]",
                "sub2[3]",
                "sub2[4]",
                "sub2[5]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[1:6:2]],
            [
                "sub2[1]",
                "sub2[3]",
                "sub2[5]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[5:]],
            [
                "sub2[5]",
                "sub2[6]",
                "sub2[7]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[5::2]],
            [
                "sub2[5]",
                "sub2[7]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[:3]],
            [
                "sub2[0]",
                "sub2[1]",
                "sub2[2]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[:3:2]],
            [
                "sub2[0]",
                "sub2[2]",
            ]
        )
        self.assertListEqual(
            [g.name for g in ral.sub2[-4:-2]],
            [
                "sub2[4]",
                "sub2[5]",
            ]
        )

        with self.assertRaises(TypeError):
            ral.sub2["invalid"]
