"""Chi ha lanciato la moneta, e come sono finite le sue monete precedenti.

PERCHE' QUESTO ATTRIBUTO (4/10). La decomposizione del 4/10
(`RILEVATORE_DI_AZZERAMENTI.md`) dice che quattro quinti del vantaggio che abbiamo vengono
dall'EVITARE le monete che muoiono. E «quale moneta muore» non e' una domanda di grafico: e'
una domanda su CHI l'ha lanciata. Un lanciatore che ha gia' fatto morire dieci monete e' il
dato piu' vicino alla causa che possiamo avere, e non l'abbiamo mai raccolto — ho inseguito
prima le squadre, poi i portafogli nuovi, poi le flotte.

Costa UNA lettura per gettone (non per scambio): l'atto di creazione del contratto.

QUALE LATO E' IL MEMECOIN, RICAVATO DAI DATI (4/10). Al primo tentativo ho messo a mano una
lista di valute (`0x0000…`) e su base quattro gettoni su cinque sono tornati vuoti: erano
`0x4200…` e `0xb200…`, cioe' contratti di sistema sul lato valuta, non memecoin.
E' la stessa famiglia del «lato valuta dedotto dalla mappa sbagliata» che il 2/10 produsse
16 milioni di dollari di perdite finte. IN POSITIVO: una valuta compare in MIGLIAIA di coppie,
un memecoin in una o due. La soglia la danno i dati, non la mia memoria.
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from a_fette import mia_parte, nome_pezzo, quale_fetta

ESPLORATORI = {"robinhood": "https://robinhoodchain.blockscout.com",
               "base": "https://base.blockscout.com"}
CAP = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/129.0 Safari/537.36",
       "Accept": "application/json"}
SOGLIA_VALUTA = 50      # oltre questo numero di coppie non e' un memecoin, e' una valuta
PAUSA = float(os.environ.get("PAUSA", 0.4))
TETTO = int(os.environ.get("TETTO", 400))
# IL BUDGET E' IN SECONDI, NON IN PEZZI (4/10). Al primo giro vero ho messo TETTO=900 e su
# robinhood, che va a 13,9 al minuto, 900 gettoni vogliono 65 minuti contro un timeout di 25:
# sei fette su sei uccise a meta' strada. Il tetto l'avevo tarato a occhio sul numero invece
# che sulla velocita' MISURATA — e la velocita' la conoscevo, l'avevo stampata un'ora prima.
# IN POSITIVO: si lavora finche' c'e' tempo e si smette da soli prima della ghigliottina.
# Un numero di pezzi e' una promessa sul futuro; un budget di tempo e' un fatto.
BUDGET_SEC = float(os.environ.get("BUDGET_SEC", 0)) or None
# E SI SALVA STRADA FACENDO: col salvataggio solo alla fine, una fetta uccisa dal timeout
# perdeva TUTTO. «Annullata» non voleva dire «non ha lavorato»: voleva dire «ha lavorato e
# l'ho buttato». Terza volta che la parola «annullata» mi inganna (1/10, 2/10).
OGNI_QUANTI = int(os.environ.get("OGNI_QUANTI", 50))
# DOVE NON C'E' UN LIMITE, LA LENTEZZA SI BATTE COL PARALLELISMO (5/10).
# Misurato sui registri della corsia: su robinhood 10 chiamate al minuto con ZERO strozzature,
# cioe' sei secondi per chiamata — non e' un tetto del servizio, e' latenza. Al ritmo di un
# filo solo servivano 40 ore. Su base invece 33 al minuto con 1.225 strozzature contro 629
# risolte: la' il tetto e' vero e il parallelismo non aiuta, va solo peggio.
# Quindi: si parallelizza e si GUARDA il conto delle strozzature. Se compaiono, si scende.
# Il 1/10 avevo concluso «cambiare il ritmo delle corse, non la pausa»: vero quando il limite
# e' per finestra, inutile quando il collo di bottiglia e' il tempo di risposta. Prima di
# scegliere il rimedio va misurato QUALE dei due si ha davanti — e si vede dal numero di
# strozzature a parita' di velocita'.
FILI = int(os.environ.get("FILI", 8))


def memecoin(coppie):
    """L'indirizzo del memecoin per ogni coppia: il lato che NON e' una valuta."""
    quante = {}
    for v in coppie.values():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if len(a) == 42:
                quante[a] = quante.get(a, 0) + 1
    valute = {a for a, n in quante.items() if n > SOGLIA_VALUTA}
    fuori = {}
    for pid, v in coppie.items():
        lati = [(v.get(l) or "").lower() for l in ("t0", "t1")]
        cand = [a for a in lati if len(a) == 42 and a not in valute]
        if len(cand) == 1:
            fuori[pid] = cand[0]
    return fuori, valute


def creatore(chain, indirizzo, intestazioni):
    """Creatore, numero di portatori e capitalizzazione: tre attributi in una lettura.

    LO STROZZAMENTO ERA UNA PORTA, NON L'EDIFICIO (4/10). L'endpoint compatibile Etherscan
    (`/api?module=contract&action=...`) qui da' 5 risposte e 25 strozzature su 30, e il 1/10
    ne avevo concluso «Blockscout pubblico da' una decina di risoluzioni per finestra, quindi
    cambiare il ritmo delle corse e non la pausa». Falso: era il limite di QUELLA porta.
    La stessa casa, sulla porta `/api/v2/`, risponde 30 su 30 senza una strozzatura —
    15 al minuto su robinhood, 61 su base.
    E' la famiglia di «robinhood non ha un esploratore pubblico», che era un 403 da
    User-Agent magro e l'ho scritto come fatto in due documenti: UN LIMITE INCONTRATO SU UNA
    VIA NON E' UNA PROPRIETA' DEL MONDO. In positivo: prima di dichiarare un tetto, provare
    l'altra porta.
    """
    u = f"{ESPLORATORI[chain]}/api/v2/addresses/{indirizzo}"
    try:
        with urllib.request.urlopen(
                urllib.request.Request(u, headers=intestazioni), timeout=30) as r:
            j = json.loads(r.read())
    except urllib.error.HTTPError as e:
        # STROZZATO NON E' VUOTO (2/10). Il 429 veniva archiviato come «nessun creatore»:
        # 133 bugie scritte come fatti. Un limite di velocita' e' una cosa che NON SAPPIAMO.
        return "strozzato" if e.code in (429, 403, 503) else None
    except Exception:
        return "strozzato"
    c = j.get("creator_address_hash")
    g = j.get("token") or {}
    return {"chi": c.lower() if c else None,
            "atto": j.get("creation_transaction_hash"),
            "portatori": g.get("holders_count") or g.get("holders"),
            "capitale": g.get("circulating_market_cap")}


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    p = f"data/multichain/{chain}/coppie.json"
    if not os.path.exists(p):
        raise SystemExit(f"LANCIATORI | manca {p}: senza le coppie non so quale sia il gettone")
    coppie = json.load(open(p))["coppie"]
    per_coppia, valute = memecoin(coppie)
    gettoni = sorted(set(per_coppia.values()))
    print(f"LANCIATORI | {chain}: {len(coppie):,} coppie, {len(valute)} valute riconosciute "
          f"dai dati, {len(gettoni):,} memecoin distinti", flush=True)

    fetta, quante = quale_fetta()
    nome = nome_pezzo(f"data/multichain/{chain}", "lanciatori")
    noti = json.load(open(nome)) if os.path.exists(nome) else {}
    # si rifanno solo quelli che non sappiamo o che erano strozzati
    da_fare = [a for a in mia_parte(gettoni)
               if not isinstance(noti.get(a), dict)][:TETTO]
    print(f"   fetta {fetta}/{quante}: {len(noti):,} gia' noti, "
          f"{len(da_fare):,} da chiedere (tetto {TETTO})", flush=True)

    h = dict(CAP)
    h["Referer"] = ESPLORATORI[chain] + "/"
    inizio, fatti, strozzati, vuoti, salvati = time.time(), 0, 0, 0, 0
    chiave = threading.Lock()
    fermati = threading.Event()

    def uno(a):
        nonlocal fatti, strozzati, vuoti, salvati
        if fermati.is_set():
            return
        if BUDGET_SEC and time.time() - inizio > BUDGET_SEC:
            fermati.set()
            return
        c = creatore(chain, a, h)
        with chiave:
            if c == "strozzato":
                strozzati += 1
                if strozzati >= 12 and fatti == 0:
                    print("   dodici strozzature di fila senza un successo: mi fermo. "
                          "Qui il tetto e' del servizio, non latenza: va cambiato il RITMO "
                          "DELLE CORSE (lezione del 1/10), non il numero di fili.",
                          flush=True)
                    fermati.set()
                return
            if c is None:
                noti[a] = {"chi": None}
                vuoti += 1
            else:
                noti[a] = c
                if not c.get("chi"):
                    vuoti += 1
            fatti += 1
            # si salva strada facendo: una fetta uccisa non butta piu' il lavoro fatto
            if fatti % OGNI_QUANTI == 0 and fatti != salvati:
                json.dump(noti, open(nome, "w"))
                salvati = fatti
        time.sleep(PAUSA)

    print(f"   {FILI} fili in parallelo (se compaiono strozzature vuol dire che il tetto "
          f"e' del servizio e non della latenza)", flush=True)
    with ThreadPoolExecutor(max_workers=FILI) as pool:
        list(pool.map(uno, da_fare))
    durata = max(time.time() - inizio, 1e-9)
    if fatti and fatti != salvati:
        json.dump(noti, open(nome, "w"))
    print(f"   risolti {fatti:,} ({vuoti:,} senza atto di creazione leggibile), "
          f"strozzati {strozzati:,}, in {durata/60:.1f} min "
          f"= {fatti/(durata/60):.1f} al minuto", flush=True)
    noti_veri = sum(1 for v in noti.values() if isinstance(v, dict) and v.get("chi"))
    print(f"   totale su questa fetta: {len(noti):,} gettoni, {noti_veri:,} con un lanciatore; "
          f"copertura {len(noti)/max(len(mia_parte(gettoni)),1):.1%} della fetta", flush=True)


if __name__ == "__main__":
    main()
