# -*- coding: utf-8 -*-
"""I BYTE GREZZI RICOSTRUITI IN CASA, senza chiedere niente alla rete.

PERCHE' ESISTE (5/11). Per mettere l'aggiornamento dell'oracolo davanti alla
nostra liquidazione nel pacchetto servono i suoi byte firmati. Li chiedevamo
con eth_getRawTransactionByHash: un giro di rete (~40-150 ms) proprio nel
momento in cui si corre, e su UNA sola fonte (drpc da 400, blastapi da 401).
Ma la sottoscrizione websocket ci da' la transazione INTERA, firma compresa:
i byte grezzi sono esattamente la codifica RLP dei suoi campi piu' la firma.
Si ricostruiscono in casa.

LA PROVA E' GRATIS E ESATTA: l'hash di una transazione firmata E' il keccak
dei suoi byte grezzi. Se il keccak di quello che ho ricostruito e' l'hash che
mi ha dato il nodo, la ricostruzione e' giusta -- non "probabilmente giusta".
Se non torna, si ripiega sulla rete e lo si GRIDA, perche' un ripiego
silenzioso su una cosa indispensabile e' una bugia.
"""
from keccak import keccak256
def _rlp(x):
    if isinstance(x, bytes):
        if len(x) == 1 and x[0] < 0x80: return x
        return _lung(len(x), 0x80) + x
    if isinstance(x, list):
        d = b"".join(_rlp(i) for i in x)
        return _lung(len(d), 0xC0) + d
    raise TypeError(type(x))
def _lung(n, base):
    if n < 56: return bytes([base + n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([base + 55 + len(b)]) + b
def _q(v):
    """Un numero in byte senza zeri davanti: RLP vuole la forma minima, e uno
    zero di troppo cambia l'hash."""
    if v is None: return b""
    n = int(v, 16) if isinstance(v, str) else int(v)
    return b"" if n == 0 else n.to_bytes((n.bit_length() + 7) // 8, "big")
def _b(v):
    if not v: return b""
    return bytes.fromhex(v[2:] if v.startswith("0x") else v)
def _liste_accesso(al):
    fuori = []
    for e in (al or []):
        fuori.append([_b(e.get("address")),
                      [_b(k) for k in (e.get("storageKeys") or [])]])
    return fuori
def grezzo(tx):
    """I byte grezzi della transazione, o None se non tornano con l'hash."""
    t = int(tx.get("type") or "0x0", 16) if isinstance(tx.get("type"), str) else int(tx.get("type") or 0)
    firma = [_q(tx.get("v") if tx.get("v") is not None else tx.get("yParity")),
             _q(tx.get("r")), _q(tx.get("s"))]
    com = [_q(tx.get("nonce")), None, None, _b(tx.get("to")),
           _q(tx.get("value")), _b(tx.get("input"))]
    if t == 0:
        campi = [_q(tx.get("nonce")), _q(tx.get("gasPrice")), _q(tx.get("gas")),
                 _b(tx.get("to")), _q(tx.get("value")), _b(tx.get("input"))] + firma
        d = _rlp(campi)
    elif t == 1:
        campi = [_q(tx.get("chainId")), _q(tx.get("nonce")), _q(tx.get("gasPrice")),
                 _q(tx.get("gas")), _b(tx.get("to")), _q(tx.get("value")),
                 _b(tx.get("input")), _liste_accesso(tx.get("accessList"))] + firma
        d = b"\x01" + _rlp(campi)
    elif t == 2:
        campi = [_q(tx.get("chainId")), _q(tx.get("nonce")),
                 _q(tx.get("maxPriorityFeePerGas")), _q(tx.get("maxFeePerGas")),
                 _q(tx.get("gas")), _b(tx.get("to")), _q(tx.get("value")),
                 _b(tx.get("input")), _liste_accesso(tx.get("accessList"))] + firma
        d = b"\x02" + _rlp(campi)
    elif t == 3:
        campi = [_q(tx.get("chainId")), _q(tx.get("nonce")),
                 _q(tx.get("maxPriorityFeePerGas")), _q(tx.get("maxFeePerGas")),
                 _q(tx.get("gas")), _b(tx.get("to")), _q(tx.get("value")),
                 _b(tx.get("input")), _liste_accesso(tx.get("accessList")),
                 _q(tx.get("maxFeePerBlobGas")),
                 [_b(h) for h in (tx.get("blobVersionedHashes") or [])]] + firma
        d = b"\x03" + _rlp(campi)
    elif t == 4:
        auth = []
        for a in (tx.get("authorizationList") or []):
            auth.append([_q(a.get("chainId")), _b(a.get("address")),
                         _q(a.get("nonce")), _q(a.get("yParity") if a.get("yParity") is not None else a.get("v")),
                         _q(a.get("r")), _q(a.get("s"))])
        campi = [_q(tx.get("chainId")), _q(tx.get("nonce")),
                 _q(tx.get("maxPriorityFeePerGas")), _q(tx.get("maxFeePerGas")),
                 _q(tx.get("gas")), _b(tx.get("to")), _q(tx.get("value")),
                 _b(tx.get("input")), _liste_accesso(tx.get("accessList")),
                 auth] + firma
        d = b"\x04" + _rlp(campi)
    else:
        return None
    # LA PROVA, e non si consegna niente che non la passi
    if "0x" + keccak256(d).hex() != (tx.get("hash") or "").lower():
        return None
    return "0x" + d.hex()
