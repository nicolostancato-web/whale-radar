"""La lista corta: chi e' vicino alla soglia.

Primo pezzo della tabella dei prezzi di caduta. Si scansionano tutti i
debitori noti e si tengono quelli con salute sotto 1,15 — gli unici che
possono cadere con un movimento di prezzo plausibile.

Si salva su file: la lista si aggiorna con calma ogni pochi minuti, mentre
la reazione all'avviso dev'essere istantanea.
"""
import json, os, time, urllib.request, sys, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
U="https://ethereum-rpc.publicnode.com"
FUORI="data/liquidazioni/lista_corta.json"
def leggi(a, giri=2):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v=json.load(urllib.request.urlopen(r,timeout=15)).get("result")
            if v and len(v)>=2+64*6:
                x=v[2:]
                return {"garanzia": int(x[0:64],16)/1e8,
                        "debito": int(x[64:128],16)/1e8,
                        "soglia": int(x[192:256],16)/100,
                        "salute": int(x[320:384],16)/1e18}
        except Exception: pass
        time.sleep(0.2)
    return None
deb=json.load(open("data/liquidazioni/debitori.json"))
print(f"   {len(deb)} debitori da controllare")
t0=time.time(); corta=[]; letti=0; falliti=0
for a in deb:
    r=leggi(a)
    if r is None: falliti+=1; continue
    letti+=1
    if r["debito"]<=0: continue
    if r["salute"] < 1.15:
        r["indirizzo"]=a
        # quanto deve scendere la garanzia perche' cada
        r["caduta_necessaria"] = (1 - 1/r["salute"])*100 if r["salute"]>0 else 0
        corta.append(r)
dt=time.time()-t0
print(f"   {letti} letti, {falliti} falliti in {dt:.0f}s ({letti/dt:.1f}/s)")
corta.sort(key=lambda x:x["salute"])
json.dump(corta, open(FUORI,"w"), indent=1)
print(f"\n   LISTA CORTA: {len(corta)} posizioni sotto 1,15\n")
print(f"   {'indirizzo':<16}{'debito USD':>14}{'salute':>9}{'caduta per cadere':>19}")
for r in corta[:14]:
    print(f"   {r['indirizzo'][:14]:<16}{r['debito']:>14,.0f}{r['salute']:>9.4f}"
          f"{r['caduta_necessaria']:>18.2f}%")
if corta:
    print(f"\n   debito totale sorvegliato: {sum(r['debito'] for r in corta):,.0f} USD")
    vicinissime=[r for r in corta if r["caduta_necessaria"]<2]
    print(f"   a meno del 2% dalla caduta: {len(vicinissime)} posizioni, "
          f"{sum(r['debito'] for r in vicinissime):,.0f} USD di debito")
