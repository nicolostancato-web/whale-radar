"""Netto zero: non ha guadagnato, o ha guadagnato e portato via?

Si distingue dalla CONTROPARTE, la regola che vale per tutto il progetto:
uscita verso il MERCATO = ricompra (era un operatore in pari);
uscita verso un INDIRIZZO = prelievo (il profitto vive altrove).
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S
W = "B6jqNwTJNyZPEeXFdoYuxGWeEtM2FX9dX7ZmzjovaVHg"
MERCATI = {"6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
           "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}

out, before = [], None
while True:
    p = {"limit": 1000}
    if before: p["before"] = before
    s = S.rpc("getSignaturesForAddress",[W,p]) or []
    out += s
    if len(s) < 1000: break
    before = s[-1]["signature"]

usc = collessione = collections.Counter(); ent = collections.Counter()
tot_u = tot_e = 0.0; dest = collections.Counter()
for x in out:
    if x.get("err"): continue
    t = S.rpc("getTransaction",[x["signature"],{"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    acc = [a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
    if W not in acc: continue
    i = acc.index(W)
    d = (t["meta"]["postBalances"][i]-t["meta"]["preBalances"][i])/1e9
    if abs(d) < 0.3: continue
    progs = {ix.get("programId") or "" for ix in t["transaction"]["message"].get("instructions",[])}
    progs |= {ix.get("program","") for ix in t["transaction"]["message"].get("instructions",[])}
    mercato = bool(progs & MERCATI)
    # gettoni mossi da/verso W in questa transazione?
    tok = any(y.get("owner")==W for y in t["meta"].get("postTokenBalances",[]))
    tipo = "mercato" if (mercato or tok) else "trasferimento"
    if d < 0:
        usc[tipo] += 1; tot_u += d
        if tipo=="trasferimento":
            for j,a in enumerate(acc):
                if a!=W and (t["meta"]["postBalances"][j]-t["meta"]["preBalances"][j]) > 3e8:
                    dest[a] += 1
    else:
        ent[tipo] += 1; tot_e += d

print(f"ENTRATE  {tot_e:+.2f} SOL  {dict(ent)}")
print(f"USCITE   {tot_u:+.2f} SOL  {dict(usc)}")
q = usc.get("trasferimento",0)/max(sum(usc.values()),1)
print(f"\n   quota delle uscite che sono PRELIEVI: {q:.0%}")
for k,v in dest.most_common(4): print(f"      verso {k[:22]}… {v} volte")
print("\n   -> " + ("PRELIEVI: il profitto esiste e vive su un terzo indirizzo"
      if q > 0.4 else "RICOMPRE: operatore che gira gli stessi soldi, netto zero = NESSUN profitto"))
