"""La classifica FRA mercati, a frequenza oraria: il selettore non viene dalla
candela del mercato stesso ma da cosa fanno gli altri.

Stamattina questa famiglia era indecidibile: 37 cicli mensili. A frequenza
oraria i cicli diventano migliaia e il problema sparisce.
Lungo-corto per costruzione, quindi niente marea. Prova della CLASSE: ogni
combinazione appaiata con la stessa classifica RIMESCOLATA fra i mercati, che
e' il caso giusto qui (stesso numero di posizioni, stesse ore, ordine casuale).
"""
import json, glob, statistics as st, random, math
random.seed(41)
S={}
for f in sorted(glob.glob("data/binance/*.json"))[:60]:
    d=json.load(open(f))
    if len(d)<6000: continue
    S[f.split("/")[-1][:-5]]={x["t"]:x["c"] for x in d}
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
nomi=sorted(S)
print(f"{len(nomi)} mercati | {len(ore):,} ore in comune\n")
P={n:[S[n][t] for t in ore] for n in nomi}
def prova(guardo, tengo, verso, mescola):
    res=[]
    for k in range(guardo, len(ore)-tengo, tengo):
        r=[(P[n][k]/P[n][k-guardo]-1, n) for n in nomi]
        r.sort(reverse=(verso=="continuazione"))
        q=max(3,len(r)//5)
        alti=[n for _,n in r[:q]]; bassi=[n for _,n in r[-q:]]
        if mescola:
            m=random.sample(nomi, 2*q); alti, bassi = m[:q], m[q:]
        ra=st.mean([P[n][k+tengo]/P[n][k]-1 for n in alti])
        rb=st.mean([P[n][k+tengo]/P[n][k]-1 for n in bassi])
        res.append(ra-rb)
    if len(res)<100: return None
    return st.mean(res)/(st.stdev(res)/math.sqrt(len(res))), st.mean(res)*100, len(res)
veri=[]; casi=[]; righe=[]
for guardo in (4,12,24,72,168):
    for tengo in (4,12,24):
        for verso in ("continuazione","ritorno"):
            a=prova(guardo,tengo,verso,False); b=prova(guardo,tengo,verso,True)
            if a and b:
                veri.append(a[0]); casi.append(b[0])
                righe.append((guardo,tengo,verso,a[0],a[1],a[2]))
def riass(et,x):
    x=sorted(x)
    print(f"   {et:<24} n={len(x):<3} mediana {st.median(x):+6.2f}  "
          f"5%={x[max(0,len(x)//20)]:+6.2f}  95%={x[min(len(x)-1,19*len(x)//20)]:+6.2f}  "
          f"estremi |t|>2: {sum(1 for v in x if abs(v)>2)}")
riass("CLASSIFICHE VERE", veri); riass("classifiche rimescolate", casi)
righe.sort(key=lambda r:-r[3])
print("\n   le piu' forti (t, resa per ciclo, cicli):")
for g,t,v,tt,m,n in righe[:5]:
    print(f"      guardo {g:>3}h tengo {t:>2}h {v:<14} t={tt:+6.2f}  {m:+7.4f}%  n={n}")
