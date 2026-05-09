"""Structured errors for the BB84 DSL front-end and runtime."""


class BB84DSLError(Exception):
    """Base class for user-facing DSL errors."""

    def __init__(self, message: str, *, line: int | None = None, col: int | None = None):
        self.message = message
        self.line = line
        self.col = col
        loc = ""
        if line is not None:
            loc = f"line {line}"
            if col is not None:
                loc += f", column {col}"
            loc = f" ({loc})"
        super().__init__(f"{message}{loc}")


class DSLLexError(BB84DSLError):
    """Invalid token or unexpected character."""


class DSLSyntaxError(BB84DSLError):
    """Parse error."""


class DSLRuntimeError(BB84DSLError):
    """Well-formed program that cannot be executed (e.g. undefined qubit)."""
