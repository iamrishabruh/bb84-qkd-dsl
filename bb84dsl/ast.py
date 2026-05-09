"""Abstract syntax tree for the BB84 educational DSL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class SeedStmt:
    value: int


@dataclass(frozen=True)
class NoiseStmt:
    probability: float


@dataclass(frozen=True)
class ErrorThresholdStmt:
    value: float


@dataclass(frozen=True)
class EavesdropStmt:
    enabled: bool


@dataclass(frozen=True)
class QubitDecl:
    name: str


@dataclass(frozen=True)
class AliceSend:
    qubit: str


@dataclass(frozen=True)
class BobMeasure:
    qubit: str
    basis: str  # "rect" | "diag"


@dataclass(frozen=True)
class SiftKeysStmt:
    pass


@dataclass(frozen=True)
class CheckEavesdroppingStmt:
    pass


@dataclass(frozen=True)
class GenerateKey:
    name: str


@dataclass(frozen=True)
class PrintStmt:
    name: str


@dataclass(frozen=True)
class Program:
    statements: list[Statement]


Statement = Union[
    SeedStmt,
    NoiseStmt,
    ErrorThresholdStmt,
    EavesdropStmt,
    QubitDecl,
    AliceSend,
    BobMeasure,
    SiftKeysStmt,
    CheckEavesdroppingStmt,
    GenerateKey,
    PrintStmt,
]
