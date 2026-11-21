"""La prova in avanti che ho registrato NON PUO' decidere: con uno scarto di ~30
punti per posizione, 200 posizioni danno +/-4,2% e il valore cercato e' 0,6%.
Servirebbero ~14.000 posizioni = 300 giorni.

Ma la domanda giusta diventa: DOVE sta quel rumore? Il guadagno ha due pezzi,
le commissioni e il prezzo. Se le commissioni sono stabili e il caos e' tutto
nel prezzo, allora non serve un segnale migliore: serve TOGLIERE l'esposizione
al prezzo e tenere le commissioni.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); FEE=0.01; NOSTRO=0.0157

comm=[]; prez=[]
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
                if P[i][0]>b_ent: break
                dp=(P[i][1]-P[i-1][1])/P[i-1][1]
                if 1e-5<abs(dp)<0.5 and abs(P[i][2])>1e-4: xs.append(2*abs(P[i][2])/abs(dp))
            if len(xs)<3: continue
            prof=st.median(xs)
            ent=next((p for b,p,_a,_s in P if b>=b_ent), None)
            if ent is None: continue
            dentro=[(b,p,a0,v) for b,p,a0,v in P if b_ent<b<=b_usc]
            if not dentro: continue
            vol=sum(abs(a0) for _b,_p,a0,_v in dentro)
            usc=next((p for b,p,a0,v in reversed(dentro) if v), None)
            comm.append(FEE*vol*min(NOSTRO/prof,0.5)/NOSTRO)
            prez.append(-1.0 if usc is None else max((usc/ent)**0.5-1,-1.0))
n=len(comm)
def riga(nome,v):
    sd=st.stdev(v)
    print(f"   {nome:<28} media {st.mean(v)*100:+7.2f}%   scarto {sd*100:6.2f}   "
          f"+/- su {n} {1.96*sd/n**0.5*100:5.2f}   servono n={int((1.96*sd/0.005)**2):,} per +/-0,5%")
print(f"{n} posizioni\n")
riga("COMMISSIONI incassate", comm)
riga("PREZZO subito", prez)
riga("totale", [a+b for a,b in zip(comm,prez)])
r=st.stdev(prez)/st.stdev(comm)
print(f"\n   il prezzo e' {r:.0f} volte piu' rumoroso delle commissioni")
print("   -> " + ("TOGLIERE L'ESPOSIZIONE AL PREZZO e' il problema vero, non trovare un segnale"
      if r>3 else "il rumore e' in entrambi: non basta coprirsi"))
