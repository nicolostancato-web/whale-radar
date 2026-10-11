"""LA SELEZIONE: quali monete comprare, deciso con cio' che si sa AL MOMENTO DEL DIPLOMA.

== PERCHE' (7/10/2026, notte) ==

Comprare OGNI moneta diplomata non ha edge, e ora e' provato fuori campione: la regola migliore
della prima metà («vendo a 2x», mediana +96,1%) in cassaforte ha fatto **−53,8%**.

Se un vantaggio esiste sta nella **selezione**. E la selezione deve usare solo informazioni
disponibili **prima** di comprare, cioe' al diploma: come e' andata la vita sulla curva. Usare
qualcosa che si sa dopo e' barare con se stessi, ed e' il modo piu' comune di inventarsi un edge.

== LA REGOLA CHE MI IMPONGO ==

Le caratteristiche si guardano **tutte** sulla prima metà (e' lecito: serve a scegliere), ne si
sceglie **UNA**, e si prova **UNA volta** sulla cassaforte. Provarne dieci sulla cassaforte
significa bruciarla, e allora tanto valeva non averla.

Il criterio di scelta e' dichiarato PRIMA di guardare: vince la caratteristica con la maggiore
differenza, sulla prima metà, fra la quota di monete che arrivano a 2x nel terzo superiore e nel
terzo inferiore. Dichiararlo dopo vorrebbe dire scegliere il risultato.
"""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
SERIE = f"{BASE}/serie_pool.jsonl"
TRATTI = f"{BASE}/tratti_al_diploma.jsonl"
FUORI = f"{BASE}/scelta_al_diploma.json"
BUDGET = int(os.environ.get("BUDGET_SEC", "2400"))
import gzip                                                  # noqa: E402


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


CRITERIO = ("vince la caratteristica con la maggiore differenza, sulla PRIMA META', fra la quota "
            "di monete che arrivano a 2x nel terzo superiore e nel terzo inferiore. Dichiarato "
            "prima di guardare i dati.")


def tratti_di(tok, L, assets, bn):
    """Cio' che si sa della curva al momento del diploma. None se la chain non risponde."""
    v = L[tok]
    curva = v["curva"].lower()
    a = assets.get((v.get("quote") or "").lower(), {})
    if a.get("decimali") is None:
        return {}
    valute = {curva: (a.get("simbolo"), a.get("decimali"))}
    comp = CP.log_di_finestra(CP.T_COMPRA, v["blocco"], min(bn, v["blocco"] + 9999999),
                              indirizzo=curva)
    vend = CP.log_di_finestra(CP.T_VENDE, v["blocco"], min(bn, v["blocco"] + 9999999),
                              indirizzo=curva)
    if comp is None or vend is None:
        return None
    B = [CP._riga(x, "compra", valute) for x in comp]
    B = [r for r in B if r and r["valuta"] > 0]
    S = [CP._riga(x, "vende", valute) for x in vend]
    S = [r for r in S if r and r["valuta"] > 0]
    if len(B) < 3:
        return {}
    B.sort(key=lambda r: (r["blocco"], r["ordine"]))
    esenti = {r["chi_riceve"] for r in B
              if r["blocco"] <= v["blocco"] + 50 and 100 * r["commissione"] / r["valuta"] < 50}
    tassati = {r["chi_riceve"] for r in B
               if r["blocco"] <= v["blocco"] + 50 and 100 * r["commissione"] / r["valuta"] >= 50}
    return {
        "compratori": len({r["chi_riceve"] for r in B}),
        "acquisti": len(B),
        "capitale": round(sum(r["valuta"] for r in B), 9),
        "blocchi_per_riempirsi": B[-1]["blocco"] - v["blocco"],
        "esenti": len(esenti),
        "tassati_99": len(tassati),
        "vendite_sulla_curva": len(S),
        "quota_venduta_sulla_curva": round(
            sum(r["gettoni"] for r in S) / max(sum(r["gettoni"] for r in B), 1e-9), 4),
        "acquisto_mediano": round(statistics.median([r["valuta"] for r in B]), 9),
        "simbolo": a.get("simbolo"),
    }


def accumula():
    dl = _lanci_interi()
    L, assets = dl["da"], dl["assets"]
    volute = []
    for l in open(SERIE):
        if l.strip():
            x = json.loads(l)
            if len(x.get("serie") or []) >= 3:
                volute.append(x["moneta"])
    fatte = set()
    if os.path.exists(TRATTI):
        for l in open(TRATTI):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    da_fare = [t for t in volute if t not in fatte]
    print(f"TRATTI | {len(volute)} monete con serie, {len(fatte)} gia' fatte, "
          f"{len(da_fare)} da fare", flush=True)
    if not da_fare:
        return
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("TRATTI | la chain non dice il blocco: non comincio.")
        return
    t0 = time.time()
    n = 0
    with open(TRATTI, "a", buffering=1) as f:
        for tok in da_fare:
            if time.time() - t0 > BUDGET:
                print("TRATTI | finito il tempo: mi fermo, l'archivio resta.", flush=True)
                break
            d = tratti_di(tok, L, assets, bn)
            if d is None:
                continue                  # mezza lettura non si scrive
            f.write(json.dumps({"moneta": tok, **d}) + "\n")
            n += 1
            time.sleep(0.3)
            if n % 25 == 0:
                print(f"TRATTI | {n} fatte, {int(time.time()-t0)}s", flush=True)
    print(f"TRATTI | aggiunte {n}", flush=True)


CARATTERISTICHE = ["compratori", "acquisti", "capitale", "blocchi_per_riempirsi", "esenti",
                   "tassati_99", "vendite_sulla_curva", "quota_venduta_sulla_curva",
                   "acquisto_mediano"]


def misura():
    serie = {}
    for l in open(SERIE):
        if l.strip():
            x = json.loads(l)
            if len(x.get("serie") or []) >= 3:
                serie[x["moneta"]] = (x["nato"], x["serie"])
    righe = []
    if not os.path.exists(TRATTI):
        print("SCELTA | nessun archivio di caratteristiche.")
        return 0
    for l in open(TRATTI):
        if not l.strip():
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d["moneta"] in serie and d.get("compratori"):
            nato, s = serie[d["moneta"]]
            d["nato"] = nato
            d["arriva_2x"] = 1 if max(s) / s[0] >= 2 else 0
            d["arriva_10x"] = 1 if max(s) / s[0] >= 10 else 0
            righe.append(d)
    righe.sort(key=lambda d: d["nato"])
    m = len(righe) // 2
    scelta, cassaforte = righe[:m], righe[m:]
    print(f"\nSCELTA | {len(righe)} monete complete: {len(scelta)} per scegliere, "
          f"{len(cassaforte)} in cassaforte", flush=True)
    if len(cassaforte) < 40:
        print(f"SCELTA | cassaforte con {len(cassaforte)} monete: non scelgo e non concludo.")
        return 0
    print(f"SCELTA | criterio dichiarato: {CRITERIO}\n")
    print(f"{'caratteristica':28} {'2x terzo alto':>14} {'terzo basso':>12} {'differenza':>11}")
    punteggi = {}
    for c in CARATTERISTICHE:
        v = sorted(scelta, key=lambda d: d.get(c) or 0)
        t = max(1, len(v) // 3)
        basso, alto = v[:t], v[-t:]
        qa = sum(d["arriva_2x"] for d in alto) / len(alto)
        qb = sum(d["arriva_2x"] for d in basso) / len(basso)
        punteggi[c] = qa - qb
        print(f"{c:28} {100*qa:13.1f}% {100*qb:11.1f}% {100*(qa-qb):+10.1f}%")
    vinta = max(punteggi, key=lambda c: abs(punteggi[c]))
    verso = "alto" if punteggi[vinta] > 0 else "basso"
    print(f"\nSCELTA | caratteristica scelta: «{vinta}», terzo {verso}", flush=True)

    # LA CASSAFORTE, UNA VOLTA SOLA
    v = sorted(cassaforte, key=lambda d: d.get(vinta) or 0)
    t = max(1, len(v) // 3)
    gruppo = v[-t:] if verso == "alto" else v[:t]
    q_sel = sum(d["arriva_2x"] for d in gruppo) / len(gruppo)
    q_tutti = sum(d["arriva_2x"] for d in cassaforte) / len(cassaforte)
    q10_sel = sum(d["arriva_10x"] for d in gruppo) / len(gruppo)
    q10_tutti = sum(d["arriva_10x"] for d in cassaforte) / len(cassaforte)
    print(f"SCELTA | IN CASSAFORTE: selezionate {len(gruppo)} monete -> arrivano a 2x il "
          f"{100*q_sel:.1f}%, contro il {100*q_tutti:.1f}% di tutte")
    print(f"SCELTA |                 arrivano a 10x il {100*q10_sel:.1f}%, contro "
          f"{100*q10_tutti:.1f}%")
    regge = q_sel > q_tutti + 0.05
    print(f"SCELTA | {'REGGE' if regge else 'NON REGGE'}")
    json.dump({"chain": CHAIN, "monete": len(righe), "criterio": CRITERIO,
               "prima_meta": {k: round(v, 4) for k, v in punteggi.items()},
               "scelta": vinta, "verso": verso,
               "cassaforte": {"monete": len(cassaforte), "selezionate": len(gruppo),
                              "2x_selezionate": round(q_sel, 4), "2x_tutte": round(q_tutti, 4),
                              "10x_selezionate": round(q10_sel, 4),
                              "10x_tutte": round(q10_tutti, 4)},
               "verdetto": "REGGE" if regge else "NON REGGE"},
              open(FUORI, "w"), indent=1)
    print(f"SCELTA | scritto {FUORI}")
    return 0


if __name__ == "__main__":
    if os.environ.get("SOLO_MISURA") != "1":
        accumula()
    sys.exit(misura())
