"""Hand-written lexer for the BB84 educational DSL."""

from __future__ import annotations

from .errors import DSLLexError
from .tokens import Token, TokenKind

_KEYWORDS: dict[str, TokenKind] = {
    "seed": TokenKind.SEED,
    "noise": TokenKind.NOISE,
    "error_threshold": TokenKind.ERROR_THRESHOLD,
    "eavesdrop": TokenKind.EAVESDROP,
    "on": TokenKind.ON,
    "off": TokenKind.OFF,
    "qubit": TokenKind.QUBIT,
    "alice_send": TokenKind.ALICE_SEND,
    "bob_measure": TokenKind.BOB_MEASURE,
    "rect": TokenKind.RECT,
    "diag": TokenKind.DIAG,
    "sift_keys": TokenKind.SIFT_KEYS,
    "check_eavesdropping": TokenKind.CHECK_EAVESDROPPING,
    "generate_key": TokenKind.GENERATE_KEY,
    "print": TokenKind.PRINT,
}


class Lexer:
    def __init__(self, text: str):
        self._text = text
        self._n = len(text)
        self._i = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.kind == TokenKind.EOF:
                break
        return tokens

    def _peek(self) -> str | None:
        return self._text[self._i] if self._i < self._n else None

    def _advance(self) -> None:
        if self._i < self._n and self._text[self._i] == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self._i += 1

    def _skip_ws_and_comments(self) -> None:
        while self._i < self._n:
            c = self._text[self._i]
            if c in " \t\r":
                self._advance()
            elif c == "\n":
                self._advance()
            elif c == "#":
                while self._i < self._n and self._peek() != "\n":
                    self._advance()
            else:
                break

    def _next_token(self) -> Token:
        self._skip_ws_and_comments()
        if self._i >= self._n:
            return Token(TokenKind.EOF, None, self.line, self.col)

        start_line, start_col = self.line, self.col
        c = self._peek()
        assert c is not None

        if c.isdigit():
            return self._number(start_line, start_col)

        if c.isalpha() or c == "_":
            return self._ident_or_kw(start_line, start_col)

        raise DSLLexError(f"Unexpected character {c!r}", line=start_line, col=start_col)

    def _number(self, start_line: int, start_col: int) -> Token:
        j = self._i
        while j < self._n and self._text[j].isdigit():
            j += 1
        if j < self._n and self._text[j] == ".":
            j += 1
            if j >= self._n or not self._text[j].isdigit():
                raise DSLLexError("Malformed floating-point literal", line=start_line, col=start_col)
            while j < self._n and self._text[j].isdigit():
                j += 1
            raw = self._text[self._i : j]
            self._i = j
            self.col += len(raw)
            return Token(TokenKind.FLOAT, float(raw), start_line, start_col)

        raw = self._text[self._i : j]
        self._i = j
        self.col += len(raw)
        return Token(TokenKind.INTEGER, int(raw), start_line, start_col)

    def _ident_or_kw(self, start_line: int, start_col: int) -> Token:
        j = self._i
        while j < self._n and (self._text[j].isalnum() or self._text[j] == "_"):
            j += 1
        raw = self._text[self._i : j]
        self._i = j
        self.col += len(raw)
        kind = _KEYWORDS.get(raw, TokenKind.IDENT)
        return Token(kind, raw if kind == TokenKind.IDENT else None, start_line, start_col)


def lex(text: str) -> list[Token]:
    return Lexer(text).tokenize()
