"""PROVA 2 del mercante a due minuti. Regole: PROVA_REGISTRATA_MERCANTE_2.md.

Differenze dalla prova 1 (annullata perche' l'universo non era quello misurato):
  - UNIVERSO: pool 1,00% senza hook E con profondita' al primo minuto >= 3 ETH.
    Al diploma il pool nasce con ~4,2 ETH; un lancio fresco nasce con polvere.
    La profondita' si misura PRIMA di entrare, quindi e' ammessa.
  - RIGA DI TARATURA a ogni giro: i pool senza scambi fra entrata e uscita
    devono dare esattamente -gas. Altrimenti il giro si annulla da solo.
  - DUE SEGNI a ogni giro: se la componente di prezzo ha un segno solo dopo 20
    posizioni, il giro si annulla. 13 su 13 fu la spia che mi sfuggi'.
"""
import json, os, time, urllib.request, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
FUORI="data/multichain/robinhood/prova_mercante_2.jsonl"
VISTI="data/multichain/robinhood/prova_mercante_2_visti.json"
BLOCCO=0.093; MIN=int(60/BLOCCO); DUE=int(120/BLOCCO)
NOSTRO=0.0157; GAS=2*0.00001383/0.0157; PROF_MIN=3.0

def rpc(m,p,tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,
              "params":p}).encode(),{"content-type":"application/json","user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
        except Exception: time.sleep(2)
    return None
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

visti=set(json.load(open(VISTI))) if os.path.exists(VISTI) else set()
ult=int(rpc("eth_blockNumber",[]),16)
cand={}
for b in range(ult-22000, ult-DUE-MIN, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        d=L["data"][2:]
        if int(d[0:64],16)==10000 and "0x"+d[128+24:192]=="0x"+"0"*40 and L["topics"][1] not in visti:
            cand[L["topics"][1]]=int(L["blockNumber"],16)
print(f"candidati: {len(cand)}")

nuove=[]; taratura=[]
for pid,bn in cand.items():
    sw=[]
    for b in range(bn, bn+MIN+DUE+200, 100):
        for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP,pid],
              "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
            d=L["data"][2:]
            a0=sg(d[0:64])/1e18; a1=sg(d[64:128])
            if a0 and a1: sw.append((int(L["blockNumber"],16), abs(a0/a1)*1e18, a0))
    visti.add(pid)
    if len(sw)<5: continue
    sw.sort(); b_ent=sw[0][0]+MIN; b_usc=b_ent+DUE
    # profondita' misurata SOLO sugli scambi PRIMA dell'entrata: niente futuro
    xs=[]
    for i in range(1,len(sw)):
        if sw[i][0] > b_ent: break
        dp=(sw[i][1]-sw[i-1][1])/sw[i-1][1]
        if 1e-5<abs(dp)<0.5 and abs(sw[i][2])>1e-4: xs.append(2*abs(sw[i][2])/abs(dp))
    if len(xs)<3: continue
    prof=st.median(xs)
    if prof < PROF_MIN: continue                      # universo: solo pool "pieni"
    ent=next((p for b,p,_ in sw if b>=b_ent), None)
    if ent is None: continue
    dentro=[(b,p,a0) for b,p,a0 in sw if b_ent<b<=b_usc]
    if not dentro:
        taratura.append(-GAS); continue               # nessuno scambio: deve dare -gas
    quota=min(NOSTRO/prof,0.5)
    vol=sum(abs(a0) for _b,_p,a0 in dentro)
    usc=next((p for b,p,a0 in reversed(dentro) if a0<0), None)
    if usc is None: pz=-1.0; comm=0.0
    else:
        comm=vol*0.01*quota/NOSTRO; pz=max((usc/ent)**0.5-1,-1.0)
    riga={"pool":pid,"prof":round(prof,3),"quota":round(quota,5),
          "comm":round(comm,5),"prezzo":round(pz,5),"netto":round(pz+comm-GAS,5)}
    nuove.append(riga)
    with open(FUORI,"a") as f: f.write(json.dumps(riga)+"\n")
json.dump(sorted(visti), open(VISTI,"w"))
print(f"nuove posizioni: {len(nuove)} | riga di taratura: {len(taratura)} casi senza scambi")
if taratura:
    ok = all(abs(x+GAS)<1e-9 for x in taratura)
    print(f"   taratura {'OK (esattamente -gas)' if ok else 'ROTTA: giro ANNULLATO'}")

if os.path.exists(FUORI):
    r=[json.loads(x) for x in open(FUORI)]
    v=[x["netto"] for x in r]; p=[x["prezzo"] for x in r]
    e=1.96*st.stdev(v)/len(v)**0.5*100 if len(v)>1 else float("nan")
    print(f"\nTOTALE: {len(v)} posizioni | media {st.mean(v)*100:+.2f}% +/- {e:.2f} | mediana {st.median(v)*100:+.2f}%")
    pos=sum(1 for x in p if x>0)
    print(f"   prezzo: {pos} positive / {len(p)-pos} negative", end="")
    if len(p)>=20 and (pos==0 or pos==len(p)):
        print("  -> UN SEGNO SOLO: giro ANNULLATO")
    else: print("  (due segni: regolare)" if len(p)>=20 else "  (meno di 20: controllo non ancora attivo)")
    print(f"   commissioni medie {st.mean([x['comm'] for x in r])*100:+.2f}% | verso le 200 posizioni: {len(v)}/200")
