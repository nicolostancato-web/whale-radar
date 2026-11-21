"""Il premio di volatilita' si puo' SCEGLIERE, o va solo subito?

Se dipende da uno stato osservabile prima di entrare, allora decidere
aggiunge valore. Stati provati, tutti noti al momento dell'ingresso:
  - livello dell'implicita (percentile sulla storia passata, non futura)
  - implicita meno realizzata RECENTE (quanto cara e' rispetto a ieri)
  - direzione dell'implicita (sta salendo o scendendo)

Potenza bassa: 50 finestre per asset. Dichiarato prima di guardare.
Il percentile usa SOLO il passato, altrimenti e' sguardo in avanti.
"""
import json, math, statistics as st
GIORNI=30; ORE=GIORNI*24
def realizzata(pr, ore, i, n):
    r=[]
    for j in range(i, i+n):
        a,b=ore[j], ore[j+1]
        if b-a!=3600000 or pr[a]<=0: return None
        r.append(math.log(pr[b]/pr[a]))
    if len(r)<n*0.9: return None
    return st.stdev(r)*math.sqrt(24*365)*100
FIN=[]
for m in ("BTC","ETH"):
    iv={int(x["t"])//3600000*3600000: x["iv"] for x in json.load(open(f"data/volatilita/dvol_{m}.json"))}
    pr={int(x["t"]): x["c"] for x in json.load(open(f"data/volatilita/prezzo_{m}.json"))}
    ore=sorted(set(iv)&set(pr))
    i=ORE
    while i+ORE+1 < len(ore):
        rv=realizzata(pr, ore, i, ORE)
        rp=realizzata(pr, ore, i-ORE, ORE)      # realizzata PASSATA
        if rv is None or rp is None: i+=1; continue
        im=iv[ore[i]]
        storia=[iv[o] for o in ore[:i]]
        perc=sum(1 for x in storia if x<im)/len(storia)
        prima=iv[ore[max(0,i-ORE)]]
        g=(im**2-rv**2)/(2*im)/100*(GIORNI/365)*100
        FIN.append({"m":m,"resa":g,"perc":perc,"caro":im-rp,"sale":im-prima})
        i+=ORE
print(f"   {len(FIN)} finestre (BTC+ETH; si muovono insieme, non sono")
print(f"   indipendenti fra loro, ma la DIVISIONE in celle lo e' meno)\n")
def taglia(nome, chiave, soglia):
    a=[x["resa"] for x in FIN if x[chiave]>=soglia]
    b=[x["resa"] for x in FIN if x[chiave]<soglia]
    if len(a)<12 or len(b)<12: return
    ma=st.mean(a); ea=1.96*st.stdev(a)/math.sqrt(len(a))
    mb=st.mean(b); eb=1.96*st.stdev(b)/math.sqrt(len(b))
    d=ma-mb; ed=math.sqrt(ea**2+eb**2)
    print(f"   {nome}")
    print(f"      sopra soglia  {len(a):>3} finestre  {ma:+7.3f}% +/-{ea:.3f}")
    print(f"      sotto soglia  {len(b):>3} finestre  {mb:+7.3f}% +/-{eb:.3f}")
    print(f"      differenza    {d:+7.3f}% +/-{ed:.3f}  "
          f"{'CONTA' if abs(d)>ed else 'non conta'}\n")
taglia("implicita alta (sopra il 70mo percentile storico)", "perc", 0.70)
taglia("implicita alta (sopra la mediana storica)", "perc", 0.50)
taglia("cara rispetto alla realizzata recente (>+5 punti)", "caro", 5)
taglia("cara rispetto alla realizzata recente (>0)", "caro", 0)
taglia("implicita in salita rispetto a 30 giorni fa", "sale", 0)
