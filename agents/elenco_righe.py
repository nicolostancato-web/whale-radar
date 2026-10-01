#!/usr/bin/env python3
"""
ELENCO_RIGHE — dice al collettore ESATTAMENTE quali pool servono.

PERCHE' (15/09). Lo scavo della storia filtrava sui pool con una serie di prezzo: 4.671 su Base. Ma
solo 1.711 di quelli diventano una riga analizzabile — gli altri non hanno abbastanza candele, o
sono stati presi troppo tardi per avere un'entrata. Risultato: l'8% dello scavo finiva su pool che
non potranno mai rispondere a una domanda.

Il cervello sa gia' quali pool diventano righe: lo calcola ogni volta. Qui lo calcoliamo UNA volta e
lo scriviamo, cosi' il collettore scava solo dove serve. Non e' un'ottimizzazione di eleganza: a
parita' di chiamate al nodo, tre volte piu' dati utili.

Scrive data/multichain/<chain>/righe.json. Sola lettura, €0.
"""
import gzip, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multichain_brain as B

CHAINS = ("base", "robinhood", "solana")


def main():
    for ch in CHAINS:
        try:
            righe = B.load_rows(ch)
        except Exception as e:
            print(f"ELENCO_RIGHE | {ch}: {type(e).__name__}", flush=True); continue
        if not righe: continue
        # oltre all'indirizzo si salva l'ISTANTE D'ENTRATA: al collettore serve per sapere QUALE
        # finestra di blocchi vale la pena leggere, invece di tenere tutto e buttare dopo.
        d = {r["pool"].lower(): {"ent": r["ent"], "t0": r.get("t0")} for r in righe if r.get("pool")}
        # LE VOCI CHE NON SONO POOL NON ENTRANO NEL REGISTRO (18/09). Verificato una per una: 199
        # voci su robinhood non hanno MAI emesso uno swap in tutta la chain, e 29 su base non ne
        # hanno nelle finestre di nascita; il 98% e il 72% non rispondono nemmeno a token0()/token1(),
        # cioe' non sono pool. Non erano un buco: erano un DENOMINATORE GONFIO.
        # Quanto e' costato tenerle: riportavo "nascite risolte dalla catena 63% su robinhood contro
        # 84% su base" e ho raccontato per settimane che robinhood era indietro. Tolte le voci
        # false, sono 85% e 85% — le due chain erano sempre state in pari.
        # Si escludono QUI, dove il registro nasce, e non in ognuno degli otto agenti che poi lo
        # dividono: un filtro in otto posti e' otto occasioni di dimenticarsene in uno.
        sporche = set()
        try:
            for a in json.load(open("data/quarantena_registro.json"))["non_sono_pool"].get(ch, []):
                sporche.add(a.lower())
        except Exception:
            pass
        if sporche:
            prima = len(d)
            d = {k: v for k, v in d.items() if k not in sporche}
            print(f"ELENCO_RIGHE | {ch}: escluse {prima - len(d)} voci che non sono pool "
                  f"(quarantena verificata sulla catena)", flush=True)
        # LA POPOLAZIONE DEFINITA ENTRA NEL REGISTRO (20/09). Finora il registro conteneva solo i
        # pool che il vecchio cervello sapeva valutare, e la popolazione di DEFINIZIONE.md la
        # raccoglieva UNA SOLA corsia (buco_base, tre fette). Tutte le altre — lo scavo storico a
        # sei fette, la coda viva — passano sopra quei blocchi di continuo e buttano via gli scambi
        # di quei pool perche' «non sono nostri».
        # Misurato: a tre fette servono ~14 ore per i 3.723 pool che mancano su robinhood. Mettendo
        # la popolazione nel registro, ogni raccoglitore che passa di li' li tiene, senza aggiungere
        # un solo lavoro ne' una sola chiamata al nodo.
        try:
            _basi = set(json.load(open("data/valute_base.json")).get(ch, []))
            _cop = {k.lower(): v for k, v in
                    json.load(open(f"data/multichain/{ch}/coppie.json")).get("coppie", {}).items()}
            _agg = 0
            with gzip.open(f"data/multichain/{ch}/censimento.jsonl.gz", "rt") as _f:
                for _l in _f:
                    if not _l.strip():
                        continue
                    _d = json.loads(_l)
                    if _d.get("scambi", 0) < 20 or _d["pool"] in d:
                        continue
                    _v = _cop.get(_d["pool"])
                    if not _v:
                        continue
                    _t0 = (_v.get("t0") or "").lower()
                    _t1 = (_v.get("t1") or "").lower()
                    if (_t0 in _basi) == (_t1 in _basi):
                        continue
                    d[_d["pool"]] = {"ent": None, "t0": None, "fonte": "popolazione"}
                    _agg += 1
            if _agg:
                print(f"ELENCO_RIGHE | {ch}: +{_agg} pool dalla popolazione definita", flush=True)
        except Exception as _e:
            print(f"ELENCO_RIGHE | {ch}: popolazione non leggibile ({type(_e).__name__})", flush=True)
        p = f"data/multichain/{ch}/righe.json"
        try:
            json.dump({"ts": int(time.time()), "n": len(d), "pool": d}, open(p, "w"))
            print(f"ELENCO_RIGHE | {ch}: {len(d)} pool che diventano righe", flush=True)
        except Exception as e:
            print(f"ELENCO_RIGHE | {ch}: non riesco a scrivere ({type(e).__name__})", flush=True)


if __name__ == "__main__":
    main()
