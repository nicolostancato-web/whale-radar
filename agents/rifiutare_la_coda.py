"""Si puo' rifiutare in anticipo l'1% di monete che uccide il risultato?

La deriva non e' una media che scende: e' l'1,15% di monete senza compratore
che vale -100%. Se si riescono a scartare PRIMA di entrare, usando solo cio'
che si sa al primo minuto, il netto passa da +0,32% a quasi +2%.

Disciplina obbligatoria: la soglia si SCEGLIE sulla prima meta' e si VERIFICA
sulla seconda, mai vista. Cercando fra tante soglie si trova sempre qualcosa.
Indizi ammessi (tutti noti al minuto uno): quanti scambi, quante VENDITE,
volume, profondita'.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); FEE=0.01; NOSTRO=0.0157

righe=[]
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip: continue
            P=[(b,abs(a0/a1),a0,a0<0) for b,a0,a1,_ in s if a1 and a0]
            if len(P)<3: continue
            b_ent=dip+RITARDO
            prima=[(b,p,a0,v) for b,p,a0,v in P if b<=b_ent]
            ent=next((p for b,p,_a,_v in P if b>=b_ent), None)
            if ent is None or ent<=0 or not prima: continue
            n_sc=len(prima); n_vend=sum(1 for _b,_p,_a,v in prima if v)
            vol_pre=sum(abs(a0) for _b,_p,a0,_v in prima)
            dentro=[(b,p,a0,v) for b,p,a0,v in P if b_ent<b<=b_ent+DUE]
            usc=next((p for b,p,a0,v in reversed(dentro) if v), None)
            vol=sum(abs(a0) for _b,_p,a0,_v in dentro)
            pz = -1.0 if usc is None else max((usc/ent)**0.5-1,-1.0)
            comm = 0.0 if usc is None else FEE*vol*min(NOSTRO/max(vol_pre,1e-9),0.5)/NOSTRO
            righe.append((dip, n_sc, n_vend, vol_pre, pz+min(comm,0.1)))
righe.sort()
m=len(righe)//2
A,B=righe[:m],righe[m:]
def resa(g): 
    v=[x[4] for x in g]; return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
print(f"prima meta' (scelgo qui): {len(A)}  |  seconda meta' (verifico qui): {len(B)}\n")
print("   criterio (noto al minuto 1)          prima meta'          seconda meta' (MAI VISTA)")
base=resa(A); baseB=resa(B)
print(f"   {'tutte (nessun filtro)':<34} {base[0]:+6.2f}% +/-{base[1]:4.2f} n={base[2]:<5} {baseB[0]:+6.2f}% +/-{baseB[1]:4.2f} n={baseB[2]}")
cands=[("almeno 5 scambi", lambda x:x[1]>=5), ("almeno 10 scambi", lambda x:x[1]>=10),
       ("almeno 20 scambi", lambda x:x[1]>=20), ("almeno 1 vendita", lambda x:x[2]>=1),
       ("almeno 3 vendite", lambda x:x[2]>=3), ("almeno 5 vendite", lambda x:x[2]>=5),
       ("volume pre >= 0,5 ETH", lambda x:x[3]>=0.5), ("volume pre >= 2 ETH", lambda x:x[3]>=2.0)]
best=None
for nome,f in cands:
    a=[x for x in A if f(x)]; b=[x for x in B if f(x)]
    if len(a)<100 or len(b)<100: continue
    ra, rb = resa(a), resa(b)
    print(f"   {nome:<34} {ra[0]:+6.2f}% +/-{ra[1]:4.2f} n={ra[2]:<5} {rb[0]:+6.2f}% +/-{rb[1]:4.2f} n={rb[2]}")
    if best is None or ra[0]>best[1]: best=(nome,ra[0],rb[0],rb[1])
if best:
    print(f"\n   migliore sulla PRIMA meta': {best[0]} ({best[1]:+.2f}%)")
    print(f"   sulla seconda, mai vista:   {best[2]:+.2f}% +/- {best[3]:.2f}")
    print("   -> " + ("REGGE fuori campione" if best[2]-best[3] > 0 else
          "NON regge: il guadagno sulla prima meta' era la ricerca stessa"))
