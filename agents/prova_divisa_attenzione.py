"""La prova registrata: lo stesso candidato su mercati e periodi mai visti insieme.

Due assi di divisione. I MERCATI sono l'unico asse davvero indipendente: gli
orizzonti condividono le entrate (lezione di stamattina), i periodi condividono
i mercati. Quindi entrambi, e devono reggere tutti e quattro.
"""
import json, glob, os, statistics as st
COSTO=0.00094
tutti=[]
for f in sorted(glob.glob("data/candele3/*.json")):
    d=json.load(open(f))
    if len(d)>1500: tutti.append((os.path.basename(f)[:-5], d))
A=[x for i,x in enumerate(tutti) if i%2==0]
B=[x for i,x in enumerate(tutti) if i%2==1]
def resa(mercati, campo, meta=None, oriz=4):
    v=[]
    for c,d in mercati:
        da,a = (0,len(d)) if meta is None else ((0,len(d)//2) if meta=="prima" else (len(d)//2,len(d)))
        storia=[x[campo] for x in d[:da]]; libero=0
        for k in range(da,a):
            storia.append(d[k][campo])
            if k<500 or k>=a-oriz or k<libero: continue
            fin=sorted(storia[-500:])
            if d[k][campo] < fin[int(0.95*len(fin))]: continue
            dire = 1 if d[k]["c"]>d[k-1]["c"] else -1
            v.append(-dire*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO)
            libero=k+oriz
    if len(v)<200: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
print("   cella                        resa netta            esito")
celle=[]
for campo,et in (("n","operazioni"),("v","volume")):
    for nome,merc,meta in (("mercati A",A,None),("mercati B",B,None),
                           ("periodo 1",tutti,"prima"),("periodo 2",tutti,"dopo")):
        r=resa(merc,campo,meta)
        if not r: print(f"   {et} / {nome:<12} dati insufficienti"); continue
        m,e,n=r
        ok = m-e>0
        celle.append((et,nome,m,e,ok))
        print(f"   {et:<11} / {nome:<10} {m:+7.4f}% +/-{e:6.4f} n={n:<6} "
              f"{'SOPRA ZERO' if ok else ('positivo ma non dimostrato' if m>0 else 'NEGATIVO')}")
for campo in ("operazioni","volume"):
    c=[x for x in celle if x[0]==campo]
    pos=sum(1 for x in c if x[2]>0); sopra=sum(1 for x in c if x[4])
    print(f"\n   {campo}: {pos}/4 celle positive, {sopra}/4 sopra zero -> "
          f"{'PASSA' if pos==4 and sopra>=3 else 'NON PASSA'}")
