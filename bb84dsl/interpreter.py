"""Execute a parsed program against the classical BB84 simulator."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import ast
from .errors import DSLRuntimeError
from .simulator import (
    Round,
    SimulationState,
    alice_prepare,
    apply_intercept_resend,
    bob_outcome_from_resent,
    detect_eavesdropping,
    sift,
    sift_error_rate,
)


@dataclass
class InterpreterResult:
    """Observable outputs after running a program."""

    printed: list[str] = field(default_factory=list)
    keys: dict[str, str] = field(default_factory=dict)
    sift_error_rate: float | None = None
    eavesdrop_detected: bool | None = None


class Interpreter:
    def __init__(
        self,
        state: SimulationState | None = None,
        *,
        override_seed: int | None = None,
    ):
        self.state = state or SimulationState()
        self.override_seed = override_seed

    def run(self, program: ast.Program) -> InterpreterResult:
        out = InterpreterResult()
        if self.override_seed is not None:
            self.state.rng.seed(self.override_seed)
        for stmt in program.statements:
            self._exec(stmt, out)
        out.sift_error_rate = self.state.last_sift_error_rate
        out.eavesdrop_detected = self.state.last_eavesdrop_detected
        out.keys = dict(self.state.keys)
        return out

    def _exec(self, stmt: ast.Statement, out: InterpreterResult) -> None:
        if isinstance(stmt, ast.SeedStmt):
            if self.override_seed is None:
                self.state.rng.seed(stmt.value)
            return
        if isinstance(stmt, ast.NoiseStmt):
            if not 0.0 <= stmt.probability <= 1.0:
                raise DSLRuntimeError("noise probability must be between 0 and 1")
            self.state.noise = stmt.probability
            return
        if isinstance(stmt, ast.ErrorThresholdStmt):
            if not 0.0 <= stmt.value <= 1.0:
                raise DSLRuntimeError("error_threshold must be between 0 and 1")
            self.state.error_threshold = stmt.value
            return
        if isinstance(stmt, ast.EavesdropStmt):
            self.state.eavesdrop_enabled = stmt.enabled
            return
        if isinstance(stmt, ast.QubitDecl):
            if stmt.name in self.state.qubits:
                raise DSLRuntimeError(f"Qubit {stmt.name!r} is already defined")
            self.state.qubits.add(stmt.name)
            return
        if isinstance(stmt, ast.AliceSend):
            self._alice_send(stmt.qubit)
            return
        if isinstance(stmt, ast.BobMeasure):
            self._bob_measure(stmt.qubit, stmt.basis)
            return
        if isinstance(stmt, ast.SiftKeysStmt):
            self._sift_keys()
            return
        if isinstance(stmt, ast.CheckEavesdroppingStmt):
            self._check_eavesdropping()
            return
        if isinstance(stmt, ast.GenerateKey):
            self._generate_key(stmt.name)
            return
        if isinstance(stmt, ast.PrintStmt):
            self._print(stmt.name, out)
            return

    def _alice_send(self, qubit: str) -> None:
        if qubit not in self.state.qubits:
            raise DSLRuntimeError(f"Unknown qubit {qubit!r}")
        bit, basis = alice_prepare(self.state.rng)
        r = Round(
            qubit=qubit,
            alice_bit=bit,
            alice_basis=basis,
            eavesdrop=self.state.eavesdrop_enabled,
        )
        if self.state.eavesdrop_enabled:
            eve_basis, eve_bit, sent_bit, sent_basis = apply_intercept_resend(
                self.state.rng, bit, basis
            )
            r.eve_basis = eve_basis
            r.eve_bit = eve_bit
            r.sent_bit = sent_bit
            r.sent_basis = sent_basis
        else:
            r.sent_bit = bit
            r.sent_basis = basis
        self.state.rounds.append(r)

    def _bob_measure(self, qubit: str, bob_basis: str) -> None:
        i = self.state.measure_index
        if i >= len(self.state.rounds):
            raise DSLRuntimeError("bob_measure has no matching alice_send round")
        r = self.state.rounds[i]
        if r.qubit != qubit:
            raise DSLRuntimeError(
                f"bob_measure order mismatch: expected qubit {r.qubit!r}, got {qubit!r}"
            )
        if r.sent_bit is None or r.sent_basis is None:
            raise DSLRuntimeError("Internal error: round missing resent state")
        r.bob_basis = bob_basis
        r.bob_bit = bob_outcome_from_resent(
            self.state.rng,
            r.sent_bit,
            r.sent_basis,
            bob_basis,
            self.state.noise,
        )
        self.state.measure_index += 1

    def _sift_keys(self) -> None:
        if self.state.measure_index != len(self.state.rounds):
            raise DSLRuntimeError("sift_keys requires one bob_measure per alice_send")
        idxs, bits = sift(self.state.rounds)
        self.state.sifted_indices = idxs
        self.state.shared_key_bits = bits
        rate = sift_error_rate(self.state.rounds, idxs)
        self.state.last_sift_error_rate = rate

    def _check_eavesdropping(self) -> None:
        if self.state.last_sift_error_rate is None:
            raise DSLRuntimeError("check_eavesdropping must run after sift_keys")
        idxs = self.state.sifted_indices
        rate = self.state.last_sift_error_rate
        detected = detect_eavesdropping(rate, self.state.error_threshold) if idxs else False
        self.state.last_eavesdrop_detected = detected

    def _generate_key(self, name: str) -> None:
        if not self.state.shared_key_bits:
            raise DSLRuntimeError("generate_key requires sift_keys with at least one matching basis")
        key = "".join(str(b) for b in self.state.shared_key_bits)
        self.state.keys[name] = key

    def _print(self, name: str, out: InterpreterResult) -> None:
        if name == "stats":
            parts = [
                f"sifted_bits={len(self.state.shared_key_bits)}",
                f"sift_error_rate={self.state.last_sift_error_rate}",
                f"eavesdrop_detected={self.state.last_eavesdrop_detected}",
            ]
            line = " ".join(parts)
            print(line)
            out.printed.append(line)
            return
        if name not in self.state.keys:
            raise DSLRuntimeError(f"Unknown key {name!r}; run generate_key first")
        line = f"{name}={self.state.keys[name]}"
        print(line)
        out.printed.append(line)


def interpret_source(source: str) -> InterpreterResult:
    from .parser import parse_source

    return Interpreter().run(parse_source(source))
