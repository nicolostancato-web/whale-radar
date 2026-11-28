#!/usr/bin/env python3
"""
COSTO_USCITA — esperimento 8 della coda.

L'INTUIZIONE. Fin qui abbiamo cercato il rendimento e poi pagato il pedaggio: fino al 26% per uscire
dai pool sottili. E' come scegliere la strada senza guardare il casello. Questo esperimento non cerca
un segnale nuovo: ripara l'aritmetica di quelli che gia' abbiamo. Se ordiniamo i candidati per quanto
costa USCIRE al nostro importo — non per quanto promettono di rendere — un vantaggio gia' esistente
potrebbe emergere solo perche' smettiamo di regalarlo all'uscita.

LA SOGLIA E' DECISA ADESSO, PRIMA DI GUARDARE GLI ESITI: uscita economica = costo misurato <= 8%.
Perche' 8: e' circa la meta' di quello che paghiamo tipicamente, ed e' l'ordine di grandezza del
vantaggio che stiamo cercando. UNA soglia, non venti: cercando fra venti si trova sempre qualcosa,
e quel qualcosa e' rumore con l'aria di un'idea.

IL CRITERIO DI MORTE, scritto adesso: se la mediana NETTA del sottoinsieme a uscita economica non
supera quella dell'insieme intero, su almeno 15 giorni indipendenti, l'idea muore. Non si abbassa la
soglia al 6% ne' la si alza al 12% per farla sopravvivere.

MEDIANE E NON MEDIE: l'esperimento 6 ci ha mostrato che il 99% di una media puo' venire da un token
solo. Una lotteria non decide un verdetto.

Nessuna chiamata di rete: usa la serie 'pulse' gia' scaricata e il metro gia' calibrato. €0.
"""
import json, gzip, os, glob, time, sys, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import metro
except Exception:
    metro = None
try:
    from indipendenza import t_onesto
except Exception:
    t_onesto = None

MC = "data/multichain"
CHAINS = ("base", "solana", "robinhood")
RITARDO_H = 1
ESITO_H = 24
MIN_LIQ = 3000
MIN_VOL = 500
SOGLIA = 0.08        # deciso prima di guardare, e non si tocca


def serie(f):
    out = []
    try:
        for l in gzip.open(f, "rt"):
            if not l.strip(): continue
            try:
                d = json.loads(l)
                out.append((int(d["ts"]), float(d.get("cl") or 0), float(d.get("liq") or 0),
                            float(d.get("vol") or 0)))
            except Exception: pass
    except Exception: return []
    out.sort(); return out


def eventi():
    ev = []
    for ch in CHAINS:
        for f in glob.glob(f"{MC}/{ch}/pulse/*.jsonl.gz"):
            s = serie(f)
            if len(s) < 8: continue
            for i, (t, pz, lq, vl) in enumerate(s):
                if lq < MIN_LIQ or pz <= 0 or vl < MIN_VOL: continue
                # IL COSTO SI LEGGE AL MOMENTO IN CUI SI DECIDE, non sulla media di tutta la storia:
                # e' l'errore che avevamo gia' fatto una volta e che sottostimava il pedaggio di 2-4 volte.
                costo = metro.uscita_liquidita(vl) if metro else None
                if costo is None: continue
                dopo = [x for x in s if x[0] >= t + RITARDO_H * 3600]
                if not dopo: continue
                pe = dopo[0][1]
                fin = [x for x in dopo if x[0] <= dopo[0][0] + ESITO_H * 3600]
                if len(fin) < 3 or pe <= 0: continue
                lordo = fin[-1][1] / pe - 1
                netto = (1 + lordo) * (1 - costo) - 1      # il pedaggio si paga all'uscita, sempre
                ev.append({"gio": time.strftime("%Y-%m-%d", time.gmtime(t)),
                           "costo": costo, "lordo": lordo, "netto": netto})
                break        # un evento per pool
    return ev


def main():
    ev = eventi()
    econ = [e for e in ev if e["costo"] <= SOGLIA]
    L = ["# 🚪💸 SCEGLIERE PER COSTO DI USCITA, NON PER RENDIMENTO ATTESO",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · esperimento 8 · solo dati già "
         f"scaricati · €0*", "",
         "> Finora abbiamo cercato il rendimento e **poi** pagato il pedaggio: fino al 26% per uscire",
         "> dai pool sottili. È scegliere la strada senza guardare il casello.", "",
         "> Questo esperimento **non cerca un segnale nuovo**: ripara l'aritmetica di quelli che",
         "> abbiamo già. Se ordiniamo i candidati per quanto costa **uscire**, un vantaggio esistente",
         "> potrebbe comparire solo perché smettiamo di regalarlo all'uscita.", "",
         f"Soglia decisa **prima** di guardare: uscita economica = costo misurato ≤ **{SOGLIA*100:.0f}%**. "
         "Una soglia sola, non venti: fra venti si trova sempre qualcosa, e quel qualcosa è rumore.", "",
         f"**Eventi: {len(ev)} · di cui a uscita economica: {len(econ)}**", ""]

    # QUANDO LA SOGLIA NON TAGLIA NIENTE (09/09). Alla prima misura TUTTI gli 1161 eventi stavano
    # sotto la soglia: il sottoinsieme era l'insieme, e il confronto non poteva dire niente. Non e'
    # un fallimento del criterio, e' la premessa che cade — e va detto, non aggiustato spostando la
    # soglia finche' separa qualcosa. Il 26% che ci spaventava viene dalla coda sottile che gia'
    # escludiamo: sui pool che scambiano davvero il pedaggio mediano e' sotto l'1%.
    if ev and len(econ) >= 0.97 * len(ev):
        L += [f"| pedaggio | mediana | 95° percentile |", "|---|---|---|",
              f"| costo d'uscita misurato | **{st.median([e['costo'] for e in ev])*100:.1f}%** | "
              f"{sorted(e['costo'] for e in ev)[int(len(ev)*0.95)]*100:.1f}% |", "",
              "## Verdetto", "",
              f"> ❌ **La premessa non regge.** La soglia dell'{SOGLIA*100:.0f}% non taglia niente: "
              f"**{len(econ)} eventi su {len(ev)}** ci stanno sotto. Sui pool che scambiano davvero il",
              "> pedaggio mediano è **sotto l'1%**, non il 26% che ci spaventava — quel 26% viene dalla",
              "> coda sottile che già escludiamo prima di guardare.", "",
              "> **Non sposto la soglia finché separa qualcosa**: sarebbe cercare venti soglie e",
              "> chiamare vantaggio quella fortunata. L'idea muore qui, e lascia un'informazione che",
              "> vale più dell'idea: **il pedaggio non è ciò che ci mangia**. Quello che manca è il",
              "> segnale, non l'aritmetica — e va cercato lì."]
        open("COSTO_USCITA.md", "w").write("\n".join(L + ([f"", f"*{metro.etichetta()}*"] if metro else [])))
        print(f"COSTO_USCITA | premessa caduta: {len(econ)}/{len(ev)} sotto soglia", flush=True)
        return

    if len(ev) >= 25 and len(econ) >= 10:
        L += ["| insieme | eventi | mediana netta 24h | mediana lorda |", "|---|---|---|---|",
              f"| **uscita economica (≤{SOGLIA*100:.0f}%)** | {len(econ)} | "
              f"**{st.median([e['netto'] for e in econ])*100:+.1f}%** | "
              f"{st.median([e['lordo'] for e in econ])*100:+.1f}% |",
              f"| tutti | {len(ev)} | {st.median([e['netto'] for e in ev])*100:+.1f}% | "
              f"{st.median([e['lordo'] for e in ev])*100:+.1f}% |", ""]
        L += [f"*Pedaggio mediano: {st.median([e['costo'] for e in ev])*100:.1f}% su tutti, "
              f"{st.median([e['costo'] for e in econ])*100:.1f}% sul sottoinsieme scelto.*", ""]
        vince = st.median([e["netto"] for e in econ]) > st.median([e["netto"] for e in ev])
        gg = 0
        if t_onesto:
            t_, gg, ting = t_onesto([e["netto"] for e in econ], [e["gio"] for e in econ])
            L += [f"Sul sottoinsieme scelto: t sui **giorni indipendenti** **{t_:+.2f}** "
                  f"({gg} giorni distinti); sulle righe sarebbe {ting:+.2f}.", ""]
        L += ["## Verdetto", ""]
        if gg < 15:
            L += [f"> ⏸️ Il sottoinsieme {'batte' if vince else 'non batte'} l'insieme intero, ma i",
                  f"> giorni indipendenti sono {gg} e il criterio ne chiede 15. Si aspetta, non si conclude."]
        elif vince:
            L += ["> ✅ **Guardare il casello paga**: scegliere per costo d'uscita alza la mediana netta.",
                  "> Prossimo passo: rifarlo sul livello di validazione, con la soglia congelata."]
        else:
            L += ["> ❌ **Criterio di morte scattato**, scritto prima di guardare: i pool a uscita",
                  "> economica non rendono di più al netto. Non si abbassa la soglia al 6% né la si alza",
                  "> al 12% per salvarla."]
    else:
        L += [f"> ⏸️ Servono almeno 25 eventi e 10 a uscita economica: ne abbiamo {len(ev)} e {len(econ)}.", ""]

    if metro:
        L += ["", f"*{metro.etichetta()}*"]
    open("COSTO_USCITA.md", "w").write("\n".join(L))
    print(f"COSTO_USCITA | eventi:{len(ev)} economici:{len(econ)}", flush=True)


if __name__ == "__main__":
    main()
