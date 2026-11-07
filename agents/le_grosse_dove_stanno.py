"""Le liquidazioni GROSSE stanno in cima al blocco?

Le tre misurate erano piccole (7-44 EUR). I soldi pero' stanno nelle grosse,
e sono quelle per cui vale la pena combattere. Se le grosse sono in cima e
le piccole no, la gara e' chiusa dove conta e aperta dove non conta —
che sarebbe il risultato peggiore e piu' facile da non vedere.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
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
WETH="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
USDC="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
for bn in (26279102, 26286758):
    r=chiama("eth_getLogs",[{"fromBlock":hex(bn),"toBlock":hex(bn),
                             "address":POOL,"topics":[LIQ]}])
    if not r: print(f"   blocco {bn}: log non ottenuti"); continue
    for x in r:
        gar="0x"+x["topics"][1][-40:]
        d=x["data"][2:]; q=int(d[64:128],16) if len(d)>=128 else 0
        val = q/1e18*eth*EUR if gar==WETH else (q/1e6*EUR if gar==USDC else None)
        rc=chiama("eth_getTransactionReceipt",[x["transactionHash"]])
        bl=chiama("eth_getBlockByNumber",[hex(bn), False])
        if not rc or not bl: continue
        idx=int(rc["transactionIndex"],16); n=len(bl.get("transactions",[]))
        pz=int(rc.get("effectiveGasPrice","0x0"),16)/1e9
        base=int(bl.get("baseFeePerGas","0x0"),16)/1e9
        print(f"   blocco {bn}  garanzia {val:,.0f} EUR" if val else f"   blocco {bn}")
        print(f"      posizione {idx} su {n}  ({idx/n*100:.0f}% del blocco)")
        print(f"      gas pagato {pz:.3f} gwei contro base {base:.3f}  "
              f"(mancia {pz-base:+.3f})")
        print(f"      -> {'IN CIMA: gara chiusa' if idx<=2 else 'non in cima'}")
