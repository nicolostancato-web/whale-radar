"""Un'istantanea non e' un tasso: qui si accumulano campioni a ore diverse.

Lezione del 24/10 sera: lo stesso script dava 68% e 0,204% il pomeriggio, 4% e
0,631% la sera. Due istantanee di un flusso eterogeneo non fanno una misura.
Questo scrive UNA riga per esecuzione in data/base/commissioni_campioni.jsonl
e stampa la distribuzione di TUTTI i campioni accumulati, con lo scarto.

Regola: non si cita un tasso finche' non ci sono almeno 6 campioni in almeno
4 ore diverse, e si stampa sempre l'intervallo fra il minimo e il massimo.
"""
import sys, os, json, collections, statistics as st, datetime
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
FUORI="data/base/commissioni_campioni.jsonl"
os.makedirs("data/base", exist_ok=True)
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
BL=1800          # ~1 ora
tx=[]
for b in range(ult-BL, ult, 900):
    L=B.log_di_finestra(SWAP3, b, min(b+899,ult))
    if L is None: continue
    tx += [x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx))
# campione CASUALE della finestra, non i primi: prendere sempre i piu' vecchi
# lega il campione a un momento preciso dell'ora.
import hashlib
tx.sort(key=lambda h: hashlib.sha256(h.encode()).hexdigest())
dest=collections.Counter(); quote=[]; letti=0
for h in tx[:120]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]
    for L in r["logs"]:
        if not L.get("topics"): continue
        if L["topics"][0]==SWAP3:
            pool.add(L["address"].lower()); d=L["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif L["topics"][0]==TRASF and len(L["topics"])>=3:
            try: tr.append(("0x"+L["topics"][2][-40:], int(L["data"],16)))
            except Exception: pass
    if not grande: continue
    for a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        f=v/grande
        if 0.0002 < f < 0.05: dest[a]+=1; quote.append(f)
ora=datetime.datetime.now(datetime.UTC)
riga={"ora_utc": ora.strftime("%Y-%m-%d %H:%M"), "blocco": ult, "letti": letti,
      "con_commissione": len(quote), "quota": round(len(quote)/max(letti,1),4),
      "mediana": round(st.median(quote),6) if quote else None,
      "app": len(dest)}
with open(FUORI,"a") as f: f.write(json.dumps(riga)+"\n")
print(f"campione: {riga['ora_utc']} UTC | {letti} ricevute | "
      f"{len(quote)} con commissione ({riga['quota']:.0%}) | mediana "
      f"{(riga['mediana'] or 0)*100:.3f}% | {len(dest)} app")
tutti=[json.loads(x) for x in open(FUORI)]
print(f"\n   campioni accumulati: {len(tutti)}")
qs=[t["quota"] for t in tutti]; ms=[t["mediana"] for t in tutti if t["mediana"]]
if len(tutti)>=2:
    print(f"   quota con commissione: da {min(qs):.0%} a {max(qs):.0%}  (mediana {st.median(qs):.0%})")
    if ms: print(f"   tariffa mediana: da {min(ms)*100:.3f}% a {max(ms)*100:.3f}%  (mediana {st.median(ms)*100:.3f}%)")
ore=len({t["ora_utc"][:13] for t in tutti})
print(f"   ore distinte coperte: {ore}")
print("   -> " + ("si puo' citare un tasso, CON l'intervallo" if len(tutti)>=6 and ore>=4
      else f"ancora non si cita: servono 6 campioni in 4 ore diverse (ora {len(tutti)}/{ore})"))
