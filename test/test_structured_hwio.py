from pyral_testutils.pyral_testcase import PyRALTestcase
from pyral_testutils.mock_hwio import MockHWIO

class TestStructuredHWIO(PyRALTestcase):
    def assertHadRead(self, hwio: MockHWIO, addr: int) -> None:
        self.assertListEqual(hwio.get_latest_xfers(), [("R", addr, 4, None),])

    def assertHadNoActivity(self, *hwios: MockHWIO) -> None:
        for hwio in hwios:
            self.assertListEqual(hwio.get_latest_xfers(), [])

    def test_subsystem_hwio(self) -> None:
        """
        Test attaching HWIO to various sub-nodes of a RAL
        """
        self.export([
            "rdl_src/soc.rdl"
        ])
        import soc
        ral = soc.get_ral()

        # Prepare some HWIO
        root_hwio = MockHWIO()
        s0_hwio = MockHWIO()
        s3_hwio = MockHWIO()
        sub_hwio = MockHWIO()
        sub_s2_hwio = MockHWIO()

        # Should fail due to no HWIO attached yet
        with self.assertRaises(LookupError):
            ral.read(0)

        # Attach them to various parts of the RAL
        ral.attach_hwio(root_hwio)
        ral.s0.attach_hwio(s0_hwio)
        ral.s23[1].attach_hwio(s3_hwio)
        ral.sub.attach_hwio(sub_hwio)
        ral.sub.s2.attach_hwio(sub_s2_hwio)

        # Test that the correct HWIO got the transaction with the correct address
        ral.s0.r0.read()
        self.assertHadRead(s0_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio, s3_hwio, sub_hwio, sub_s2_hwio)

        ral.s1.r0.read()
        self.assertHadRead(root_hwio, 0x1000)
        self.assertHadNoActivity(s0_hwio, s3_hwio, sub_hwio, sub_s2_hwio)

        ral.s23[0].r0.read()
        self.assertHadRead(root_hwio, 0x2000)
        self.assertHadNoActivity(s0_hwio, s3_hwio, sub_hwio, sub_s2_hwio)

        ral.s23[1].r0.read()
        self.assertHadRead(s3_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio, s0_hwio, sub_hwio, sub_s2_hwio)

        ral.sub.s0.r0.read()
        self.assertHadRead(sub_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio, s0_hwio, s3_hwio, sub_s2_hwio)

        ral.sub.s1.r0.read()
        self.assertHadRead(sub_hwio, 0x1000)
        self.assertHadNoActivity(root_hwio, s0_hwio, s3_hwio, sub_s2_hwio)

        ral.sub.s2.r0.read()
        self.assertHadRead(sub_s2_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio, s0_hwio, s3_hwio, sub_hwio)

        # Detach the sub_hwio and see that children pass-through
        ral.sub.detach_hwio()

        ral.sub.s0.r0.read()
        self.assertHadRead(root_hwio, 0x10000)
        self.assertHadNoActivity(s0_hwio, s3_hwio, sub_hwio, sub_s2_hwio)

        ral.sub.s1.r0.read()
        self.assertHadRead(root_hwio, 0x11000)
        self.assertHadNoActivity(s0_hwio, s3_hwio, sub_hwio, sub_s2_hwio)

        ral.sub.s2.r0.read()
        self.assertHadRead(sub_s2_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio, s0_hwio, s3_hwio, sub_hwio)

    def test_extra_offsets(self) -> None:
        """
        Test applying extra offsets to a system via various methods.
        - via the HWIO at the ral root
        - via the RAL root
        - via both
        - via HWIO at an internal node
        """
        self.export([
            "rdl_src/soc.rdl"
        ])
        import soc

        # Offset on the HWIO attached to the RAL root
        ral = soc.get_ral()
        root_hwio = MockHWIO(offset=0xA0_0000)
        sub_hwio = MockHWIO(offset=0xB0_0000)
        ral.attach_hwio(root_hwio)
        ral.sub.attach_hwio(sub_hwio)

        ral.s1.r0.read()
        self.assertHadRead(root_hwio, 0xA0_1000)
        self.assertHadNoActivity(sub_hwio)

        ral.sub.s0.r0.read()
        self.assertHadRead(sub_hwio, 0xB0_0000)
        self.assertHadNoActivity(root_hwio)

        # Offset defined by the RAL root
        ral = soc.get_ral(offset=0xB0_0000)
        root_hwio = MockHWIO()
        sub_hwio = MockHWIO()
        ral.attach_hwio(root_hwio)
        ral.sub.attach_hwio(sub_hwio)

        ral.s1.r0.read()
        self.assertHadRead(root_hwio, 0xB0_1000)
        self.assertHadNoActivity(sub_hwio)

        ral.sub.s0.r0.read()
        self.assertHadRead(sub_hwio, 0x0000)
        self.assertHadNoActivity(root_hwio)

        # Both
        ral = soc.get_ral(offset=0xC0_0000)
        root_hwio = MockHWIO(offset=0x100_0000)
        sub_hwio = MockHWIO(offset=0x200_0000)
        ral.attach_hwio(root_hwio)
        ral.sub.attach_hwio(sub_hwio)

        ral.s1.r0.read()
        self.assertHadRead(root_hwio, 0x1C0_1000)
        self.assertHadNoActivity(sub_hwio)

        ral.sub.s0.r0.read()
        self.assertHadRead(sub_hwio, 0x200_0000)
        self.assertHadNoActivity(root_hwio)
