import ast
import enum
import os
import sqlite3

from pyral_testutils.pyral_testcase import PyRALTestcase
from pyral_testutils.mock_hwio import MockHWIO

class TestEnums(PyRALTestcase):
    async def test_field_access(self) -> None:
        top = self.export(["rdl_src/enums.rdl"], output_lib_name="enumlib_access")
        from enumlib_access import enum_test
        ral = enum_test.get_ral()
        self.compare_rdl_with_ral(top, ral)
        hwio = MockHWIO()
        ral.attach_hwio(hwio)

        mode_e = ral.r0.mode.enum
        assert mode_e is not None
        self.assertTrue(issubclass(mode_e, enum.IntEnum))
        self.assertEqual(mode_e.__name__, "mode_e")
        self.assertListEqual(
            [(m.name, m.value) for m in mode_e],
            [("OFF", 0), ("SLOW", 1), ("FAST", 2)],
        )

        # Fields without an encoding
        self.assertIsNone(ral.r0.plain.enum)

        # Same RDL enum type maps to the same class
        self.assertIs(ral.r1.mode2.enum, mode_e)

        # Same-named enums in different scopes are distinct
        ctrl_state_e = ral.ctrl.state.enum
        status_state_e = ral.status.state.enum
        assert ctrl_state_e is not None and status_state_e is not None
        self.assertIsNot(ctrl_state_e, status_state_e)
        self.assertListEqual([m.name for m in ctrl_state_e], ["IDLE", "BUSY"])
        self.assertListEqual([m.name for m in status_state_e], ["READY", "ERROR", "DONE"])

        # Read returns the enum member
        ral.r0.write(0x1202)
        value = ral.r0.mode.read()
        self.assertIs(value, mode_e.FAST)
        self.assertEqual(value, 2)
        plain = ral.r0.plain.read()
        self.assertIs(type(plain), int)
        self.assertEqual(plain, 0x12)

        # Unencoded value falls back to int
        ral.r0.write(0x3)
        value = ral.r0.mode.read()
        self.assertIs(type(value), int)
        self.assertEqual(value, 3)

        # Change with an enum member
        ral.r0.write(0xAB00)
        hwio.get_latest_xfers()
        ral.r0.mode.change(mode_e.SLOW)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x0, 4, None),
            ("W", 0x0, 4, 0xAB01),
        ])
        self.assertIs(ral.r0.mode.read(), mode_e.SLOW)

        # Async variants
        await ral.r0.mode.achange(mode_e.FAST)
        self.assertIs(await ral.r0.mode.aread(), mode_e.FAST)

    async def test_regvalue_access(self) -> None:
        self.export(["rdl_src/enums.rdl"], output_lib_name="enumlib_rv")
        from enumlib_rv import enum_test
        ral = enum_test.get_ral()
        hwio = MockHWIO()
        ral.attach_hwio(hwio)

        mode_e = ral.r1.mode2.enum
        kw_e = ral.r1.kw.enum
        assert mode_e is not None and kw_e is not None

        # Keyword and reserved names are renamed
        self.assertListEqual(
            [(m.name, m.value) for m in kw_e],
            [("None_", 0), ("pass_", 1), ("m_x_", 2), ("mro_", 3)],
        )
        self.assertIs(kw_e.None_, kw_e(0))

        with ral.r1.write_fields() as rv:
            rv.mode2 = mode_e.FAST
            rv.kw = kw_e.mro_
        self.assertEqual(ral.r1.read(), 0x320)

        rv = ral.r1.read_fields()
        self.assertIs(rv.mode2, mode_e.FAST)
        self.assertIs(rv.kw, kw_e.mro_)
        self.assertListEqual(list(rv), [("mode2", mode_e.FAST), ("kw", kw_e.mro_)])

        # Unencoded value falls back to int
        with ral.r1.change_fields() as rv:
            rv.mode2 = 3
        rv = ral.r1.read_fields()
        self.assertIs(type(rv.mode2), int)
        self.assertEqual(rv.mode2, 3)
        self.assertIs(rv.kw, kw_e.mro_)

        # Async variants
        async with ral.r1.achange_fields() as rv:
            rv.mode2 = mode_e.OFF
        rv = await ral.r1.aread_fields()
        self.assertIs(rv.mode2, mode_e.OFF)
        async with ral.r1.awrite_fields() as rv:
            rv.kw = kw_e.pass_
        self.assertEqual(await ral.r1.aread(), 0x100)

    async def test_legacy_db(self) -> None:
        # A DB generated before enum support has no enum tables.
        # It must still load, with fields returning plain ints
        self.export(["rdl_src/enums.rdl"], output_lib_name="enumlib_legacy")
        db_path = os.path.join(self.get_run_dir(), "enumlib_legacy", "enum_test.db")
        db = sqlite3.connect(db_path)
        db.execute("DROP TABLE enums")
        db.execute("DROP TABLE enum_members")
        db.execute("DROP TABLE field_enums")
        db.commit()
        db.close()

        from enumlib_legacy import enum_test
        ral = enum_test.get_ral()
        ral.attach_hwio(MockHWIO())

        self.assertIsNone(ral.r0.mode.enum)
        ral.r0.write(0x2)
        value = ral.r0.mode.read()
        self.assertIs(type(value), int)
        self.assertEqual(value, 2)
        rv = ral.r0.read_fields()
        self.assertIs(type(rv.mode), int)
        self.assertEqual(rv.mode, 2)

    def test_stubs(self) -> None:
        self.export(["rdl_src/enums.rdl"], output_lib_name="enumlib_stubs")
        pyi_path = os.path.join(self.get_run_dir(), "enumlib_stubs", "enum_test_stubs.pyi")
        with open(pyi_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)

        enum_classes = {
            node.name: [t.id for stmt in node.body if isinstance(stmt, ast.Assign) for t in stmt.targets if isinstance(t, ast.Name)]
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and any(isinstance(b, ast.Name) and b.id == "IntEnum" for b in node.bases)
        }
        self.assertDictEqual(enum_classes, {
            "mode_e_Enum": ["OFF", "SLOW", "FAST"],
            "kw_e_Enum": ["None_", "pass_", "m_x_", "mro_"],
            "ctrl_t__state_e_Enum": ["IDLE", "BUSY"],
            "status_t__state_e_Enum": ["READY", "ERROR", "DONE"],
        })
        self.assertIn("mode: mode_Field", content)
        self.assertIn("enum: type[mode_e_Enum]", content)
        self.assertIn("def read(self) -> mode_e_Enum | int: ...", content)
        self.assertIn("mode: mode_e_Enum | int", content)
        self.assertIn("plain: RALField", content)
        self.assertIn("plain: int", content)
