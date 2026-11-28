# -*- coding: utf-8 -*-
"""La cassa e' cambiata? E' il controllo che non dipende da nessuno dei
nostri strumenti.

Tutta la nostra strumentazione puo' mentire insieme: la sentinella potrebbe
non accorgersi di un'inclusione, il pescatore potrebbe non scrivere il flag,
l'email potrebbe non partire. Ma se i soldi sono arrivati, il saldo della
cassa lo dice, e non c'e' niente da credere.

Si guardano i gettoni che possiamo incassare come premio: il debito ripagato
arriva nella valuta del debito, quindi uno di questi.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
from keccak import firma
CASSA="0x055e75aEaCF141c3118d039D5E099a821152eB66"
U="https://ethereum-rpc.publicnode.com"
SEL=firma("balanceOf(address)")[2:10]
D="data/liquidazioni"
PR=json.load(open(f"{D}/prezzi_oracolo.json"))
NOMI={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH",
"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC","0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT",
"0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f":"GHO","0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"weETH",
"0x9d39a5de30e57443bff2a8307a4256c8797a3497":"sUSDe","0xc139190f447e929f090edeb554d95abb8b18ac1c":"USDtb",
"0x4c9edd5852cd905f086c759e8383e09bff1e68b3":"USDe","0x6b175474e89094c44da98b954eedeac495271d0f":"DAI"}
def rpc(m,p):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(2):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3)
    return None
ora={}
eth=rpc("eth_getBalance",[CASSA,"latest"])
ora["ETH"]=int(eth,16)/1e18 if eth else None
for a,n in NOMI.items():
    v=rpc("eth_call",[{"to":a,"data":"0x"+SEL+CASSA[2:].zfill(64)},"latest"])
    p=PR.get(a)
    if v and v!="0x" and p:
        q=int(v,16)/10**p["decimali"]
        if q>0: ora[n]=q
    time.sleep(0.06)
F=f"{D}/cassa.json"
prima=json.load(open(F)) if os.path.exists(F) else None
val=0.0
for n,q in ora.items():
    if n=="ETH": val+=q*PR["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"]["prezzo_usd"]
    else:
        for a,nn in NOMI.items():
            if nn==n and a in PR: val+=q*PR[a]["prezzo_usd"]
print(f"   cassa {CASSA[:14]} — valore totale circa ${val:,.2f}")
for n,q in sorted(ora.items(), key=lambda x:-(x[1] or 0)):
    print(f"     {n:<8} {q:,.8f}".rstrip("0").rstrip("."))
if prima:
    cambi=[]
    for n,q in ora.items():
        q0=(prima.get("saldi") or {}).get(n, 0)
        if abs(q-q0) > max(1e-12, abs(q0)*1e-9): cambi.append((n,q0,q))
    for n,q in (prima.get("saldi") or {}).items():
        if n not in ora and q: cambi.append((n,q,0))
    if cambi:
        print(f"\n   *** LA CASSA E' CAMBIATA dall'ultimo controllo "
              f"({prima.get('quando_leggibile','?')}) ***")
        for n,q0,q1 in cambi:
            print(f"     {n}: {q0:,.8f} -> {q1:,.8f}")
    else:
        print(f"\n   nessun cambiamento dall'ultimo controllo "
              f"({prima.get('quando_leggibile','?')})")
json.dump({"quando":int(time.time()),
           "quando_leggibile":time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime()),
           "saldi":ora,"valore_usd":round(val,2)}, open(F,"w"), indent=1)
