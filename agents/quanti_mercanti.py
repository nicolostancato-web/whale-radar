"""Quanti sono i mercanti, e sono robot o persone?

1.011 mosse di liquidita' in 3 minuti: se vengono da 3 indirizzi e' una gara di
velocita' persa in partenza; se da 200, e' un mestiere aperto.
Il mittente dell'evento e' il ROUTER, non il portafoglio: serve il `from` della
transazione (lezione gia' scritta in chi_vende_nel_dump.py).
Identita': NON si contano gli indirizzi, si contano le ENTITA' (stessi pool
negli stessi blocchi = una mano sola), lezione del 23/10 sulla flotta.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")

ult=int(rpc("eth_blockNumber",[]),16)
tx=collections.OrderedDict()
for b in range(ult-1500, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[MODL],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        tx.setdefault(L["transactionHash"], (L["topics"][1], int(L["blockNumber"],16)))
print(f"{len(tx)} transazioni con mosse di liquidita'")

chi=collections.Counter(); pool_di=collections.defaultdict(set); blocchi_di=collections.defaultdict(set)
for h,(pid,bn) in list(tx.items())[:260]:
    t=rpc("eth_getTransactionByHash",[h])
    if not t: continue
    f=t["from"].lower(); chi[f]+=1; pool_di[f].add(pid); blocchi_di[f].add(bn)
print(f"   lette {sum(chi.values())} transazioni | indirizzi distinti: {len(chi)}")
print("   i piu' attivi:")
for k,v in chi.most_common(6):
    print(f"      {k[:20]}…  {v:>3} mosse su {len(pool_di[k])} pool")
q=sum(v for _,v in chi.most_common(3))/max(sum(chi.values()),1)
print(f"\n   quota dei primi 3 indirizzi: {q:.0%}")
print("   -> " + ("POCHE MANI: gara di velocita', non entriamo" if q>0.6 else
      "MOLTE MANI: mestiere aperto, vale misurare se rende"))
