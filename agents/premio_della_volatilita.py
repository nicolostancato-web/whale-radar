"""Quanto si fa pagare l'incertezza, rispetto a quanta ne arriva davvero.

DVOL = volatilita' a 30 giorni prezzata dalle opzioni (in % annue).
Realizzata = quella che poi si e' verificata nei 30 giorni SUCCESSIVI.
La differenza e' il premio: se e' sistematicamente positiva, chi vende
protezione viene pagato per un rischio che in media non si materializza.

Attenzione (lezioni gia' pagate):
  - finestre NON sovrapposte: 30 giorni di distanza l'una dall'altra;
  - l'unita' indipendente e' la finestra, e BTC/ETH nella stessa finestra
    NON sono due osservazioni (si muovono insieme): si misurano separati
    e poi si guarda se concordano;
  - la realizzata va misurata DOPO l'istante in cui leggo l'implicita.
"""
import json, math, statistics as st
GIORNI=30; ORE=GIORNI*24
def carica(m):
    iv={int(x["t"])//3600000*3600000: x["iv"] for x in json.load(open(f"data/volatilita/dvol_{m}.json"))}
    pr={int(x["t"]): x["c"] for x in json.load(open(f"data/volatilita/prezzo_{m}.json"))}
    return iv, pr
def realizzata(pr, ore, i, n):
    r=[]
    for j in range(i, i+n):
        a,b=ore[j], ore[j+1]
        if b-a != 3600000 or pr[a]<=0: return None
        r.append(math.log(pr[b]/pr[a]))
    if len(r)<n*0.9: return None
    return st.stdev(r)*math.sqrt(24*365)*100     # in % annue
for m in ("BTC","ETH"):
    iv, pr = carica(m)
    ore=sorted(set(iv) & set(pr))
    print(f"\n   {m}: {len(ore)} ore in comune "
          f"({(ore[-1]-ore[0])/86400000:.0f} giorni)")
    d=[]; coppie=[]
    i=0
    while i+ORE+1 < len(ore):
        rv=realizzata(pr, ore, i, ORE)
        if rv is None: i+=1; continue
        im=iv[ore[i]]
        d.append(im-rv); coppie.append((im,rv))
        i+=ORE                     # finestre non sovrapposte
    if len(d)<10:
        print(f"      solo {len(d)} finestre: non basta"); continue
    mi=st.mean(x[0] for x in coppie); mr=st.mean(x[1] for x in coppie)
    mm=st.mean(d); e=1.96*st.stdev(d)/math.sqrt(len(d))
    print(f"      {len(d)} finestre indipendenti da {GIORNI} giorni")
    print(f"      implicita media   {mi:6.2f}%")
    print(f"      realizzata media  {mr:6.2f}%")
    print(f"      PREMIO            {mm:+6.2f}  +/-{e:.2f}   "
          f"{'SOPRA ZERO' if mm-e>0 else 'non dimostrato'}")
    print(f"      finestre in cui l'implicita era piu' alta: "
          f"{sum(1 for x in d if x>0)}/{len(d)}")
    print(f"      peggiore {min(d):+.1f}   migliore {max(d):+.1f}")
