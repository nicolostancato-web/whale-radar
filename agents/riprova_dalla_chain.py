"""RICALCOLARE UN CASO DA ZERO, dalla chain, senza passare dalla nostra pipeline.

== PERCHE' NON BASTANO LE NOSTRE PROVE (7/10/2026) ==

`prima_la_prova.py` controlla gli hash che le nostre righe si portano dietro. E' un passo avanti,
ma ha un limite: **le prove le scrive la stessa pipeline che potrebbe sbagliare**, e sulla curva
sono tenute solo per i candidati (99,5% delle posizioni non ne ha, per una scelta di peso: con le
prove per tutti il file pesava 290 MB a giro). Quindi il caso in cima a una classifica NUOVA e'
quasi sempre non verificabile.

Qui la verifica e' un **cammino indipendente**: si parte dall'indirizzo del portafoglio e da
quello della moneta, si rileggono gli eventi della sua curva dalla chain, e si rifa' il conto da
zero. Se il numero della pipeline e quello ricalcolato non combaciano, non e' importante quale dei
due sia giusto: **il caso non esce**.

E' la differenza fra chiedere a qualcuno di ricontrollare il proprio compito e rifarlo da capo.

Uso:
    riprova_dalla_chain.py <portafoglio> <moneta>
"""
import json
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
LANCI = os.environ.get("LANCI", f"{BASE}/curva_lanci.json.gz")


def _lanci():
    with gzip.open(LANCI, "rt") as f:
        d = json.load(f)
    return d.get("da", {}), d.get("assets", {})


def conto_dalla_chain(chi, moneta, lanci=None, assets=None, finestra=None):
    """Il conto di QUEL portafoglio su QUELLA moneta, rifatto dalla chain. None se non si puo'."""
    chi, moneta = chi.lower(), moneta.lower()
    if lanci is None:
        lanci, assets = _lanci()
    L = lanci.get(moneta)
    if not L:
        return {"esito": "moneta non nei lanci: non posso verificare"}
    curva = L["curva"].lower()
    a = (assets or {}).get((L.get("quote") or "").lower(), {})
    dec = a.get("decimali")
    valute = {curva: (a.get("simbolo"), dec)}

    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    fuori = {"compra_valuta": 0.0, "compra_gettoni": 0.0, "vende_valuta": 0.0,
             "vende_gettoni": 0.0, "n_compra": 0, "n_vende": 0, "grezzo": dec is None,
             "simbolo": a.get("simbolo"), "tx": [],
             "eventi_dentro_finestra": 0, "eventi_fuori_finestra": 0}
    for topic, verso in ((CP.T_COMPRA, "compra"), (CP.T_VENDE, "vende")):
        # UNA SOLA CHIAMATA per evento: col filtro sull'indirizzo la chain regge 10 milioni di
        # blocchi (misurato, non assunto), e la curva di una moneta vive in meno di cosi'.
        log = CP.log_di_finestra(topic, L["blocco"], min(bn, L["blocco"] + 9999999),
                                 indirizzo=curva)
        if log is None:
            return {"esito": "la chain non ha risposto: non dichiaro niente"}
        for x in log:
            r = CP._riga(x, verso, valute)
            if not r:
                continue
            # chi_riceve, non chi firma: il router compra per altri (25,8% degli eventi)
            if r["chi_riceve"] != chi and r["chi_compra"] != chi:
                continue
            fuori[verso + "_valuta"] += r["valuta"]
            fuori[verso + "_gettoni"] += r["gettoni"]
            fuori["n_" + verso] += 1
            if len(fuori["tx"]) < 6:
                fuori["tx"].append(r["tx"])
            # LA POSIZIONE E' INTERA O E' UNA FETTA? (7/10, terza causa trovata)
            # Le nostre somme coprono una FINESTRA di blocchi, e «coperto 100%» significa 100%
            # della finestra, non della storia di un portafoglio. Su un campione di 13
            # posizioni verificabili, 5 avevano operazioni fuori dalla finestra, e quando
            # succede ne vediamo in mediana il 25%. Di un portafoglio di cui si vedono le
            # vendite ma non gli acquisti si dice che e' bravissimo: e' il modo piu' semplice
            # di inventarsi una X, e non lo risolvono ne' le versioni ne' i duplicati.
            if finestra:
                dentro = finestra[0] <= r["blocco"] <= finestra[1]
                fuori["eventi_" + ("dentro" if dentro else "fuori") + "_finestra"] += 1
    fuori["esito"] = "ok"
    return fuori


def caso_pulito(chi, moneta, dichiarato, finestra=None, lanci=None, assets=None):
    """I TRE REQUISITI perche' un caso possa essere mostrato a Nicolo'. Tutti e tre, o niente.

    1. i numeri della pipeline combaciano con quelli ricalcolati dalla chain;
    2. i gettoni venduti sono quelli comprati (altrimenti e' un rapporto fra merci diverse);
    3. la posizione e' INTERA: nessuna operazione fuori dalla finestra che abbiamo letto.
    """
    r = conto_dalla_chain(chi, moneta, lanci, assets, finestra)
    ok, guai = combacia(dichiarato, r)
    if finestra and r.get("eventi_fuori_finestra", 0) > 0:
        d, f = r["eventi_dentro_finestra"], r["eventi_fuori_finestra"]
        ok = False
        guai.append(f"posizione PARZIALE: {d} operazioni dentro la finestra letta, {f} fuori "
                    f"({100*d/max(d+f,1):.0f}% della sua storia). Il moltiplicatore sarebbe "
                    f"calcolato su una fetta.")
    return ok, guai, r


def combacia(dichiarato, ricalcolato, tolleranza=0.02):
    """Combaciano? Si confrontano i quattro numeri che contano, non uno solo."""
    if ricalcolato.get("esito") != "ok":
        return False, [ricalcolato.get("esito")]
    guai = []
    for c in ("compra_valuta", "compra_gettoni", "vende_valuta", "vende_gettoni"):
        a, b = float(dichiarato.get(c, 0.0) or 0.0), float(ricalcolato.get(c, 0.0) or 0.0)
        if max(abs(a), abs(b)) <= 0:
            continue
        if abs(a - b) / max(abs(a), abs(b)) > tolleranza:
            guai.append(f"{c}: pipeline {a:.10g} vs chain {b:.10g}")
    # IL CONTROLLO CHE IL 7/10 MANCAVA: i gettoni venduti devono essere quelli comprati. Un
    # rapporto fra due cifre di denaro su merce diversa non e' un guadagno, e il «157x» era
    # esattamente questo: un portafoglio che vendeva 100 volte i gettoni che aveva comprato.
    ci, co = ricalcolato["compra_gettoni"], ricalcolato["vende_gettoni"]
    if ci > 0 and co > 0 and not (0.9 <= co / ci <= 1.1):
        guai.append(f"gettoni che non tornano: venduti {co/ci:.2f}x quelli comprati "
                    f"(sulla chain, non nei nostri file)")
    return not guai, guai


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    r = conto_dalla_chain(sys.argv[1], sys.argv[2])
    print(json.dumps(r, indent=1))
    if r.get("esito") == "ok":
        sp = r["vende_valuta"] - r["compra_valuta"]
        x = (r["vende_valuta"] / r["compra_valuta"]) if r["compra_valuta"] > 0 else None
        print(f"\nRICALCOLATO DALLA CHAIN: speso {r['compra_valuta']:.9g}, "
              f"incassato {r['vende_valuta']:.9g} ({r['simbolo']}) -> "
              f"{'%.3fx' % x if x else 'mai uscito'}, saldo {sp:+.9g}")
        if r["compra_gettoni"] > 0:
            print(f"   gettoni: comprati {r['compra_gettoni']:.6g}, venduti "
                  f"{r['vende_gettoni']:.6g} "
                  f"({100*r['vende_gettoni']/r['compra_gettoni']:.1f}% — sotto il 90% o sopra "
                  f"il 110% il conto non e' un guadagno)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
