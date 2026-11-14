"""Il mercante mette e toglie nello stesso blocco, o lascia li' la liquidita'?

Se e' "nello stesso blocco attorno a uno scambio grosso" (JIT), e' una gara di
millisecondi e col nostro secondo di ritardo non giochiamo: strada chiusa.
Se la liquidita' resta minuti/ore, e' un mestiere di pazienza, ed e' nostro.

Si misura dal SEGNO della liquidita' nell'evento ModifyLiquidity:
liquidityDelta e' l'ultima parola del data, in complemento a due.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
def s256(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16)
ev=[]
for b in range(ult-4000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[MODL],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        d=L["data"][2:]
        # (tickLower, tickUpper, liquidityDelta, salt) -> delta e' la 3a parola
        delta=s256(d[128:192]) if len(d)>=192 else 0
        ev.append((int(L["blockNumber"],16), L["topics"][1], L["topics"][2], delta))
print(f"{len(ev)} mosse di liquidita' su ~{4000*0.093/60:.0f} minuti")
agg=sum(1 for e in ev if e[3]>0); tog=sum(1 for e in ev if e[3]<0)
print(f"   aggiunte: {agg} | tolte: {tog}")

# vita di una posizione: stessa (pool, proprietario), aggiunta -> prima rimozione
apert={}; vite=[]; stesso_blocco=0
for bn,pid,own,d in sorted(ev):
    k=(pid,own)
    if d>0: apert.setdefault(k,bn)
    elif d<0 and k in apert:
        v=bn-apert.pop(k); vite.append(v)
        if v==0: stesso_blocco+=1
if vite:
    vite.sort()
    import statistics as st
    sec=[v*0.093 for v in vite]
    print(f"\n   posizioni chiuse osservate: {len(vite)}")
    print(f"   durata mediana: {st.median(sec):.1f} s | media {st.mean(sec):.1f} s")
    print(f"   chiuse nello STESSO blocco (JIT): {stesso_blocco} ({stesso_blocco/len(vite):.0%})")
    print(f"   sotto 1 secondo: {sum(1 for x in sec if x<1)/len(vite):.0%} | sopra 1 minuto: {sum(1 for x in sec if x>60)/len(vite):.0%}")
    print("\n   -> " + ("GARA DI MILLISECONDI: col nostro ritardo non giochiamo"
          if stesso_blocco/len(vite) > 0.5 else
          "MESTIERE DI PAZIENZA: la liquidita' resta, il ritardo non ci esclude"))
else:
    print("   nessuna posizione aperta e chiusa dentro la finestra: gia' un indizio di pazienza")
