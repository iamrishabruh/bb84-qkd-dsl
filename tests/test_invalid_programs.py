"""Parser and runtime rejection of invalid programs."""

import pytest

from bb84dsl.errors import DSLRuntimeError, DSLSyntaxError
from bb84dsl.interpreter import Interpreter
from bb84dsl.lexer import lex
from bb84dsl.parser import parse_source, parse_tokens


def test_parser_requires_eavesdrop_mode():
    with pytest.raises(DSLSyntaxError):
        parse_source("eavesdrop")


def test_parser_requires_bob_basis():
    with pytest.raises(DSLSyntaxError):
        parse_source("qubit q1\nalice_send q1\nbob_measure q1\n")


def test_parser_rejects_unknown_statement():
    with pytest.raises(DSLSyntaxError):
        parse_tokens(lex("unknown_op x"))


def test_runtime_duplicate_qubit():
    prog = parse_source("qubit q1\nqubit q1\n")
    with pytest.raises(DSLRuntimeError):
        Interpreter().run(prog)


def test_runtime_bob_measure_without_alice():
    prog = parse_source("qubit q1\nbob_measure q1 rect\n")
    with pytest.raises(DSLRuntimeError):
        Interpreter().run(prog)


def test_runtime_mismatched_qubit_order():
    prog = parse_source(
        """
        qubit q1
        qubit q2
        alice_send q1
        alice_send q2
        bob_measure q2 rect
        bob_measure q1 rect
        """
    )
    with pytest.raises(DSLRuntimeError):
        Interpreter().run(prog)


def test_runtime_sift_without_full_measures():
    prog = parse_source(
        """
        qubit q1
        alice_send q1
        sift_keys
        """
    )
    with pytest.raises(DSLRuntimeError):
        Interpreter().run(prog)
