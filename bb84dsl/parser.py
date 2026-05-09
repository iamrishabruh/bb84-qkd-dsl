"""Recursive-descent parser: token list -> AST."""

from __future__ import annotations

from .ast import (
    AliceSend,
    BobMeasure,
    CheckEavesdroppingStmt,
    EavesdropStmt,
    ErrorThresholdStmt,
    GenerateKey,
    NoiseStmt,
    PrintStmt,
    Program,
    QubitDecl,
    SeedStmt,
    SiftKeysStmt,
    Statement,
)
from .errors import DSLSyntaxError
from .tokens import Token, TokenKind


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._i = 0

    def parse(self) -> Program:
        stmts: list[Statement] = []
        while not self._at_end():
            stmts.append(self._statement())
        return Program(stmts)

    def _at_end(self) -> bool:
        return self._peek().kind == TokenKind.EOF

    def _peek(self) -> Token:
        return self._tokens[self._i]

    def _advance(self) -> Token:
        t = self._peek()
        if t.kind != TokenKind.EOF:
            self._i += 1
        return t

    def _expect(self, kind: TokenKind, what: str) -> Token:
        t = self._peek()
        if t.kind != kind:
            raise DSLSyntaxError(f"Expected {what}, got {t.kind.name}", line=t.line, col=t.col)
        return self._advance()

    def _statement(self) -> Statement:
        t = self._peek()
        if t.kind == TokenKind.SEED:
            self._advance()
            v = self._expect(TokenKind.INTEGER, "integer seed")
            assert isinstance(v.value, int)
            return SeedStmt(v.value)
        if t.kind == TokenKind.NOISE:
            self._advance()
            return NoiseStmt(self._expect_probability("noise probability"))
        if t.kind == TokenKind.ERROR_THRESHOLD:
            self._advance()
            return ErrorThresholdStmt(self._expect_probability("error threshold"))
        if t.kind == TokenKind.EAVESDROP:
            self._advance()
            n = self._peek()
            if n.kind == TokenKind.ON:
                self._advance()
                return EavesdropStmt(True)
            if n.kind == TokenKind.OFF:
                self._advance()
                return EavesdropStmt(False)
            raise DSLSyntaxError(
                "Expected 'on' or 'off' after 'eavesdrop'", line=n.line, col=n.col
            )
        if t.kind == TokenKind.QUBIT:
            self._advance()
            name = self._expect_ident()
            return QubitDecl(name)
        if t.kind == TokenKind.ALICE_SEND:
            self._advance()
            name = self._expect_ident()
            return AliceSend(name)
        if t.kind == TokenKind.BOB_MEASURE:
            self._advance()
            q = self._expect_ident()
            basis_tok = self._peek()
            if basis_tok.kind not in (TokenKind.RECT, TokenKind.DIAG):
                raise DSLSyntaxError(
                    "Expected basis 'rect' or 'diag'", line=basis_tok.line, col=basis_tok.col
                )
            self._advance()
            basis = "rect" if basis_tok.kind == TokenKind.RECT else "diag"
            return BobMeasure(q, basis)
        if t.kind == TokenKind.SIFT_KEYS:
            self._advance()
            return SiftKeysStmt()
        if t.kind == TokenKind.CHECK_EAVESDROPPING:
            self._advance()
            return CheckEavesdroppingStmt()
        if t.kind == TokenKind.GENERATE_KEY:
            self._advance()
            name = self._expect_ident()
            return GenerateKey(name)
        if t.kind == TokenKind.PRINT:
            self._advance()
            name = self._expect_ident()
            return PrintStmt(name)

        raise DSLSyntaxError(f"Unexpected token {t.kind.name}", line=t.line, col=t.col)

    def _expect_ident(self) -> str:
        t = self._expect(TokenKind.IDENT, "identifier")
        assert t.value is not None
        return str(t.value)

    def _expect_probability(self, what: str) -> float:
        t = self._peek()
        if t.kind == TokenKind.FLOAT:
            self._advance()
            assert isinstance(t.value, float)
            return t.value
        if t.kind == TokenKind.INTEGER:
            self._advance()
            assert isinstance(t.value, int)
            return float(t.value)
        raise DSLSyntaxError(f"Expected number for {what}", line=t.line, col=t.col)


def parse_tokens(tokens: list[Token]) -> Program:
    return Parser(tokens).parse()


def parse_source(source: str) -> Program:
    from .lexer import lex

    return parse_tokens(lex(source))
