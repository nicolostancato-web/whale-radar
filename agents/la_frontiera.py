"""La frontiera: quanto puo' rendere OGNI strada misurata, al giorno.

Correzione del 27/10 (errore mio, trovato guardando l'uscita): il vincolo
non e' la capienza per operazione, e' QUANTE VOLTE AL GIORNO LA CASSA GIRA.
Con 52 EUR non si fanno 16 operazioni al giorno se ognuna tiene 3 giorni:
se ne fa un terzo di una. Il numero giusto e':

   EUR/giorno = cassa x lordo% x (giri al giorno)
   giri al giorno = min( occasioni al giorno , 24 / ore di tenuta )

e la cassa impiegabile e' min(cassa, capienza per operazione).
"""
R=[
 # nome, lordo%, capienza EUR/op, occasioni/gg, ore di tenuta, fonte
 ("Pons: compra ogni diplomata", 15.0, 200, 16, 72,
  "scivolamento misurato; >50% posizioni bloccate -> tenuta ottimistica"),
 ("vendere il debutto", 6.30, 50, 0.4, 72, "bocciata fuori campione"),
 ("impennata di volume", 0.22, 1000, 8, 12, "bocciata fuori campione"),
 ("arbitraggio fra piazze", 0.0, 1000, 1.3, 1, "lordo zero"),
 # 27/10: l'1,31% era un pool con l'ultimo prezzo vecchio su 6 blocchi.
 # Leggendo le commissioni vere, 12 paia su 12 stanno DENTRO la banda senza
 # arbitraggio (somma delle due commissioni). Lordo reale: zero.
 ("stesso paio, due pool", 0.0, 25, 48, 0.02, "dentro la banda: 12/12"),
]
REND=[("differenza di finanziamento", 6.0, "tetto misurato")]
def giorno(cassa, l, cap, occ, ore):
    giri = min(occ, 24.0/ore)
    return min(cassa,cap) * l/100 * giri
for cassa in (52, 5000, 10**9):
    print(f"\n   CASSA {'illimitata' if cassa>10**8 else str(cassa)+' EUR'}\n")
    print(f"   {'strada':<30}{'giri/gg':>9}{'EUR/gg':>10}{'EUR/anno':>11}")
    tot=0
    for n,l,cap,occ,ore,f in R:
        g=min(occ,24.0/ore); e=giorno(cassa,l,cap,occ,ore); tot=max(tot,e)
        print(f"   {n:<30}{g:>9.2f}{e:>10.2f}{e*365:>11.0f}")
    for n,l,f in REND:
        # DIFETTO DICHIARATO: la capienza di questa strada non e' mai stata
        # misurata, qui e' trattata come infinita. A cassa illimitata il
        # numero che esce e' una sciocchezza del modello: in realta' la
        # limitano le posizioni aperte sul mercato, e la propria posizione
        # sposta il tasso che si sta incassando. Non leggere quella riga.
        e=cassa*l/100/365
        print(f"   {n:<30}{'continuo':>9}{e:>10.2f}{e*365:>11.0f}")
    print(f"\n   la migliore: {tot:.2f} EUR/giorno  ({tot*365:.0f} EUR/anno)")
print("\n   E tutte e cinque le strade della tabella sono gia' BOCCIATE.")
print("   Il numero serve a sapere quanto avrebbero reso SE fossero state vere.")
