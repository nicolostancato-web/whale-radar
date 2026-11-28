"""I colpi grossi sono di parti collegate alla posizione?

Tre controlli, dal piu' economico:
  1) il liquidatore COINCIDE col debitore (autoliquidazione)?
  2) e' un CONTRATTO o una persona? I mestieranti usano contratti apposta.
  3) RICOMPARE su piu' occasioni o protocolli? Chi ricompare lavora; chi
     appare una volta sola puo' essere un parente della posizione.

Se i grossi sono quasi tutti persone che appaiono una volta, il mercato
aperto e' solo la polvere e il candidato crolla.
"""
import json, time, urllib.request, collections
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
U="https://ethereum-rpc.publicnode.com"
def codice(a, giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getCode",
                  "params":[a,"latest"]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3*(g+1))
    return None
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"ut":set(),"prot":set(),"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]
    o["liq"]="0x"+d[64*2+24:64*3]
    if e.get("utente"): o["ut"].add(e["utente"])
    o["prot"].add(e["prot"])
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
quante=collections.Counter(o["liq"] for o in occ.values() if o["liq"])
protdi=collections.defaultdict(set)
for o in occ.values():
    if o["liq"]: protdi[o["liq"]] |= o["prot"]
gr=sorted([o for o in occ.values() if o["ign"]==0 and o["prem"]>=1000],
          key=lambda x:-x["prem"])
print(f"   {len(gr)} occasioni sopra 1.000 EUR\n")
auto=0; contratti=0; ripetuti=0
print(f"   {'premio':>11}  {'liquidatore':<14}{'tipo':<10}{'occasioni':>10}"
      f"{'protocolli':>12}{'  autoliq.'}")
for o in gr[:16]:
    l=o["liq"]
    c=codice(l)
    tipo = "contratto" if c and len(c)>4 else "persona"
    if tipo=="contratto": contratti+=1
    n=quante[l]
    if n>1: ripetuti+=1
    a = l in o["ut"]
    if a: auto+=1
    print(f"   {o['prem']:>10,.0f}€  {l[:12]}..  {tipo:<10}{n:>10}"
          f"{len(protdi[l]):>12}{'   SI' if a else '   no'}")
    time.sleep(0.15)
n=min(16,len(gr))
print(f"\n   su {n} occasioni grandi esaminate:")
print(f"      autoliquidazioni: {auto}")
print(f"      liquidatore e' un contratto: {contratti}/{n}")
print(f"      liquidatore ricompare su piu' occasioni: {ripetuti}/{n}")
print(f"   -> {'sono mestieranti: mercato aperto' if contratti>=n*0.7 else 'molti one-shot: sospetto parti collegate'}")
