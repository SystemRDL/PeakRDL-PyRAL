from unittest import TestCase
from enum import IntEnum
from collections import OrderedDict

from peakrdl_pyral_runtime.model.regvalue import RegValue, make_decode_map

class TestRegValue(TestCase):
    def test_fields(self) -> None:
        spec = OrderedDict([
            ("a", (0, 8, None)),
            ("b", (8, 8, None)),
            ("c", (16, 8, None)),
            ("d", (24, 8, None)),
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
            ("a", (0, 8, None)),
            ("b", (8, 8, None)),
            ("c", (16, 8, None)),
            ("d", (24, 8, None)),
        ])
        rv = RegValue(0x12345678, spec)
        with self.assertRaises(AttributeError):
            rv.x = 123

        with self.assertRaises(AttributeError):
            _ = rv.x

        with self.assertRaises(ValueError):
            rv.a = 256

    def test_enum_fields(self) -> None:
        class Mode(IntEnum):
            OFF = 0
            FAST = 2

        spec = OrderedDict([
            ("a", (0, 2, make_decode_map(Mode))),
            ("b", (2, 2, None)),
        ])
        rv = RegValue(0b1010, spec)
        self.assertIs(rv.a, Mode.FAST)
        self.assertIs(type(rv.b), int)
        self.assertEqual(rv.b, 2)

        # Unencoded value falls back to int
        rv.a = 3
        self.assertIs(type(rv.a), int)
        self.assertEqual(rv.a, 3)

        # Enum members can be assigned
        rv.a = Mode.OFF
        self.assertIs(rv.a, Mode.OFF)
        self.assertEqual(int(rv), 0b1000)
        self.assertListEqual(list(rv), [("a", Mode.OFF), ("b", 2)])
