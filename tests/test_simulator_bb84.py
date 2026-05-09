"""Unit tests for BB84 sifting, noise, and eavesdropping statistics."""

import random

import pytest

from bb84dsl.simulator import (
    Round,
    alice_prepare,
    apply_intercept_resend,
    bob_outcome,
    bob_outcome_from_resent,
    detect_eavesdropping,
    sift,
    sift_error_rate,
)


def test_sift_keeps_only_matching_bases():
    rounds = [
        Round("q1", 1, "rect", sent_bit=1, sent_basis="rect", bob_basis="rect", bob_bit=1),
        Round("q2", 0, "diag", sent_bit=0, sent_basis="diag", bob_basis="rect", bob_bit=1),
    ]
    idxs, bits = sift(rounds)
    assert idxs == [0]
    assert bits == [1]


def test_sift_error_rate_on_matching_bases():
    rounds = [
        Round("q1", 1, "rect", sent_bit=1, sent_basis="rect", bob_basis="rect", bob_bit=0),
        Round("q2", 0, "rect", sent_bit=0, sent_basis="rect", bob_basis="rect", bob_bit=0),
    ]
    idxs, _ = sift(rounds)
    assert sift_error_rate(rounds, idxs) == pytest.approx(0.5)


def test_detect_eavesdropping_threshold():
    assert detect_eavesdropping(0.5, 0.11) is True
    assert detect_eavesdropping(0.05, 0.11) is False


def test_deterministic_bob_outcome_with_seed():
    rng = random.Random(123)
    assert bob_outcome(rng, 1, "rect", "rect", 0.0) == 1
    rng = random.Random(123)
    assert bob_outcome(rng, 1, "rect", "diag", 0.0) == 0


def test_eavesdrop_increases_typical_sift_errors():
    """Across many rounds, intercept–resend yields higher sift errors than honest channel."""

    def run_honest(rng: random.Random, n: int) -> float:
        rounds: list[Round] = []
        for _ in range(n):
            bit, basis = alice_prepare(rng)
            bob_basis = "rect" if rng.random() < 0.5 else "diag"
            sent_bit, sent_basis = bit, basis
            bob_bit = bob_outcome_from_resent(rng, sent_bit, sent_basis, bob_basis, 0.0)
            rounds.append(
                Round(
                    "q",
                    bit,
                    basis,
                    sent_bit=sent_bit,
                    sent_basis=sent_basis,
                    bob_basis=bob_basis,
                    bob_bit=bob_bit,
                )
            )
        idxs, _ = sift(rounds)
        return sift_error_rate(rounds, idxs)

    def run_eve(rng: random.Random, n: int) -> float:
        rounds = []
        for _ in range(n):
            bit, basis = alice_prepare(rng)
            _eb, _ev, sent_bit, sent_basis = apply_intercept_resend(rng, bit, basis)
            bob_basis = "rect" if rng.random() < 0.5 else "diag"
            bob_bit = bob_outcome_from_resent(rng, sent_bit, sent_basis, bob_basis, 0.0)
            rounds.append(
                Round(
                    "q",
                    bit,
                    basis,
                    sent_bit=sent_bit,
                    sent_basis=sent_basis,
                    bob_basis=bob_basis,
                    bob_bit=bob_bit,
                )
            )
        idxs, _ = sift(rounds)
        return sift_error_rate(rounds, idxs)

    rng_h = random.Random(999)
    rng_e = random.Random(999)
    h = run_honest(rng_h, 5_000)
    e = run_eve(rng_e, 5_000)
    assert e > h
