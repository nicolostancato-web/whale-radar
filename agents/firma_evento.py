"""keccak256 in puro Python, per dare un NOME agli eventi della chain.

PERCHE' ESISTE. Il 6/10 Grok ha indicato un meccanismo preciso (la curva di Pons vende i gettoni
prima che il pool esista, emettendo `CurveBuy`). Per verificarlo serviva riconoscere un evento dal
suo `topic0`, che e' il keccak256 della firma. Sulla macchina non c'e' nessuna libreria keccak
(pycryptodome, eth_utils, pysha3: tutte assenti) e `hashlib.sha3_256` NON e' keccak: lo standard
SHA-3 ha un padding diverso e da' un risultato diverso. Scambiarli e' un errore classico.

NON e' decorativo: senza nome, l'unico modo di dire "questo evento e' un acquisto" e' l'occhio
sulla forma dei dati. Quell'occhio e' esattamente cio' che ci ha fatto invertire acquisti e
vendite sul 67-78% dei pool. Un nome e' una verifica, una forma e' un'impressione.

CONTROLLO INTERNO: `prova()` confronta con due valori noti, e uno dei due
(Transfer(address,address,uint256)) lo avevamo GIA' letto nei log della chain prima di scrivere
questo file. Se quel confronto passa, l'implementazione e' giusta per costruzione.
"""
MASCHERA = (1 << 64) - 1
_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
       0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
       0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
       0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_R = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
      [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]


def _rot(v, n):
    n %= 64
    return ((v << n) | (v >> (64 - n))) & MASCHERA if n else v


def _giri(A):
    for r in range(24):
        C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
        D = [C[(x - 1) % 5] ^ _rot(C[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                A[x][y] ^= D[x]
        B = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2 * x + 3 * y) % 5] = _rot(A[x][y], _R[x][y])
        for x in range(5):
            for y in range(5):
                A[x][y] = B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y] & MASCHERA)
        A[0][0] ^= _RC[r]
    return A


def keccak256(dati):
    if isinstance(dati, str):
        dati = dati.encode()
    tasso = 136  # 1088 bit, quello di keccak256
    m = bytearray(dati)
    m.append(0x01)                      # padding di KECCAK, non di SHA-3 (che userebbe 0x06)
    while len(m) % tasso:
        m.append(0x00)
    m[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for off in range(0, len(m), tasso):
        blocco = m[off:off + tasso]
        for i in range(tasso // 8):
            x, y = i % 5, i // 5
            A[x][y] ^= int.from_bytes(blocco[i * 8:i * 8 + 8], "little")
        A = _giri(A)
    fuori = bytearray()
    for i in range(4):                  # 32 byte = 4 corsie
        x, y = i % 5, i // 5
        fuori += A[x][y].to_bytes(8, "little")
    return bytes(fuori)


def firma(testo):
    """Il topic0 di un evento, dalla sua firma Solidity."""
    return "0x" + keccak256(testo).hex()


def prova():
    casi = [("", "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
            ("Transfer(address,address,uint256)",
             "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")]
    ok = True
    for t, atteso in casi:
        avuto = firma(t)
        buono = avuto == atteso
        ok = ok and buono
        print(f"{'ok ' if buono else 'NO '} keccak256({t!r}) = {avuto[:22]}…")
    return ok


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for t in sys.argv[1:]:
            print(f"{firma(t)}  {t}")
    else:
        sys.exit(0 if prova() else 1)
