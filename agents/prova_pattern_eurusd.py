"""I pattern classici sull'EUR/USD, passati nel nostro strumento.

Regole dichiarate PRIMA di guardare:
  - entrata alla CHIUSURA della candela che genera il segnale (niente sbirciate)
  - uscita dopo N candele, fisse, dichiarate prima
  - costo di giro 0,05% (pedaggio misurato su gTrade; su trade.xyz e' 0,018%)
  - la soglia si sceglie sulla PRIMA META' e si verifica sulla SECONDA mai vista
  - RIGA DI TARATURA: entrate a caso devono dare circa -pedaggio
  - si riporta sempre l'intervallo, mai la sola media
"""
import json, statistics as st, random
D=json.load(open("data/mercati/EURUSD_X_1h.json"))
c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
COSTO=0.0005
print(f"{n:,} candele orarie EUR/USD\n")
def resa(ingressi, orizz):
    v=[]
    for i in ingressi:
        if i+orizz>=n: continue
        v.append((c[i+orizz]/c[i]-1)-COSTO)
    if len(v)<30: return None
    m=st.mean(v)*100; e=1.96*st.stdev(v)/len(v)**0.5*100
    return m,e,len(v)
def segnali(nome, f, meta):
    da,a = (0,n//2) if meta=="A" else (n//2,n)
    return [i for i in range(da+100,a) if f(i)]   # 100 = piu della finestra piu lunga (72)
REGOLE={
 "rottura massimo 24h":   lambda i: c[i] > max(h[i-24:i]),
 "rottura minimo 24h":    lambda i: c[i] < min(l[i-24:i]),
 "rottura massimo 72h":   lambda i: c[i] > max(h[i-72:i]),
 "ritorno: 3 cali di fila": lambda i: c[i]<c[i-1]<c[i-2]<c[i-3],
 "ritorno: 3 salite di fila": lambda i: c[i]>c[i-1]>c[i-2]>c[i-3],
 "espansione di volatilita'": lambda i: (h[i]-l[i]) > 2*st.mean([h[j]-l[j] for j in range(i-24,i)]),
}
ORIZZONTI=[6,24,72]
print("   regola                        oriz   PRIMA META'          SECONDA (mai vista)")
for nome,f in REGOLE.items():
    for o in ORIZZONTI:
        A=resa(segnali(nome,f,"A"), o); B=resa(segnali(nome,f,"B"), o)
        if not A or not B: continue
        print(f"   {nome:<28} {o:>3}h  {A[0]:+7.4f}% +/-{A[1]:5.4f} n={A[2]:<5} "
              f"{B[0]:+7.4f}% +/-{B[1]:5.4f} n={B[2]}")
random.seed(1)
for o in ORIZZONTI:
    R=resa(random.sample(range(60,n-80), 1500), o)
    print(f"   {'TARATURA (entrate a caso)':<28} {o:>3}h  "
          f"{R[0]:+7.4f}% +/-{R[1]:5.4f} n={R[2]}   <- deve valere circa -{COSTO*100:.2f}%")
