# -*- coding: utf-8 -*-
"""LA FIRMA IN CASA: ECDSA su secp256k1, senza sottoprocessi e senza librerie.

PERCHE' ESISTE (6/11). La consegna di un pacchetto a quattro porte costava
~400 ms dopo aver messo le connessioni persistenti, e dentro quei 400 ms
c'era ancora UN avvio di processo: `cast wallet sign`, ~150 ms. La finestra
fra l'apparire dell'aggiornamento dell'oracolo e la chiusura del blocco e'
80-250 ms (Astra e Grok, misurato), quindi un solo processo si mangia mezza
finestra.

Non si installa niente: PEP 668 blocca pip qui, e una ECDSA deterministica
e' ~70 righe di interi. Il k si ricava con RFC 6979 (deterministico) cosi'
la firma e' riproducibile e non serve entropia di qualita'.

LA PROVA E' ESATTA, non statistica: la firma prodotta qui deve essere
IDENTICA a quella di `cast wallet sign` sullo stesso messaggio e con la
stessa chiave. Se non combacia, non si usa.
"""
import hashlib, hmac
from keccak import keccak256
P  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
A  = 0
def _inv(x, m): return pow(x, m - 2, m)
def _somma(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if p1 == p2:
        l = (3 * x1 * x1 + A) * _inv(2 * y1, P) % P
    else:
        l = (y2 - y1) * _inv((x2 - x1) % P, P) % P
    x3 = (l * l - x1 - x2) % P
    return (x3, (l * (x1 - x3) - y1) % P)
def _molt(k, p=(GX, GY)):
    r = None
    while k:
        if k & 1: r = _somma(r, p)
        p = _somma(p, p); k >>= 1
    return r
def _k_rfc6979(chiave_int, h):
    """Il k deterministico: niente casualita', quindi la firma e'
    riproducibile e verificabile contro quella di cast."""
    v = b"\x01" * 32; k = b"\x00" * 32
    x = chiave_int.to_bytes(32, "big")
    k = hmac.new(k, v + b"\x00" + x + h, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v + b"\x01" + x + h, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    while True:
        v = hmac.new(k, v, hashlib.sha256).digest()
        cand = int.from_bytes(v, "big")
        if 1 <= cand < N: return cand
        k = hmac.new(k, v + b"\x00", hashlib.sha256).digest()
        v = hmac.new(k, v, hashlib.sha256).digest()
def _firma_digest(chiave_hex, digest):
    d = int(chiave_hex[2:] if chiave_hex.startswith("0x") else chiave_hex, 16)
    h = digest
    z = int.from_bytes(h, "big")
    k = _k_rfc6979(d, h)
    x1, y1 = _molt(k)
    r = x1 % N
    s = (_inv(k, N) * (z + r * d)) % N
    recid = (y1 & 1) ^ (0 if s <= N // 2 else 1)
    if s > N // 2: s = N - s      # forma canonica, come fa ogni firmatario
    return r, s, 27 + recid
def messaggio_personale(testo):
    """La busta EIP-191 che usa `cast wallet sign` per default."""
    d = testo.encode() if isinstance(testo, str) else testo
    return keccak256(b"\x19Ethereum Signed Message:\n" + str(len(d)).encode() + d)
def firma_personale(chiave_hex, testo):
    """La firma a 65 byte, come la stampa `cast wallet sign`."""
    r, s, v = _firma_digest(chiave_hex, messaggio_personale(testo))
    return "0x" + r.to_bytes(32, "big").hex() + s.to_bytes(32, "big").hex() + bytes([v]).hex()
