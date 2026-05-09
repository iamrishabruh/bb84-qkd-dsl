# Intercept-resend eavesdropper on the quantum channel (simulated classically).
# With enough rounds, sifted-bit disagreement tends to rise above a loose threshold.

seed 7
error_threshold 0.12
noise 0.0
eavesdrop on

qubit q1
qubit q2
qubit q3
qubit q4
qubit q5
qubit q6
qubit q7
qubit q8
qubit q9
qubit q10
qubit q11
qubit q12
qubit q13
qubit q14
qubit q15
qubit q16
qubit q17
qubit q18
qubit q19
qubit q20

alice_send q1
alice_send q2
alice_send q3
alice_send q4
alice_send q5
alice_send q6
alice_send q7
alice_send q8
alice_send q9
alice_send q10
alice_send q11
alice_send q12
alice_send q13
alice_send q14
alice_send q15
alice_send q16
alice_send q17
alice_send q18
alice_send q19
alice_send q20

bob_measure q1 rect
bob_measure q2 diag
bob_measure q3 rect
bob_measure q4 diag
bob_measure q5 rect
bob_measure q6 diag
bob_measure q7 rect
bob_measure q8 diag
bob_measure q9 rect
bob_measure q10 diag
bob_measure q11 rect
bob_measure q12 diag
bob_measure q13 rect
bob_measure q14 diag
bob_measure q15 rect
bob_measure q16 diag
bob_measure q17 rect
bob_measure q18 diag
bob_measure q19 rect
bob_measure q20 diag

sift_keys
check_eavesdropping
generate_key k_eve
print k_eve
print stats
