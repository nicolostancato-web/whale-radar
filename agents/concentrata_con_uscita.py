"""Concentrare E USCIRE quando il prezzo lascia la fascia.

Concentrando, la mediana sale molto (+4,76%) ma la media crolla (-4,58%):
tutta la differenza e' la coda di chi resta dentro mentre la monetina muore.
I 63 mercanti veri non restano fermi: ricentrano ogni ~50 blocchi.

Qui si esce alla PRIMA stampa fuori fascia, al prezzo di quella stampa. La
perdita massima diventa cosi' la larghezza della fascia, non il 100%.
Niente sbirciata: la decisione usa solo il prezzo di quella stampa.
Si paga il gas DOPPIO quando si esce prima (si ricentra o si chiude).
"""
import gzip, glob, json, math, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); FEE=0.01
NOSTRO=0.0157; GAS=2*0.00001383/0.0157

def valore(L,p,pa,pb):
    if p<=pa: return L*(1/math.sqrt(pa)-1/math.sqrt(pb))*p
    if p>=pb: return L*(math.sqrt(pb)-math.sqrt(pa))
    return L*(2*math.sqrt(p)-math.sqrt(pa)-p/math.sqrt(pb))

def prova(a, esci):
    res=[]; usciti=0
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
                pa,pb=p0*(1-a), p0/(1-a)
                den=2*math.sqrt(p0)-math.sqrt(pa)-p0/math.sqrt(pb)
                if den<=0: continue
                L=NOSTRO/den; Lp=prof/(2*math.sqrt(p0)); q=L/(L+Lp)
                vol=0.0; fine=None; gas=GAS; fuori=False
                for b,p,a0,vend in P:
                    if b<=b_ent or b>b_usc: continue
                    if pa<=p<=pb: vol+=abs(a0)
                    elif esci:
                        fine=p; fuori=True; break        # si chiude alla stampa fuori fascia
                if fine is None:
                    ult=None
                    for b,p,a0,vend in P:
                        if b_ent<b<=b_usc and vend: ult=p
                    if ult is None: res.append(-1.0-GAS); continue
                    fine=ult
                if fuori: usciti+=1
                comm=FEE*vol*q/NOSTRO
                res.append(valore(L,fine,pa,pb)/NOSTRO-1+comm-gas)
    n=len(res)
    return (n, st.mean(res)*100, st.median(res)*100, 1.96*st.stdev(res)/n**0.5*100, usciti/n*100)

print("   fascia      uscita?      n     netto medio       mediana   usciti prima")
for a,et in ((0.50,"+/-50%"),(0.30,"+/-30%"),(0.15,"+/-15%"),(0.08,"+/-8%")):
    for esci,eu in ((False,"resta "),(True,"ESCE  ")):
        n,m,md,e,u = prova(a,esci)
        print(f"   {et:<10} {eu}  {n:>5} {m:+8.2f}% +/-{e:4.2f} {md:+8.2f}%   {u:5.1f}%")
