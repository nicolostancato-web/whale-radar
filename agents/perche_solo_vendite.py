"""Il 42-44% di «solo vendite» e' un buco nei dati o e' la realta'?

LA DOMANDA DI NICOLO' (4/10): «quanto ci metti ad avere tutti gli acquisti?» — perche' senza
il lato acquisto non si sa chi ha guadagnato.

PRIMA DI RISPONDERE CON UN ETA, VA CAPITO SE L'ETA ESISTE. Tre cose misurate stasera:
  · pool con file di scambi: 84,6% su base, 90,2% su robinhood → il buco non e' qui;
  · mappa di chi ha firmato: 397.820 e 723.814 transazioni → praticamente completa;
  · i file vengono riscritti ogni giorno (155.000 tocchi in 24h su 136.000 file) → la
    copertura e' al suo tetto, non in crescita.
Quindi il 42-44% NON e' spiegato dalla copertura. L'ipotesi: quei gettoni non sono stati
comprati, sono stati RICEVUTI — trasferiti dal lanciatore, da un altro portafoglio, o
distribuiti. Su questi mercati e' normale.

SE E' COSI', L'ETA NON ESISTE: quegli acquisti non sono «non ancora raccolti», sono
**mai avvenuti su un mercato**. E aspettare il 100% sarebbe aspettare una cosa che non arriva.

IL TEST, scritto prima di guardare. Per ogni posizione «solo vendite» si guarda se la storia
di quella pool ce l'abbiamo DALLA NASCITA (primo scambio archiviato vicino al blocco di
nascita). Due esiti, entrambi informativi:
  · storia completa e nessun acquisto → li ha RICEVUTI. Niente da raccogliere.
  · storia incompleta → e' un buco nostro, e si puo' colmare. Allora l'ETA ha senso.
IL PRIMO CRITERIO NON FUNZIONAVA E L'HO SOSTITUITO (4/10). Usavo l'indice del primo scambio
archiviato per sapere se avevamo la storia dall'inizio. Quel campo NON ESISTE nei file: il test
ha girato su 43.000 posizioni e ha risposto «0 giudicabili». Un test che non puo' rispondere non
va interpretato, va rifatto — e il modo di accorgersene e' aver stampato il denominatore.

IL CRITERIO NUOVO, piu' stretto e con soli dati che abbiamo: se il PRIMO scambio archiviato
della pool (di chiunque) e' avvenuto PRIMA della prima vendita di quel portafoglio, allora
stavamo guardando quando lui ha avuto i gettoni. Se non l'abbiamo visto comprare mentre
guardavamo, non li ha comprati: li ha RICEVUTI.
Si chiede un margine di un'ora, perche' «prima» di un minuto non e' una prova.
"""
import glob
import gzip
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import a_fette as AF                                              # noqa: E402
import verso as V                                                 # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")


def main():
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"SOLO VENDITE | manca {p}")
    mappa = {k.lower(): str(v).lower() for k, v in
             json.load(gzip.open(p, "rt")).get("da", {}).items()}
    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    print(f"SOLO VENDITE | {CHAIN} fetta {i_f+1}/{n_f}: {len(file_tutti):,} file, "
          f"{len(mappa):,} firmatari noti", flush=True)

    t0 = time.time()
    conta = {"posizioni": 0, "chiuse": 0, "aperte": 0, "parziali": 0,
             "solo_vendite": 0, "solo_vendite_con_storia_piena": 0,
             "solo_vendite_con_storia_corta": 0}
    letti = 0
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {letti:,} file", flush=True)
            break
        pool = os.path.basename(percorso).split(".")[0]
        vp = V.valuta_lato(CHAIN, pool)
        if not vp:
            continue
        lato, decimali, _ = vp
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        if not righe:
            continue
        letti += 1
        # la storia e' «piena» se il primo scambio archiviato e' fra i primissimi della pool.
        # Lo si sa dal campo dell'indice se c'e'; altrimenti si usa il numero di scambi noti
        # come prova indiretta e si DICHIARA che e' indiretta.
        tempi = [x.get("ts") or x.get("t") for x in righe]
        tempi = [z for z in tempi if isinstance(z, (int, float))]
        primo_archivio = min(tempi) if tempi else None
        meme = "t1" if lato == "t0" else "t0"
        per = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            if V.quantita_lato(x, lato) <= 0:
                continue
            d = per.setdefault(chi, {"in": 0.0, "out": 0.0, "gin": 0.0, "gout": 0.0,
                                     "prima_vendita": None})
            g = V.quantita_lato(x, meme)
            tt = x.get("ts") or x.get("t")
            if V.entra_valuta(x, lato):
                d["in"] += 1
                d["gin"] += g
            else:
                d["out"] += 1
                d["gout"] += g
                if isinstance(tt, (int, float)):
                    d["prima_vendita"] = (tt if d["prima_vendita"] is None
                                          else min(d["prima_vendita"], tt))
        for d in per.values():
            conta["posizioni"] += 1
            if d["in"] <= 0 < d["out"]:
                conta["solo_vendite"] += 1
                pv = d["prima_vendita"]
                if primo_archivio is not None and pv is not None:
                    # un'ora di margine: «prima» di un minuto non e' una prova
                    if primo_archivio <= pv - 3600:
                        conta["solo_vendite_con_storia_piena"] += 1
                    else:
                        conta["solo_vendite_con_storia_corta"] += 1
            elif d["out"] <= 0:
                conta["aperte"] += 1
            elif d["gin"] > 0 and (d["gin"] - d["gout"]) <= 0.01 * d["gin"]:
                conta["chiuse"] += 1
            else:
                conta["parziali"] += 1
    pezzo = AF.nome_pezzo(BASE, "perche_solo_vendite")
    json.dump({"letti": letti, "conta": conta,
               "nota": "storia_piena = il primo scambio archiviato della pool precede di "
                       "almeno un'ora la prima vendita di quel portafoglio, quindi stavamo "
                       "guardando e non l'abbiamo visto comprare: gettoni RICEVUTI. Se manca "
                       "un tempo, la posizione non entra ne' in piena ne' in corta: non "
                       "sapere non e' sapere."},
              open(pezzo, "w"), ensure_ascii=False, indent=1)
    sv = conta["solo_vendite"]
    print(f"   {conta['posizioni']:,} posizioni: {conta['chiuse']:,} chiuse, "
          f"{conta['aperte']:,} aperte, {conta['parziali']:,} parziali, {sv:,} solo vendite",
          flush=True)
    if sv:
        pi = conta["solo_vendite_con_storia_piena"]
        co = conta["solo_vendite_con_storia_corta"]
        noto = pi + co
        print(f"   delle solo-vendite con storia giudicabile ({noto:,}): "
              f"{pi:,} con storia PIENA = gettoni RICEVUTI, non comprati "
              f"({pi/max(noto,1):.1%}); {co:,} con storia corta = buco nostro, colmabile",
              flush=True)


if __name__ == "__main__":
    main()
