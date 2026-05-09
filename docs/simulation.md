# What is simulated, and what is simplified

This repository is an **educational, classical statistical model** of BB84-style quantum key distribution. It is **not** a quantum hardware control stack, a full density-matrix simulator, or a production cryptography toolkit.

## Simulated behavior

- **Random preparation**: Alice draws an independent random bit and a random basis (`rect` or `diag`) for each `alice_send` using the configured pseudo-random generator.
- **Measurement statistics**: When Bob’s measurement basis matches the basis of the state Alice intended, Bob’s outcome follows Alice’s bit, subject to optional classical **noise** (a stand-in for device error). When the bases differ, Bob’s outcome is an unbiased random bit.
- **Sifting**: After all rounds complete, the interpreter keeps rounds where Alice’s and Bob’s bases match. The sifted key material is the sequence of Alice’s bits on those rounds (the usual textbook description of the raw key after basis reconciliation).
- **Intercept–resend eavesdropping**: With `eavesdrop on`, a classical Eve measures in a random basis and resends the observed bit in that basis before Bob measures. This increases the chance of disagreement on sifted rounds compared to the honest channel.
- **Eavesdropping alarm**: After sifting, the interpreter compares Alice’s bits to Bob’s bits on sifted rounds. The **sift error rate** is the fraction of mismatches. If it exceeds `error_threshold`, `check_eavesdropping` records that an eavesdropper is **detected** (a pedagogical alarm, not a formal security proof).

## Simplifications and limitations

- **No quantum state evolution**: There is no Hilbert space, no entanglement, and no decoherence model beyond the optional classical noise knob.
- **Single-round qubits**: Each `alice_send` is one independent round. Qubit names are labels for ordering and pairing with `bob_measure`, not registers in a joint circuit.
- **Noise model**: `noise` is a classical bit-flip probability applied only when Bob’s basis matches the resent state’s basis. It does not model loss, dark counts, or calibration drift.
- **Security claims**: The DSL helps **illustrate** why mismatches rise under intercept–resend. It does **not** implement privacy amplification, authentication, finite-size statistics, or side-channel analysis.

For a programming-languages perspective, the valuable artifact is the **pipeline** (lex → parse → AST → interpreter) and the **explicit separation** between language semantics and this simulation story.
