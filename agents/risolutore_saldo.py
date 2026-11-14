"""0 su 42 in perdita e' un referto di guasto, non un risultato.

Il pezzo mancante: l'ether NATIVO non emette un evento di trasferimento, quindi
contando solo gli ERC20 si vedono le uscite del risolutore e non i suoi incassi.
Qui si guarda il saldo nativo prima e dopo il blocco, che include tutto.
(Il blocco puo' contenere altre sue transazioni: si tengono solo i blocchi dove
il risolutore compare una volta sola.)
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
FILL="0x78ad7ec0e9f89e74012afa58738b6b661c024cb0fd185ee2f616c0a28924bd66"
TRASF="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"
DEC={USDG:6, WETH:18}; EUR={USDG:0.92, WETH:3030.0}; ETH_EUR=3030.0
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
ult=int(rpc("eth_blockNumber",[]),16); FIN=120000; PASSO=3000
fills=[]
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"topics":[FILL],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        if len(L["topics"])>2:
            fills.append((L["transactionHash"], "0x"+L["topics"][2][-40:], int(L["blockNumber"],16)))
print(f"{len(fills)} riempimenti | ne esamino 50")
tot=[]
for h,solver,bn in fills[:50]:
    r=rpc("eth_getTransactionReceipt",[h])
    if not r: continue
    pri=rpc("eth_getBalance",[solver,hex(bn-1)]); dopo=rpc("eth_getBalance",[solver,hex(bn)])
    if not isinstance(pri,str) or not isinstance(dopo,str):
        print("   stato storico non disponibile a questa distanza"); break
    d_nat=(int(dopo,16)-int(pri,16))/1e18*ETH_EUR     # il gas e' gia' dentro
    netto=collections.Counter()
    for L in r["logs"]:
        if not L.get("topics") or L["topics"][0]!=TRASF or len(L["topics"])<3: continue
        tok=L["address"].lower(); da="0x"+L["topics"][1][-40:]; a="0x"+L["topics"][2][-40:]
        try: v=int(L["data"],16)
        except Exception: continue
        if da==solver or a==solver: netto[tok]+= v if a==solver else -v
    resid=[t for t,v in netto.items() if t not in DEC and abs(v)>0]
    if resid: continue
    erc=sum(v/10**DEC[t]*EUR[t] for t,v in netto.items() if t in DEC)
    tot.append(d_nat+erc)
if tot:
    tot.sort()
    print(f"\n   {len(tot)} riempimenti con magazzino azzerato, saldo nativo incluso:")
    print(f"      mediana {st.median(tot):+.4f} EUR | media {st.mean(tot):+.4f}")
    print(f"      peggiore {tot[0]:+.3f} | migliore {tot[-1]:+.3f} | positivi {sum(1 for x in tot if x>0)}/{len(tot)}")
    print("   -> " + ("ora ha senso: il mestiere rende poco ma rende" if st.median(tot)>0 else
          "ancora tutti negativi: manca ancora un pezzo, non concludere"))
