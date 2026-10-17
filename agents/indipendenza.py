#!/usr/bin/env python3
"""
INDIPENDENZA — quante PROVE abbiamo davvero, non quante righe.

Dalla revisione esterna del 04/09, ed e' il punto piu' profondo ricevuto finora:

    «Cento trade legati allo stesso evento non sono cento prove indipendenti.»

Abbiamo sempre contato le righe. Ma se dieci token nascono lo stesso pomeriggio dallo stesso
creator e salgono insieme perche' sale tutto il mercato, quelle non sono dieci conferme: e' UNA
conferma osservata dieci volte. Contarle dieci volte non ci rende piu' sicuri — ci rende piu'
sicuri di sbagliare, perche' l'errore statistico si calcola dividendo per la radice del numero
di prove, e noi stiamo dividendo per un numero gonfiato.

Concretamente: 250 righe raggruppate in 12 giornate valgono, per la statistica, molto piu' vicino
a 12 che a 250. E un "t = 2,5" calcolato su 250 diventa un "t = 0,5" calcolato su 12 — cioe' la
differenza fra "abbiamo trovato qualcosa" e "non abbiamo trovato niente".

Qui si calcola:
  - il NUMERO EFFETTIVO di prove, raggruppando per giornata / creator / lancio
  - il t-stat CORRETTO, con l'errore standard calcolato sui gruppi e non sulle righe
  - quanto ci stavamo illudendo: il rapporto fra i due

E' una libreria: la usano i verbali che devono dichiarare un risultato.
"""
import math, statistics as st
from collections import defaultdict


def per_gruppo(valori, chiavi):
    """{chiave: media del gruppo} — ogni gruppo conta UNA volta, qualunque sia la sua numerosita'."""
    g = defaultdict(list)
    for v, k in zip(valori, chiavi):
        g[k].append(v)
    return {k: st.mean(v) for k, v in g.items()}


def t_onesto(valori, chiavi=None):
    """(t, prove_effettive, t_ingenuo). Se `chiavi` manca, i due t coincidono e si vede la differenza
    solo quando i dati sono davvero raggruppati — che e' esattamente quando conta."""
    if len(valori) < 3: return 0.0, len(valori), 0.0
    m = st.mean(valori)
    sd = st.pstdev(valori) or 1e-9
    t_ing = m / (sd / math.sqrt(len(valori)))
    if not chiavi: return t_ing, len(valori), t_ing
    g = per_gruppo(valori, chiavi)
    medie = list(g.values())
    if len(medie) < 3: return 0.0, len(medie), t_ing
    mg = st.mean(medie); sdg = st.pstdev(medie) or 1e-9
    return mg / (sdg / math.sqrt(len(medie))), len(medie), t_ing


def giornata(ts):
    """la chiave di raggruppamento piu' importante: cio' che succede lo stesso giorno si muove insieme."""
    return int(ts) // 86400


def riga_verdetto(valori, chiavi, soglia_t=2.0):
    """la riga da mettere nei verbali: dice quante prove abbiamo DAVVERO e se bastano."""
    t, n_eff, t_ing = t_onesto(valori, chiavi)
    gonfiaggio = (t_ing / t) if t else float("inf")
    esito = "✅ regge" if abs(t) >= soglia_t else "❌ non regge"
    return (f"{len(valori)} righe → **{n_eff} prove indipendenti** · t onesto **{t:+.2f}** "
            f"(contando le righe sarebbe {t_ing:+.2f}, cioè {gonfiaggio:.1f} volte più generoso) · {esito}")


if __name__ == "__main__":
    # dimostrazione: 200 righe che sono in realta' 8 giornate
    import random
    r = random.Random(1)
    val, ch = [], []
    for g in range(8):
        base = r.gauss(0.03, 0.10)              # l'effetto vero e' della GIORNATA
        for _ in range(25):
            val.append(base + r.gauss(0, 0.02)); ch.append(g)
    print(riga_verdetto(val, ch))
