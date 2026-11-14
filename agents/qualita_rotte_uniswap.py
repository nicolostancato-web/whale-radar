# -*- coding: utf-8 -*-
"""QUANTO RENDE DAVVERO una rotta Uniswap costruita da noi.

Perche' esiste (4/11 mattina). Stanotte ho collegato il ripiego su Uniswap
perche' l'aggregatore ci aveva bloccati, e nella calldata ho messo il
minimo in uscita a ZERO -- di proposito, perche' a difendere il guadagno
c'e' la guardia in dollari del contratto.
Ma quella guardia pretende solo un quarto del premio atteso, cioe' l'1,75%
del debito: una vasca sottile potrebbe riempirci al 90% e la guardia
ACCETTEREBBE, lasciandoci un guadagno da niente su un premio del 7%.
L'aggregatore scelgieva la rotta migliore fra tutte le piazze; noi
scegliamo la vasca piu' liquida fra quattro livelli di una sola piazza.
Quindi va MISURATO, non supposto.

Si usa il Quoter di Uniswap, che e' una lettura: costa zero e non dipende
da nessuna API.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
from keccak import firma
import vendita_uniswap as VU
D = "data/liquidazioni"
QUOTER = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"   # QuoterV2
FONTI = VU.FONTI
S_UNO  = firma("quoteExactInputSingle((address,address,uint256,uint24,uint160))")[2:10]
S_PATH = firma("quoteExactInput(bytes,uint256)")[2:10]
TAGLIA = float(os.environ.get("TAGLIA_DOLLARI", "100000"))
def _call(to, dati):
    c = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
        "params":[{"to":to,"data":dati},"latest"]}).encode()
    for f in FONTI:
        try:
            r = urllib.request.Request(f, data=c, headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v = json.load(urllib.request.urlopen(r, timeout=25))
            if v.get("result"): return v["result"]
        except Exception: pass
    return None
def _par(a):
    return a[2:].lower().zfill(64)
def resa(src, dst, q, dec_dst, prezzo_dst, cache):
    """Quanti dollari torna la nostra rotta, in frazione del valore messo."""
    f = VU.vasca(src, dst, cache)
    if f:
        d = ("0x"+S_UNO+_par(src)+_par(dst)+hex(q)[2:].zfill(64)
             +hex(f)[2:].zfill(64)+"0"*64)
        h = _call(QUOTER, d)
        if not h or len(h) < 66: return None, f"diretta fee {f}: muta"
        out = int(h[2:66], 16)
        return out/10**dec_dst*prezzo_dst, f"diretta fee {f/10000:.2f}%"
    for ponte in VU.PONTI:
        if ponte in (src, dst): continue
        f1 = VU.vasca(src, ponte, cache); f2 = VU.vasca(ponte, dst, cache)
        if not (f1 and f2): continue
        p = VU._percorso([src, f1, ponte, f2, dst])[2:]
        # quoteExactInput(bytes,uint256): offset, amount, lunghezza, dati
        n = len(p)//2
        corpo = ("0x"+S_PATH+hex(64)[2:].zfill(64)+hex(q)[2:].zfill(64)
                 +hex(n)[2:].zfill(64)+p+"0"*((32-n%32)%32*2))
        h = _call(QUOTER, corpo)
        if not h or len(h) < 66: continue
        out = int(h[2:66], 16)
        return out/10**dec_dst*prezzo_dst, f"via {ponte[:8]} {f1/10000:.2f}+{f2/10000:.2f}%"
    return None, "nessuna rotta"
def main():
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    U = {x["gettone"]: x["simbolo"] for x in json.load(open(f"{D}/unita_gettoni.json"))}
    co = {k.lower(): v for k, v in json.load(open(f"{D}/composizione.json")).items()}
    s = json.load(open(f"{D}/salute_note.json"))
    # le coppie che useremmo davvero: quelle delle posizioni vicine a cadere
    coppie, visti = [], set()
    for a, d in sorted(((v["salute"], k) for k, v in s.items() if v.get("debito",0) > 2000)):
        c = co.get(d)
        if not c: continue
        g = c["garanzia_principale"].lower(); de = c["debito_principale"].lower()
        if g == de or (g, de) in visti: continue
        if g not in PR or de not in PR: continue
        visti.add((g, de)); coppie.append((g, de))
        if len(coppie) >= 12: break
    cache = VU._carica()
    print(f"   {len(coppie)} coppie, vendita da ${TAGLIA:,.0f} ciascuna")
    print(f"   {'coppia':22s} {'resa':>8s}  {'premio reale':>13s}  rotta")
    esiti, cattive = {}, []
    for g, de in coppie:
        pg = PR[g]; pd = PR[de]
        q = int(TAGLIA/pg["prezzo_usd"]*10**pg["decimali"])
        dollari, come = resa(g, de, q, pd["decimali"], pd["prezzo_usd"], cache)
        eti = f"{U.get(g,g[:8])}->{U.get(de,de[:8])}"
        if dollari is None:
            print(f"   {eti:22s} {'—':>8s}  {'—':>13s}  {come}")
            esiti[eti] = {"resa": None, "rotta": come}
            continue
        r = dollari/TAGLIA
        premio = 1.07*r - 1.0005        # quel che resta del 7%
        ok = premio >= 0.035            # almeno la META' del premio
        if not ok: cattive.append((eti, r, premio, come))
        print(f"   {eti:22s} {100*r:7.2f}% {100*premio:12.2f}%  {come}"
              f"{'  <<< MANGIA IL PREMIO' if not ok else ''}")
        esiti[eti] = {"resa": round(r,4), "premio_reale": round(premio,4),
                      "rotta": come, "buona": ok}
    VU._salva(cache)
    json.dump({"quando": time.time(), "taglia_dollari": TAGLIA,
               "esiti": esiti, "cattive": len(cattive)},
              open(f"{D}/qualita_rotte.json","w"), indent=1)
    print(f"   {len(cattive)} rotte lasciano meno di meta' premio")
    return 0
if __name__ == "__main__":
    sys.exit(main())
