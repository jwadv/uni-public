import random

t1 = [0,1]
t2 = [0,2]
t3 = [0,1]
# per semplicità li ho fissati... (da modificare in un secondo momento)

# stati iniziali di default
s1 = [1, 0, 1, 1]
s2 = [1, 0, 0, 1, 0]
s3 = [1, 0, 1, 1, 0, 1]

# GENERAORE DI GEFFE

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


# CIFRATURA E DECIFRATURA

def encrypt(p_text: str, s1, s2, s3):
    p_bytes = [] #devo convertire il testo in byte, quindi in bit
    for c in p_text:
        if ord(c) > 255:
            raise ValueError("Il testo contiene caratteri non supportati (servono caratteri con codice <= 255)")
        p_bytes.append(ord(c))

    num_bits = len(p_bytes) * 8 #quanti bit servono
    k_stream = geffe(s1, s2, s3, num_bits)
    c_text = [p_bytes[i] ^ k_stream[i] for i in range(len(p_bytes))] #cifrato in binario

    c_int = int("".join(str(b) for b in c_text), 2) #cifrato intero base 2
    c_hex = format(c_int, "0" + str(len(c_text) // 4) + "x")
    return c_hex


def decrypt(c_text: str, s1, s2, s3):
    c_int = int(c_text, 16)
    c_bytes = [int(b) for b in format(c_int, '0' + str(len(c_text) * 4) + 'b')] #cifrato in binario

    k_stream = geffe(s1, s2, s3, len(c_bytes))
    p_bytes = [c_bytes[i] ^ k_stream[i] for i in range(len(c_bytes))]

    # da bit a stringa
    messaggio = ""
    for i in range(0, len(p_bytes), 8):
        byte = "".join(str(b) for b in p_bytes[i:i + 8])
        messaggio += chr(int(byte, 2))
    return messaggio
        
# ATTACCO

# MENU
