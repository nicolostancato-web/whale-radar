"""Due mesi di liquidazioni, non quattro occasioni.

publicnode accetta finestre da 10.000 blocchi: 60 giorni sono ~44 chiamate
per protocollo invece di 2.200. Il valore della garanzia sta gia' dentro il
log, quindi non servono le ricevute.
Il gas e' trattato come costante dichiarata (0,50 EUR): misurato fra 0,03 e
1,06 su sei transazioni, e comunque trascurabile sulle occasioni che contano.
"""
import json, time, urllib.request, sys, collections, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
U="https://ethereum-rpc.publicnode.com"
GAS_EUR=0.50
def chiama(m,p=None,giri=5):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=60))
            if "result" in d and d["result"] is not None: return d["result"]
        except Exception: pass
        time.sleep(0.8*(g+1))
    return None
def spot(s):
    r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                             headers={"user-agent":"Mozilla/5.0"})
    return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
eth=spot("ETHUSDT"); btc=spot("BTCUSDT"); EUR=1/1.08
NOTE={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH",18,eth),
      "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC",6,1.0),
      "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT",6,1.0),
      "0x6b175474e89094c44da98b954eedeac495271d0f":("DAI",18,1.0),
      "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":("WBTC",8,btc),
      "0x83f20f44975d03b1b09e64809b757c47f942beea":("sDAI",18,1.0),
      "0xae78736cd615f374d3085123a210448e74fc6393":("rETH",18,eth),
      "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":("wstETH",18,eth),
      "0xbe9895146f7af43049ca1c1ae358b0541ea49704":("cbETH",18,eth)}
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
POOL={"aave_v3":"0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
      "spark":"0xc13e21b648a5ee794902342038ff3adab66be987"}
ult=int(chiama("eth_blockNumber"),16)
GIORNI=60; BL=GIORNI*7200
print(f"   {GIORNI} giorni = {BL:,} blocchi, finestre da 10.000\n")
log=[]; falliti=0; fin=0
for nome,ind in POOL.items():
    b=ult-BL
    while b<ult:
        f=min(b+9999, ult)
        r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                                 "address":ind,"topics":[LIQ]}])
        fin+=1
        if r is None: falliti+=1
        else:
            for x in r: x["_prot"]=nome
            log+=r
        b=f+1; time.sleep(0.25)
    print(f"   {nome}: fatto")
print(f"\n   finestre {fin}, fallite {falliti} ({falliti/fin*100:.0f}%)")
print(f"   eventi: {len(log)}")
pertx=collections.defaultdict(float); ign=0; prot={}
for x in log:
    gar="0x"+x["topics"][1][-40:]
    d=x["data"][2:]
    if len(d)<128: continue
    q=int(d[64:128],16)
    if gar not in NOTE: ign+=1; continue
    n,dec,pz=NOTE[gar]
    pertx[x["transactionHash"]] += q/10**dec*pz*EUR
    prot[x["transactionHash"]]=x["_prot"]
print(f"   occasioni (transazioni distinte): {len(pertx)}   "
      f"posizioni in monete ignote: {ign}")
cop=(fin-falliti)/fin
giorni_veri=GIORNI*cop
v=sorted(pertx.values(), reverse=True)
net=[x*0.05-GAS_EUR for x in v]
print(f"\n   copertura {cop*100:.0f}% -> {giorni_veri:.0f} giorni effettivi")
print(f"   occasioni al giorno: {len(v)/giorni_veri:.1f}")
for s in (10, 100, 1000):
    g=[x for x in net if x>=s]
    print(f"   occasioni che rendono oltre {s:>5} EUR: {len(g):>4}  "
          f"({len(g)/giorni_veri:.2f} al giorno)  somma {sum(g):>12,.0f} EUR")
print(f"\n   netto totale del mestiere in {giorni_veri:.0f} giorni: "
      f"{sum(x for x in net if x>0):,.0f} EUR")
print(f"   AL GIORNO, per TUTTI: {sum(x for x in net if x>0)/giorni_veri:,.0f} EUR")
print(f"   la piu' grossa: {max(net):,.0f} EUR")
