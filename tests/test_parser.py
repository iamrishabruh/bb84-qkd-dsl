"""Parser tests: valid programs become well-formed ASTs."""

from bb84dsl.ast import (
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
)
from bb84dsl.parser import parse_source


def test_parse_minimal_program():
    src = """
    seed 1
    noise 0
    error_threshold 0.11
    eavesdrop off
    qubit q1
    alice_send q1
    bob_measure q1 diag
    sift_keys
    check_eavesdropping
    generate_key k1
    print k1
    """
    prog = parse_source(src)
    assert isinstance(prog, Program)
    assert [type(s) for s in prog.statements] == [
        SeedStmt,
        NoiseStmt,
        ErrorThresholdStmt,
        EavesdropStmt,
        QubitDecl,
        AliceSend,
        BobMeasure,
        SiftKeysStmt,
        CheckEavesdroppingStmt,
        GenerateKey,
        PrintStmt,
    ]
    bob = prog.statements[6]
    assert isinstance(bob, BobMeasure)
    assert bob.basis == "diag"


def test_eavesdrop_on_off():
    p = parse_source("eavesdrop on\neavesdrop off\n")
    assert isinstance(p.statements[0], EavesdropStmt)
    assert p.statements[0].enabled is True
    assert p.statements[1].enabled is False
