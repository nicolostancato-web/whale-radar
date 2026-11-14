"""La commissione dei pool dove si muove la liquidita' OGGI.

Il Donate vale l'11% del gas: morto come canale. Ma gli LP incassano anche la
commissione NORMALE del pool, che non passa da Donate. Se e' zero come su Pons,
il mestiere del mercante non esiste; se e' >0, esiste.
Initialize(id indexed, currency0 indexed, currency1 indexed,
           fee, tickSpacing, hooks, sqrtPriceX96, tick)
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None

ult=int(rpc("eth_blockNumber",[]),16)
fee_di={}; hook_di={}; scambi=collections.Counter()
for b in range(ult-20000, ult, 100):
    a=hex(min(b+99,ult))
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":a}]) or []:
        d=L["data"][2:]
        fee_di[L["topics"][1]] = int(d[0:64],16)
        hook_di[L["topics"][1]] = "0x"+d[128+24:192]
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":a}]) or []:
        scambi[L["topics"][1]] += 1

print(f"pool nati nella finestra (~31 min): {len(fee_di)} | pool con scambi: {len(scambi)}")
c=collections.Counter(fee_di.values())
print("\n   commissione dichiarata alla nascita (centomillesimi):")
for f,n in c.most_common():
    et = "DINAMICA (decide l'hook)" if f==0x800000 else f"{f/10000:.2f}%"
    print(f"      {f:>9}  = {et:<26} {n} pool")
hk=collections.Counter(hook_di.values())
print("\n   hook agganciati:")
for h,n in hk.most_common(4):
    print(f"      {h}  {n} pool  {'<- NESSUN hook' if h=='0x'+'0'*40 else ''}")
# incrocio: i pool che scambiano di piu' hanno commissione?
print("\n   i 6 pool piu' scambiati fra quelli nati ora:")
for pid,n in scambi.most_common(20):
    if pid in fee_di:
        f=fee_di[pid]
        print(f"      {pid[:16]}…  {n:>4} scambi  fee={f} ({'dinamica' if f==0x800000 else f'{f/10000:.2f}%'})")
