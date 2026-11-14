"""Che cosa hanno in comune i destinatari di una distribuzione AMPIA.

La domanda di Nicolo': come fanno ad AVERE questi gettoni?
Un mittente che serve 1-2 indirizzi e' una quota privata: porta chiusa.
Un mittente che ne serve decine ha dei CRITERI, e un criterio si puo' soddisfare.

Qui prendo i destinatari e guardo che cosa avevano fatto PRIMA di ricevere.
Nota: "prima" si misura sullo slot, non sull'ordine di lettura: le firme
tornano dalla piu' recente, un errore che mi e' gia' costato un verdetto.
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S

DIST = sys.argv[1] if len(sys.argv) > 1 else "4B8nfUUvp3yAx3nP7oJKjSF7dCW8h6nCbhsZNsKXq9sB"
MAX = 160

def letture(addr, n):
    sig = S.rpc("getSignaturesForAddress", [addr, {"limit": n}]) or []
    for x in sig:
        if x.get("err"): continue
        t = S.rpc("getTransaction", [x["signature"], {"maxSupportedTransactionVersion":2,
              "encoding":"jsonParsed","commitment":"confirmed"}])
        if t: yield t

print(f"DISTRIBUTORE {DIST[:16]}…")
dest, gettoni = collections.Counter(), collections.Counter()
for t in letture(DIST, 70):
    meta = t["meta"]
    pre = {y["accountIndex"]: float(y["uiTokenAmount"]["uiAmount"] or 0)
           for y in meta.get("preTokenBalances", [])}
    for y in meta.get("postTokenBalances", []):
        o = y.get("owner")
        if o and o != DIST and float(y["uiTokenAmount"]["uiAmount"] or 0) - pre.get(y["accountIndex"],0.0) > 0:
            dest[o] += 1; gettoni[y["mint"]] += 1
print(f"   {len(dest)} destinatari distinti, {len(gettoni)} gettoni distinti")
print(f"   gettone piu' consegnato: {gettoni.most_common(1)}")

# ripetizione: un destinatario servito molte volte NON e' una lista aperta
rip = collections.Counter(dest.values())
print(f"   consegne per destinatario: {dict(sorted(rip.items()))}")

print("\n   che cosa facevano i destinatari PRIMA (campione)")
prog_prima = collections.Counter(); eta = []
for d in list(dest)[:8]:
    sig = S.rpc("getSignaturesForAddress", [d, {"limit": 1000}]) or []
    eta.append(len(sig))
    for t in list(letture(d, 12)):
        for ix in t["transaction"]["message"].get("instructions", []):
            prog_prima[ix.get("program") or ix.get("programId","?")[:28]] += 1
print(f"      storia dei destinatari (n. transazioni): {sorted(eta)}")
print(f"      {'pagina piena = conti VECCHI e attivi' if max(eta)>=1000 else 'conti giovani'}")
for p, n in prog_prima.most_common(8):
    print(f"      {p:<46} {n}")
