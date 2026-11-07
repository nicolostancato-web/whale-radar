"""Cerca un filtro che renda positiva la strategia dentro la curva. Con la cassaforte.

IL MANDATO (Nicolo', 12/10): «applichiamo altri filtri finche' troviamo una metrica che ci da'
di nuovo una percentuale positiva. Usa strategie diverse una dopo l'altra, poi le smonti, poi
ne crei un'altra.»

E la sua prima ipotesi: «quella aveva una velocita' d'acquisto alta, ma c'erano i BOT dentro» —
cioe' il punteggio di andamento conta i SOLDI e non le PERSONE, e una curva riempita da un bot
solo sembra identica a una riempita da trenta compratori veri.

LA DISCIPLINA, perche' senza questa su 56 operazioni si trova sempre qualcosa:
  · le caratteristiche si calcolano SOLO con cio' che si sapeva PRIMA di comprare. Una
    caratteristica che usa il futuro e' una profezia, non un filtro.
  · si cerca sulla PRIMA META' delle operazioni e si verifica sulla SECONDA. Un filtro che
    funziona solo dove l'ho cercato non e' un filtro.
  · si stampano tutte le caratteristiche provate, non solo quella che ha funzionato: sapere
    quante ne ho provate e' l'unico modo di sapere quanto vale quella che resta.
"""
import json
import os
import statistics
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import curva_pons as CP                                        # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
STATO = f"{BASE}/prova_nella_curva.json"
ARCH = f"{BASE}/caratteristiche_entrata.json"
COSTO = 1.0591
QUANTE = int(os.environ.get("QUANTE", "20"))


NOTI = f"{BASE}/compratori_noti.json"


def _compratori_noti():
    """Chi abbiamo gia' visto comprare su altre curve. Si accumula fra una lettura e l'altra."""
    if os.path.exists(NOTI):
        try:
            return json.load(open(NOTI))
        except json.JSONDecodeError:
            return {}
    return {}


def esito(cam, stop=0.95, bers=1.5):
    for _b, x in cam:
        if x <= stop:
            return stop / COSTO
        if x >= bers:
            return bers / COSTO
    return (cam[-1][1] if cam else 1.0) / COSTO


def caratteristiche(cur, nato, fino_a):
    """Tutto cio' che si sapeva PRIMA di comprare, letto dalla chain."""
    comp, vend = [], []
    for topic, dove in ((CP.T_COMPRA, comp), (CP.T_VENDE, vend)):
        lg = CP.log_di_finestra(topic, nato, fino_a, indirizzo=cur)
        if lg is None:
            return None
        for x in lg:
            r = CP._riga(x, "compra" if dove is comp else "vende", {cur: (None, 18)})
            if r and r["valuta"] > 0:
                dove.append(r)
    if len(comp) < 3:
        return None
    chi = {}
    for r in comp:
        a = (r.get("chi_riceve") or r.get("chi_compra") or "").lower()
        chi[a] = chi.get(a, 0.0) + r["valuta"]
    # LA STORIA DI CHI COMPRA (12/10, idea di Nicolo' sui bot): «un indirizzo che esiste da ieri
    # e compra una volta sola e' diverso da uno che compra su dieci monete al giorno». Qui si
    # conta quanti dei compratori sono NOTI, cioe' li avevamo gia' visti comprare su altre curve.
    # Una curva riempita da indirizzi mai visti somiglia a una flotta creata per l'occasione;
    # una riempita da indirizzi ricorrenti somiglia a gente che compra memecoin di mestiere.
    noti = _compratori_noti()
    ricorrenti = sum(1 for a in chi if a in noti)
    for a in chi:
        noti[a] = noti.get(a, 0) + 1
    tot = sum(chi.values()) or 1e-18
    minuti = max((fino_a - nato) / 600, 0.01)
    piu_grosso = max(chi.values())
    return {
        "compratori": len(chi),
        "compratori_al_minuto": round(len(chi) / minuti, 3),
        "acquisti": len(comp),
        "acquisto_medio": round(tot / len(comp), 5),
        "quota_del_piu_grosso": round(piu_grosso / tot, 4),
        "quota_dei_primi_tre": round(sum(sorted(chi.values(), reverse=True)[:3]) / tot, 4),
        "vendite_prima": len(vend),
        "quota_venduta_prima": round(sum(r["valuta"] for r in vend) / tot, 4),
        "minuti_alla_soglia": round(minuti, 2),
        "velocita": round(tot / minuti, 3),
        "compratori_ricorrenti": ricorrenti,
        "quota_compratori_ricorrenti": round(ricorrenti / max(len(chi), 1), 3),
    }


def main():
    st = json.load(open(STATO))
    cur = st["curve"]
    ch = [p for p in st["posizioni"].values()
          if p["stato"] == "chiusa" and p.get("cammino") and p.get("soglia") == 1.5]
    ch.sort(key=lambda p: p["aperta_il"])
    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {}
    fatte = 0
    for p in ch:
        k = p["gettone"]
        if k in db or fatte >= QUANTE:
            continue
        c = cur.get(p["curva"])
        if not c:
            db[k] = {"niente": True}
        else:
            d = caratteristiche(p["curva"], c["nata_al_blocco"], p["blocco_entrata"])
            db[k] = d or {"niente": True}
        fatte += 1
        json.dump(db, open(ARCH, "w"), indent=1)
        if d:
            noti = _compratori_noti()
            json.dump(noti, open(NOTI, "w"))

    casi = []
    for p in ch:
        d = db.get(p["gettone"])
        if d and not d.get("niente"):
            casi.append((d, esito(p["cammino"]), max(x for _b, x in p["cammino"])))
    print(f"FILTRO | {len(casi)} operazioni con le caratteristiche lette\n")
    if len(casi) < 16:
        print("   servono almeno 16 operazioni per dividere in due meta'")
        return 0
    mezzo = len(casi) // 2
    cerca, prova = casi[:mezzo], casi[mezzo:]
    nomi = [k for k in casi[0][0] if isinstance(casi[0][0][k], (int, float))]
    print(f"{'caratteristica':<24}{'verso':>7}{'CERCA (1a meta)':>20}{'PROVA (2a meta)':>20}")
    print("-" * 71)
    for n in nomi:
        for verso in (1, -1):
            med = statistics.median(d[n] for d, _r, _m in cerca)
            def gruppo(g):
                sel = [r for d, r, _m in g if (d[n] >= med) == (verso > 0)]
                return (statistics.mean(sel) - 1) * 100 if len(sel) >= 4 else None
            a, b = gruppo(cerca), gruppo(prova)
            if a is None or b is None:
                continue
            if a < 2.0:
                continue                 # non promettente nemmeno dove l'ho cercato
            print(f"{n:<24}{'alto' if verso > 0 else 'basso':>7}{a:>19.2f}%{b:>19.2f}%")
    print("-" * 71)
    print("si legge SOLO la colonna PROVA: la prima e' dove ho cercato, e li' si trova\n"
          "sempre qualcosa. Un filtro vale se tiene nella seconda.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
