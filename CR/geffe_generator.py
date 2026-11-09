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

def text_to_bits(text):
    """Ogni carattere diventa 8 bit: 'A' -> [0,1,0,0,0,0,0,1].
    Con un codice > 255 i bit sarebbero più di 8 e tutto si sfaserebbe,
    quindi in quel caso si ferma con un errore."""
    bits = []
    for ch in text:
        if ord(ch) > 255:
            raise ValueError(f"carattere non supportato: '{ch}' (servono caratteri con codice <= 255)")
        for b in format(ord(ch), "08b"):
            bits.append(int(b))
    return bits


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
    p_bits = text_to_bits(p_text)

    k_stream = geffe(s1, s2, s3, len(p_bits))
    c_text = [p_bits[i] ^ k_stream[i] for i in range(len(p_bits))] #cifrato in binario

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
        
# ATTACCO: funzioni

def all_states(numero_bit):
    """Tutti gli stati possibili di un registro, escluso quello tutto zero """
    stati = []
    for num in range(1, 2 ** numero_bit):
        stati.append([int(b) for b in format(num, "0" + str(numero_bit) + "b")]) 
    return stati

def find_initial_state(taps, numero_bit, k_noto):
    """Prova tutti i possibili stati iniziali non nulli di un registro e
    sceglie quello la cui sequenza assomiglia di più al tratto di keystream noto"""
    n = len(k_noto)
    best_state = None
    best_score = -1
    for candidato in all_states(numero_bit):
        seq = lfsr(candidato, taps, n)
        corrispondenze = 0
        for i in range(n):
            if seq[i] == k_noto[i]:
                corrispondenze += 1
        if corrispondenze / n > best_score:
            best_score = corrispondenze / n
            best_state = candidato
    return best_state, best_score

def find_lfsr1(ks, f2, f3):


# ATTACCO

def attack(c_hex, known_text):
    c_noto = hex_to_bits(c_hex)
    p_noto = text_to_bits(known_text)
    num_bit_noti = len(p_noto)

    # 1) Ricavare il pezzo di keystream noto
    k_noto = [c_noto[i] ^ p_noto[i] for i in range(num_bit_noti)]

    print()
    print(SEP)
    print("KEYSTREAM NOTO = chiaro noto XOR cifrato (solo sui primi", num_bit_noti, "bit)")
    print(SEP)
    print("   chiaro noto:", bits_to_str(p_noto))
    print("   cifrato:    ", bits_to_str(c_noto[:num_bit_noti]))
    print("   keystream:  ", bits_to_str(k_noto))

    # 2) Recuperare i 3 semi iniziali dei registri (s1, s2, s3) tramite correlazione:
    #    Data la forte correlazione tra l'output di Geffe con z2 e z3 (75%)
    #    si procede indovinando LFSR2 e LFSR3 e verificando se il risultato coincide con il keystream noto,
    #    provando 31 + 63 stati.
    print()
    print(SEP)
    print("2) RECUPERO DEI SEMI")
    print(SEP)

    f2, score2 = find_initial_state(t2, 5, k_noto)
    print(f"   LFSR2 = {f2} (coincidenza {score2:.0%})")

    f3, score3 = find_initial_state(t3, 6, k_noto)
    print(f"   LFSR3 = {f3} (coincidenza {score3:.0%})")

    f1 = find_lfsr1(k_noto, f2, f3)
    print(f"   LFSR1 = {f1}")


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

if scelta == "2":
    print()
    print(SEP)
    print("DECIFRATURA")
    print(SEP)
    cifrato_hex = input("Testo cifrato (hex): ").strip()

    if not cifrato_hex:
        raise ValueError("Il testo cifrato non può essere vuoto")

    if any(c not in "0123456789abcdefABCDEF" for c in cifrato_hex):
        raise ValueError("Sono ammesse solo cifre esadecimali: 0-9, A-F")

    if len(cifrato_hex) % 2 != 0:
        raise ValueError("Il numero di cifre esadecimali deve essere pari")

    print()
    print(SEP)
    print("Testo decifrato:", decrypt(cifrato_hex, s1, s2, s3))
    print(SEP)


if scelta == "3":