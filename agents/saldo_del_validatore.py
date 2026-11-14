"""Il liquidatore ha girato il premio al validatore?

Non potendo vedere dentro la transazione, si guarda il saldo del validatore
PRIMA e DOPO il blocco. Se nel blocco che contiene la liquidazione da 614
EUR il validatore ha incassato una cifra di quell'ordine, il premio e' stato
ribattuto via nella gara; se ha incassato spiccioli, e' rimasto al
liquidatore.

Limite dichiarato: la variazione include TUTTI i pagamenti del blocco, non
solo il nostro. Quindi serve come TETTO: se il totale del blocco e' piccolo,
il nostro pagamento e' per forza piu' piccolo ancora.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=6):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
def spot(s):
    r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                             headers={"user-agent":"Mozilla/5.0"})
    return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
eth=spot("ETHUSDT"); EUR=1/1.08
ult=int(chiama("eth_blockNumber"),16)
ev=[]; b=ult-7200*3
while b<ult:
    f=min(b+199,ult)
    r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                             "address":POOL,"topics":[LIQ]}])
    if r: ev+=r
    b=f+1; time.sleep(0.1)
print(f"   {len(ev)} liquidazioni\n")
for x in ev:
    d=x["data"][2:]
    q=int(d[64:128],16) if len(d)>=128 else 0
    gar="0x"+x["topics"][1][-40:]
    if gar=="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": val=q/1e18*eth*EUR
    elif gar=="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": val=q/1e6*EUR
    else: continue
    if val < 100: continue            # solo le grosse: le altre sono spiccioli
    bn=int(x["blockNumber"],16)
    bl=chiama("eth_getBlockByNumber",[hex(bn), False])
    if not bl: continue
    v=bl["miner"]
    a=chiama("eth_getBalance",[v, hex(bn-1)])
    c=chiama("eth_getBalance",[v, hex(bn)])
    if a is None or c is None:
        print(f"   blocco {bn}: saldo storico non esposto (serve nodo d'archivio)")
        continue
    dif=(int(c,16)-int(a,16))/1e18*eth*EUR
    print(f"   blocco {bn} | garanzia presa {val:,.0f} EUR")
    print(f"      il validatore ha incassato nel blocco INTERO: {dif:,.2f} EUR")
    print(f"      premio stimato al 5%: {val*0.05:,.2f} EUR")
    print(f"      -> {'il premio NON e stato girato: resta al liquidatore' if dif < val*0.05*0.5 else 'compatibile con un premio ribattuto via'}")
