"""La cassaforte: quanto entra, quanto esce, e da quante casse di passaggio.

La cassa di passaggio B6jqNw… svuota in HfEWP4YG…. Se la cassaforte riceve da
MOLTE casse, l'operazione e' industriale e la sua dimensione si misura qui.
Il profitto dell'entita' = quanto la cassaforte TRATTIENE, al netto di quanto
rimanda indietro per finanziare gli acquisti sulla curva.
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S

# indirizzo intero della cassaforte, ripescato da una transazione della cassa
CASSA = "B6jqNwTJNyZPEeXFdoYuxGWeEtM2FX9dX7ZmzjovaVHg"
s = S.rpc("getSignaturesForAddress",[CASSA,{"limit":40}]) or []
H = None
for x in s:
    if x.get("err"): continue
    t = S.rpc("getTransaction",[x["signature"],{"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    for a in t["transaction"]["message"]["accountKeys"]:
        if a["pubkey"].startswith("HfEWP4YGu9PKaNmQzzAbLU"): H = a["pubkey"]
    if H: break
if not H: print("cassaforte non ritrovata"); sys.exit(0)
print(f"CASSAFORTE {H}")

out, before = [], None
while True:
    p = {"limit":1000}
    if before: p["before"]=before
    z = S.rpc("getSignaturesForAddress",[H,p]) or []
    out += z
    if len(z) < 1000 or len(out) >= 2000: break
    before = z[-1]["signature"]
print(f"   {len(out)} firme" + (" (fermato a 2000)" if len(out)>=2000 else ""))

ent = usc = 0.0; mitt = collections.Counter(); dest = collections.Counter(); n=0
for x in out[:1200]:
    if x.get("err"): continue
    t = S.rpc("getTransaction",[x["signature"],{"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    acc=[a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
    if H not in acc: continue
    i=acc.index(H); n+=1
    d=(t["meta"]["postBalances"][i]-t["meta"]["preBalances"][i])/1e9
    if d>0.05:
        ent+=d
        for j,a in enumerate(acc):
            if a!=H and (t["meta"]["postBalances"][j]-t["meta"]["preBalances"][j])<-5e7: mitt[a]+=1
    elif d<-0.05:
        usc+=d
        for j,a in enumerate(acc):
            if a!=H and (t["meta"]["postBalances"][j]-t["meta"]["preBalances"][j])>5e7: dest[a]+=1

print(f"   letta su {n} transazioni")
print(f"   ENTRA  {ent:+.2f} SOL da {len(mitt)} mittenti distinti")
print(f"   ESCE   {usc:+.2f} SOL verso {len(dest)} destinatari distinti")
print(f"   TRATTIENE {ent+usc:+.2f} SOL  (~{(ent+usc)*170:+,.0f} EUR)")
print("   principali mittenti (le casse di passaggio):")
for k,v in mitt.most_common(5): print(f"      {k[:24]}… {v}")
print("   principali destinazioni:")
for k,v in dest.most_common(5): print(f"      {k[:24]}… {v}")
