"""+18,9% PER MONETA NON E' +18,9% SUL CONTO (Astra, 23/10).

La media tratta ogni moneta come se avesse soldi suoi. Con 52 EUR e un
biglietto da 50 si tiene UNA posizione: se resta impiccata, le monete che
passano intanto si guardano. Qui si misurano DUE registri sulle stesse
occasioni:
   - LIBERO: come la media originale, capitale infinito
   - VINCOLATO: 52 EUR veri, una posizione alla volta, occasioni perse contate

Regole dichiarate PRIMA di guardare l'esito (altrimenti e' selezione):
   entrata  = primo scambio di ACQUISTO a/dopo (diploma + 60s)
   uscita   = primo scambio di VENDITA a prezzo >= 2x l'entrata
   scadenza = 24h; alla scadenza si esce all'ultima VENDITA disponibile
   se non esiste nessuna vendita dopo l'entrata: -100% (impiccata)
   costo    = 6% di giro, costante unica dichiarata
Segno: a0 < 0 = acquisto, verificato sulla chain il 21/10.
"""
import gzip, glob, json, statistics as st

BLOCCO = 0.093
RITARDO = int(60 / BLOCCO)        # fine del primo minuto
SCADENZA = int(24 * 3600 / BLOCCO)
COSTO = 0.06
CASSA0 = 52.0

def prezzi(s):
    out = []
    for b, a0, a1, _sq in s:
        if a1 == 0: continue
        out.append((b, abs(a0 / a1), a0 < 0))
    return out

posizioni = []
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f, "rt") as fh:
        for riga in fh:
            try: d = json.loads(riga)
            except Exception: continue
            P = prezzi(d.get("s") or [])
            if len(P) < 4: continue
            dip = d.get("diploma")
            if not dip: continue
            ini = None
            for b, p, acq in P:
                if b >= dip + RITARDO and acq:
                    ini = (b, p); break
            if not ini: continue
            b0, p0 = ini
            esito, b1 = None, None
            ultima_vend = None
            for b, p, acq in P:
                if b <= b0: continue
                if b > b0 + SCADENZA: break
                if not acq:
                    ultima_vend = (b, p)
                    if p >= 2 * p0:
                        esito, b1 = 2.0, b; break
            if esito is None:
                if ultima_vend is None:
                    esito, b1 = 0.0, b0 + SCADENZA      # impiccata: -100%
                else:
                    esito, b1 = ultima_vend[1] / p0, ultima_vend[0]
            posizioni.append({"ini": b0, "fin": b1, "mult": esito})

posizioni.sort(key=lambda x: x["ini"])
N = len(posizioni)
res = [(p["mult"] * (1 - COSTO) - 1) for p in posizioni]
print(f"OCCASIONI: {N} monete diplomate\n")
print("== REGISTRO LIBERO (capitale infinito, come la media originale) ==")
print(f"   resa media per moneta: {st.mean(res)*100:+.1f}%  mediana {st.median(res)*100:+.1f}%")
print(f"   +/- (errore sulla media): {1.96*st.stdev(res)/N**0.5*100:.1f} punti")
print(f"   vinte (>0): {sum(1 for r in res if r>0)/N:.0%} | impiccate: {sum(1 for p in posizioni if p['mult']==0)/N:.0%}")
dur = [(p["fin"]-p["ini"])*BLOCCO/3600 for p in posizioni]
print(f"   durata: mediana {st.median(dur):.1f}h, media {st.mean(dur):.1f}h")

# quante posizioni sarebbero APERTE insieme
eventi = sorted([(p["ini"],1) for p in posizioni] + [(p["fin"],-1) for p in posizioni])
cur = picco = 0
for _b, d in eventi:
    cur += d; picco = max(picco, cur)
print(f"   posizioni CONTEMPORANEE al picco: {picco}  -> servirebbero {picco*50} EUR a 50/biglietto")

print("\n== REGISTRO VINCOLATO (52 EUR veri, una posizione alla volta) ==")
cassa = CASSA0; libero_da = -1; fatte = perse = 0; equity = []
for p in posizioni:
    if p["ini"] < libero_da:
        perse += 1; continue
    biglietto = cassa                      # tutto dentro: non c'e' spazio per frazionare
    cassa = cassa - biglietto + biglietto * p["mult"] * (1 - COSTO)
    libero_da = p["fin"]; fatte += 1; equity.append(cassa)
    if cassa < 1: break
print(f"   operazioni fatte: {fatte} | occasioni PERSE perche' il denaro era impegnato: {perse} ({perse/N:.0%})")
print(f"   cassa finale: {cassa:.2f} EUR  (partenza {CASSA0:.0f})")
if equity:
    print(f"   massimo toccato: {max(equity):.2f} | minimo: {min(equity):.2f}")
print(f"   -> {'IL CONTO CRESCE' if cassa > CASSA0 else 'IL CONTO NON CRESCE: la media era per-moneta, non per-conto'}")
