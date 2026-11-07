"""+18,9% contro -4,5%: non possono essere entrambi giusti.

Due misure della stessa strategia danno segno opposto. La differenza NON e'
rumore (l'errore sulla media e' 2,3 punti). Qui provo le varianti una per una
per trovare quale scelta non dichiarata produceva il +18,9%.
La lezione di Astra: se la regola di scadenza non era dichiarata, la strategia
non era specificata, e un numero da una strategia non specificata non e' un
risultato.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); COSTO=0.06

monete=[]
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip or len(s)<4: continue
            P=[(b,abs(a0/a1),a0<0) for b,a0,a1,_ in s if a1!=0]
            if len(P)<4: continue
            monete.append((dip,P))
print(f"{len(monete)} monete in memoria\n")

def prova(nome, scadenza_h, solo_vendite, impiccata_a_zero, min_scambi=0):
    res=[]
    for dip,P in monete:
        if len(P)<min_scambi: continue
        ini=next(((b,p) for b,p,a in P if b>=dip+RITARDO and a), None)
        if not ini: continue
        b0,p0=ini; lim=b0+int(scadenza_h*3600/BLOCCO) if scadenza_h else 10**18
        mult=None; ultima=None
        for b,p,acq in P:
            if b<=b0: continue
            if b>lim: break
            if solo_vendite and acq: continue
            ultima=p
            if p>=2*p0: mult=2.0; break
        if mult is None:
            if ultima is None:
                if not impiccata_a_zero: continue
                mult=0.0
            else: mult=ultima/p0
        res.append(mult*(1-COSTO)-1)
    if not res: print(f"   {nome}: nessuna"); return
    m=st.mean(res)*100; e=1.96*st.stdev(res)/len(res)**0.5*100
    print(f"   {nome:<52} {m:+6.1f}% +/-{e:4.1f}  n={len(res)}")

print("   variante                                            media")
prova("A  scadenza 24h, uscita solo su VENDITA (la mia)", 24, True, True)
prova("B  come A ma il 2x vale su QUALSIASI stampa", 24, False, True)
prova("C  nessuna scadenza: si tiene finche' ci sono dati", None, True, True)
prova("D  nessuna scadenza + 2x su qualsiasi stampa", None, False, True)
prova("E  scadenza 24h, le impiccate SCARTATE invece di -100%", 24, True, False)
prova("F  come C ma solo monete con >=50 scambi", None, True, True, 50)
prova("G  come D ma solo monete con >=50 scambi", None, False, True, 50)
