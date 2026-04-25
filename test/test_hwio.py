import os

from pyral_testutils.pyral_testcase import PyRALTestcase

from peakrdl_pyral_runtime.hwio import HWIO
from peakrdl_pyral_runtime.hwio.demo import DemoHWIO
from peakrdl_pyral_runtime.hwio.callback import CallbackHWIO
from peakrdl_pyral_runtime.hwio.mmap import MMapFileHWIO
from peakrdl_pyral_runtime.hwio.openocd import OpenOCDHWIO # TODO: make a testcase for this somehow

class TestHWIO(PyRALTestcase):
    def do_hwio_tests(self, hwio: HWIO) -> None:
        # Read range to confirm readback of 0's
        self.assertListEqual(
            hwio.read_list(0, 16),
            [0] * 16
        )

        # Test write + read of each access size
        for size in [1, 2, 4, 8]:
            words = []
            for i in range(32):
                word  = 0
                for bidx in range(size):
                    word |= (i + bidx) << (bidx * 8)
                words.append(word)

            hwio.write_list(size, words, size)

            self.assertListEqual(
                words,
                hwio.read_list(size, len(words), size)
            )

        # read/write bytes
        hwio.write_bytes(0x100, bytes([0xCA, 0xFE, 0xBA, 0xBE]))
        self.assertEqual(hwio.read_bytes(0x100, 4), bytes([0xCA, 0xFE, 0xBA, 0xBE]))

        # Unaligned access assertions
        with self.assertRaises(ValueError):
            hwio.read(1)
        with self.assertRaises(ValueError):
            hwio.read_list(1, 1)
        with self.assertRaises(ValueError):
            hwio.write(1, 0)
        with self.assertRaises(ValueError):
            hwio.write_list(1, [0])

    def test_demo(self) -> None:
        hwio = DemoHWIO()
        self.do_hwio_tests(hwio)

    def test_callback(self) -> None:
        demo_hwio = DemoHWIO()
        hwio = CallbackHWIO(
            read_cb=demo_hwio._read_impl,
            write_cb=demo_hwio._write_impl,
        )
        self.do_hwio_tests(hwio)

    def test_mmap(self) -> None:
        outdir = self.get_run_dir()
        dev_file_path = os.path.join(outdir, "dev_file.bin")

        # Create a blank file first
        with open(dev_file_path, "wb") as f:
            f.write(bytes(0x1000))

        hwio = MMapFileHWIO(dev_file_path)
        self.do_hwio_tests(hwio)
