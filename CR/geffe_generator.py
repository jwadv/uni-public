# =====================================================================
# GEFFE GENERATOR: ENCRYPTION, DECRYPTION AND CORRELATION ATTACK
# =====================================================================

import random

def LFSR(state, taps, length):
    current_state = list(state)
    sequence = []
    for _ in range(length):
        # XOR tramite somma mod 2 dei taps
        next_bit = sum(current_state[tap] for tap in taps) % 2
        sequence.append(current_state[0])
        current_state = current_state[1:] + [next_bit] # shift a sx e push del bit generato
    return sequence









