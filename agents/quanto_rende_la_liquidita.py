"""Quanto rende mettere liquidita' nei pool con commissione vera?

Lo Swap v4 porta dentro la LIQUIDITA' attiva e il prezzo, quindi il conto si fa
senza ricostruire posizioni:
   commissioni pagate = fee% * volume in nativo
   capitale attivo    ~ 2*L/sqrtP  (riserve virtuali al prezzo corrente)
   resa lorda         = commissioni / capitale attivo
ATTENZIONE, e va detto a voce alta: questa e' la resa LORDA, senza la perdita
da riposizionamento (impermanent loss). E' il numero che dice se vale la pena
fare il lavoro difficile, non il guadagno.
Swap(id, sender, amount0, amount1, sqrtPriceX96, liquidity, tick, fee)
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s(h,bits=256):
    v=int(h,16); return v-(1<<bits) if v>>(bits-1) else v

ult=int(rpc("eth_blockNumber",[]),16); FIN=20000
fee_di={}; dati=collections.defaultdict(lambda:{"vol":0.0,"n":0,"L":[],"sq":[]})
for b in range(ult-FIN, ult, 100):
    a=hex(min(b+99,ult))
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":a}]) or []:
        fee_di[L["topics"][1]] = int(L["data"][2:][0:64],16)
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":a}]) or []:
        d=L["data"][2:]
        if len(d) < 384: continue
        a0=s(d[0:64],128) if False else s(d[0:64])
        sq=int(d[128:192],16); liq=int(d[192:256],16)
        k=L["topics"][1]; e=dati[k]
        e["vol"] += abs(a0)/1e18; e["n"] += 1
        if liq>0: e["L"].append(liq); e["sq"].append(sq)

ore = FIN*0.093/3600
print(f"finestra ~{ore:.1f} ore | pool con scambi: {len(dati)}\n")
print("   pool              scambi   volume(nativi)   fee     capitale attivo   resa LORDA   annuo")
righe=0
for k,e in sorted(dati.items(), key=lambda x:-x[1]["vol"]):
    if e["n"] < 30 or not e["L"]: continue
    f = fee_di.get(k)
    if f is None or f == 0 or f == 0x800000: continue
    import statistics as st
    Lm = st.median(e["L"]); sqm = st.median(e["sq"])/2**96
    if sqm <= 0: continue
    cap = 2*Lm/sqm/1e18
    if cap < 1e-9: continue
    comm = e["vol"]*f/1e6
    resa = comm/cap
    print(f"   {k[:14]}…  {e['n']:>5}  {e['vol']:>14,.2f}  {f/10000:>5.2f}%  {cap:>14,.2f}  {resa*100:>9.3f}%  {resa*(8760/ore)*100:>8,.0f}%")
    righe += 1
    if righe >= 8: break
if not righe: print("   nessun pool con commissione vera e abbastanza scambi nella finestra")
print("\n   NB: resa LORDA, senza la perdita da riposizionamento. Serve a decidere")
print("       se vale la pena misurare quella, non e' il guadagno.")
