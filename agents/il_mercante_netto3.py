"""Profondita' del pool misurata dall'IMPATTO, che e' un rapporto.

Nell'archivio gli importi nativi sono gia' in ether e sqrtPrice e' grezzo:
mescolarli sbaglia la scala. L'impatto no: per prodotto costante, uno scambio
di a0 nativi su una riserva nativa x muove il prezzo di  dP/P ~ 2*a0/x,
quindi  x ~ 2*a0 / (dP/P).  Tutto in unita' d'archivio, niente conversioni.

Prezzo in unita' d'archivio: |a0/a1| = nativi per gettone (dritto, non inverso).
Segno: a0<0 = VENDITA (verificato nei due versi il 23/10).
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); NOSTRO=0.0157   # ether

def run(fee):
    netti=[]; comm=[]; prez=[]; quote=[]; prof=[]
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip or len(s)<30: continue
                P=[(b,abs(a0/a1),a0,a0<0) for b,a0,a1,_ in s if a1 and a0]
                if len(P)<20: continue
                # profondita' dall'impatto, mediana sugli scambi non minuscoli
                xs=[]
                for i in range(1,len(P)):
                    dp=(P[i][1]-P[i-1][1])/P[i-1][1]
                    if 1e-5 < abs(dp) < 0.5 and abs(P[i][2])>1e-4:
                        xs.append(2*abs(P[i][2])/abs(dp))
                if len(xs)<10: continue
                x=st.median(xs); prof.append(x)
                ini=next(((b,p) for b,p,_a,_s in P if b>=dip+RITARDO), None)
                if not ini: continue
                b0,p0=ini
                if p0<=0: continue
                quota=min(NOSTRO/x, 0.5); quote.append(quota)
                vol=0.0; ult=None
                for b,p,a0,vend in P:
                    if b<=b0: continue
                    vol+=abs(a0)
                    if vend: ult=p
                if ult is None: netti.append(-1.0); continue
                r=ult/p0
                c=vol*fee*quota/NOSTRO
                pz=max(r**0.5-1, -1.0)
                netti.append(pz+c); comm.append(c); prez.append(pz)
    n=len(netti)
    return (n, st.mean(netti)*100, st.median(netti)*100, 1.96*st.stdev(netti)/n**0.5*100,
            st.mean(comm)*100, st.median(comm)*100, st.median(prez)*100,
            st.median(quote)*100, st.median(prof))

print("   fee      n    netto medio      mediana  commissioni med/mediana  prezzo med  quota  profondita'")
for fee,et in ((0.003,"0,30%"),(0.01,"1,00%")):
    n,m,md,e,cm,cmd,p,q,pf = run(fee)
    print(f"   {et} {n:>5} {m:+8.1f}% +/-{e:4.1f} {md:+8.1f}%  {cm:+7.1f}% / {cmd:+6.1f}%  {p:+8.1f}%  {q:5.2f}%  {pf:.3f} ether")
