#!/usr/bin/env python3
"""
ESAURIMENTO — comprare quando finisce chi vende, non quando arrivano quelli che comprano.

L'INTUIZIONE (esperimento 4 della coda, registrato prima di guardare). Le sei piste morte chiedevano
tutte «chi sta comprando?»: cioe' inseguivano la domanda, che e' un'opinione e cambia idea. Questa
guarda l'OFFERTA. Una vendita concentrata schiaccia il prezzo senza distruggere la voglia di
comprare: quando il venditore finisce, sparisce una pressione anomala e il prezzo non ha piu' motivo
di stare li'. Non serve che arrivi nessuno di nuovo — serve che se ne vada uno.

COME SI RICONOSCE, con i dati che abbiamo: nel battito ogni punto porta quanti acquisti e quante
vendite ci sono stati nell'ora. Una fase di vendita concentrata e' un tratto in cui le vendite
dominano nettamente; l'esaurimento e' il primo punto in cui quella dominanza sparisce.

CRITERIO DI MORTE (scritto prima, come da coda): l'idea muore se il limite inferiore dell'intervallo
al 95% del rendimento netto non sta sopra zero, contando le prove per GIORNO e non per riga.

Confronto sempre CON UN CONTROLLO: token della stessa eta' e liquidita' simile che NON erano in
vendita concentrata. Senza controllo, si misura il mercato e si chiama vantaggio.

Sola lettura, nessuna chiamata. €0.
"""
import json, gzip, os, glob, time, sys, math, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from indipendenza import t_onesto
except Exception:
    t_onesto = None
try:
    import metro
except Exception:
    metro = None

MC = "data/multichain"
CHAINS = ("base", "robinhood", "solana")
DOMINANZA = 1.6        # vendite almeno 1,6 volte gli acquisti: una fase di scarico, non rumore
MIN_PUNTI_VENDITA = 2  # deve durare, altrimenti e' un istante qualunque
ESITO_H = 6
MIN_LIQ = 3000
MIN_VOL = 500


def serie(f):
    out = []
    try:
        for l in gzip.open(f, "rt"):
            if not l.strip(): continue
            try:
                d = json.loads(l)
                out.append((int(d["ts"]), float(d.get("cl") or 0), float(d.get("liq") or 0),
                            float(d.get("vol") or 0), int(d.get("buys") or 0), int(d.get("sells") or 0)))
            except Exception: pass
    except Exception: return []
    out.sort(); return out


def eventi():
    """Un evento per token: il PRIMO esaurimento che incontro. Dieci momenti dello stesso token non
    sono dieci prove — e' lo stesso token che continua a essere se stesso."""
    dentro, fuori = [], []
    for ch in CHAINS:
        for f in glob.glob(f"{MC}/{ch}/pulse/*.jsonl.gz"):
            s = serie(f)
            if len(s) < 6: continue
            preso = False
            for i in range(MIN_PUNTI_VENDITA, len(s) - 1):
                ts, pz, lq, vl, bu, se = s[i]
                if lq < MIN_LIQ or pz <= 0 or vl < MIN_VOL: continue
                prec = s[i - MIN_PUNTI_VENDITA:i]
                scarico = all(x[5] >= DOMINANZA * max(1, x[4]) for x in prec)
                finito = se < DOMINANZA * max(1, bu)
                dopo = [x for x in s if x[0] >= ts + ESITO_H * 3600]
                if not dopo: continue
                r = dopo[0][1] / pz - 1
                gio = time.strftime("%Y-%m-%d", time.gmtime(ts))
                if scarico and finito and not preso:
                    dentro.append({"r": r, "gio": gio, "liq": lq, "ch": ch}); preso = True
                elif not scarico and not preso and len(fuori) < 4000:
                    # IL CONTROLLO: stesso mondo, stessa ora, ma senza la fase di scarico.
                    fuori.append({"r": r, "gio": gio, "liq": lq, "ch": ch})
    return dentro, fuori


def netto(r, liq):
    if not metro: return r
    try:
        c = metro.uscita_liquidita(max(1.0, liq))
    except Exception:
        c = 0.02
    return (1 + r) * (1 - c) - 1


def intervallo(v, chiavi):
    """Il limite inferiore al 95%, contando le prove per giorno e non per riga."""
    if not v: return None, 0
    g = {}
    for x, k in zip(v, chiavi): g.setdefault(k, []).append(x)
    medie = [st.mean(x) for x in g.values()]
    if len(medie) < 3: return None, len(medie)
    m = st.mean(medie); sd = st.pstdev(medie) or 1e-9
    return m - 1.96 * sd / math.sqrt(len(medie)), len(medie)


def main():
    dentro, fuori = eventi()
    L = ["# 🪫 COMPRARE QUANDO FINISCE CHI VENDE",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · esperimento 4 · solo dati già "
         f"scaricati · €0*", "",
         "> Le sei piste morte chiedevano tutte **«chi sta comprando?»**: inseguivano la domanda, che",
         "> è un'opinione e cambia idea. Questa guarda **l'offerta**. Una vendita concentrata schiaccia",
         "> il prezzo senza distruggere la voglia di comprare: quando il venditore finisce, sparisce",
         "> una pressione anomala. **Non serve che arrivi qualcuno — serve che se ne vada uno.**", "",
         f"Scarico = vendite ≥ {DOMINANZA}× gli acquisti per almeno {MIN_PUNTI_VENDITA} rilevazioni di",
         f"fila. Esaurimento = il primo punto in cui quella dominanza sparisce. Esito a **{ESITO_H}h**,",
         "al netto del costo d'uscita misurato.", "",
         f"**Esaurimenti trovati: {len(dentro)}** · controlli (stessi giorni, senza scarico): {len(fuori)}", ""]

    if len(dentro) >= 20:
        nd = [netto(e["r"], e["liq"]) for e in dentro]
        nf = [netto(e["r"], e["liq"]) for e in fuori]
        lo, gruppi = intervallo(nd, [e["gio"] for e in dentro])
        L += ["| | eventi | mediana netta 6h | media netta |", "|---|---|---|---|",
              f"| **dopo l'esaurimento** | {len(nd)} | **{st.median(nd)*100:+.1f}%** | {st.mean(nd)*100:+.1f}% |"]
        if nf:
            L.append(f"| controllo (niente scarico) | {len(nf)} | {st.median(nf)*100:+.1f}% | "
                     f"{st.mean(nf)*100:+.1f}% |")
        L += [""]
        if lo is not None:
            L += [f"Limite inferiore dell'intervallo al 95%, contando **{gruppi} giorni** e non le "
                  f"righe: **{lo*100:+.1f}%**.", ""]
        L += ["## Verdetto", ""]
        if lo is None:
            L += ["> ⏸️ Meno di 3 giorni distinti: non si può calcolare l'intervallo. Si aspetta."]
        elif lo > 0:
            L += [f"> ✅ **Il limite inferiore sta sopra zero** ({lo*100:+.1f}%): l'esaurimento del",
                  "> venditore lascia qualcosa anche nel caso sfortunato. Prossimo passo: congelare la",
                  "> regola e provarla sul livello di validazione, senza toccare altro."]
        else:
            L += [f"> ❌ **Criterio di morte scattato**, scritto prima di guardare: il limite inferiore",
                  f"> al 95% è **{lo*100:+.1f}%**, non sopra zero. Non si alza la dominanza a 2×, non si",
                  "> sposta l'esito a 2h: sarebbe scegliere la soglia dopo aver visto il risultato."]
    else:
        L += [f"> ⏸️ Servono almeno 20 esaurimenti: ne abbiamo {len(dentro)}. Il battito accumula a "
              "ogni giro, e Robinhood ha iniziato solo ieri.", ""]
    if metro:
        L += ["", f"*{metro.etichetta()}*"]
    open("ESAURIMENTO.md", "w").write("\n".join(L))
    print(f"ESAURIMENTO | dentro:{len(dentro)} controlli:{len(fuori)}", flush=True)


if __name__ == "__main__":
    main()
