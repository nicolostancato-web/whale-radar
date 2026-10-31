"""LA LEVA MAI PROVATA: concentrare la liquidita' in una fascia stretta.

Finora ho simulato una posizione su TUTTO l'arco dei prezzi, che e' il modo piu'
inefficiente. In v4 si puo' concentrare: per lo stesso capitale si incassano
molte piu' commissioni (a +/-30% circa sei volte), ma se il prezzo esce dalla
fascia non si incassa piu' nulla e si resta con la monetina intera.

Formule v3/v4, con p = prezzo della monetina in ether:
   valore dentro la fascia : L*(2*sqrt(p) - sqrt(pa) - p/sqrt(pb))
   sotto pa (tutto monetina): L*(1/sqrt(pa) - 1/sqrt(pb)) * p
   sopra pb (tutto ether)   : L*(sqrt(pb) - sqrt(pa))
Le commissioni maturano SOLO mentre il prezzo e' dentro la fascia, in
proporzione alla nostra quota della liquidita' li' presente.

RIGA DI TARATURA: una fascia larghissima (a=0,99) deve riprodurre il risultato
a tutto campo gia' misurato (+0,3% circa). Se non lo fa, le formule sono rotte.
"""
import gzip, glob, json, math, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); FEE=0.01
NOSTRO=0.0157; GAS=2*0.00001383/0.0157

def valore(L, p, pa, pb):
    if p <= pa:  return L*(1/math.sqrt(pa) - 1/math.sqrt(pb))*p
    if p >= pb:  return L*(math.sqrt(pb) - math.sqrt(pa))
    return L*(2*math.sqrt(p) - math.sqrt(pa) - p/math.sqrt(pb))

def prova(a):
    res=[]; dentro_q=[]
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip: continue
                P=[(b,abs(a0/a1),a0,a0<0) for b,a0,a1,_ in s if a1 and a0]
                if len(P)<10: continue
                b_ent=dip+RITARDO; b_usc=b_ent+DUE
                xs=[]
                for i in range(1,len(P)):
                    if P[i][0]>b_ent: break
                    dp=(P[i][1]-P[i-1][1])/P[i-1][1]
                    if 1e-5<abs(dp)<0.5 and abs(P[i][2])>1e-4: xs.append(2*abs(P[i][2])/abs(dp))
                if len(xs)<3: continue
                prof=st.median(xs)
                p0=next((p for b,p,_a,_v in P if b>=b_ent), None)
                if p0 is None or p0<=0: continue
                pa, pb = p0*(1-a), p0/(1-a)
                den = 2*math.sqrt(p0) - math.sqrt(pa) - p0/math.sqrt(pb)
                if den<=0: continue
                L = NOSTRO/den                       # nostra liquidita'
                Lp = prof/(2*math.sqrt(p0))          # liquidita' del pool (equivalente a tutto campo)
                quota = L/(L+Lp)
                vol_dentro=0.0; ult=None
                for b,p,a0,vend in P:
                    if b<=b_ent or b>b_usc: continue
                    if pa <= p <= pb: vol_dentro += abs(a0)
                    if vend: ult=p
                if ult is None:
                    res.append(-1.0-GAS); continue
                comm = FEE*vol_dentro*quota/NOSTRO
                fine = valore(L, ult, pa, pb)/NOSTRO - 1
                res.append(fine+comm-GAS)
                dentro_q.append(1.0 if pa<=ult<=pb else 0.0)
    n=len(res)
    return (n, st.mean(res)*100, st.median(res)*100, 1.96*st.stdev(res)/n**0.5*100,
            st.mean(dentro_q)*100 if dentro_q else 0)

print("   fascia      n     netto medio       mediana   uscita ancora dentro")
for a,et in ((0.99,"+/-99% (taratura)"),(0.80,"+/-80%"),(0.50,"+/-50%"),
             (0.30,"+/-30%"),(0.15,"+/-15%")):
    n,m,md,e,dq = prova(a)
    print(f"   {et:<18} {n:>5} {m:+8.2f}% +/-{e:4.2f} {md:+8.2f}%      {dq:5.1f}%")
