"""Classical simulation core for BB84-style rounds (educational model)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Round:
    qubit: str
    alice_bit: int
    alice_basis: str  # "rect" | "diag"
    eavesdrop: bool = False
    eve_basis: str | None = None
    eve_bit: int | None = None
    sent_bit: int | None = None  # bit encoded for Bob after optional Eve
    sent_basis: str | None = None
    bob_basis: str | None = None
    bob_bit: int | None = None


@dataclass
class SimulationState:
    """Mutable state used while executing a program."""

    rng: random.Random = field(default_factory=random.Random)
    noise: float = 0.0
    error_threshold: float = 0.11
    eavesdrop_enabled: bool = False
    qubits: set[str] = field(default_factory=set)
    rounds: list[Round] = field(default_factory=list)
    alice_send_queue: list[str] = field(default_factory=list)
    measure_index: int = 0

    # After sift_keys
    sifted_indices: list[int] = field(default_factory=list)
    shared_key_bits: list[int] = field(default_factory=list)
    last_sift_error_rate: float | None = None
    last_eavesdrop_detected: bool | None = None
    keys: dict[str, str] = field(default_factory=dict)


def _flip_with_noise(rng: random.Random, bit: int, noise: float) -> int:
    if noise <= 0.0:
        return bit
    return 1 - bit if rng.random() < noise else bit


def alice_prepare(rng: random.Random) -> tuple[int, str]:
    bit = rng.randint(0, 1)
    basis = "rect" if rng.random() < 0.5 else "diag"
    return bit, basis


def bob_outcome(
    rng: random.Random,
    alice_bit: int,
    alice_basis: str,
    bob_basis: str,
    noise: float,
) -> int:
    """Ideal BB84 measurement statistics: matching basis reveals the bit (with optional noise)."""
    if alice_basis == bob_basis:
        return _flip_with_noise(rng, alice_bit, noise)
    return rng.randint(0, 1)


def apply_intercept_resend(
    rng: random.Random,
    alice_bit: int,
    alice_basis: str,
) -> tuple[str, int, int, str]:
    """Eve measures in a random basis and resends the measured bit in that basis.

    Returns ``(eve_basis, eve_bit, sent_bit, sent_basis)`` where the resent
    state is ``(sent_bit, sent_basis) == (eve_bit, eve_basis)``.
    """
    eve_basis = "rect" if rng.random() < 0.5 else "diag"
    if eve_basis == alice_basis:
        eve_bit = alice_bit
    else:
        eve_bit = rng.randint(0, 1)
    return eve_basis, eve_bit, eve_bit, eve_basis


def bob_outcome_from_resent(
    rng: random.Random,
    sent_bit: int,
    sent_basis: str,
    bob_basis: str,
    noise: float,
) -> int:
    return bob_outcome(rng, sent_bit, sent_basis, bob_basis, noise)


def sift(rounds: list[Round]) -> tuple[list[int], list[int]]:
    """Return (indices where bases match, alice bits at those indices)."""
    idxs: list[int] = []
    bits: list[int] = []
    for i, r in enumerate(rounds):
        if r.bob_basis is None or r.bob_bit is None:
            continue
        if r.alice_basis == r.bob_basis:
            idxs.append(i)
            bits.append(r.alice_bit)
    return idxs, bits


def sift_error_rate(rounds: list[Round], sifted_indices: list[int]) -> float:
    if not sifted_indices:
        return 0.0
    mismatches = 0
    for i in sifted_indices:
        r = rounds[i]
        assert r.bob_bit is not None
        if r.alice_bit != r.bob_bit:
            mismatches += 1
    return mismatches / len(sifted_indices)


def detect_eavesdropping(error_rate: float, threshold: float) -> bool:
    return error_rate > threshold
