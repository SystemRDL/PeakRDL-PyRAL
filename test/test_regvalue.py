from unittest import TestCase
from collections import OrderedDict

from peakrdl_pyral_runtime.model.regvalue import RegValue

class TestRegValue(TestCase):
    def test_fields(self) -> None:
        spec = OrderedDict([
            ("a", (0, 8)),
            ("b", (8, 8)),
            ("c", (16, 8)),
            ("d", (24, 8)),
        ])
        rv = RegValue(0x12345678, spec)

        self.assertEqual(rv.a, 0x78)
        self.assertEqual(rv.b, 0x56)
        self.assertEqual(rv.c, 0x34)
        self.assertEqual(rv.d, 0x12)

        rv.b = 0xAA

        self.assertEqual(rv.a, 0x78)
        self.assertEqual(rv.b, 0xAA)
        self.assertEqual(rv.c, 0x34)
        self.assertEqual(rv.d, 0x12)

        self.assertEqual(int(rv), 0x1234AA78)

        self.assertListEqual(
            list(rv),
            [
                ("a", 0x78),
                ("b", 0xAA),
                ("c", 0x34),
                ("d", 0x12),
            ],
        )

    def test_invalid_fields(self) -> None:
        spec = OrderedDict([
            ("a", (0, 8)),
            ("b", (8, 8)),
            ("c", (16, 8)),
            ("d", (24, 8)),
        ])
        rv = RegValue(0x12345678, spec)
        with self.assertRaises(AttributeError):
            rv.x = 123

        with self.assertRaises(AttributeError):
            _ = rv.x
