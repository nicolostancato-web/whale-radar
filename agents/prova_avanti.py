"""Il contabile della prova in avanti: tiene il punteggio e NON lo guarda prima del tempo.

PERCHE' ESISTE (30/09). La regola e' scritta in PROVA_IN_AVANTI.md: $25 su ogni pool al suo 5°
scambio, liquidazione entro 168 ore, su pool nati DOPO il 30/09/2026. Serve almeno 1.500 pool
nuovi per chain, e **si guarda una volta sola**.

Una prova che dipende da me che mi ricordo di farla, e che resisto alla tentazione di sbirciare
quando va bene, non e' una prova. Quindi:

· questo processo accumula i pool nuovi e i loro esiti, ogni giorno, senza dire com'e' andata;
· stampa SOLO quanti ne ha (il progresso), mai il rendimento, finche' la soglia non e' raggiunta;
· quando la soglia arriva, stampa il verdetto UNA volta e lo scrive nel registro;
· da quel momento non lo ricalcola piu': il primo verdetto e' quello che conta.

Sbirciare e fermarsi quando il numero piace e' il modo classico di comprare rumore. Qui non si
puo' sbirciare perche' il numero **non viene stampato**.
"""
import gzip
import json
import os
import statistics
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
NASCITA_MINIMA = 1790726400          # 30/09/2026 00:00 UTC: prima di questo, e' passato
# SOGLIA ALZATA DA 1.500 A 5.000 IL 30/09, PRIMA DI VEDERE UN SOLO ESITO.
# Misurato il ritmo: ~2.000 pool giudicabili al giorno su robinhood, ~1.100 su base. A 1.500 la
# prova si chiudeva in UN giorno — troppo pochi per una distribuzione a code grasse, dove il 10%
# dei vincitori porta tutto: con pochi casi, la fortuna decide.
# Alzare l'asta PRIMA di guardare rende la prova piu' difficile da superare per caso, ed e' lecito.
# Abbassarla dopo aver visto il risultato non lo e', e questa riga esiste per ricordarlo.
MINIMO_POOL = 5000
SOGLIA_VERDETTO = 0.03
# IL CAMPO SU CUI SI GIUDICA (1/10, riscritto dopo la scoperta della latenza).
# Prima era `_uscita_25`: l'esito comprando al prezzo dello scambio a cui entriamo. Ma quel
# prezzo non si puo' avere — per comprare si manda una transazione, eseguita DOPO quelle
# davanti. Si paga il prezzo successivo, e sui pool veloci costa il 38% in piu'.
# Misurato: il primo numero positivo del progetto (+17,6%) diventa -11,4% con UN solo scambio
# di latenza. Il giudice stava per dare un verdetto preciso su un prezzo che non esiste.
CAMPO = os.environ.get("CAMPO_ESITO", "_uscita_25_ritardo")               # media sopra +3% al netto dei costi
# UN REGISTRO PER CHAIN (30/09). Era uno solo, e appena ho separato i lavori per chain i due
# hanno iniziato a scrivere lo stesso file: il pubblicatore FONDE solo gli archivi `.jsonl.gz`,
# un `.json` lo copia — quindi l'ultima chain pubblicata cancellava l'altra, e il conteggio
# sarebbe tornato indietro senza che nessuno protestasse.
# Trovato subito dopo la separazione, chiedendomi «cosa cambia per chi non ho toccato?».
REGISTRO = f"data/loop1/prova_avanti_{CHAIN}.json"
SORGENTE = f"data/loop1/insieme_{CHAIN}_sc5.jsonl.gz"


_MOD = {}


def punteggio(x):
    """Quanto il modello congelato preferisce questo pool. None se non c'e' il modello."""
    global _MOD
    if not _MOD:
        try:
            _MOD = json.load(open("data/loop1/modello_congelato.json"))
        except (OSError, ValueError):
            _MOD = {"_manca": True}
    m = _MOD.get(CHAIN)
    if not m:
        return None
    s = m["b"]
    for k, w, mu, sd in zip(m["nomi"], m["w"], m["mu"], m["sd"]):
        v = x.get(k)
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = 0.0
        if v != v or v in (float("inf"), float("-inf")):
            v = 0.0
        s += w * (v - mu) / sd
    return round(s, 4)


def carica_registro():
    try:
        return json.load(open(REGISTRO))
    except (OSError, ValueError):
        return {}


def main():
    reg = carica_registro()
    mio = reg.setdefault(CHAIN, {"pool": {}, "verdetto": None, "campo": CAMPO})
    if mio.get("campo") != CAMPO:
        # IL CONTEGGIO RIPARTE SE CAMBIA LA MISURA (1/10). I pool registrati con il vecchio
        # campo misuravano un prezzo non ottenibile: mescolarli con i nuovi darebbe un verdetto
        # su due cose diverse. Si ricomincia, e si dice che si e' ricominciato.
        print(f"PROVA AVANTI | {CHAIN}: la misura e' cambiata da {mio.get('campo')} a {CAMPO}. "
              f"Il conteggio RIPARTE da zero: {len(mio['pool'])} pool registrati col vecchio "
              f"campo non valgono.", flush=True)
        mio = {"pool": {}, "verdetto": None, "campo": CAMPO}
        reg[CHAIN] = mio

    if not os.path.exists(SORGENTE):
        print(f"PROVA AVANTI | {CHAIN}: manca {SORGENTE}, non faccio niente", flush=True)
        return

    nuovi = 0
    for riga in gzip.open(SORGENTE, "rt"):
        if not riga.strip():
            continue
        x = json.loads(riga)
        if not x.get("_giudicabile") or x.get(CAMPO) is None:
            continue
        if x["_t"] < NASCITA_MINIMA:
            continue                                  # nato prima: e' passato, non conta
        if x["_pool"] in mio["pool"]:
            continue
        # SI REGISTRA ANCHE IL PUNTEGGIO DEL MODELLO CONGELATO (30/09). Il contratto misurava
        # solo il fondale «compra tutto». Ma la selezione, bocciata quindici volte, sul dato
        # corretto batte il fondale in undici finestre su dodici: e' il secondo candidato, e
        # senza registrarlo adesso non lo si potra' giudicare sul futuro.
        # Il punteggio si calcola col modello CONGELATO oggi: applicato, mai riaddestrato.
        mio["pool"][x["_pool"]] = [round(x[CAMPO], 5), punteggio(x)]
        nuovi += 1

    n = len(mio["pool"])
    print(f"PROVA AVANTI | {CHAIN}: {n} pool nati dopo il 30/09 ({nuovi} nuovi oggi), "
          f"servono {MINIMO_POOL}", flush=True)

    if mio["verdetto"]:
        v = mio["verdetto"]
        print(f"   verdetto GIA' EMESSO il {v['quando']}: {v['esito']} "
              f"(media {100*v['media']:+.1f}% su {v['pool']} pool). Non si ricalcola.", flush=True)
    elif n < MINIMO_POOL:
        # IL PUNTO DI TUTTO: qui NON si stampa il rendimento. Nemmeno per curiosita'.
        print(f"   ancora {MINIMO_POOL - n} pool al traguardo. "
              f"Il rendimento non si guarda: e' il contratto.", flush=True)
    else:
        v = [p[0] if isinstance(p, list) else p for p in mio["pool"].values()]
        sc = [p for p in mio["pool"].values() if isinstance(p, list) and p[1] is not None]
        media = statistics.mean(v)
        mediana = statistics.median(v)
        esito = "PASSA" if media >= SOGLIA_VERDETTO else "NON PASSA"
        mio["verdetto"] = {"quando": os.environ.get("OGGI", "ignoto"), "media": media,
                           "mediana": mediana, "pool": len(v), "esito": esito}
        print(f"   === VERDETTO: {esito} ===", flush=True)
        print(f"   media {100*media:+.1f}%  mediana {100*mediana:+.1f}%  su {len(v)} pool nuovi",
              flush=True)
        print(f"   serviva sopra +{100*SOGLIA_VERDETTO:.0f}%. Questo numero non si ricalcola.",
              flush=True)
        # IL SECONDO CANDIDATO: il decimo migliore secondo il modello congelato oggi.
        if len(sc) >= MINIMO_POOL // 2:
            sc.sort(key=lambda p: -p[1])
            k = max(20, len(sc) // 10)
            decile = statistics.mean(p[0] for p in sc[:k])
            mio["verdetto"]["decile_modello"] = decile
            print(f"   selezione (decimo migliore del modello CONGELATO): {100*decile:+.1f}% "
                  f"su {k} pool — {'BATTE' if decile > media else 'NON batte'} il fondale",
                  flush=True)

    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    json.dump(reg, open(REGISTRO, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
