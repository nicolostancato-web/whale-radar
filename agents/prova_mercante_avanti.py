"""PROVA IN AVANTI del mercante a due minuti. Regole in PROVA_REGISTRATA_MERCANTE.md,
scritte PRIMA e non modificabili.

Scrive una riga per posizione in data/multichain/robinhood/prova_mercante.jsonl
(righe singole in chiaro, mai .gz in append: un'interruzione lo renderebbe
illeggibile per intero - lezione gia' pagata).
Idempotente: i pool gia' visti non si rifanno.
"""
import json, os, time, urllib.request, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
FUORI="data/multichain/robinhood/prova_mercante.jsonl"
VISTI="data/multichain/robinhood/prova_mercante_visti.json"
BLOCCO=0.093; MIN=int(60/BLOCCO); DUE=int(120/BLOCCO)
NOSTRO=0.0157; GAS=2*0.00001383/0.0157      # due transazioni, frazione del capitale

def rpc(m,p,tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,
              "params":p}).encode(),{"content-type":"application/json","user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
        except Exception: time.sleep(2)
    return None
def s(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

visti=set(json.load(open(VISTI))) if os.path.exists(VISTI) else set()
ult=int(rpc("eth_blockNumber",[]),16)
# pool ammissibili: fee 1,00% e NESSUN hook, nati di recente ma gia' maturi
nuovi={}
for b in range(ult-22000, ult-DUE-MIN, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        d=L["data"][2:]
        fee=int(d[0:64],16); hook="0x"+d[128+24:192]
        if fee==10000 and hook=="0x"+"0"*40 and L["topics"][1] not in visti:
            nuovi[L["topics"][1]]=int(L["blockNumber"],16)
print(f"pool ammissibili nuovi: {len(nuovi)}")

scritte=0
for pid,bn in nuovi.items():
    sw=[]
    for b in range(bn, bn+MIN+DUE+200, 100):
        for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP,pid],
              "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
            d=L["data"][2:]
            a0=s(d[0:64])/1e18; a1=s(d[64:128])
            if a0 and a1: sw.append((int(L["blockNumber"],16), abs(a0/a1)*1e18, a0))
    visti.add(pid)
    if len(sw)<5: continue
    sw.sort(); b_primo=sw[0][0]; b_ent=b_primo+MIN; b_usc=b_ent+DUE
    ent=next((p for b,p,_ in sw if b>=b_ent), None)
    if ent is None: continue
    xs=[]
    for i in range(1,len(sw)):
        dp=(sw[i][1]-sw[i-1][1])/sw[i-1][1]
        if 1e-5<abs(dp)<0.5 and abs(sw[i][2])>1e-4: xs.append(2*abs(sw[i][2])/abs(dp))
    if len(xs)<5: continue
    prof=st.median(xs); quota=min(NOSTRO/prof,0.5)
    vol=sum(abs(a0) for b,_,a0 in sw if b_ent<b<=b_usc)
    usc=next((p for b,p,a0 in reversed(sw) if b<=b_usc and a0<0), None)
    if usc is None:
        netto=-1.0; comm=0.0
    else:
        comm=vol*0.01*quota/NOSTRO
        netto=max((usc/ent)**0.5-1,-1.0)+comm-GAS
    with open(FUORI,"a") as f:
        f.write(json.dumps({"pool":pid,"blocco":b_primo,"prof":round(prof,4),
            "quota":round(quota,5),"comm":round(comm,5),"netto":round(netto,5),
            "scambi":len(sw),"impiccata":usc is None})+"\n")
    scritte+=1
json.dump(sorted(visti), open(VISTI,"w"))
print(f"posizioni registrate in questo giro: {scritte}")
if os.path.exists(FUORI):
    v=[json.loads(r)["netto"] for r in open(FUORI)]
    if v:
        e=1.96*st.stdev(v)/len(v)**0.5*100 if len(v)>1 else float('nan')
        print(f"TOTALE prova in avanti: {len(v)} posizioni | media {st.mean(v)*100:+.2f}% +/- {e:.2f} | mediana {st.median(v)*100:+.2f}%")
