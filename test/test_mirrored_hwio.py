from unittest import IsolatedAsyncioTestCase

from pyral_testutils.mock_hwio import MockHWIO
from peakrdl_pyral_runtime.hwio.mirror import MirroredHWIOWrapper

class TestMirroredHWIO(IsolatedAsyncioTestCase):
    def test_mirrored_rw(self) -> None:
        mockio = MockHWIO()
        hwio = MirroredHWIOWrapper(mockio)

        # Normal write
        hwio.write(0x10, 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("W", 0x10, 4, 0x1234ABCD),
        ])
        self.assertEqual(mockio.mem[0x10], 0xCD)
        self.assertEqual(mockio.mem[0x11], 0xAB)
        self.assertEqual(mockio.mem[0x12], 0x34)
        self.assertEqual(mockio.mem[0x13], 0x12)

        # Read from mirror should have written data
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Write only to mirror
        with hwio.write_to_mirror_only():
            hwio.write(0x10, 0xCAFEBABE)
        self.assertListEqual(mockio.get_latest_xfers(), [])
        self.assertEqual(mockio.mem[0x10], 0xCD)
        self.assertEqual(mockio.mem[0x11], 0xAB)
        self.assertEqual(mockio.mem[0x12], 0x34)
        self.assertEqual(mockio.mem[0x13], 0x12)

        # Read from mirror
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read(0x10), 0xCAFEBABE)
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Read from hardware to get actual value
        self.assertEqual(hwio.read(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("R", 0x10, 4, None),
        ])

        # Confirm mirror updated
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [])

    async def test_mirrored_rw_async(self) -> None:
        mockio = MockHWIO()
        hwio = MirroredHWIOWrapper(mockio)

        # Normal write
        await hwio.awrite(0x10, 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("aW", 0x10, 4, 0x1234ABCD),
        ])
        self.assertEqual(mockio.mem[0x10], 0xCD)
        self.assertEqual(mockio.mem[0x11], 0xAB)
        self.assertEqual(mockio.mem[0x12], 0x34)
        self.assertEqual(mockio.mem[0x13], 0x12)

        # Read from mirror should have written data
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Write only to mirror
        with hwio.write_to_mirror_only():
            await hwio.awrite(0x10, 0xCAFEBABE)
        self.assertListEqual(mockio.get_latest_xfers(), [])
        self.assertEqual(mockio.mem[0x10], 0xCD)
        self.assertEqual(mockio.mem[0x11], 0xAB)
        self.assertEqual(mockio.mem[0x12], 0x34)
        self.assertEqual(mockio.mem[0x13], 0x12)

        # Read from mirror
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread(0x10), 0xCAFEBABE)
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Read from hardware to get actual value
        self.assertEqual(await hwio.aread(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("aR", 0x10, 4, None),
        ])

        # Confirm mirror updated
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread(0x10), 0x1234ABCD)
        self.assertListEqual(mockio.get_latest_xfers(), [])


    def test_mirrored_bytes_rw(self) -> None:
        mockio = MockHWIO()
        hwio = MirroredHWIOWrapper(mockio)

        # Normal write
        hwio.write_bytes(0x10, bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("W", 0x10, 1, 0x12),
            ("W", 0x11, 1, 0x34),
            ("W", 0x12, 1, 0xAB),
            ("W", 0x13, 1, 0xCD),
        ])
        self.assertEqual(mockio.mem[0x10], 0x12)
        self.assertEqual(mockio.mem[0x11], 0x34)
        self.assertEqual(mockio.mem[0x12], 0xAB)
        self.assertEqual(mockio.mem[0x13], 0xCD)

        # Read from mirror should have written data
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Write only to mirror
        with hwio.write_to_mirror_only():
            hwio.write_bytes(0x10, bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(mockio.get_latest_xfers(), [])
        self.assertEqual(mockio.mem[0x10], 0x12)
        self.assertEqual(mockio.mem[0x11], 0x34)
        self.assertEqual(mockio.mem[0x12], 0xAB)
        self.assertEqual(mockio.mem[0x13], 0xCD)

        # Read from mirror
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read_bytes(0x10, 4), bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Read from hardware to get actual value
        self.assertEqual(hwio.read_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("R", 0x10, 1, None),
            ("R", 0x11, 1, None),
            ("R", 0x12, 1, None),
            ("R", 0x13, 1, None),
        ])

        # Confirm mirror updated
        with hwio.read_from_mirror():
            self.assertEqual(hwio.read_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [])

    async def test_mirrored_bytes_rw_async(self) -> None:
        mockio = MockHWIO()
        hwio = MirroredHWIOWrapper(mockio)

        # Normal write
        await hwio.awrite_bytes(0x10, bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("aW", 0x10, 1, 0x12),
            ("aW", 0x11, 1, 0x34),
            ("aW", 0x12, 1, 0xAB),
            ("aW", 0x13, 1, 0xCD),
        ])
        self.assertEqual(mockio.mem[0x10], 0x12)
        self.assertEqual(mockio.mem[0x11], 0x34)
        self.assertEqual(mockio.mem[0x12], 0xAB)
        self.assertEqual(mockio.mem[0x13], 0xCD)

        # Read from mirror should have written data
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Write only to mirror
        with hwio.write_to_mirror_only():
            await hwio.awrite_bytes(0x10, bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(mockio.get_latest_xfers(), [])
        self.assertEqual(mockio.mem[0x10], 0x12)
        self.assertEqual(mockio.mem[0x11], 0x34)
        self.assertEqual(mockio.mem[0x12], 0xAB)
        self.assertEqual(mockio.mem[0x13], 0xCD)

        # Read from mirror
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread_bytes(0x10, 4), bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertListEqual(mockio.get_latest_xfers(), [])

        # Read from hardware to get actual value
        self.assertEqual(await hwio.aread_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [
            ("aR", 0x10, 1, None),
            ("aR", 0x11, 1, None),
            ("aR", 0x12, 1, None),
            ("aR", 0x13, 1, None),
        ])

        # Confirm mirror updated
        with hwio.read_from_mirror():
            self.assertEqual(await hwio.aread_bytes(0x10, 4), bytes([0x12, 0x34, 0xAB, 0xCD]))
        self.assertListEqual(mockio.get_latest_xfers(), [])
