# Basic BB84-style run: Alice prepares random bits/bases, Bob measures in declared bases.
# This is a classical statistical model for teaching, not a quantum device backend.

seed 4242
error_threshold 0.15
noise 0.0
eavesdrop off

qubit q1
qubit q2
qubit q3
qubit q4
qubit q5

alice_send q1
alice_send q2
alice_send q3
alice_send q4
alice_send q5

bob_measure q1 rect
bob_measure q2 diag
bob_measure q3 rect
bob_measure q4 diag
bob_measure q5 rect

sift_keys
check_eavesdropping
generate_key k1
print k1
print stats
