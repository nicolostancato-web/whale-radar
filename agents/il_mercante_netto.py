"""IL CONTO VERO DEL MERCANTE: commissioni MENO la perdita da prezzo.

Mettere liquidita' su una monetina vuol dire convertirne meta' in quella
monetina. Se crolla, crolli con lei. Per una posizione a tutto campo il valore
scala con la RADICE del rapporto di prezzo:  V1 = V0 * sqrt(P1/P0).
Quindi il guadagno netto e':   sqrt(r) - 1 + commissioni/V0.

La liquidita' del pool non e' nell'archivio, ma si RICAVA: per v3/v4
   delta_amount1 = L * (sqrtP_nuovo - sqrtP_vecchio)
quindi L = delta_a1 / delta_sqrtP, misurata su ogni scambio e presa in mediana.

Regole dichiarate prima: si entra a fine primo minuto dopo il diploma, si sta
dentro fino all'ultimo scambio del pool, la merce finale si valuta al prezzo
dell'ultima stampa di VENDITA (col segno corretto del 23/10: a0>0 = acquisto,
quindi la vendita e' a0<0), e se non esiste nessuna vendita finale: -100%.
"""
import gzip, glob, json, statistics as st

BLOCCO=0.093; RITARDO=int(60/BLOCCO); Q=2**96
NOSTRO=0.0157          # 52 EUR in ETH, a ~3.300 USD/ETH
def run(fee):
    netti=[]; comm_r=[]; prez_r=[]
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip or len(s)<30: continue
                # liquidita' dal movimento di sqrtP
                Ls=[]
                for i in range(1,len(s)):
                    dsq=(s[i][3]-s[i-1][3])/Q
                    if dsq!=0 and s[i][1]!=0: Ls.append(abs(s[i][1]/dsq))
                if len(Ls)<10: continue
                L=st.median(Ls)
                if L<=0: continue
                # entrata
                ent=None
                for b,a0,a1,sq in s:
                    if b>=dip+RITARDO and sq>0: ent=(b,(sq/Q)**2); break
                if not ent: continue
                b0,P0=ent
                if P0<=0: continue
                # capitale attivo in nativo ~ 2*L*sqrtP  (riserve virtuali)
                cap = 2*L*(P0**0.5)/1e18
                if cap<=0: continue
                quota = min(NOSTRO/cap, 0.5)        # mai oltre meta' del pool
                vol=0.0; ultima_vend=None; Pfin=None
                for b,a0,a1,sq in s:
                    if b<=b0: continue
                    vol += abs(a0)/1e18
                    if a0 < 0 and sq>0: ultima_vend=(sq/Q)**2     # a0<0 = VENDITA
                    if sq>0: Pfin=(sq/Q)**2
                if ultima_vend is None: netti.append(-1.0); continue
                r = ultima_vend/P0
                comm = vol*fee*quota/NOSTRO          # in frazione del nostro capitale
                prezzo = r**0.5 - 1
                netti.append(prezzo+comm); comm_r.append(comm); prez_r.append(prezzo)
    if not netti: return None
    n=len(netti)
    return (n, st.mean(netti)*100, st.median(netti)*100,
            1.96*st.stdev(netti)/n**0.5*100, st.mean(comm_r)*100, st.mean(prez_r)*100)

print("   fee      n      netto medio        mediana     di cui commissioni   di cui prezzo")
for fee,et in ((0.003,"0,30%"),(0.01,"1,00%")):
    r=run(fee)
    if not r: print(f"   {et}: nessuna"); continue
    n,m,md,e,c,p = r
    print(f"   {et}  {n:>5}   {m:+8.1f}% +/-{e:4.1f}   {md:+8.1f}%        {c:+8.1f}%        {p:+8.1f}%")
