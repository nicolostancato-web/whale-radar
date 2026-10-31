"""Coppie legate da una relazione MECCANICA, non statistica.

La benzina si raffina dal petrolio; il gasolio pure. Oro e argento sono
entrambi metalli rifugio. Quando due cose sono legate da un vincolo reale, lo
scarto fra loro deve tornare indietro — non per un pattern, per la fisica
dell'economia.

Soddisfa i filtri: lungo-corto (niente marea), usa la RELAZIONE e non la storia
di un prezzo (non e' chiuso dal risultato sui pattern), e a 5 minuti produce
decine di migliaia di osservazioni.

Regola: quando il rapporto fra i due si allontana di piu' di K deviazioni dalla
sua media recente, si compra il sottovalutato e si vende il sopravvalutato.
Pedaggio 0,018% per gamba = 0,036% a giro (due gambe).
"""
import json, os, statistics as st
# una coppia e' 4 gambe, non 2: apri A, apri B, chiudi A, chiudi B.
# 4 x 0,018% (trade.xyz: 0,9 punti base per gamba) = 0,072%.
# PRIMA era 0,00036, cioe' due gambe: sottostimato della meta'.
COSTO=4*0.00018
COPPIE=[("RB_F","CL_F","benzina/petrolio"), ("HO_F","CL_F","gasolio/petrolio"),
        ("RB_F","HO_F","benzina/gasolio"), ("GC_F","SI_F","oro/argento"),
        ("PL_F","PA_F","platino/palladio"), ("ZC_F","ZW_F","mais/grano"),
        ("ZS_F","ZC_F","soia/mais"), ("GC_F","PL_F","oro/platino"),
        ("HG_F","ALI_F","rame/alluminio"), ("KC_F","CC_F","caffe/cacao")]
def carica(s):
    D=json.load(open(f"data/mercati/{s}_5m.json"))
    return {t:c for t,c in zip(D["t"],D["c"]) if c}
print("   coppia               oss.NON sovrapposte  oriz   resa media            esito")
for a,b,nome in COPPIE:
    try: A,B=carica(a),carica(b)
    except Exception: print(f"   {nome:<20} dati mancanti"); continue
    t=sorted(set(A)&set(B))
    if len(t)<2000: print(f"   {nome:<20} solo {len(t)} istanti in comune"); continue
    r=[A[x]/B[x] for x in t]
    for oriz in (3,12,36):
        # LE OSSERVAZIONI NON DEVONO SOVRAPPORSI: a 36 candele di orizzonte,
        # due segnali consecutivi condividono 35 periodi su 36 e l'intervallo
        # calcolato come se fossero indipendenti e' falso di un fattore sqrt(36).
        v=[]; prossimo_libero=0
        for i in range(60,len(r)-oriz):
            if i < prossimo_libero: continue
            fin=r[i-60:i]
            m=st.mean(fin); sd=st.stdev(fin)
            if sd<=0: continue
            z=(r[i]-m)/sd
            if abs(z)<2: continue
            # z>0: il rapporto e' alto -> si vende A e si compra B
            seg=-1 if z>0 else 1
            v.append(seg*((A[t[i+oriz]]/A[t[i]]-1)-(B[t[i+oriz]]/B[t[i]]-1))-COSTO)
            prossimo_libero = i + oriz
        if len(v)<60: continue
        m=st.mean(v)*100; e=1.96*st.stdev(v)/len(v)**0.5*100
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {nome:<20} {len(v):>6}  {oriz:>4}   {m:+7.4f}% +/-{e:6.4f}   {esito}")
