"""PROVA 3 del mercante a due minuti: universo letto dall'EVENTO di diploma.

Le prove 1 e 2 sono state annullate perche' definivano l'universo per
somiglianza (pool pieno, 1%, senza hook): cosi' entravano 465 nascite all'ora
quando i diplomi veri sono 2 all'ora. Il 99,6% era rampa di lancio.

Il diploma emette TRE firme nello stesso blocco in cui nasce il pool (misurato
3/3 su 1,6 ore). Qui si ammette un pool solo se nel suo blocco di nascita c'e'
almeno una di quelle firme. E' un dato noto PRIMA di entrare.
"""
# SPENTO il 24/10. Non per stanchezza: per aritmetica.
#  - il mercante: scarto 30 punti per posizione, servirebbero ~14.000 posizioni
#    per distinguere lo 0,6% cercato. Con 200 l'intervallo e' +/-4,2%: il test
#    NON PUO' concludere. E la strada e' gia' chiusa per altra via (concentrata
#    -2,9% +/- 0,4).
#  - i risolutori UniswapX: la torta intera della chain e' ~40 EUR al giorno.
# Tenere in piedi una misura su una strada chiusa non e' prudenza: e' lavoro
# che si autoalimenta. Se la strada riapre, si riaccende togliendo questo blocco.
import sys as _sys
print("SPENTO: vedi la nota in cima al file"); _sys.exit(0)


import json, os, time, urllib.request, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
FAB="0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"; HOOK="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
DIPL={"0xa0a18f5bf205becee8b268d7cf69addab8548ae8ef361791464cf0e0e17c1361",
      "0x0a44ef75df69c534f43cd6c1aa3ef8983065fe5fe79ef9e79f6494e6f258c259",
      "0x01bf263a1db1652580721573296e1a1fa70b3d4c87f61d02a69c4e1109d2d573"}
FUORI="data/multichain/robinhood/prova_mercante_3.jsonl"
VISTI="data/multichain/robinhood/prova_mercante_3_visti.json"
BLOCCO=0.093; MIN=int(60/BLOCCO); DUE=int(120/BLOCCO); PASSO=1000
NOSTRO=0.0157; GAS=2*0.00001383/0.0157

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
FIN=int(os.environ.get("FIN","40000"))
bl_dip=set(); nascite={}
for b in range(ult-FIN, ult-DUE-MIN, PASSO):
    a=hex(min(b+PASSO-1,ult))
    for ind in (FAB,HOOK):
        for L in rpc("eth_getLogs",[{"address":ind,"fromBlock":hex(b),"toBlock":a}]) or []:
            if L["topics"][0] in DIPL: bl_dip.add(int(L["blockNumber"],16))
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":a}]) or []:
        nascite[L["topics"][1]] = int(L["blockNumber"],16)
cand={p:b for p,b in nascite.items() if b in bl_dip and p not in visti}
print(f"finestra ~{FIN*0.093/3600:.1f} ore | diplomi: {len(bl_dip)} | pool diplomati nuovi: {len(cand)}")

nuove=[]; taratura=[]
for pid,bn in cand.items():
    sw=[]
    for b in range(bn, bn+MIN+DUE+300, PASSO):
        for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP,pid],
              "fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
            d=L["data"][2:]; a0=sg(d[0:64])/1e18; a1=sg(d[64:128])
            if a0 and a1: sw.append((int(L["blockNumber"],16), abs(a0/a1)*1e18, a0))
    visti.add(pid)
    if len(sw)<5: continue
    sw.sort(); b_ent=bn+MIN; b_usc=b_ent+DUE       # dal DIPLOMA, come nell'archivio
    xs=[]
    for i in range(1,len(sw)):
        if sw[i][0] > b_ent: break
        dp=(sw[i][1]-sw[i-1][1])/sw[i-1][1]
        if 1e-5<abs(dp)<0.5 and abs(sw[i][2])>1e-4: xs.append(2*abs(sw[i][2])/abs(dp))
    if len(xs)<3: continue
    prof=st.median(xs)
    ent=next((p for b,p,_ in sw if b>=b_ent), None)
    if ent is None: continue
    dentro=[(b,p,a0) for b,p,a0 in sw if b_ent<b<=b_usc]
    if not dentro: taratura.append(-GAS); continue
    quota=min(NOSTRO/prof,0.5)
    vol=sum(abs(a0) for _b,_p,a0 in dentro)
    usc=next((p for b,p,a0 in reversed(dentro) if a0<0), None)
    if usc is None: pz=-1.0; comm=0.0
    else: comm=vol*0.01*quota/NOSTRO; pz=max((usc/ent)**0.5-1,-1.0)
    riga={"pool":pid,"prof":round(prof,3),"quota":round(quota,5),"comm":round(comm,5),
          "prezzo":round(pz,5),"netto":round(pz+comm-GAS,5)}
    nuove.append(riga)
    with open(FUORI,"a") as f: f.write(json.dumps(riga)+"\n")
json.dump(sorted(visti), open(VISTI,"w"))
print(f"nuove posizioni: {len(nuove)} | taratura: {len(taratura)} casi senza scambi"
      + (" (OK, -gas)" if taratura and all(abs(x+GAS)<1e-9 for x in taratura) else ""))
if os.path.exists(FUORI):
    r=[json.loads(x) for x in open(FUORI)]; v=[x["netto"] for x in r]; p=[x["prezzo"] for x in r]
    e=1.96*st.stdev(v)/len(v)**0.5*100 if len(v)>1 else float("nan")
    pos=sum(1 for x in p if x>0)
    print(f"\nTOTALE: {len(v)}/200 | media {st.mean(v)*100:+.2f}% +/- {e:.2f} | mediana {st.median(v)*100:+.2f}%")
    print(f"   prezzo {pos} positive / {len(p)-pos} negative"
          + ("  -> UN SEGNO SOLO: ANNULLATO" if len(p)>=20 and pos in (0,len(p)) else ""))
    print(f"   commissioni medie {st.mean([x['comm'] for x in r])*100:+.2f}%")
