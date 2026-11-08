import random

t1 = [0,1]
t2 = [0,2]
t3 = [0,1]
# per semplicità li ho fissati... (da modificare in un secondo momento)

# stati iniziali di default
s1 = [1, 0, 1, 1]
s2 = [1, 0, 0, 1, 0]
s3 = [1, 0, 1, 1, 0, 1]

SEP = "-" * 60

# FUNZIONI DI SUPPORTO

def hex_to_bits(hex):
    """Ogni cifra esadecimale diventa 4 bit, tenendo gli zeri iniziali."""
    return [int(b) for b in format(int(hex, 16), "0" + str(len(hex) * 4) + "b")]

def bits_to_str(bits):
    """[1,0,1,1] -> '1011', per stampare i bit su una riga."""
    return "".join(str(b) for b in bits)

def ask_seeds():
    """Chiede i 3 stati iniziali dei registri (Invio = default).
    Controlla lunghezza, che ci siano solo 0 e 1 e che non siano tutti zero.
    Ritorna (s1, s2, s3)."""
    seeds = []
    for registro, default in [("LFSR1", s1), ("LFSR2", s2), ("LFSR3", s3)]:
        while True:
            stato = input(
                f"{registro} ({len(default)} bit) "
                f"[Default: {bits_to_str(default)}]: "
            ).strip()
            if stato == "":
                seeds.append(default)
                break

            try:
                if len(stato) != len(default) or stato.strip("01") != "":
                    raise ValueError(f"servono {len(default)} cifre, solo 0 e 1")
                if "1" not in stato:
                    raise ValueError("lo stato non può essere tutto zero")
            except ValueError as errore:
                print(errore)
                continue

            seeds.append([int(b) for b in stato])
            break
    return seeds[0], seeds[1], seeds[2]

# GENERATORE DI GEFFE

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

def encrypt(p_text, s1, s2, s3):
    p_bytes = [] #devo convertire il testo in byte, quindi in bit
    for c in p_text:
        if ord(c) > 255:
            raise ValueError("Il testo contiene caratteri non supportati (servono caratteri con codice <= 255)")
        p_bytes.append(ord(c))

    num_bits = len(p_bytes) * 8 #quanti bit servono
    k_stream = geffe(s1, s2, s3, num_bits)
    c_text = [p_bytes[i] ^ k_stream[i] for i in range(len(p_bytes))] #cifrato in binario

    c_int = int(bits_to_str(c_text), 2) #cifrato intero base 2
    c_hex = format(c_int, "0" + str(len(c_text) // 4) + "x")
    return c_hex


def decrypt(c_text: str, s1, s2, s3):
    c_bytes = hex_to_bits(c_text)

    k_stream = geffe(s1, s2, s3, len(c_bytes))
    p_bytes = [c_bytes[i] ^ k_stream[i] for i in range(len(c_bytes))]

    # da bit a stringa
    plaintext = ""
    for i in range(0, len(p_bytes), 8):
        byte = bits_to_str(p_bytes[i:i + 8])
        plaintext += chr(int(byte, 2))
    return plaintext
        
# ATTACCO

 # def attack(c_hex)


# MENU

print(SEP)
print("  GENERATORE DI GEFFE: CIFRATURA E ATTACCO")
print("Quale operazione vuoi eseguire?")
print("1) Cifratura")
print("2) Decifratura")
print("3) Attacco a chiaro noto con correlazione")
scelta = ""
while scelta not in ["1", "2", "3"]:
    scelta = input("Scelta (1, 2 o 3) [Default: 3]: ").strip()
    if scelta == "":
        scelta = "3"
    elif scelta not in ["1", "2", "3"]:
        print("Scelta non valida: scrivi 1, 2 o 3.")
print()

# stati iniziali (servono per cifratura e decifratura)
if scelta in ["1", "2"]:
    print(SEP)
    print("DEFINIZIONE DEGLI STATI INIZIALI DEI 3 REGISTRI (Invio = default)")
    print(SEP)
    s1, s2, s3 = ask_seeds()


if scelta == "1":
    print()
    print(SEP)
    print("CIFRATURA")
    print(SEP)
    messaggio = input("Messaggio da cifrare [Default: Corso di crittografia 2026/2027]: ").strip()
    if messaggio == "":
        messaggio = "Corso di crittografia 2026/2027"

    print()
    print(SEP)
    print("Testo cifrato (hex):", encrypt(messaggio, s1, s2, s3))
    print(SEP)
