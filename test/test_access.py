from pyral_testutils.pyral_testcase import PyRALTestcase
from pyral_testutils.mock_hwio import MockHWIO

class TestAccess(PyRALTestcase):
    async def test_group_access(self) -> None:
        self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral = structural.get_ral()
        hwio = MockHWIO()
        ral.attach_hwio(hwio)


        # Simple read/write
        ral.write(0x10, 0x1234ABCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x10, 4, 0x1234ABCD),
        ])
        self.assertEqual(hwio.mem[0x10], 0xCD)
        self.assertEqual(hwio.mem[0x11], 0xAB)
        self.assertEqual(hwio.mem[0x12], 0x34)
        self.assertEqual(hwio.mem[0x13], 0x12)
        self.assertEqual(ral.read(0x10), 0x1234ABCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x10, 4, None),
        ])

        # Simple read/write - async
        await ral.awrite(0x10, 0xABCD1234)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x10, 4, 0xABCD1234),
        ])
        self.assertEqual(hwio.mem[0x10], 0x34)
        self.assertEqual(hwio.mem[0x11], 0x12)
        self.assertEqual(hwio.mem[0x12], 0xCD)
        self.assertEqual(hwio.mem[0x13], 0xAB)
        self.assertEqual(await ral.aread(0x10), 0xABCD1234)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x10, 4, None),
        ])

        # Simple read/write from sub-block
        ral.sub2[1].write(0x10, 0x4321, 2)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x2090, 2, 0x4321),
        ])
        self.assertEqual(hwio.mem[0x2090], 0x21)
        self.assertEqual(hwio.mem[0x2091], 0x43)
        self.assertEqual(ral.sub2[1].read(0x10, 2), 0x4321)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x2090, 2, None),
        ])

        # Simple read/write from sub-block - async
        await ral.sub2[1].awrite(0x10, 0x1234, 2)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x2090, 2, 0x1234),
        ])
        self.assertEqual(hwio.mem[0x2090], 0x34)
        self.assertEqual(hwio.mem[0x2091], 0x12)
        self.assertEqual(await ral.sub2[1].aread(0x10, 2), 0x1234)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x2090, 2, None),
        ])

        # Write/read list
        ral.write_list(0x80, [0x1234, 0x5678, 0xABCD], 2)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x80, 2, 0x1234),
            ("W", 0x82, 2, 0x5678),
            ("W", 0x84, 2, 0xABCD),
        ])
        self.assertListEqual(ral.read_list(0x80, 3, 2), [0x1234, 0x5678, 0xABCD])
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x80, 2, None),
            ("R", 0x82, 2, None),
            ("R", 0x84, 2, None),
        ])

        # Write/read list - async
        await ral.awrite_list(0x80, [0x4567, 0x1357, 0xACE0], 2)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x80, 2, 0x4567),
            ("aW", 0x82, 2, 0x1357),
            ("aW", 0x84, 2, 0xACE0),
        ])
        self.assertListEqual(await ral.aread_list(0x80, 3, 2), [0x4567, 0x1357, 0xACE0])
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x80, 2, None),
            ("aR", 0x82, 2, None),
            ("aR", 0x84, 2, None),
        ])

        # Write/read bytes
        ral.write_bytes(0x100, bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x100, 1, 0xCA),
            ("W", 0x101, 1, 0xFE),
            ("W", 0x102, 1, 0xBA),
            ("W", 0x103, 1, 0xBE),
        ])
        self.assertEqual(ral.read_bytes(0x100, 4), bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x100, 1, None),
            ("R", 0x101, 1, None),
            ("R", 0x102, 1, None),
            ("R", 0x103, 1, None),
        ])

        # Write/read bytes - async
        await ral.awrite_bytes(0x100, bytes([0xDE, 0xAD, 0xBE, 0xEF]))
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x100, 1, 0xDE),
            ("aW", 0x101, 1, 0xAD),
            ("aW", 0x102, 1, 0xBE),
            ("aW", 0x103, 1, 0xEF),
        ])
        self.assertEqual(await ral.aread_bytes(0x100, 4), bytes([0xDE, 0xAD, 0xBE, 0xEF]))
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x100, 1, None),
            ("aR", 0x101, 1, None),
            ("aR", 0x102, 1, None),
            ("aR", 0x103, 1, None),
        ])

    async def test_reg_access(self) -> None:
        self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral = structural.get_ral()
        hwio = MockHWIO()
        ral.attach_hwio(hwio)

        # sync
        ral.r0.write(0x1234ABCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x000, 4, 0x1234ABCD),
        ])
        self.assertEqual(hwio.mem[0x0], 0xCD)
        self.assertEqual(hwio.mem[0x1], 0xAB)
        self.assertEqual(hwio.mem[0x2], 0x34)
        self.assertEqual(hwio.mem[0x3], 0x12)
        self.assertEqual(ral.r0.read(), 0x1234ABCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x0, 4, None),
        ])

        # async
        await ral.r0.awrite(0x19283746)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x000, 4, 0x19283746),
        ])
        self.assertEqual(hwio.mem[0x0], 0x46)
        self.assertEqual(hwio.mem[0x1], 0x37)
        self.assertEqual(hwio.mem[0x2], 0x28)
        self.assertEqual(hwio.mem[0x3], 0x19)
        self.assertEqual(await ral.r0.aread(), 0x19283746)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x0, 4, None),
        ])

        # sync
        with ral.r2.write_fields() as r:
            r.a = 0x54
            r.b = 0x32
            # implied: r.c = 0
            r.d = 1
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x3000, 4, 0x80320054),
        ])
        ral.r2.write(0x4F23FF45)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x3000, 4, 0x4F23FF45),
        ])
        r = ral.r2.read_fields()
        self.assertEqual(int(r), 0x4F23FF45)
        self.assertEqual(r.a, 0x45)
        self.assertEqual(r.b, 0x23)
        self.assertEqual(r.c, 1)
        self.assertEqual(r.d, 0)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x3000, 4, None),
        ])

        # async
        async with ral.r2.awrite_fields() as r:
            r.a = 0x54
            r.b = 0x32
            # implied: r.c = 0
            r.d = 1
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x3000, 4, 0x80320054),
        ])
        await ral.r2.awrite(0x4F23FF45)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x3000, 4, 0x4F23FF45),
        ])
        r = await ral.r2.aread_fields()
        self.assertEqual(int(r), 0x4F23FF45)
        self.assertEqual(r.a, 0x45)
        self.assertEqual(r.b, 0x23)
        self.assertEqual(r.c, 1)
        self.assertEqual(r.d, 0)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x3000, 4, None),
        ])

        # sync
        with ral.r2.change_fields() as r:
            self.assertListEqual(hwio.get_latest_xfers(), [
                ("R", 0x3000, 4, None),
            ])
            self.assertEqual(int(r), 0x4F23FF45)
            r.b = 0x55
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x3000, 4, 0x4F55FF45),
        ])

        # async
        async with ral.r2.achange_fields() as r:
            self.assertListEqual(hwio.get_latest_xfers(), [
                ("aR", 0x3000, 4, None),
            ])
            self.assertEqual(int(r), 0x4F55FF45)
            r.b = 0x44
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x3000, 4, 0x4F44FF45),
        ])


    async def test_field_access(self) -> None:
        self.export([
            "rdl_src/structural.rdl"
        ])
        import structural
        ral = structural.get_ral()
        hwio = MockHWIO()
        ral.attach_hwio(hwio)

        # sync
        ral.r2.b.change(0xAB)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x3000, 4, None),
            ("W", 0x3000, 4, 0x00AB0000),
        ])
        self.assertEqual(ral.r2.b.read(), 0xAB)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x3000, 4, None),
        ])

        # async
        await ral.r2.b.achange(0xCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x3000, 4, None),
            ("aW", 0x3000, 4, 0x00CD0000),
        ])
        self.assertEqual(await ral.r2.b.aread(), 0xCD)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x3000, 4, None),
        ])

    async def test_wide_reg(self) -> None:
        self.export([
            "rdl_src/wide_regs.rdl"
        ])
        import wide_regs
        ral = wide_regs.get_ral()
        hwio = MockHWIO()
        ral.attach_hwio(hwio)

        # sync
        ral.r0.write(0xABCD1234_DEADBEEF)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("W", 0x0, 4, 0xDEADBEEF),
            ("W", 0x4, 4, 0xABCD1234),
        ])
        self.assertEqual(ral.r0.read(), 0xABCD1234_DEADBEEF)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("R", 0x0, 4, None),
            ("R", 0x4, 4, None),
        ])

        # async
        await ral.r0.awrite(0x98765432_CAFEBABE)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aW", 0x0, 4, 0xCAFEBABE),
            ("aW", 0x4, 4, 0x98765432),
        ])
        self.assertEqual(await ral.r0.aread(), 0x98765432_CAFEBABE)
        self.assertListEqual(hwio.get_latest_xfers(), [
            ("aR", 0x0, 4, None),
            ("aR", 0x4, 4, None),
        ])
