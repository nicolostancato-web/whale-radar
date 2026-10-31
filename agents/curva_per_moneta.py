"""LA CURVA DI UNA MONETA, TUTTA INTERA — letta dal suo blocco di nascita, non da una finestra.

== PERCHE' ESISTE (7/10/2026, pomeriggio) ==

`curva_pons.fase_scambi` legge per FINESTRE DI BLOCCHI recenti, senza filtro sull'indirizzo
(senza address la chain regge 30.000 blocchi per chiamata). Funziona, e i suoi conti sono esatti:
verificato il 7/10 contro la chain, identici fino alla decima cifra.

Ma legge il pezzo sbagliato di mondo. Di una moneta nata mesi fa vediamo solo la coda: su un
campione di 13 posizioni verificabili, **5 erano parziali**, e quando lo sono si vede in mediana
il **25%** delle operazioni di quel portafoglio. Di uno di cui si vedono le vendite ma non gli
acquisti si dice che e' un fenomeno: e' il modo piu' semplice di inventarsi una X.

Qui si gira la lettura: non «quali scambi sono successi di recente», ma **«tutta la vita di questa
moneta»**. Col filtro sull'indirizzo della curva la chain regge 10 milioni di blocchi per chiamata
(misurato, non assunto), e la vita di una moneta ci sta dentro. Due chiamate per moneta, e la
posizione di ogni portafoglio su quella moneta e' **intera per costruzione**: il terzo requisito
non va piu' verificato caso per caso, e' garantito da come si legge.

Costo: zero euro (il nostro RPC). ~5.300 monete graduate x 2 chiamate, divise fra le fette.
"""
import collections
import glob
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import a_fette as AF                                         # noqa: E402


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
LANCI = os.environ.get("LANCI", f"{BASE}/curva_lanci.json.gz")
COPPIE = os.environ.get("COPPIE", f"{BASE}/coppie.json")
BUDGET = int(os.environ.get("BUDGET_SEC", "2700"))
VERSIONE = 1
ZERO = "0x" + "0" * 40


def graduate(lanci):
    """Le monete che hanno chiuso la curva: quelle per cui la storia e' finita e misurabile."""
    if not os.path.exists(COPPIE):
        # NON ripiego su «prendile tutte»: sono 675.145 lanci contro 5.268 graduate, 128 volte
        # il lavoro, e nessuno se ne accorgerebbe guardando l'output. Un elenco che manca e' un
        # elenco che manca: lo dico e non parto. E' la stessa famiglia dell'errore che mi
        # perseguita da tre giorni — un'assenza trattata come un fatto.
        print(f"MONETA | manca {COPPIE}: senza il registro delle coppie non so QUALI monete "
              f"hanno graduato, e leggerle tutte sarebbe 128 volte il lavoro. Non parto.")
        return []
    fuori = set()
    try:
        for _p, v in _coppie().items():
            for lato in ("t0", "t1"):
                a = (v.get(lato) or "").lower()
                if a and a != ZERO and a in lanci:
                    fuori.add(a)
    except Exception as e:
        print(f"MONETA | coppie illeggibili ({str(e)[:60]}): non tiro a indovinare, non parto.")
        return []
    return sorted(fuori)


def una_moneta(tok, L, assets, bn):
    """Tutta la curva di una moneta, per portafoglio. None se la chain non ha risposto."""
    curva = L["curva"].lower()
    a = (assets or {}).get((L.get("quote") or "").lower(), {})
    valute = {curva: (a.get("simbolo"), a.get("decimali"))}
    per_chi = collections.defaultdict(lambda: {"compra_valuta": 0.0, "compra_gettoni": 0.0,
                                               "vende_valuta": 0.0, "vende_gettoni": 0.0,
                                               "n_compra": 0, "n_vende": 0,
                                               "primo": None, "ultimo": None,
                                               "tx_compra": [], "tx_vende": []})
    for topic, verso in ((CP.T_COMPRA, "compra"), (CP.T_VENDE, "vende")):
        log = CP.log_di_finestra(topic, L["blocco"], min(bn, L["blocco"] + 9999999),
                                 indirizzo=curva)
        if log is None:
            # UNA MONETA LETTA A META' NON SI SCRIVE. Se la seconda chiamata fallisce e la prima
            # no, le righe direbbero «ha comprato e non ha mai venduto»: una perdita del 100%
            # inventata da un errore di rete. Meglio niente che una storia mutilata.
            return None
        for x in log:
            r = CP._riga(x, verso, valute)
            if not r:
                continue
            # chi_riceve: il router compra per altri (25,8% degli eventi)
            d = per_chi[r["chi_riceve"]]
            d[verso + "_valuta"] += r["valuta"]
            d[verso + "_gettoni"] += r["gettoni"]
            d["n_" + verso] += 1
            if len(d["tx_" + verso]) < 3:
                d["tx_" + verso].append(r["tx"])
            b = r["blocco"]
            d["primo"] = b if d["primo"] is None else min(d["primo"], b)
            d["ultimo"] = b if d["ultimo"] is None else max(d["ultimo"], b)
    sim, dec = valute[curva]
    for d in per_chi.values():
        d["simbolo"] = sim
        d["grezzo"] = dec is None
    return per_chi


def main():
    if CHAIN != "robinhood":
        print(f"MONETA | la curva di Pons e' di robinhood: su {CHAIN} niente da fare.")
        return 0
    t0 = time.time()
    if not os.path.exists(LANCI):
        print(f"MONETA | manca {LANCI}: senza l'elenco dei lanci non so dove sono le curve.")
        return 0
    dl = json.load(gzip.open(LANCI, "rt"))
    lanci, assets = dl.get("da", {}), dl.get("assets", {})
    tutte = AF.mia_parte_stabile(graduate(lanci), lambda t: t)
    i_f, n_f = AF.quale_fetta()
    print(f"MONETA | fetta {i_f+1}/{n_f}: {len(tutte):,} monete graduate da leggere intere",
          flush=True)
    if not tutte:
        return 0

    pf = f"{BASE}/moneta_fatte_pezzo_{i_f}.json"
    ps = f"{BASE}/moneta_pezzo_{i_f}.jsonl.gz"
    fatte = set()
    if os.path.exists(pf):
        try:
            c = json.load(open(pf))
            if int(c.get("versione", 0)) < VERSIONE:
                print(f"MONETA | versione {c.get('versione')}: butto e rifaccio")
                for q in (pf, ps):
                    try:
                        os.remove(q)
                    except OSError:
                        pass
            else:
                fatte = set(c["monete"])
        except Exception:
            fatte = set()
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("MONETA | la chain non dice il blocco attuale: non comincio nemmeno.")
        return 0

    nuove = righe = saltate = 0
    with gzip.open(ps, "at") as f:
        for tok in tutte:
            if tok in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print(f"MONETA | finito il tempo: mi fermo e segno dove sono.", flush=True)
                break
            d = una_moneta(tok, lanci[tok], assets, bn)
            if d is None:
                saltate += 1
                continue
            for chi, v in d.items():
                # INTERA PER COSTRUZIONE: letta dal blocco di nascita col filtro sull'indirizzo,
                # quindi non c'e' una «parte fuori finestra». E' il terzo requisito, garantito
                # dalla lettura invece che verificato caso per caso.
                f.write(json.dumps({"v": VERSIONE, "moneta": tok, "chi": chi,
                                    "intera": True, **v}) + "\n")
                righe += 1
            fatte.add(tok)
            nuove += 1
            if nuove % 25 == 0:
                json.dump({"versione": VERSIONE, "monete": sorted(fatte)}, open(pf, "w"))
                print(f"MONETA | {nuove:,} monete, {righe:,} righe, "
                      f"{int(time.time()-t0)}s", flush=True)
    json.dump({"versione": VERSIONE, "monete": sorted(fatte)}, open(pf, "w"))
    print(f"MONETA | fatte {nuove:,} monete in questo giro ({len(fatte):,} in tutto), "
          f"{righe:,} righe, {saltate} saltate perche' la chain non ha risposto", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
