"""Tests for the hand-written lexer."""

import pytest

from bb84dsl.errors import DSLLexError
from bb84dsl.lexer import lex
from bb84dsl.tokens import TokenKind


def test_lex_keywords_and_identifiers():
    src = """
    seed 1
    qubit q1
    alice_send q1
    bob_measure q1 rect
    sift_keys
    """
    toks = lex(src)
    kinds = [t.kind for t in toks[:-1]]  # drop EOF
    assert kinds[:9] == [
        TokenKind.SEED,
        TokenKind.INTEGER,
        TokenKind.QUBIT,
        TokenKind.IDENT,
        TokenKind.ALICE_SEND,
        TokenKind.IDENT,
        TokenKind.BOB_MEASURE,
        TokenKind.IDENT,
        TokenKind.RECT,
    ]
    assert kinds[-1] == TokenKind.SIFT_KEYS


def test_comments_and_whitespace_ignored():
    src = "# leading\nseed 42  # inline\n"
    toks = lex(src)
    assert toks[0].kind == TokenKind.SEED
    assert toks[1].value == 42


def test_float_and_integer():
    toks = lex("noise 0.1 error_threshold 0")
    assert toks[0].kind == TokenKind.NOISE
    assert toks[1].kind == TokenKind.FLOAT
    assert toks[1].value == pytest.approx(0.1)
    assert toks[2].kind == TokenKind.ERROR_THRESHOLD
    assert toks[3].kind == TokenKind.INTEGER
    assert toks[3].value == 0


def test_illegal_character_raises():
    with pytest.raises(DSLLexError):
        lex("qubit q$1")
