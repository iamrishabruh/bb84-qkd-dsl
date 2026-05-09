"""Token kinds and token values produced by the lexer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    EOF = auto()

    # Literals
    IDENT = auto()
    INTEGER = auto()
    FLOAT = auto()

    # Keywords
    SEED = auto()
    NOISE = auto()
    ERROR_THRESHOLD = auto()
    EAVESDROP = auto()
    ON = auto()
    OFF = auto()
    QUBIT = auto()
    ALICE_SEND = auto()
    BOB_MEASURE = auto()
    RECT = auto()
    DIAG = auto()
    SIFT_KEYS = auto()
    CHECK_EAVESDROPPING = auto()
    GENERATE_KEY = auto()
    PRINT = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str | int | float | None
    line: int
    col: int
