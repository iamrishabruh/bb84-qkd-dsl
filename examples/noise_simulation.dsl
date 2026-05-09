# Classical bit-flip noise on matching-basis outcomes (pedagogical stand-in for hardware errors).

seed 100
error_threshold 0.4
noise 0.25
eavesdrop off

qubit q1
qubit q2
qubit q3
qubit q4
qubit q5
qubit q6
qubit q7
qubit q8

alice_send q1
alice_send q2
alice_send q3
alice_send q4
alice_send q5
alice_send q6
alice_send q7
alice_send q8

bob_measure q1 rect
bob_measure q2 rect
bob_measure q3 rect
bob_measure q4 rect
bob_measure q5 rect
bob_measure q6 rect
bob_measure q7 rect
bob_measure q8 rect

sift_keys
check_eavesdropping
generate_key k_noisy
print k_noisy
print stats
