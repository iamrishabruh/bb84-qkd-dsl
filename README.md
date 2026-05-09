# BB84 DSL

A small **programming-languages style** project: a domain-specific language for **classically simulating** the BB84 quantum key distribution protocol at a high level. The point of the repo is the **language pipeline** (lexer → parser → AST → interpreter) plus **tests**, **examples**, and honest documentation about what is modeled versus simplified.

This is **not** quantum hardware firmware, a circuit simulator, or a production QKD stack. Treat it as a **pedagogical** tool for reasoning about basis choice, sifting, noise, and intercept–resend eavesdropping in a toy statistical model.

## What this DSL is for

- Describe a batch of BB84-style rounds: Alice prepares random bits in random bases; Bob measures in bases you specify in the program.
- Sift on matching bases, estimate disagreement on those rounds, and raise a simple **eavesdropping alarm** when the sift error rate crosses a threshold.
- Experiment with **classical noise** on outcomes as a coarse stand-in for device error.

The implementation keeps quantum mechanics implicit: measurement statistics are encoded directly in the simulator, which keeps the interpreter small and the semantics easy to read in Python.

## Example program

```text
seed 4242
error_threshold 0.15
noise 0.0
eavesdrop off

qubit q1
alice_send q1
bob_measure q1 rect

sift_keys
check_eavesdropping
generate_key k1
print k1
print stats
```

See also `examples/basic_bb84.dsl`, `examples/eavesdropping.dsl`, and `examples/noise_simulation.dsl`.

## Language features

- **Configuration**: `seed`, `noise`, `error_threshold`, `eavesdrop on|off`
- **Protocol steps**: `qubit`, `alice_send`, `bob_measure … rect|diag`
- **Post-processing**: `sift_keys`, `check_eavesdropping`, `generate_key`, `print`
- **Front-end**: hand-written lexer, recursive-descent parser, explicit AST dataclasses, structured errors (`DSLLexError`, `DSLSyntaxError`, `DSLRuntimeError`)

Full syntax is written out in EBNF in [`docs/grammar.md`](docs/grammar.md).

## Grammar

The formal grammar lives in [`docs/grammar.md`](docs/grammar.md). The parser accepts the statement-oriented language sketched above; static well-formedness rules (for example, matching `alice_send` / `bob_measure` ordering) are enforced by the interpreter.

## Interpreter architecture

1. **`bb84dsl/lexer.py`** scans the source into `Token` values (line/column preserved for errors).
2. **`bb84dsl/parser.py`** builds a `Program` of immutable AST nodes (`bb84dsl/ast.py`).
3. **`bb84dsl/interpreter.py`** walks the AST and updates `SimulationState` (`bb84dsl/simulator.py`): rounds, sifting, key material, and the last error-rate / detection flags.
4. **`bb84dsl/errors.py`** centralizes user-facing exceptions.

There are **no third-party runtime dependencies**; the standard library is enough for the language and simulation loop.

## Running examples

Install in editable mode (optional, for local development):

```bash
pip install -e ".[dev]"
```

Run a program:

```bash
python -m bb84dsl examples/basic_bb84.dsl
```

Override the program’s `seed` statements from the CLI (file seeds are ignored when this flag is present):

```bash
python -m bb84dsl --seed 999 examples/basic_bb84.dsl
```

## Testing

```bash
pytest
```

The suite covers tokenization, parsing (including invalid programs), BB84 sifting and intercept–resend statistics in `bb84dsl/simulator.py`, interpreter integration, and deterministic behavior under a fixed seed.

## Simulation assumptions and limitations

A dedicated discussion lives in [`docs/simulation.md`](docs/simulation.md). In short: the model is **classical**, **round-local**, and **not** a substitute for a full quantum formalism or security analysis—see the doc for the explicit simplifications (no joint quantum state, coarse noise, no privacy amplification, and so on).

## Future work

- Richer surface syntax (blocks, procedures, or explicit `for` loops over rounds) without hiding the pedagogical semantics.
- Additional QKD toy models (B92, decoy-state style classical abstractions) sharing the same pipeline.
- Optional visualization of basis matches / error rates per round.
- Stricter separation of “language semantics” and “physics story” via pluggable simulation backends—still explicitly non-hardware.

## License

MIT — see [`LICENSE`](LICENSE).
