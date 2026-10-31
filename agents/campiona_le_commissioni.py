"""RITIRATO il 27/10/2026 — NON RIPRENDERE L'ACCUMULO.

Questo campionatore serviva a misurare la "commissione d'instradamento":
l'ipotesi che un'app potesse incassare una quota degli scambi che indirizza.
Il 27/10 quell'ipotesi si e' dissolta in due passaggi:

  1) i prelievi erano contati come transazioni -> il tasso era gonfiato 7x
     (5%, non 47-68%);
  2) soprattutto, quei prelievi NON sono commissioni d'app: 58 destinatari
     su 59 incassano su un solo gettone, e un gettone paga 55 destinatari
     diversi. Sono tasse di trasferimento e distribuzioni ai detentori —
     cose che si emettono, non che si costruiscono.

Vedi L_ULTIMA_ARCHITETTURA_CHIUSA_27OTT.md. Accumulare altri campioni
risponderebbe con grande precisione a una domanda che non esiste piu'.
Lo script resta leggibile perche' il metodo (sei campioni in quattro ore
diverse prima di citare un tasso) vale ancora; il suo oggetto no.
"""
import sys as _s
print(__doc__)
_s.exit(0)

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
dest=collections.Counter(); quote=[]; letti=0; paganti=0
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
    # LEZIONE 27/10: contavo un rigo per TRASFERIMENTO e dividevo per le
    # TRANSAZIONI. Numeratore e denominatore di unita' diverse: la quota
    # poteva superare il 100% e il 47-68% iniziale era solo questo difetto.
    # L'unita' indipendente e' la transazione. Le tariffe restano tutte,
    # perche' li' l'unita' giusta e' il singolo prelievo.
    pagante=False
    for a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        f=v/grande
        if 0.0002 < f < 0.05: dest[a]+=1; quote.append(f); pagante=True
    if pagante: paganti+=1
ora=datetime.datetime.now(datetime.UTC)
riga={"ora_utc": ora.strftime("%Y-%m-%d %H:%M"), "blocco": ult, "letti": letti,
      "versione": 2, "con_commissione": paganti,
      "quota": round(paganti/max(letti,1),4), "prelievi": len(quote),
      "mediana": round(st.median(quote),6) if quote else None,
      "app": len(dest)}
with open(FUORI,"a") as f: f.write(json.dumps(riga)+"\n")
print(f"campione: {riga['ora_utc']} UTC | {letti} ricevute | "
      f"{paganti} transazioni con commissione ({riga['quota']:.0%}), "
      f"{len(quote)} prelievi | tariffa mediana "
      f"{(riga['mediana'] or 0)*100:.3f}% | {len(dest)} app")
# le righe versione 1 contavano i prelievi al posto delle transazioni: escluse
tutti=[json.loads(x) for x in open(FUORI)]
tutti=[t for t in tutti if t.get('versione',1)>=2]
print(f"\n   campioni accumulati: {len(tutti)}")
qs=[t["quota"] for t in tutti]; ms=[t["mediana"] for t in tutti if t["mediana"]]
if len(tutti)>=2:
    print(f"   quota con commissione: da {min(qs):.0%} a {max(qs):.0%}  (mediana {st.median(qs):.0%})")
    if ms: print(f"   tariffa mediana: da {min(ms)*100:.3f}% a {max(ms)*100:.3f}%  (mediana {st.median(ms)*100:.3f}%)")
ore=len({t["ora_utc"][:13] for t in tutti})
print(f"   ore distinte coperte: {ore}")
print("   -> " + ("si puo' citare un tasso, CON l'intervallo" if len(tutti)>=6 and ore>=4
      else f"ancora non si cita: servono 6 campioni in 4 ore diverse (ora {len(tutti)}/{ore})"))
