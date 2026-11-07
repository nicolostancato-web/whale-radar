"""Il giro istantaneo e' positivo: segno rovesciato o pedaggio vero?

La prova che decide, gia' imparata: misurare NEI DUE VERSI.
   verso A: compro su stampa di ACQUISTO, vendo su stampa di VENDITA
   verso B: compro su stampa di VENDITA, vendo su stampa di ACQUISTO
Un PEDAGGIO vero rende NEGATIVI tutti e due (si paga lo spread in entrambi).
Un SEGNO ROVESCIATO rende uno positivo e l'altro negativo, simmetrici.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO)

A=[]; B=[]
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip or len(s)<4: continue
            P=[(b,abs(a0/a1),a0<0) for b,a0,a1,_ in s if a1!=0 and a0!=0]
            for i,(b,p,acq) in enumerate(P):
                if b < dip+RITARDO: continue
                for j in range(i+1,min(i+12,len(P))):
                    bj,pj,aj=P[j]
                    if bj!=b: break          # SOLO stesso blocco: niente movimento di prezzo
                    if aj==acq: continue
                    (A if acq else B).append(pj/p-1)
                    break
            if len(A)+len(B) > 60000: break

for nome,v in (("A  acquisto -> vendita", A), ("B  vendita -> acquisto", B)):
    if len(v)<50: print(f"   {nome}: troppo pochi ({len(v)})"); continue
    m=st.mean(v)*100; e=1.96*st.stdev(v)/len(v)**0.5*100
    print(f"   {nome:<26} n={len(v):>6,}  media {m:+6.2f}% +/-{e:4.2f}  mediana {st.median(v)*100:+6.2f}%")
if len(A)>50 and len(B)>50:
    sa,sb=st.mean(A),st.mean(B)
    print()
    if sa>0 and sb<0 or sa<0 and sb>0:
        print(f"   -> SIMMETRICI ({sa*100:+.2f} / {sb*100:+.2f}): e' lo SPREAD, non un guadagno.")
        print("      Il verso positivo e' quello di chi INCASSA lo spread (il gestore),")
        print("      non quello di chi lo paga. Il costo vero per noi e' il verso negativo.")
    else:
        print(f"   -> concordi ({sa*100:+.2f} / {sb*100:+.2f}): pedaggio vero in entrambi i versi.")
