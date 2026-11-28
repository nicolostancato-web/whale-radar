"""Quanto resta davvero al liquidatore, dopo la gara per entrare nel blocco.

Su Ethereum il premio di una liquidazione viene in gran parte ribattuto via
in commissione di priorita' ai costruttori di blocco. Il guadagno netto e'
premio MENO il costo pagato per vincere la corsa, e quel costo sta nelle
ricevute: gas usato x prezzo effettivo, piu' eventuali pagamenti diretti
al validatore del blocco (il modo tipico di pagare in queste gare).
"""
import sys, json, time, urllib.request
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=8):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d: return d["result"]
            except Exception: pass
        time.sleep(0.5*(g+1))
    return None
def spot(s):
    r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                             headers={"user-agent":"Mozilla/5.0"})
    return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
eth=spot("ETHUSDT"); EUR=1/1.08
NOTE={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH",18,eth),
      "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC",6,1.0)}
ult=int(chiama("eth_blockNumber"),16)
ev=[]; fal=0; fin=0
b=ult-7200*3
while b<ult:
    f=min(b+199,ult)
    r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                             "address":POOL,"topics":[LIQ]}])
    fin+=1
    if r is None: fal+=1
    else: ev+=r
    b=f+1; time.sleep(0.12)
print(f"   finestre {fin}, fallite {fal} ({fal/fin*100:.0f}%) | eventi {len(ev)}\n")
for x in ev:
    h=x["transactionHash"]
    r=chiama("eth_getTransactionReceipt",[h])
    if not r: print(f"   {h[:14]}: ricevuta non ottenuta"); continue
    gas=int(r["gasUsed"],16); pz=int(r.get("effectiveGasPrice","0x0"),16)
    costo=gas*pz/1e18*eth*EUR
    bl=chiama("eth_getBlockByNumber",[r["blockNumber"], False])
    vali=(bl or {}).get("miner","?")
    # pagamento diretto al validatore dentro la stessa transazione
    diretto=0.0
    for L in r.get("logs",[]):
        pass
    gar="0x"+x["topics"][1][-40:]
    d=x["data"][2:]
    q=int(d[64:128],16) if len(d)>=128 else 0
    val=None
    if gar in NOTE:
        n,dec,p=NOTE[gar]; val=q/10**dec*p*EUR
    prem5 = val*0.05 if val else None
    print(f"   {h[:14]}  garanzia {val:,.0f} EUR" if val else f"   {h[:14]}  garanzia ?")
    print(f"      gas {gas:,} x {pz/1e9:.2f} gwei = {costo:,.2f} EUR di costo")
    if prem5:
        print(f"      premio al 5% = {prem5:,.2f} EUR  ->  "
              f"netto {prem5-costo:+,.2f} EUR  "
              f"({'conviene' if prem5>costo else 'NON conviene'})")
    print(f"      validatore {str(vali)[:20]}")
