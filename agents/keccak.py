"""Keccak-256 in Python puro.

Serve per calcolare i selettori delle funzioni dei contratti e gli identificativi dei pool, e sul
cloud non possiamo installare librerie native. Sessanta righe, nessuna dipendenza.
"""
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
       0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
       0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
       0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_R = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
      [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
M = (1 << 64) - 1


def _rot(x, n):
    n %= 64
    return ((x << n) | (x >> (64 - n))) & M


def _f(a):
    for rnd in range(24):
        c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rot(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                a[x][y] ^= d[x]
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rot(a[x][y], _R[x][y])
        for x in range(5):
            for y in range(5):
                a[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y] & M) & b[(x + 2) % 5][y])
        a[0][0] ^= _RC[rnd]
    return a


def keccak256(dati: bytes) -> bytes:
    tasso = 136                                    # 1088 bit, per il 256
    m = bytearray(dati)
    m.append(0x01)                                 # padding di Keccak originale, non di SHA-3
    while len(m) % tasso != 0:
        m.append(0x00)
    m[-1] ^= 0x80
    a = [[0] * 5 for _ in range(5)]
    for pos in range(0, len(m), tasso):
        blocco = m[pos:pos + tasso]
        for i in range(tasso // 8):
            x, y = i % 5, i // 5
            a[x][y] ^= int.from_bytes(blocco[i * 8:(i + 1) * 8], "little")
        a = _f(a)
    fuori = bytearray()
    while len(fuori) < 32:
        for i in range(tasso // 8):
            x, y = i % 5, i // 5
            fuori += a[x][y].to_bytes(8, "little")
            if len(fuori) >= 32:
                break
        if len(fuori) < 32:
            a = _f(a)
    return bytes(fuori[:32])


def selettore(firma: str) -> str:
    """Il codice a 4 byte con cui si chiama una funzione, es. «getSlot0(bytes32)»."""
    return "0x" + keccak256(firma.encode()).hex()[:8]
