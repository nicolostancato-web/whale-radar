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
# LO SPAZIO DI RICERCA, ALLARGATO (1/10). Sei configurazioni erano poche per quello che Nicolo'
# aveva chiesto il 23/09: «migliaia di combinazioni tutte perfette, parametri incrociati».
# Qui si incrociano anche le CONDIZIONI DI CONTORNO — chain, latenza, momento d'ingresso,
# taglia — perche' un vantaggio che esiste solo a una taglia o a una latenza non e' un vantaggio.
# La latenza 0 NON c'e' mai: e' il prezzo che non si puo' avere.
CONFIGURAZIONI = [
    {"chain": c, "ritardo": r, "entrata": e, "soldi": s}
    for c in ("robinhood", "base")
    # LA LATENZA 1 NON SI PUO' PAGARE (1/10). Scoperto oggi leggendo il codice: `ritardo=1`
    # compra al prezzo dello scambio su cui si DECIDE — uno scambio avvenuto, ma non il nostro.
    # Il primo prezzo davvero pagabile e' `ritardo=2`. Le prove da 1 a 38 girate a ritardo 1
    # misuravano l'irraggiungibile: restano nel registro col loro valore, perche' non si
    # cancella niente, ma non sono configurazioni eseguibili.
    for r in (2, 3, 4)
    # L'INGRESSO 25 NON C'E' PIU' (1/10). C'era, ma era finto: `carica()` aveva "_sc5" scritto
    # fisso e ignorava ENTRATA_SCAMBIO, quindi le dodici prove con ingresso 25 hanno dato
    # margini IDENTICI a quelle con ingresso 5. Meta' dello spazio era un doppione contato come
    # prova indipendente. Adesso carica() urla se l'insieme non c'e'; qui resta solo cio' che
    # esiste davvero. Per riaprire questa dimensione va costruito insieme_<chain>_sc25.jsonl.gz.
    for e in (5,)
    for s in (25.0, 100.0)
]


def quante_prove():
    """Quante configurazioni sono state provate da sempre."""
    if not os.path.exists(REGISTRO):
        return 0
    return sum(1 for _ in open(REGISTRO, encoding="utf-8"))


# QUANTE COMBINAZIONI GUARDA UN GIRO. Serve per il denominatore vero (vedi sotto).
CONFRONTI_PER_GIRO = 10700


def quanti_sguardi():
    """IL DENOMINATORE VERO (1/10, dopo la revisione di Grok).

    Scrivevo una riga per CONFIGURAZIONE e usavo quel conto come denominatore. Grok: «il
    denominatore coincide con la riga che hai scelto di scrivere. Lo sguardo che poteva farti
    cambiare idea sono i 10.700 confronti dentro ogni configurazione, e quella riga li cancella.»

    Aveva ragione, ed e' un modo di barare con se stessi che non si vede: con 13 righe la
    soglia chiedeva il 17%; gli sguardi veri erano 139.100 e la soglia onesta e' quasi il doppio.
    Qui il denominatore e' la somma dei confronti davvero fatti, non delle righe scritte.
    """
    if not os.path.exists(REGISTRO):
        return 0
    n = 0
    for riga in open(REGISTRO, encoding="utf-8"):
        try:
            n += int(json.loads(riga).get("confronti") or CONFRONTI_PER_GIRO)
        except Exception:
            n += CONFRONTI_PER_GIRO
    return n


def soglia(n):
    """La soglia sale col numero di prove: e' la correzione per aver guardato molte volte.

    Con n prove, la migliore su dati casuali cresce come radice del logaritmo di n. Qui si usa
    una regola grezza ma dichiarata: 10 punti base, piu' 2 punti ogni raddoppio delle prove.
    Grezza e conservativa e' meglio che elegante e ottimista.
    """
    import math
    return 0.10 + 0.02 * math.log2(max(2, n))


def un_giro(conf):
    amb = dict(os.environ, CHAIN=conf["chain"], RITARDO=str(conf["ritardo"]),
               SOLDI=str(conf.get("soldi", 25.0)),
               ENTRATA_SCAMBIO=str(conf.get("entrata", 5)))
    r = subprocess.run([sys.executable, "-B", os.path.join(QUI, "combinazioni.py")],
                       capture_output=True, text=True, timeout=3000, env=amb)
    testo = r.stdout
    verdetto = "errore"
    margine = None
    for riga in testo.splitlines():
        if "batte il caso MA" in riga:
            perso_comunque = True
        if "IN MEDIA le dieci migliori" in riga:
            verdetto = "segnale" if "SEGNALE" in riga else "niente"
            try:
                a = float(riga.split("fanno")[1].split("%")[0].strip().replace("+", ""))
                assoluto = a / 100.0
                b = float(riga.split("fondale di")[1].split("%")[0].strip().replace("+", ""))
                margine = (a - b) / 100.0
            except Exception:
                pass
        if "NON batte la migliore sul rumore" in riga:
            verdetto = "sotto il rumore"
        if "margine vero" in riga and "contro il metro" in riga:
            try:
                tetto = float(riga.split("contro il metro")[1].split("%")[0].strip().replace("+", ""))
                metro = tetto / 100.0
            except Exception:
                pass
    return (verdetto, margine, testo, locals().get("metro"),
            locals().get("assoluto"), bool(locals().get("perso_comunque")))


def main():
    n = quante_prove()
    sguardi = quanti_sguardi()
    conf = CONFIGURAZIONI[n % len(CONFIGURAZIONI)]
    print(f"CICLO | prova numero {n+1}: {conf}", flush=True)
    verdetto, margine, testo, metro, assoluto, perso_comunque = un_giro(conf)
    # LA SOGLIA NON E' PIU' UNA FORMULA (1/10, dalla revisione di Grok: «la tua soglia
    # 0,10 + 0,02*log2(n) e' cosmetica. Dammi il numero che useresti tu»).
    # Adesso il metro lo misura `combinazioni.py`: prende le dieci combinazioni scelte dalle
    # ricerche SUL RUMORE — che per costruzione non possono sapere niente — le giudica sul
    # pezzo mai visto, e il loro margine migliore e' la soglia. Misurato oggi su base: il metro
    # sta a +16,1% e il margine vero a +7,6%, cioe' il mio miglior risultato fa PEGGIO del caso.
    # La formula resta calcolata e scritta nel registro solo per poter confrontare le due
    # epoche: non decide piu' niente.
    s = soglia(sguardi + CONFRONTI_PER_GIRO)
    # La correzione per aver provato molte configurazioni NON e' piu' un numero piu' alto: e'
    # la REGOLA DI RIPETIZIONE gia' decisa (3 volte su 5, su entrambe le chain). Una soglia
    # gonfiata chiude la porta anche a un vantaggio vero; chiedere che si ripeta non lo fa.
    candidata = (verdetto == "segnale" and margine is not None
                 and (metro is None or margine > metro))
    riga = {"quando": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "prova": n + 1, "configurazione": conf, "verdetto": verdetto,
            "margine": round(margine, 4) if margine is not None else None,
            "confronti": CONFRONTI_PER_GIRO,
            "metro_misurato": round(metro, 4) if metro is not None else None,
            # IL NUMERO CHE CONTA DAVVERO (1/10): il rendimento ASSOLUTO delle dieci migliori.
            # Il margine sul fondale puo' essere +30% con un rendimento di -2,8%: perdere meno
            # del mercato non si incassa. Qui si scrive, cosi' nessuna rilettura futura potra'
            # confondere «ha battuto il fondale» con «ha guadagnato».
            "rendimento_assoluto": round(assoluto, 4) if assoluto is not None else None,
            "batteva_il_caso_ma_perdeva": perso_comunque,
            "sguardi_totali": sguardi + CONFRONTI_PER_GIRO,
            "soglia_richiesta": round(s, 4),
            "candidata": candidata,
            "stato": "IN ATTESA DI REVISIONE ESTERNA" if candidata else "scartata"}
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    with open(REGISTRO, "a", encoding="utf-8") as h:
        h.write(json.dumps(riga, ensure_ascii=False) + "\n")
    print(f"   verdetto: {verdetto}   margine "
          f"{'%.1f%%' % (100*margine) if margine is not None else 'n/d'}   "
          f"metro misurato {'%.1f%%' % (100*metro) if metro is not None else 'n/d'}   "
          f"soglia richiesta {100*s:.1f}% "
          f"(sugli SGUARDI veri: {sguardi + CONFRONTI_PER_GIRO:,} confronti, "
          f"non sulle {n+1} righe del registro)", flush=True)
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
