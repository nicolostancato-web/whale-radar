"""E se la liquidita' si mette per POCO tempo, come fanno i mercanti veri?

Tenendola per tutta la vita del pool si perde il 44-57%: le commissioni (3-10%)
non coprono il crollo (-63,7%). Ma i 63 mercanti veri ricentrano ogni ~50
blocchi e non restano fino alla morte della moneta.
Qui si misura, a orizzonte FISSO e dichiarato prima: commissioni incassate in
quella finestra meno il movimento di prezzo in quella finestra.
SUPPORTO COMUNE: una moneta entra in tabella solo se esiste a TUTTI gli
orizzonti, altrimenti ogni colonna parla di un insieme diverso.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); NOSTRO=0.0157
ORIZ=[("1 min",int(60/BLOCCO)),("2 min",int(120/BLOCCO)),("5 min",int(300/BLOCCO)),
      ("10 min",int(600/BLOCCO)),("20 min",int(1200/BLOCCO))]

def leggi():
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip or len(s)<30: continue
                P=[(b,abs(a0/a1),a0,a0<0) for b,a0,a1,_ in s if a1 and a0]
                if len(P)<20: continue
                yield dip,P

def profondita(P):
    xs=[]
    for i in range(1,len(P)):
        dp=(P[i][1]-P[i-1][1])/P[i-1][1]
        if 1e-5<abs(dp)<0.5 and abs(P[i][2])>1e-4: xs.append(2*abs(P[i][2])/abs(dp))
    return st.median(xs) if len(xs)>=10 else None

for fee,et in ((0.003,"0,30%"),(0.01,"1,00%")):
    righe={k:[] for k,_ in ORIZ}; comm={k:[] for k,_ in ORIZ}
    for dip,P in leggi():
        x=profondita(P)
        if not x: continue
        ini=next(((b,p) for b,p,_a,_s in P if b>=dip+RITARDO), None)
        if not ini: continue
        b0,p0=ini
        if p0<=0: continue
        q=min(NOSTRO/x,0.5)
        val={}
        ok=True
        for nome,salto in ORIZ:
            vol=0.0; ult=None
            for b,p,a0,vend in P:
                if b<=b0: continue
                if b>b0+salto: break
                vol+=abs(a0)
                if vend: ult=p
            if ult is None: ok=False; break
            c=vol*fee*q/NOSTRO
            val[nome]=(max((ult/p0)**0.5-1,-1.0)+c, c)
        if not ok: continue              # supporto comune
        for k,(v,c) in val.items(): righe[k].append(v); comm[k].append(c)
    n=len(righe[ORIZ[0][0]])
    print(f"\n   commissione {et} | {n} monete presenti a TUTTI gli orizzonti")
    print(f"      orizzonte   netto medio      mediana    di cui commissioni")
    for k,_ in ORIZ:
        v=righe[k]
        if not v: continue
        e=1.96*st.stdev(v)/len(v)**0.5*100
        print(f"      {k:<10} {st.mean(v)*100:+8.1f}% +/-{e:4.1f} {st.median(v)*100:+8.1f}%   {st.mean(comm[k])*100:+8.1f}%")
