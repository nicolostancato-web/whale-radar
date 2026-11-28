"""Il +1,5% a due minuti esiste ancora nella meta' RECENTE dell'archivio?

Lezione gia' pagata: su questa chain il mercato e' peggiorato nel tempo. Una
media su tutto l'archivio puo' essere il ricordo di un periodo finito. Se il
risultato vive solo nella meta' vecchia, la prova in avanti fallira' e conviene
saperlo ora invece che fra quattro giorni.
Si divide per blocco di diploma in tre terzi e si guarda la tendenza.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); NOSTRO=0.0157
GAS=2*0.00001383/0.0157; FEE=0.01

righe=[]
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip or len(s)<30: continue
            P=[(b,abs(a0/a1),a0,a0<0) for b,a0,a1,_ in s if a1 and a0]
            if len(P)<20: continue
            b_ent=dip+RITARDO; b_usc=b_ent+DUE
            xs=[]
            for i in range(1,len(P)):
                if P[i][0] > b_ent: break
                dp=(P[i][1]-P[i-1][1])/P[i-1][1]
                if 1e-5<abs(dp)<0.5 and abs(P[i][2])>1e-4: xs.append(2*abs(P[i][2])/abs(dp))
            if len(xs)<3: continue
            prof=st.median(xs)
            ent=next((p for b,p,_a,_s in P if b>=b_ent), None)
            if ent is None: continue
            dentro=[(b,p,a0,v) for b,p,a0,v in P if b_ent<b<=b_usc]
            if not dentro: continue
            q=min(NOSTRO/prof,0.5)
            vol=sum(abs(a0) for _b,_p,a0,_v in dentro)
            usc=next((p for b,p,a0,v in reversed(dentro) if v), None)
            if usc is None: pz=-1.0; comm=0.0
            else: comm=vol*FEE*q/NOSTRO; pz=max((usc/ent)**0.5-1,-1.0)
            righe.append((dip, pz+comm-GAS, comm, prof))
righe.sort()
n=len(righe); t=n//3
print(f"{n} monete con una posizione valida a due minuti\n")
print("   terzo          n      netto medio        mediana   commissioni  profondita'")
for i,et in ((0,"piu' VECCHIO"),(1,"di mezzo"),(2,"piu' RECENTE")):
    g=righe[i*t:(i+1)*t] if i<2 else righe[2*t:]
    v=[x[1] for x in g]
    e=1.96*st.stdev(v)/len(v)**0.5*100
    print(f"   {et:<13} {len(v):>5}  {st.mean(v)*100:+8.2f}% +/-{e:4.2f} {st.median(v)*100:+8.2f}%   {st.mean([x[2] for x in g])*100:+7.2f}%   {st.median([x[3] for x in g]):.2f} ETH")
v=[x[1] for x in righe]
print(f"\n   tutto l'archivio: {st.mean(v)*100:+.2f}% +/- {1.96*st.stdev(v)/n**0.5*100:.2f}")
