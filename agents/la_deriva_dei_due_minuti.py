"""L'UNICO numero che manca: di quanto scende una diplomata in due minuti?

Scoperta di stanotte: le commissioni sono certe (+2,09% +/- 0,09), tutta
l'incertezza sta nella deriva del prezzo (-1,35% +/- 0,81). Quindi non serve
una prova in avanti da 300 giorni: serve misurare LA DERIVA su piu' monete.

Questa misura non richiede una posizione valida, solo due prezzi, quindi entrano
anche le monete scartate prima (profondita' non stimabile, pochi scambi).
Come l'LP subisce il prezzo: V = V0*sqrt(r). Quindi si misura sqrt(r)-1.
Segno: a0<0 = VENDITA (verificato nei due versi). Si entra a fine primo minuto
dal diploma e si esce due minuti dopo, sull'ultima stampa di VENDITA.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO)
d2=[]; scartate=0
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip: continue
            P=[(b,abs(a0/a1),a0<0) for b,a0,a1,_ in s if a1 and a0]
            if len(P)<3: scartate+=1; continue
            b_ent=dip+RITARDO
            ent=next((p for b,p,_v in P if b>=b_ent), None)
            if ent is None or ent<=0: scartate+=1; continue
            usc=None
            for b,p,v in P:
                if b_ent<b<=b_ent+DUE and v: usc=p
            if usc is None: scartate+=1; continue
            d2.append(max((usc/ent)**0.5-1,-1.0))
n=len(d2); sd=st.stdev(d2)
print(f"monete con due prezzi utili: {n:,}  (scartate {scartate:,})")
print(f"   deriva a due minuti (come la subisce chi mette liquidita'):")
print(f"      media {st.mean(d2)*100:+.3f}%  +/- {1.96*sd/n**0.5*100:.3f}   mediana {st.median(d2)*100:+.3f}%")
comm=2.09; e_c=0.09
m=st.mean(d2)*100; e_p=1.96*sd/n**0.5*100
lo=comm-e_c+m-e_p; hi=comm+e_c+m+e_p
print(f"\n   NETTO = commissioni (+2,09 +/- 0,09) + deriva ({m:+.2f} +/- {e_p:.2f})")
print(f"      = {comm+m:+.2f}%   intervallo [{lo:+.2f}% , {hi:+.2f}%]")
print("   -> " + ("POSITIVO anche nel caso peggiore" if lo>0 else
      "il bordo inferiore e' ancora sotto zero: serve piu' campione"))
