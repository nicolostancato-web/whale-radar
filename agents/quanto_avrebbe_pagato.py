# -*- coding: utf-8 -*-
"""Quanto avrebbero pagato gli ultimi 9 giorni, se fossimo stati armati.

Non e' una stima: ogni liquidazione vera porta scritto nel log il debito
che e' stato chiuso. Il premio e' il 7,00% letto dal protocollo su quello.
Si convertono gli importi coi decimali VERI di ogni gettone e coi prezzi
dell'oracolo Aave -- mai assunti.

Lezione applicata: un importo senza la sua moneta non e' un numero.
"""
import json
PR={k.lower():v for k,v in json.load(open("data/liquidazioni/prezzi_oracolo.json")).items()}
# i decimali li porta il file dell'oracolo, letti dalla catena: niente
# tabella scritta a mano, che invecchia e sbaglia in silenzio.
DEC={k:v["decimali"] for k,v in PR.items()}
PRZ={k:v["prezzo_usd"] for k,v in PR.items()}
TET=json.load(open("data/liquidazioni/tetti.json"))
D=json.load(open("data/liquidazioni/caduti.json"))
deb=json.load(open("data/liquidazioni/debitori.json"))
nostri=set(x.lower() for x in (deb if isinstance(deb,list) else deb.keys()))
sconosciuti=set(); righe=[]
for e in D["eventi"]:
    a=e["debito"].lower(); g=e["garanzia"].lower()
    grezzo=int(e["dati"][2:66],16)
    if a not in DEC or a not in PR:
        sconosciuti.add(a); continue
    usd=grezzo/10**DEC[a]*PRZ[a]
    vendibile = g in TET
    righe.append({"u":e["utente"].lower(),"b":e["blocco"],"usd":usd,
      "premio":usd*0.07,"nostro":e["utente"].lower() in nostri,
      "vendibile":vendibile,"gar":g})
tot=sum(r["premio"] for r in righe)
nos=sum(r["premio"] for r in righe if r["nostro"])
vnd=sum(r["premio"] for r in righe if r["vendibile"])
nv =sum(r["premio"] for r in righe if r["nostro"] and r["vendibile"])
G=D["giorni"]
print(f"   {len(righe)} liquidazioni decodificate su {len(D['eventi'])} "
      f"({len(sconosciuti)} gettoni che non so convertire: saltati, non stimati)")
print(f"   finestra: {G} giorni\n")
print(f"   PREMIO LORDO TOTALE del mercato      EUR {tot:>12,.0f}   ({tot/G:>8,.0f}/giorno)")
print(f"   ...di cui su garanzie che so vendere EUR {vnd:>12,.0f}   ({vnd/G:>8,.0f}/giorno)")
print(f"   ...di cui su debitori NOSTRI         EUR {nos:>12,.0f}   ({nos/G:>8,.0f}/giorno)")
print(f"   ...NOSTRI e vendibili = aggredibile  EUR {nv:>12,.0f}   ({nv/G:>8,.0f}/giorno)\n")
righe.sort(key=lambda r:-r["premio"])
print("   le 12 piu' grosse:")
for r in righe[:12]:
    tag=("NOSTRO " if r["nostro"] else "       ")+("vendibile" if r["vendibile"] else "NO vendita")
    print(f"     EUR {r['premio']:>10,.0f}  su debito EUR {r['usd']:>12,.0f}  {r['u'][:10]}  {tag}")
mediana=sorted(r["premio"] for r in righe)[len(righe)//2]
print(f"\n   mediana del premio per liquidazione: EUR {mediana:,.0f}")
print(f"   quante valgono piu' di EUR 50: {sum(1 for r in righe if r['premio']>50)} su {len(righe)}"
      f"  ({sum(1 for r in righe if r['premio']>50)/G:.1f}/giorno)")
json.dump({"giorni":G,"tot":tot,"vendibile":vnd,"nostri":nos,"aggredibile":nv,
  "n":len(righe),"mediana":mediana},open("data/liquidazioni/avrebbe_pagato.json","w"),indent=1)
if sconosciuti: print("\n   gettoni saltati:", ", ".join(sorted(sconosciuti)))
