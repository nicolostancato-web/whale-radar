# IL SEGNO NEI DATI POST-DIPLOMA E' OPPOSTO A QUELLO DELLA CURVA (23/10).
# Prova nei due versi, stesso blocco: "acquisto"(a0<0) -> "vendita" rende +0,72%,
# il verso opposto -1,01%. Simmetrici = e' lo SPREAD. Il verso che GUADAGNA e'
# quello di chi lo incassa, quindi a0<0 e' una VENDITA (prezzo basso, il bid) e
# a0>0 e' un ACQUISTO (prezzo alto, l'ask). Con l'etichetta vecchia si entrava
# dalla parte favorevole e la strategia sembrava migliore di quello che e'.
"""Strategia del raddoppio col segno CORRETTO. Costo = spread misurato, non dichiarato."""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); SCAD=int(24*3600/BLOCCO)
CREATORE=0.02   # tassa del creatore, dichiarata; lo spread e' gia' nei prezzi

def giro(acquisto_e):
    res=[]
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip or len(s)<4: continue
                P=[(b,abs(a0/a1),(a0<0)) for b,a0,a1,_ in s if a1!=0 and a0!=0]
                if len(P)<4: continue
                ini=next(((b,p) for b,p,sg in P if b>=dip+RITARDO and sg==acquisto_e),None)
                if not ini: continue
                b0,p0=ini; mult=None; ult=None
                for b,p,sg in P:
                    if b<=b0: continue
                    if b>b0+SCAD: break
                    if sg==acquisto_e: continue      # si esce sull'altra parte del libro
                    ult=p
                    if p>=2*p0: mult=2.0; break
                if mult is None: mult = 0.0 if ult is None else ult/p0
                res.append(mult*(1-CREATORE)-1)
    return res

for et,sg in (("ETICHETTA VECCHIA (a0<0 = acquisto)", True),
              ("ETICHETTA CORRETTA (a0>0 = acquisto)", False)):
    r=giro(sg)
    m=st.mean(r)*100; e=1.96*st.stdev(r)/len(r)**0.5*100
    print(f"   {et:<40} {m:+6.1f}% +/-{e:4.1f}  mediana {st.median(r)*100:+6.1f}%  n={len(r)}")
