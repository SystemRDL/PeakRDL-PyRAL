from typing import Iterator, Tuple, Dict, Any
from collections.abc import Iterable

# Far more performant to store the spec as a tuple rather than a higher order object
SpecEntry = Tuple[int, int] # (offset, width)

class RegValue(Iterable):
    def __init__(self, value: int, spec: Dict[str, SpecEntry]):
        self._value = value
        self._spec = spec

    def __int__(self) -> int:
        return self._value

    def __getattr__(self, name: str) -> int:
        if name not in self._spec:
            raise AttributeError(f"'{self.__class__.__name__}' object has no field '{name}'")

        offset, width = self._spec[name]
        return (self._value >> offset) & ((1 << width) - 1)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"_value", "_spec"}:
            super().__setattr__(name, value)
            return

        if name not in self._spec:
            raise AttributeError(f"'{self.__class__.__name__}' object has no field '{name}'")

        assert isinstance(value, int)
        offset, width = self._spec[name]
        mask = ((1 << width) - 1) << offset
        self._value = (self._value & ~mask) | ((value << offset) & mask)

    def __iter__(self) -> Iterator[Tuple[str, int]]:
        items = [(name, getattr(self, name)) for name in self._spec.keys()]
        return iter(items)
