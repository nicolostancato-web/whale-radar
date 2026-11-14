# -*- coding: utf-8 -*-
"""Ogni quanto arriva un premio grosso? Misurato su 90 giorni, non su 9.

Nasce da una domanda di Nicolo' (1/11): «la grossa arriva una volta ogni due
mesi, giusto?». Sui 9 giorni misurati prima la risposta non si poteva dare:
ZERO premi sopra 100.000 su 93 liquidazioni, e con zero osservazioni non si
stima una frequenza -- si puo' solo dire «piu' rara di 1 su 93».
Allungare la finestra e' l'unico modo di avere un numero invece di un limite.

Finestra di 50.000 blocchi per richiesta (provata: le due fonti la reggono,
20.000 su mevblocker a volte no). 90 giorni = 13 richieste.

RIPRENDIBILE: salva dopo ogni finestra. Se una fonte rifiuta si ferma e
riparte da dove era, senza buttare il lavoro fatto.
"""
import json, os, sys, time, urllib.request, itertools
sys.path.insert(0,"agents"); from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SIG=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
FONTI=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
_g=itertools.cycle([0,1])
FUORI="data/liquidazioni/novanta_giorni.json"
PASSO=50_000
GIORNI=90
def rpc(m,p):
    i=next(_g)
    for u in (FONTI[i],FONTI[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=60))
            if "result" in d: return d["result"]
        except Exception: pass
    return None
try: st=json.load(open(FUORI))
except Exception: st={"eventi":{}, "finestre":[]}
fatte=set(tuple(x) for x in st["finestre"])
testa=int(rpc("eth_blockNumber",[]),16)
fine=testa - GIORNI*7200
print(f"   testa {testa} | indietro fino a {fine} ({GIORNI} giorni)")
print(f"   gia' fatte {len(fatte)} finestre, {len(st['eventi'])} eventi\n")
a=testa
while a > fine:
    b=a; a=max(fine, a-PASSO)
    if (a,b) in fatte: continue
    lg=rpc("eth_getLogs",[{"address":POOL,"topics":[SIG],
        "fromBlock":hex(a),"toBlock":hex(b)}])
    if lg is None:
        print(f"   rifiuto su {a}-{b}: mi fermo e salvo (riprendibile)"); break
    for L in lg:
        # la CHIAVE e' tx+indice del log: la stessa transazione puo'
        # liquidare 8 posizioni, e sono 8 eventi ma UNA occasione di mercato
        st["eventi"][f"{L['transactionHash']}:{L['logIndex']}"]={
          "blocco":int(L["blockNumber"],16),"tx":L["transactionHash"],
          "garanzia":"0x"+L["topics"][1][-40:],"debito":"0x"+L["topics"][2][-40:],
          "utente":"0x"+L["topics"][3][-40:],"dati":L["data"]}
    st["finestre"].append([a,b])
    json.dump(st, open(FUORI,"w"))
    print(f"   {a}-{b}: {len(lg):>3} eventi  (totale {len(st['eventi'])})")
    time.sleep(1.2)
json.dump(st, open(FUORI,"w"))
print(f"\n   {len(st['eventi'])} eventi su {len(st['finestre'])} finestre")
