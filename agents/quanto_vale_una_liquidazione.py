"""Quanto vale una liquidazione su questa chain, e chi se la prende?

Morpho Blue e' qui (indirizzo non canonico) con ~14 liquidazioni al giorno.
Il premio e' scritto nel contratto: chi ripaga il debito si prende il
collaterale scontato. Quindi niente previsioni, solo due domande:
   1. quanto e' GROSSO il debito ripagato? (con 300 euro si toccano solo i piccoli)
   2. quanti liquidatori distinti? se e' un bot solo, e' il suo giardino.
Liquidate(id indexed, caller indexed, borrower indexed,
          repaidAssets, repaidShares, seizedAssets, badDebtAssets, badDebtShares)
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import firma
RPC="https://rpc.mainnet.chain.robinhood.com"
T=firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,d): return rpc("eth_call",[{"to":to,"data":d},"latest"])
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(rpc("eth_blockNumber",[]),16); FIN=1200000; PASSO=5000
ev=[]
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"topics":[T],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]
        ev.append({"mercato":L["topics"][1], "chi":"0x"+L["topics"][2][-40:],
                   "debitore":"0x"+L["topics"][3][-40:],
                   "ripagato":int(d[0:64],16), "preso":int(d[128:192],16),
                   "insolvenza":int(d[192:256],16), "blocco":int(L["blockNumber"],16),
                   "contratto":L["address"].lower(), "tx":L["transactionHash"]})
ore=FIN*0.093/3600
print(f"{len(ev)} liquidazioni in ~{ore:.1f} ore  ({len(ev)/ore*24:.0f}/giorno)\n")
chi=collections.Counter(e["chi"] for e in ev)
print(f"   liquidatori distinti: {len(chi)}")
for a,n in chi.most_common(5): print(f"      {a[:24]}…  {n}")
merc=collections.Counter(e["mercato"] for e in ev)
print(f"   mercati distinti: {len(merc)}")
print("\n   ripagato (unita' grezze del gettone di prestito) e preso:")
for e in sorted(ev, key=lambda x:-x["ripagato"])[:8]:
    ins = " INSOLVENZA" if e["insolvenza"] else ""
    print(f"      ripagato {e['ripagato']:>24,}  preso {e['preso']:>26,}{ins}")
