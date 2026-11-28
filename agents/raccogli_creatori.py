"""Raccoglie i creatori di TUTTI i liquidatori, poco per volta.

Lezione del 28/10 sera: l'unita' giusta per dire «chi e' un professionista»
non e' il CONTRATTO ma il CREATORE. Su 8 contratti usa-e-getta c'erano 6
creatori: la rotazione esiste e va tolta prima di contare gli attori.
Stessa famiglia di «le righe non sono i casi».

Va piano: 8 richieste per giro, pausa di 4 secondi, stop al primo rifiuto.
"""
import json, time, urllib.request, collections, os
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
liq=set()
for e in ev:
    d=e["dati"][2:]
    if len(d)>=64*3: liq.add("0x"+d[64*2+24:64*3])
F="data/liquidazioni/creatori.json"
noti=json.load(open(F)) if os.path.exists(F) else {}
restano=[a for a in sorted(liq) if a not in noti]
print(f"   {len(liq)} liquidatori | {len(noti)} gia' risolti | {len(restano)} da fare")
presi=0
for a in restano[:8]:
    try:
        r=urllib.request.Request(f"https://eth.blockscout.com/api/v2/addresses/{a}",
                                 headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        d=json.load(urllib.request.urlopen(r, timeout=40))
    except Exception as e:
        print(f"   rifiuto su {a[:12]}: {str(e)[:36]} — mi fermo"); break
    noti[a]={"creatore":(d.get("creator_address_hash") or "").lower(),
             "nome":d.get("name"),"verificato":bool(d.get("is_verified"))}
    json.dump(noti, open(F,"w"))
    presi+=1
    time.sleep(4)
print(f"   risolti {presi} in questo giro | totale {len(noti)}/{len(liq)}")
# TRAPPOLA (vista il 28/10): alcune «fabbriche» sono condivise da tutti gli
# strumenti di sviluppo. Contratti di persone che non si conoscono risultano
# creati dallo stesso indirizzo. Vanno escluse o si raggruppano estranei.
FABBRICHE={
 "0x4e59b44847b379578588920ca78fbf26c0b4956c",  # deployer deterministico (Foundry)
 "0x0000000000ffe8b47b3e2130213b802212439497",  # immutable create2
 "0x7a0d94f55792c434d74a40883c6ed8545e406d12",  # create2 factory
}
cr=collections.Counter(v["creatore"] for v in noti.values()
                       if v.get("creatore") and v["creatore"] not in FABBRICHE)
cond=sum(1 for v in noti.values() if v.get("creatore") in FABBRICHE)
if cond: print(f"   {cond} contratti creati da fabbriche condivise: esclusi dal conteggio")
senza=sum(1 for v in noti.values() if not v.get("creatore"))
print(f"   {len(cr)} creatori distinti per {len(noti)-senza} contratti "
      f"({senza} senza creatore noto)")
for a,n in cr.most_common(6):
    if n>1: print(f"      {a[:26]}..  ha creato {n} contratti")
