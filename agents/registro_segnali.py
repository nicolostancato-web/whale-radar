"""REGISTRO DEI SEGNALI — si scrive prima, si valuta dopo, e il voto arriva da solo.

Sesto e ultimo pezzo della macchina del loop 1. Idea presa da TradingAgents (22/09): loro scrivono
ogni decisione PRIMA di conoscerne l'esito, e un processo separato la valuta quando la finestra di
detenzione si chiude — anche quando e' andata male.

PERCHE' MANCAVA PROPRIO QUESTO PEZZO. Avevamo gia' deciso di scrivere le ipotesi prima di
misurarle. Ma mancava il meccanismo che va a PRENDERE IL VOTO dopo: senza, ci si ricorda delle
previsioni azzeccate e si dimenticano le altre, e nessuno mente — semplicemente la memoria e'
selettiva, e in tre mesi il ricordo di come e' andata non somiglia a come e' andata.

LE REGOLE, TUTTE NATE DA UN ERRORE GIA' FATTO:

  1. NIENTE SI CANCELLA. Un segnale annotato resta, quale che sia l'esito. La revisione esterna ci
     aveva contestato che «escludere i candidati non eseguibili» era una selezione nuova: qui non
     si esclude niente, si registra lo stato.

  2. GLI STATI SONO SEI, e non due. «Riuscito/fallito» nasconde i casi che contano:
       rifiutato_prima     scartato con informazioni gia' disponibili — nessun costo
       tentato_fallito     tentato e non eseguito — CON i costi sostenuti
       eseguito_parziale   riempito in parte
       comprato_venduto    ciclo completo
       comprato_bloccato   comprato e NON vendibile: perdita totale, non un candidato da scartare
       finestra_aperta     ancora in corso, non si giudica

  3. IL VOTO NON SI CHIEDE, ARRIVA. `chiudi()` gira per conto suo, trova i segnali la cui finestra
     e' scaduta, calcola l'esito dai dati e lo scrive. Non serve che nessuno si ricordi.

  4. IL COSTO SI CONTA AL DOPPIO DI QUELLO OSSERVATO. Preso dai post-mortem di chi ha perso soldi:
     un bot con 140 operazioni e un segnale valido ha chiuso a -22% solo per costi. Il nostro
     impatto e' misurato su scambi riusciti e piccoli — il doppio e' un margine, non pessimismo.

  5. LA LATENZA E' LA NOSTRA, NON QUELLA CHE VORREMMO. Misurata: 1-3 secondi mediani, fino a 15
     minuti. Il prezzo di entrata e' quello disponibile DOPO il ritardo, non quello che ha fatto
     scattare il segnale.
"""
import gzip
import json
import os
import sys
import time

REG = "data/loop1/segnali.jsonl"
MOLTIPLICATORE_COSTO = float(os.environ.get("MOLT_COSTO", 2.0))

STATI = ("rifiutato_prima", "tentato_fallito", "eseguito_parziale",
         "comprato_venduto", "comprato_bloccato", "finestra_aperta")


def annota(chain, pool, ipotesi, t_decisione, finestra_ore, prezzo_segnale,
           latenza_s, nota=""):
    """Scrive un segnale PRIMA di sapere com'e' andata. E' l'unico momento in cui si puo' farlo."""
    os.makedirs(os.path.dirname(REG), exist_ok=True)
    # L'IDENTIFICATIVO DEVE COMPRENDERE L'IPOTESI (22/09). Senza, tre previsioni diverse sullo
    # stesso pool nello stesso istante collassavano in una sola: scritte 120, contate 40. Fra sei
    # ore ne avrei giudicato un terzo credendo di giudicarle tutte — e il conto delle domande
    # fatte, che e' il denominatore della fortuna, sarebbe stato sbagliato per difetto.
    r = {"id": f"{chain}:{pool}:{int(t_decisione)}:{ipotesi}",
         "chain": chain, "pool": pool.lower(),
         "ipotesi": ipotesi,                      # QUALE ipotesi lo ha generato: senza, non e'
                                                  # verificabile che fosse registrata prima
         "t_decisione": int(t_decisione),
         "scade": int(t_decisione + finestra_ore * 3600),
         "prezzo_segnale": prezzo_segnale,
         "latenza_s": latenza_s,
         "stato": "finestra_aperta",
         "annotato": int(time.time()),
         "nota": nota}
    with open(REG, "a") as f:
        f.write(json.dumps(r) + "\n")
    return r["id"]


def _scambi(chain, pool):
    fuori = []
    for sub in ("storico", "vivo"):
        p = f"data/multichain/{chain}/{sub}/{pool}.jsonl.gz"
        if not os.path.exists(p):
            continue
        try:
            for l in gzip.open(p, "rt"):
                if l.strip():
                    fuori.append(json.loads(l))
        except Exception:
            # UN ARCHIVIO ILLEGGIBILE NON E' UN ARCHIVIO VUOTO (lezione del 21/09).
            return None
    return fuori


def _prezzo(r):
    """IL PREZZO DAL RAPPORTO FRA LE QUANTITA' NON E' AFFIDABILE (22/09, scoperto dalla prima
    prova di questo registro).

    Alla prima esecuzione su 25 segnali veri il rendimento mediano e' uscito plausibile (-1,56%) ma
    la MEDIA a +533.877.973%, con casi da sei miliardi percento. Numeri impossibili.
    La mattina stessa avevo archiviato lo stesso sintomo come «un singolo scambio anomalo»: era
    sbagliato, il problema e' diffuso.

    La sostituzione giusta e' gia' in raccolta da un'ora, e non sapevo servisse a questo: le
    RISERVE del pool (evento SYNC) danno un prezzo non ambiguo — riserva1 / riserva0 — invece di
    dedurlo da uno scambio. Appena la raccolta delle riserve copre abbastanza pool, questa funzione
    legge di li'.

    Fino ad allora il registro NON deve pubblicare medie: e' il motivo per cui `rapporto()` mostra
    quanti eventi sostengono il guadagno e cosa succede togliendo i tre maggiori. Una media da sei
    miliardi percento non e' un risultato da spiegare: e' un dato da smascherare."""
    try:
        a0, a1 = abs(float(r["a0"])), abs(float(r["a1"]))
        return a1 / a0 if a0 > 0 and a1 > 0 else None
    except Exception:
        return None


def chiudi():
    """Va a prendere il voto dei segnali la cui finestra e' scaduta. Nessuno deve ricordarsene."""
    if not os.path.exists(REG):
        print("REGISTRO | nessun segnale annotato")
        return
    righe = [json.loads(l) for l in open(REG) if l.strip()]
    ultimo = {}
    for r in righe:
        ultimo[r["id"]] = r                       # l'ultimo stato scritto per ogni segnale
    ora = time.time()
    chiusi = 0
    aggiornati = []
    for sid, r in ultimo.items():
        if r["stato"] != "finestra_aperta" or ora < r["scade"]:
            continue
        rr = _scambi(r["chain"], r["pool"])
        if rr is None:
            continue                              # illeggibile: si ritenta, non si giudica
        rr = [x for x in rr if x.get("ts") and x["ts"] >= r["t_decisione"]]
        rr.sort(key=lambda x: (x.get("blocco", 0), x.get("li", 0)))
        # LA LATENZA E' NOSTRA: si entra al prezzo disponibile DOPO il ritardo, non a quello del
        # segnale.
        dopo_latenza = [x for x in rr if x["ts"] >= r["t_decisione"] + r["latenza_s"]]
        p_entrata = next((_prezzo(x) for x in dopo_latenza if _prezzo(x)), None)
        dentro = [x for x in dopo_latenza if x["ts"] <= r["scade"]]
        p_uscita = None
        for x in reversed(dentro):
            p_uscita = _prezzo(x)
            if p_uscita:
                break
        nuovo = dict(r)
        if p_entrata is None:
            # nessuno scambio dopo il nostro ritardo: non saremmo mai entrati
            nuovo["stato"] = "tentato_fallito"
            nuovo["rendimento"] = 0.0
        elif p_uscita is None:
            nuovo["stato"] = "comprato_bloccato"
            nuovo["rendimento"] = -1.0            # perdita totale: non un candidato da scartare
        else:
            lordo = p_uscita / p_entrata - 1
            # il costo al doppio dell'osservato, entrata e uscita
            costo = 2 * MOLTIPLICATORE_COSTO * float(r.get("impatto_atteso") or 0.0045)
            nuovo["stato"] = "comprato_venduto"
            nuovo["rendimento"] = round(lordo - costo, 5)
            nuovo["lordo"] = round(lordo, 5)
            nuovo["costo_applicato"] = round(costo, 5)
        nuovo["chiuso"] = int(ora)
        aggiornati.append(nuovo)
        chiusi += 1
    if aggiornati:
        with open(REG, "a") as f:
            for r in aggiornati:
                f.write(json.dumps(r) + "\n")
    print(f"REGISTRO | {chiusi} segnali chiusi in questo giro")
    return chiusi


def rapporto():
    if not os.path.exists(REG):
        print("REGISTRO | nessun segnale annotato")
        return
    ultimo = {}
    for l in open(REG):
        if l.strip():
            r = json.loads(l)
            ultimo[r["id"]] = r
    per_stato = {}
    rend = []
    for r in ultimo.values():
        per_stato[r["stato"]] = per_stato.get(r["stato"], 0) + 1
        if r.get("rendimento") is not None:
            rend.append(r["rendimento"])
    # SI CONTANO I POOL DISTINTI, NON LE RIGHE (22/09). Lo stesso pool osservato tre volte a
    # venti minuti di distanza non e' tre prove: e' una prova guardata tre volte. Se la condizione
    # di morte di un'ipotesi dice «dopo 300 previsioni», quel 300 deve essere di POOL, altrimenti
    # il denominatore si gonfia da solo e l'ipotesi sembra piu' provata di quanto sia.
    # Misurato alla prima mezz'ora: 391 previsioni su 332 pool distinti, il 17% ripetizioni.
    distinti = len({(r["chain"], r["pool"]) for r in ultimo.values()})
    print(f"REGISTRO | {len(ultimo)} previsioni su {distinti} pool distinti")
    for s in STATI:
        if s in per_stato:
            print(f"   {s:<20} {per_stato[s]}")
    if rend:
        rend.sort()
        med = rend[len(rend) // 2]
        media = sum(1 + x for x in rend) / len(rend) - 1
        print(f"   rendimento di portafoglio dopo costi: {100*media:+.2f}%")
        print(f"   mediano (descrittivo, non criterio):  {100*med:+.2f}%")
        vinc = [x for x in rend if x > 0]
        if vinc:
            piu_grossi = sorted(rend, reverse=True)[:3]
            print(f"   quanti eventi sostengono il guadagno: {len(vinc)} su {len(rend)}")
            print(f"   i tre maggiori: {[round(100*x,1) for x in piu_grossi]}%")
            senza = [x for x in rend if x not in piu_grossi]
            if senza:
                m2 = sum(1 + x for x in senza) / len(senza) - 1
                print(f"   senza i tre maggiori (DIAGNOSTICA, non criterio): {100*m2:+.2f}%")


if __name__ == "__main__":
    if "--chiudi" in sys.argv:
        chiudi()
    rapporto()
