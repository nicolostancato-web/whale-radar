"""Il ciclo che sforna ipotesi e le scarta da solo, senza potersi approvare.

PERCHE' ESISTE (1/10). Nicolo': «un sistema che sa il goal e crea una soluzione in loop, una
dietro l'altra, finche' non ne trova una, senza scordarsi niente». Finora il ciclo c'era ma lo
guidavo io a mano: quindi si fermava quando mi distraevo, ed e' esattamente quello che e'
successo per due giorni.

LA TRAPPOLA CHE ASTRA HA NOMINATO, e come si disinnesca.
`adaptive overfitting` / `reward hacking`: «chi propone influenza anche il test o interpreta il
risultato. Ripetendo la ricerca si trova prima o poi qualcosa che soddisfa il misuratore senza
soddisfare il goal.» Con un ciclo automatico questo rischio non cresce: ESPLODE, perche' le
prove diventano centinaia.

Le quattro regole, tutte dentro il codice:

  1. **Il registro di TUTTE le prove.** Ogni giro scrive cosa ha provato, anche quando non trova
     niente. Senza il denominatore, «abbiamo trovato una cosa che fa +40%» non significa nulla.
  2. **Il conto delle configurazioni.** Si dichiara quante ne sono state provate in totale, da
     sempre. Una su cento e' quello che il caso produce da solo.
  3. **Nessuna auto-approvazione.** Un'ipotesi che passa NON diventa una strategia: diventa una
     CANDIDATA, e resta li' finche' un revisore esterno (Astra o Grok) non la guarda. Il codice
     non ha nessun percorso che porti da «promettente» a «adottata».
  4. **La soglia sale col numero di prove.** Piu' cose si provano, piu' alto deve essere il
     risultato per contare. E' la correzione per il fatto di aver guardato molte volte.
"""
import datetime as dt
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
REGISTRO = os.path.join(RADICE, "data", "ipotesi_provate.jsonl")

# Le configurazioni da girare, a rotazione: chain, latenza, scambio d'ingresso.
# La latenza 0 NON c'e': e' il prezzo che non si puo' avere.
CONFIGURAZIONI = [
    {"chain": "robinhood", "ritardo": 1, "entrata": 5},
    {"chain": "base", "ritardo": 1, "entrata": 5},
    {"chain": "robinhood", "ritardo": 2, "entrata": 5},
    {"chain": "base", "ritardo": 2, "entrata": 5},
    {"chain": "robinhood", "ritardo": 1, "entrata": 25},
    {"chain": "base", "ritardo": 1, "entrata": 25},
]


def quante_prove():
    """Quante configurazioni sono state provate da sempre. E' il denominatore."""
    if not os.path.exists(REGISTRO):
        return 0
    return sum(1 for _ in open(REGISTRO, encoding="utf-8"))


def soglia(n):
    """La soglia sale col numero di prove: e' la correzione per aver guardato molte volte.

    Con n prove, la migliore su dati casuali cresce come radice del logaritmo di n. Qui si usa
    una regola grezza ma dichiarata: 10 punti base, piu' 2 punti ogni raddoppio delle prove.
    Grezza e conservativa e' meglio che elegante e ottimista.
    """
    import math
    return 0.10 + 0.02 * math.log2(max(2, n))


def un_giro(conf):
    amb = dict(os.environ, CHAIN=conf["chain"], RITARDO=str(conf["ritardo"]))
    r = subprocess.run([sys.executable, "-B", os.path.join(QUI, "combinazioni.py")],
                       capture_output=True, text=True, timeout=3000, env=amb)
    testo = r.stdout
    verdetto = "errore"
    margine = None
    for riga in testo.splitlines():
        if "IN MEDIA le dieci migliori" in riga:
            verdetto = "segnale" if "SEGNALE" in riga else "niente"
            try:
                a = float(riga.split("fanno")[1].split("%")[0].strip().replace("+", ""))
                b = float(riga.split("fondale di")[1].split("%")[0].strip().replace("+", ""))
                margine = (a - b) / 100.0
            except Exception:
                pass
        if "NON batte la migliore sul rumore" in riga:
            verdetto = "sotto il rumore"
    return verdetto, margine, testo


def main():
    n = quante_prove()
    conf = CONFIGURAZIONI[n % len(CONFIGURAZIONI)]
    print(f"CICLO | prova numero {n+1}: {conf}", flush=True)
    verdetto, margine, testo = un_giro(conf)
    s = soglia(n + 1)
    candidata = verdetto == "segnale" and margine is not None and margine >= s
    riga = {"quando": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "prova": n + 1, "configurazione": conf, "verdetto": verdetto,
            "margine": round(margine, 4) if margine is not None else None,
            "soglia_richiesta": round(s, 4),
            "candidata": candidata,
            "stato": "IN ATTESA DI REVISIONE ESTERNA" if candidata else "scartata"}
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    with open(REGISTRO, "a", encoding="utf-8") as h:
        h.write(json.dumps(riga, ensure_ascii=False) + "\n")
    print(f"   verdetto: {verdetto}   margine "
          f"{'%.1f%%' % (100*margine) if margine is not None else 'n/d'}   "
          f"soglia richiesta {100*s:.1f}% (sale col numero di prove: {n+1} finora)", flush=True)
    if candidata:
        # NESSUNA AUTO-APPROVAZIONE: da qui non esiste percorso verso «adottata».
        print("   === CANDIDATA ===  supera la soglia. NON e' una strategia: resta in attesa "
              "che un revisore esterno la guardi. Il codice non ha un percorso per adottarla.",
              flush=True)
    else:
        print("   scartata. Il registro tiene il conto: senza il denominatore, un successo "
              "non significa niente.", flush=True)
    print(testo[-600:] if verdetto == "errore" else "", flush=True)


if __name__ == "__main__":
    main()
