"""Il risultato di +1,5% vive TUTTO sulla commissione dell'1%. Quindi:
quanti pool DIPLOMATI hanno davvero l'1%?

Il marchio del diploma su questa chain e' l'hook 0xe5e7026… (gia' in memoria).
Qui si guardano gli Initialize recenti, si separano per hook, e si legge la
commissione dichiarata. Se i diplomati stanno allo 0,30%, il risultato e' zero
e la strada si chiude stasera.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
PONS="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None

ult=int(rpc("eth_blockNumber",[]),16); FIN=60000     # ~1,5 ore
pool={}
for b in range(ult-FIN, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        d=L["data"][2:]
        pool[L["topics"][1]] = (int(d[0:64],16), "0x"+d[128+24:192])
scambi=collections.Counter()
for b in range(ult-FIN, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        scambi[L["topics"][1]] += 1

print(f"{len(pool)} pool nati in ~{FIN*0.093/3600:.1f} ore\n")
per_hook=collections.defaultdict(collections.Counter)
att=collections.defaultdict(collections.Counter)
for pid,(fee,hook) in pool.items():
    per_hook[hook][fee] += 1
    if scambi.get(pid,0) >= 20: att[hook][fee] += 1
for hook,c in sorted(per_hook.items(), key=lambda x:-sum(x[1].values()))[:5]:
    et = "PONS (diploma)" if hook.lower()==PONS else ("nessun hook" if hook=="0x"+"0"*40 else "altro hook")
    print(f"   {hook}  {et}")
    for f,n in c.most_common(4):
        nome = "DINAMICA" if f==0x800000 else f"{f/10000:.2f}%"
        viva = att[hook].get(f,0)
        print(f"      fee {nome:<9} {n:>4} pool   di cui con >=20 scambi: {viva}")
tot_uno = sum(n for h,c in att.items() for f,n in c.items() if f==10000)
tot_att = sum(n for h,c in att.items() for n in c.values())
print(f"\n   pool VIVI con commissione 1,00%: {tot_uno}/{tot_att}" +
      (f"  ({tot_uno/tot_att:.0%})" if tot_att else ""))
