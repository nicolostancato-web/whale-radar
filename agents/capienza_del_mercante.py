"""LA CAPIENZA, misurata insieme alla percentuale (regola del 23/10).

Un 5% che regge 200 euro e' una percentuale, non una macchina. Per il mestiere
del mercante la capienza ha forma chiusa:
   commissioni incassate = fee * volume * nostro/(profondita' + nostro)
   resa                  = commissioni / nostro = fee*volume/(profondita'+nostro)
quindi la resa DIMEZZA quando il nostro capitale eguaglia la profondita'.
Diverso dal lato compratore, dove lo scivolamento uccideva gia' a 5.000 dollari.
La parte di prezzo non cambia col capitale: subiamo lo stesso crollo a ogni taglia.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO); FEE=0.01
GAS_ETH=2*0.00001383; ETH_EUR=3030.0     # ~3.300 USD a 0,92

casi=[]
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
            pz = -1.0 if usc is None else max((usc/ent)**0.5-1,-1.0)
            casi.append((prof,vol,pz))
print(f"{len(casi)} posizioni | profondita' mediana {st.median([c[0] for c in casi]):.2f} ETH"
      f" = {st.median([c[0] for c in casi])*ETH_EUR:,.0f} EUR\n")
print("   capitale      per posizione       commissioni    euro guadagnati per posizione")
for eur in (52, 200, 1000, 5000, 15000, 50000):
    C=eur/ETH_EUR
    net=[]; com=[]
    for prof,vol,pz in casi:
        c=FEE*vol/(prof+C)
        net.append(pz+c-GAS_ETH/C)
        com.append(c)
    m=st.mean(net)*100; e=1.96*st.stdev(net)/len(net)**0.5*100
    print(f"   {eur:>6} EUR   {m:+7.2f}% +/-{e:4.2f}     {st.mean(com)*100:+6.2f}%      {st.mean(net)*eur:+8.2f} EUR")
print("\n   la resa cala come 1/(profondita'+capitale): dimezza quando il capitale")
print("   eguaglia la profondita' del pool. Il gas invece pesa di MENO salendo.")
