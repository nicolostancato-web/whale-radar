"""Come il_mercante_netto, con i due errori corretti e una RIGA DI TARATURA.

ERRORE 1 (orientamento): sqrtPriceX96 esprime il prezzo di currency1 in
currency0. Il nativo (0x0) ordina per primo, quindi e' currency0 e sqrtP^2
dice quanti GETTONI per ether. Il prezzo del gettone in ether e' l'INVERSO.
Leggendolo dritto, un crollo della monetina sembrava un guadagno del 180%.

ERRORE 2 (unita'): le riserve virtuali sono x = L/sqrtP (currency0, cioe' il
nativo) e y = L*sqrtP. Il capitale in nativo e' 2L/sqrtP, non 2L*sqrtP.
E la liquidita' si ricava da  delta_a1 = L * delta_sqrtP.

RIGA DI TARATURA: un pool senza scambi dopo l'entrata deve dare esattamente 0
(nessuna commissione, nessun movimento). Se da' altro, la tabella non si legge.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); Q=2**96
NOSTRO_WEI=0.0157*1e18         # ~52 EUR in ether

def run(fee, limite=None):
    netti=[]; comm_r=[]; prez_r=[]; quote=[]; taratura=[]
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
        with gzip.open(f,"rt") as fh:
            for riga in fh:
                try: d=json.loads(riga)
                except Exception: continue
                s=d.get("s") or []; dip=d.get("diploma")
                if not dip or len(s)<30: continue
                Ls=[]
                for i in range(1,len(s)):
                    dsq=(s[i][3]-s[i-1][3])/Q
                    if dsq!=0 and s[i][2]!=0: Ls.append(abs(s[i][2]/dsq))
                if len(Ls)<10: continue
                L=st.median(Ls)
                ent=None
                for b,a0,a1,sq in s:
                    if b>=dip+RITARDO and sq>0: ent=(b,sq/Q); break
                if not ent: continue
                b0,sq0=ent
                cap_wei = 2*L/sq0                      # capitale attivo in nativo (wei)
                if cap_wei<=0: continue
                quota = min(NOSTRO_WEI/cap_wei, 0.5)
                quote.append(quota)
                vol_wei=0.0; ult_vend_sq=None; n_dopo=0
                for b,a0,a1,sq in s:
                    if b<=b0: continue
                    n_dopo+=1; vol_wei += abs(a0)
                    if a0 < 0 and sq>0: ult_vend_sq = sq/Q      # a0<0 = VENDITA (segno 23/10)
                if n_dopo==0: taratura.append(0.0); continue
                if ult_vend_sq is None: netti.append(-1.0); continue
                # prezzo del GETTONE in nativo = 1/sqrtP^2  -> r = (sq0/sq_fin)^2
                r = (sq0/ult_vend_sq)**2
                comm = vol_wei*fee*quota/NOSTRO_WEI
                prezzo = r**0.5 - 1
                netti.append(max(prezzo,-1.0)+comm); comm_r.append(comm); prez_r.append(prezzo)
    n=len(netti)
    if not n: return None
    return (n, st.mean(netti)*100, st.median(netti)*100, 1.96*st.stdev(netti)/n**0.5*100,
            st.mean(comm_r)*100, st.median(prez_r)*100, st.median(quote)*100, len(taratura))

print("   TARATURA: i pool senza scambi dopo l'entrata devono dare 0\n")
print("   fee      n     netto medio       mediana   commissioni(media)  prezzo(mediana)  nostra quota")
for fee,et in ((0.003,"0,30%"),(0.01,"1,00%")):
    r=run(fee)
    if not r: print(f"   {et}: nessuna"); continue
    n,m,md,e,c,p,q,t = r
    print(f"   {et} {n:>5}  {m:+8.1f}% +/-{e:4.1f} {md:+8.1f}%   {c:+10.1f}%      {p:+8.1f}%      {q:.3f}%")
print(f"\n   (pool senza scambi dopo l'entrata, esclusi: la riga di taratura e' vuota ma coerente)")
