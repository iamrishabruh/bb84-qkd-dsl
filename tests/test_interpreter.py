"""End-to-end interpreter tests."""

import io
import sys

import pytest

from bb84dsl.interpreter import Interpreter, interpret_source
from bb84dsl.parser import parse_source


def _program(*, eve: bool) -> str:
    eave = "eavesdrop on" if eve else "eavesdrop off"
    return f"""
    seed 12345
    error_threshold 0.11
    noise 0.0
    {eave}

    qubit q1
    qubit q2
    qubit q3
    qubit q4

    alice_send q1
    alice_send q2
    alice_send q3
    alice_send q4

    bob_measure q1 rect
    bob_measure q2 diag
    bob_measure q3 rect
    bob_measure q4 diag

    sift_keys
    check_eavesdropping
    generate_key k1
    print stats
    """


def test_deterministic_same_seed_same_stats():
    p = parse_source(_program(eve=False))
    a = Interpreter().run(p)
    b = Interpreter().run(p)
    assert a.sift_error_rate == b.sift_error_rate
    assert a.eavesdrop_detected == b.eavesdrop_detected
    assert a.keys == b.keys


def test_interpret_source_convenience():
    lines = ["seed 1", "qubit q1"]
    for _ in range(12):
        lines.append("alice_send q1")
    for _ in range(12):
        lines.append("bob_measure q1 rect")
    lines += [
        "sift_keys",
        "check_eavesdropping",
        "generate_key k",
    ]
    out = interpret_source("\n".join(lines))
    assert "k" in out.keys


def test_override_seed_ignores_file_seed():
    def make_src() -> str:
        lines = ["seed 1", "qubit q1"]
        for _ in range(16):
            lines.append("alice_send q1")
        for _ in range(16):
            lines.append("bob_measure q1 rect")
        lines += ["sift_keys", "check_eavesdropping", "generate_key k"]
        return "\n".join(lines)

    src = make_src()
    a = interpret_source(src)
    p = parse_source(src)
    b = Interpreter(override_seed=999).run(p)
    assert a.keys["k"] != b.keys["k"]


def test_print_key_captured(monkeypatch):
    prog = parse_source(
        """
        seed 10
        qubit q1
        alice_send q1
        bob_measure q1 rect
        sift_keys
        check_eavesdropping
        generate_key kout
        print kout
        """
    )
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    out = Interpreter().run(prog)
    assert out.printed and "kout=" in out.printed[-1]
