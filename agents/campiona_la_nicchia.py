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

"""Quale nicchia servono le app che incassano? Campioni accumulati, non una
fotografia sola.

La rilevazione delle commissioni oscilla molto fra le ore (misurato: dal 4% al
68% delle transazioni). Quindi una lettura sola non dice niente — come per la
tariffa, si accumula e si cita solo con abbastanza campioni.
Scrive una riga per giro in data/base/nicchia_campioni.jsonl.
"""
import sys, os, json, collections, hashlib, datetime
sys.path.insert(0,"agents"); from keccak import keccak256
import base_rpc as B
SWAP3="0x"+keccak256(b"Swap(address,address,int256,int256,uint160,uint128,int24)").hex()
TRASF="0x"+keccak256(b"Transfer(address,address,uint256)").hex()
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
FUORI="data/base/nicchia_campioni.jsonl"; os.makedirs("data/base", exist_ok=True)
GROSSI={"0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":"USDC",
        "0x4200000000000000000000000000000000000006":"WETH",
        "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC",
        "0x50c5725949a6f0c72e6c4a641f24049a917db0cb":"DAI"}
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return None
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
L=B.log_di_finestra(SWAP3, ult-1800, ult) or []
tx=list(dict.fromkeys([x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]))
# estrazione CASUALE dentro la finestra, non le piu' vecchie (lezione del 24/10)
tx.sort(key=lambda h: hashlib.sha256(h.encode()).hexdigest())
alt=collections.Counter(); letti=0; conf=0; nomi={}
for h in tx[:110]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]; tok=set()
    for x in r["logs"]:
        if not x.get("topics"): continue
        if x["topics"][0]==SWAP3:
            pool.add(x["address"].lower()); d=x["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif x["topics"][0]==TRASF and len(x["topics"])>=3:
            tok.add(x["address"].lower())
            try: tr.append(("0x"+x["topics"][2][-40:], int(x["data"],16)))
            except Exception: pass
    if not grande: continue
    if not any(0.0002 < v/grande < 0.05 for a,v in tr
               if a not in pool and a!=UR and a!=chi and a!="0x"+"0"*40): continue
    conf+=1
    for t in tok:
        if t in GROSSI: alt[GROSSI[t]]+=1
        else:
            if t not in nomi:
                nomi[t]=testo(B.chiama("eth_call",[{"to":t,"data":sel("symbol()")},"latest"])) or "?"
            alt[nomi[t]]+=1
ora=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M")
riga={"ora":ora,"letti":letti,"con_commissione":conf,"gettoni":dict(alt.most_common(25))}
with open(FUORI,"a") as f: f.write(json.dumps(riga)+"\n")
print(f"campione {ora}: {letti} ricevute, {conf} con commissione")
tutti=[json.loads(x) for x in open(FUORI)]
tot=collections.Counter(); C=0; Lt=0
for t in tutti:
    C+=t["con_commissione"]; Lt+=t["letti"]
    for g,n in t["gettoni"].items(): tot[g]+=n
print(f"\n   campioni accumulati: {len(tutti)} | {C} transazioni con commissione su {Lt}")
if C>=40:
    print("   gettoni piu' coinvolti:")
    for g,n in tot.most_common(12): print(f"      {g:<18} {n}")
    gr=sum(n for g,n in tot.items() if g in GROSSI.values())
    print(f"\n   quota di gettoni grandi: {gr/max(sum(tot.values()),1):.0%}")
else:
    print(f"   servono almeno 40 transazioni con commissione prima di leggere i gettoni (ora {C})")
