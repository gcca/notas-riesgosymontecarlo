from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import singledispatchmethod
from math import fabs
from typing import Callable, Dict, List, Optional, Self, Type, Union, cast

import pandas as pd

__all__ = ("AsInts", "Case", "Cases", "pd")


def AsInts(l: List[float]) -> List[int]:
    return [round(v) for v in l]


@dataclass(frozen=True)
class Ratio:

    _value: Decimal

    __slots__ = ("_value",)

    def __add__(self, other: Union[Ratio, float, int]) -> Ratio:
        if isinstance(other, Ratio):
            return Ratio.Make(self._value + other._value)
        raise TypeError("other is not a Ratio on add")

    def __mul__(self, other: Union[Ratio, float, int]) -> Ratio:
        if isinstance(other, Ratio):
            return Ratio.Make(self._value * other._value)
        raise TypeError("other is not a Ratio on mul")

    def __float__(self) -> float:
        return float(self._value)

    def __str__(self) -> str:
        return f"{self._value*100:.2f}%"

    @singledispatchmethod
    @staticmethod
    def Make(value: Union[float, Decimal]) -> Ratio:
        raise NotImplementedError("")

    @Make.register
    @classmethod
    def MakeInt(cls, value: int):
        cls._Validate(value, int, abs)
        return Ratio(Decimal(value))

    @Make.register
    @classmethod
    def MakeFloat(cls, value: float):
        cls._Validate(value, float, fabs)
        return Ratio(Decimal(value))

    @Make.register
    @classmethod
    def MakeDecimal(cls, value: Decimal):
        cls._Validate(value, Decimal, abs)
        return Ratio(value)

    @staticmethod
    def _Validate[T](value: T, kind: Type[T], xabs: Callable[[T], T]) -> None:
        if not (0 <= cast(int, xabs(value)) <= 1):
            raise ValueError(
                f"Ratio must be between {kind.__name__} inclusived zero and one"
            )


@dataclass(frozen=True)
class Level:

    _parent: float
    _ratio: Ratio
    _offset: Ratio
    _length: int
    _boot: float

    __slots__ = ("_parent", "_ratio", "_offset", "_length", "_boot")

    def __str__(self) -> str:
        return f"{self._offset}"

    def Throw(self) -> List[float]:
        return _Throw(self._boot, self._ratio, self._length)

    @staticmethod
    def Make(parent: float, ratio: Ratio, offset: Ratio, length: int) -> Level:
        return Level(
            parent, ratio, offset, length, parent * (float(offset) + 1)
        )


@dataclass
class Case:

    _base: float
    _boot: float
    _ratio: Ratio
    _length: int
    _levels: List[Level]
    _title: str

    __slots__ = ("_base", "_boot", "_ratio", "_length", "_levels", "_title")

    def Relength(self, length: int) -> Self:
        self._length = length
        return self

    def Leveling(self, *values: float) -> Self:
        self._levels = [
            Level.Make(
                self._boot, self._ratio, Ratio.Make(value), self._length
            )
            for value in values
        ]
        return self

    @property
    def AsDF(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "base": _Throw(self._boot, self._ratio, self._length),
                **self._GenerateLeveSeries(),
            }
        )

    def _GenerateLeveSeries(self) -> Dict[str, List[float]]:
        return {f"{level}": level.Throw() for level in self._levels}

    @staticmethod
    def Make(base: float, boot: float, ratio: float, title: str = "") -> Case:
        return Case(base, boot, Ratio.Make(ratio), 0, [], title)


@dataclass
class Cases:

    _cases: List[Case]

    __slots__ = ("_cases",)

    def Add(self, title: str, base: float, boot: float, ratio: float) -> Self:
        self._cases.append(Case.Make(base, boot, ratio, title))
        return self

    @staticmethod
    def Make(cases: Optional[List[Case]] = None) -> Cases:
        if cases is None:
            cases = []
        return Cases(cases)


def _Throw(boot: float, ratio: Ratio, length: int) -> List[float]:
    return [boot * (float(ratio) + 1) ** i for i in range(length)]
