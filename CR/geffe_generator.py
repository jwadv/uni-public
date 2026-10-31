import random

t1 = [0,1]
t2 = [0,2]
t3 = [0,1]
# per semplicità li ho fissati... (da modificare in un secondo momento)

def lfsr(state, taps, length):
    current_state = list(state)
    sequence = []
    for _ in range(length):
        # XOR tramite somma mod 2 dei taps
        next_bit = sum(current_state[tap] for tap in taps) % 2
        sequence.append(current_state[0])
        current_state = current_state[1:] + [next_bit] # shift a sx e push del bit generato
    return sequence

def geffe(s1, s2, s3, lenght):
    """Costruzione della keystream"""
    z1 = lfsr(s1, t1, lenght)
    z2 = lfsr(s2, t2, lenght)
    z3 = lfsr(s3, t3, lenght)
    return [(z1[i] & z2[i]) ^ ((1 - z1[i]) & z3[i]) for i in range(lenght)]

def encrypt(msg: str, s1, s2, s3):



