# -*- coding: utf-8 -*-
"""Chi cade davvero su Aave, e stava nel nostro laghetto?

La domanda vera non e' "quante posizioni sorvegliamo" ma "quante delle
posizioni che CADONO erano nostre". Si misura, non si stima.

Regola imparata: pochi colpi alla fonte, stop al primo rifiuto.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SIG=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
# fonti provate il 31/10: drpc da 400 su getLogs, publicnode chiude a 403 dopo
# due giri, llamarpc 525, 1rpc max 50 blocchi, nodies limita la finestra.
# Queste due reggono 4.000 blocchi con archivio di giorni:
FONTI=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
import itertools
_giro=itertools.cycle([0,1])
def rpc(m,p):
    # alterna le fonti: non si bruciano insieme
    i=next(_giro)
    for u in (FONTI[i],FONTI[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=40))
            if "result" in d: return d["result"]
            print(f"   rifiuto da {u}: {str(d.get('error'))[:90]}")
        except Exception as e:
            print(f"   {u}: {str(e)[:70]}")
    return None
testa=int(rpc("eth_blockNumber",[]),16)
print(f"   testa catena: {testa}")
PASSO=4000; GIRI=18          # ~72.000 blocchi = ~10 giorni
eventi=[]
for g in range(GIRI):
    a=testa-(g+1)*PASSO+1; b=testa-g*PASSO
    lg=rpc("eth_getLogs",[{"address":POOL,"topics":[SIG],
        "fromBlock":hex(a),"toBlock":hex(b)}])
    if lg is None:
        print(f"   fermato al giro {g}: la fonte ha detto no"); break
    for L in lg:
        eventi.append({"blocco":int(L["blockNumber"],16),
          "tx":L["transactionHash"],
          "garanzia":"0x"+L["topics"][1][-40:],
          "debito":"0x"+L["topics"][2][-40:],
          "utente":"0x"+L["topics"][3][-40:],
          "dati":L["data"]})
    print(f"   giro {g+1}/{GIRI}: blocchi {a}-{b} -> {len(lg)} liquidazioni")
    time.sleep(1.4)
if not eventi: print("   nessun evento"); sys.exit(1)
blocchi=sorted({e["blocco"] for e in eventi})
span=(max(blocchi)-min(blocchi)); giorni=span*12/86400
# un utente liquidato due volte nello stesso blocco e' UN caso, non due
casi={}
for e in eventi: casi[(e["utente"],e["blocco"])]=e
utenti=sorted({e["utente"] for e in eventi})
deb=json.load(open("data/liquidazioni/debitori.json"))
insieme=set(x.lower() for x in (deb if isinstance(deb,list) else deb.keys()))
corta=json.load(open("data/liquidazioni/lista_corta.json"))
cl=corta if isinstance(corta,list) else list(corta.keys())
def ind(x): return (x if isinstance(x,str) else x.get("utente","")).lower()
corta_s=set(ind(x) for x in cl)
sorv=set(json.load(open("data/liquidazioni/composizione.json")).keys())
sorv={s.lower() for s in sorv}
dentro=[u for u in utenti if u in insieme]
in_corta=[u for u in utenti if u in corta_s]
in_sorv=[u for u in utenti if u in sorv]
json.dump({"eventi":eventi,"giorni":round(giorni,1)},
  open("data/liquidazioni/caduti.json","w"),indent=1)
print()
print(f"   finestra misurata: {giorni:.1f} giorni, {len(eventi)} righe di evento")
print(f"   casi indipendenti (utente+blocco): {len(casi)}")
print(f"   utenti distinti caduti:            {len(utenti)}")
print(f"   ritmo: {len(casi)/giorni:.1f} casi/giorno, "
      f"{len(utenti)/giorni:.1f} utenti/giorno")
print()
print(f"   di questi {len(utenti)} caduti, quanti erano NOSTRI:")
print(f"     nei 5.262 debitori raccolti : {len(dentro)}  ({100*len(dentro)/len(utenti):.0f}%)")
print(f"     nei 140 della lista corta   : {len(in_corta)}  ({100*len(in_corta)/len(utenti):.0f}%)")
print(f"     negli 11 sorvegliati        : {len(in_sorv)}  ({100*len(in_sorv)/len(utenti):.0f}%)")
