"""BB84 educational domain-specific language: lexer, parser, AST, and interpreter."""

from .errors import BB84DSLError, DSLLexError, DSLRuntimeError, DSLSyntaxError
from .interpreter import Interpreter, InterpreterResult, interpret_source
from .lexer import lex
from .parser import parse_source, parse_tokens
from .simulator import (
    Round,
    SimulationState,
    alice_prepare,
    apply_intercept_resend,
    bob_outcome,
    bob_outcome_from_resent,
    detect_eavesdropping,
    sift,
    sift_error_rate,
)

__all__ = [
    "BB84DSLError",
    "DSLLexError",
    "DSLSyntaxError",
    "DSLRuntimeError",
    "Interpreter",
    "InterpreterResult",
    "Round",
    "SimulationState",
    "alice_prepare",
    "apply_intercept_resend",
    "bob_outcome",
    "bob_outcome_from_resent",
    "detect_eavesdropping",
    "interpret_source",
    "lex",
    "parse_source",
    "parse_tokens",
    "sift",
    "sift_error_rate",
]
