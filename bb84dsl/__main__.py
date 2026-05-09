"""CLI entrypoint: ``python -m bb84dsl <script.dsl>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import BB84DSLError
from .interpreter import Interpreter
from .lexer import lex
from .parser import parse_tokens


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Run a BB84 educational DSL program (classical simulation).",
    )
    p.add_argument("script", type=Path, help="Path to a .dsl file")
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override seed statement in the program (applied before execution)",
    )
    args = p.parse_args(argv)

    path: Path = args.script
    if not path.is_file():
        print(f"bb84dsl: file not found: {path}", file=sys.stderr)
        return 2

    source = path.read_text(encoding="utf-8")
    try:
        program = parse_tokens(lex(source))
        interp = Interpreter(override_seed=args.seed)
        interp.run(program)
    except BB84DSLError as e:
        print(f"bb84dsl: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
