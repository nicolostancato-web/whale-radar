# -*- coding: utf-8 -*-
"""Un'istantanea di CHI sorvegliamo, con l'ora e il blocco.

Perche' serve. La copertura — quante delle liquidazioni che avvengono cadono
su posizioni nostre, armate e con la vendita pronta — l'avevo misurata
confrontando la lista di OGGI con liquidazioni di 88 giorni fa. Dava 20,6%,
e quel numero e' strutturalmente sbagliato: chi e' caduto allora e' stato
liquidato, la liquidazione gli ha ALZATO la salute, e cosi' e' uscito dalla
nostra lista di oggi. Stavo misurando «quanti dei caduti sono ancora
malati», che non e' la domanda.

Controprova che il confine non c'entra: il 100% delle vittime era sotto
salute 1,12 un'ora prima di cadere, e il 94% lo era un giorno prima
(agents/da_che_salute_cadono.py). La finestra prende tutti.

La copertura vera si misura solo IN AVANTI: si fotografa chi sorvegliamo
ADESSO, e si guarda su quali cadute future si posa. Da qui in poi ogni
liquidazione e' una prova.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
from pescatore import AMMESSI
D="data/liquidazioni"
DOVE=f"{D}/istantanee"
os.makedirs(DOVE, exist_ok=True)
def blocco():
    try:
        c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber",
                      "params":[]}).encode()
        r=urllib.request.Request("https://ethereum-rpc.publicnode.com",data=c,
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        return int(json.load(urllib.request.urlopen(r,timeout=10))["result"],16)
    except Exception: return None
co=json.load(open(f"{D}/composizione.json"))
VP=json.load(open(f"{D}/vendite_pronte.json"))
try: corta={x["indirizzo"].lower():x for x in json.load(open(f"{D}/lista_corta.json"))}
except Exception: corta={}
armate=[u for u,v in co.items() if v["garanzia_principale"].lower() in AMMESSI]
pronte=[u for u in armate
        if (VP.get(u) or VP.get(u.lower()) or {}).get("chiamata")
        or (VP.get(u) or VP.get(u.lower()) or {}).get("stesso")]
b=blocco()
ora=int(time.time())
nome=f"{DOVE}/{ora}.json"
json.dump({"quando":ora,"blocco":b,
           "armate":sorted(a.lower() for a in armate),
           "pronte":sorted(p.lower() for p in pronte)},
          open(nome,"w"))
# si tengono le ultime 400 istantanee: bastano per settimane
vecchie=sorted(os.listdir(DOVE))
for f in vecchie[:-400]:
    try: os.remove(f"{DOVE}/{f}")
    except OSError: pass
print(f"   istantanea al blocco {b}: {len(armate)} armate, {len(pronte)} pronte")
print(f"   ({len(os.listdir(DOVE))} istantanee in archivio)")
