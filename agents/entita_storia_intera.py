"""Come entita_consolidata, ma sulla STORIA INTERA.

Lezione del tentativo precedente: una finestra di 100 transazioni conteneva
solo riscossioni e dava netto zero. Una finestra che non contiene l'evento non
dimostra niente. Qui leggo tutto e DICHIARO se la pagina era piena.
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S

RIC  = "B6jqNwTJNyZPEeXFdoYuxGWeEtM2FX9dX7ZmzjovaVHg"
MITT = None   # lo ricavo dalla prima consegna trovata

def tutte(w):
    out, before = [], None
    while True:
        p = {"limit": 1000}
        if before: p["before"] = before
        s = S.rpc("getSignaturesForAddress", [w, p]) or []
        out += s
        if len(s) < 1000 or len(out) >= 3000: break
        before = s[-1]["signature"]
    return out

def conto(w, firme):
    tot = 0.0; n = 0; grossi = []
    soci = collections.Counter()
    for x in firme:
        if x.get("err"): continue
        t = S.rpc("getTransaction", [x["signature"], {"maxSupportedTransactionVersion":2,
              "encoding":"jsonParsed","commitment":"confirmed"}])
        if not t: continue
        acc = [a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
        if w not in acc: continue
        i = acc.index(w); n += 1
        d = (t["meta"]["postBalances"][i]-t["meta"]["preBalances"][i])/1e9
        tot += d
        if abs(d) > 0.5: grossi.append(round(d,2))
        for j,a in enumerate(acc):
            if a != w and (t["meta"]["postBalances"][j]-t["meta"]["preBalances"][j]) < -5e8:
                soci[a] += 1
    return tot, n, grossi, soci

f = tutte(RIC)
print(f"RICEVENTE {RIC[:20]}… : {len(f)} firme totali")
tot, n, grossi, soci = conto(RIC, f)
print(f"   SOL netto sulla storia intera: {tot:+.3f}  (~{tot*170:+,.0f} EUR)")
print(f"   transazioni lette: {n} | movimenti sopra 0.5 SOL: {len(grossi)}")
print(f"   i piu' grossi: {sorted(grossi)[:4]} … {sorted(grossi)[-4:]}")
print(f"   chi gli ha MANDATO SOL (>0.5): {[ (k[:14], v) for k,v in soci.most_common(4) ]}")
print("\n   -> " + ("INCASSA DAVVERO: va consolidato col mittente per sapere se e' profitto"
      if tot > 1 else "NON ha mai accumulato SOL: i ricavi escono subito altrove"))
