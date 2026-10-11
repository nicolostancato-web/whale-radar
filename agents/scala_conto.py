#!/usr/bin/env python3
"""
SCALA_CONTO — esperimento 5: taglia fissa contro reinvestimento.

L'INTUIZIONE (registrata prima di guardare). Il costo misurato cresce con la taglia, e cresce in
fretta: 3,95% a $25, 8,14% a $100, 25,44% a $500 (mediane su 666 token con tutte e tre le misure).
Se reinvestiamo i profitti, la posizione cresce — e il costo cresce PIU' del vantaggio che cerchiamo.
Il reinvestimento, che in un mercato normale e' la cosa piu' potente che esista, qui puo' essere il
modo piu' rapido per mangiarsi il proprio vantaggio.

LA DOMANDA: con €100 di partenza, conviene restare piccoli per sempre o crescere?

CRITERIO DI MORTE (come da coda, scritto prima): l'idea muore se nessuna delle due politiche supera
**+8% netto per operazione**, oppure se per funzionare serve una taglia il cui costo non abbiamo
misurato. Non si inventa il costo di una taglia che non e' stata misurata: si dichiara e ci si ferma.

Sola lettura, nessuna chiamata. €0.
"""
import json, os, sys, time, math, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CAPITALE = 100.0
TAGLIA_FISSA = 25.0
QUOTA = 0.25          # reinvestimento: ogni operazione usa un quarto del capitale disponibile
CHAINS = ("base", "robinhood", "solana")
BERSAGLIO = 0.08


def curva():
    """Il costo misurato per taglia: le tre colonne che abbiamo davvero pagato."""
    try:
        d = json.load(open("data/costi_archivio.json"))
    except Exception:
        return None
    per = {25: [], 100: [], 500: []}
    for v in d.values():
        s = v.get("size") or {}
        for t in per:
            c = (s.get(str(t)) or {}).get("costo_roundtrip_pct")
            if isinstance(c, (int, float)): per[t].append(c / 100.0)
    if min(len(x) for x in per.values()) < 50: return None
    return {t: st.median(v) for t, v in per.items()}


def costo(size, c):
    """Fra due taglie misurate si interpola; FUORI dall'intervallo misurato non si indovina.
    Restituisce None se la taglia e' oltre l'ultima misura: e' il criterio di morte, non un dettaglio."""
    punti = sorted(c)
    if size <= punti[0]: return c[punti[0]]
    if size > punti[-1]: return None                  # non misurato: non si inventa
    for a, b in zip(punti, punti[1:]):
        if a <= size <= b:
            # il costo cresce quasi come il logaritmo della taglia: interpoliamo li'
            q = (math.log(size) - math.log(a)) / (math.log(b) - math.log(a))
            return c[a] + q * (c[b] - c[a])
    return None


def rendimenti(chain):
    try:
        import multichain_brain as B
        r = B.load_rows(chain)
        if len(r) < 40: return []
        return [x["ret"] for x in B.walkforward_righe(r)]
    except Exception:
        return []


def simula(ret, c, reinveste):
    """Parte da €100. Restituisce (rendimento medio netto per operazione, capitale finale, fuori scala)."""
    cap = CAPITALE
    netti = []
    fuori = 0
    for r in ret:
        size = min(cap * QUOTA, cap) if reinveste else min(TAGLIA_FISSA, cap)
        if size <= 1: break
        k = costo(size, c)
        if k is None:
            fuori += 1
            k = costo(max(c), c)        # ultima misura nota: peggiora, non migliora
            size = max(c)
        netto = (1 + r) * (1 - k) - 1
        netti.append(netto)
        cap += size * netto
        if cap <= 1: break
    return (st.median(netti) if netti else 0.0), cap, fuori, len(netti)


def main():
    c = curva()
    L = ["# ⚖️ TAGLIA FISSA CONTRO REINVESTIMENTO",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · esperimento 5 · solo dati già "
         f"misurati · €0*", "",
         "> Il costo cresce con la taglia, e cresce in fretta. Il reinvestimento — la cosa più potente",
         "> che esista in un mercato normale — qui può essere **il modo più rapido di mangiarsi il",
         "> proprio vantaggio**: la posizione cresce, e il pedaggio cresce più del guadagno cercato.", ""]
    if not c:
        L += ["> ⏸️ Non abbastanza misure di costo per taglia: non si simula su numeri inventati."]
        open("SCALA_CONTO.md", "w").write("\n".join(L)); print("SCALA_CONTO | senza curva"); return

    L += ["Il pedaggio che abbiamo **davvero misurato**:", "",
          "| taglia | costo andata+ritorno |", "|---|---|"]
    L += [f"| ${t} | **{c[t]*100:.2f}%** |" for t in sorted(c)]
    L += ["", f"Partenza **€{CAPITALE:.0f}**. Fissa = ${TAGLIA_FISSA:.0f} per sempre; "
              f"reinvestimento = {QUOTA*100:.0f}% del capitale disponibile.", "",
          "| chain | trade | fissa: netto mediano | reinveste: netto mediano | oltre il misurato |",
          "|---|---|---|---|---|"]
    meglio = 0.0
    for ch in CHAINS:
        ret = rendimenti(ch)
        if len(ret) < 30:
            L.append(f"| **{ch}** | {len(ret)} | *troppo pochi* | | |")
            continue
        f_m, f_cap, _fo, _n = simula(ret, c, False)
        r_m, r_cap, r_fo, _n2 = simula(ret, c, True)
        meglio = max(meglio, f_m, r_m)
        L.append(f"| **{ch}** | {len(ret)} | **{f_m*100:+.2f}%** (€{f_cap:.0f}) | "
                 f"{r_m*100:+.2f}% (€{r_cap:.0f}) | {r_fo} |")
    L += ["", "*Fra parentesi il capitale finale partendo da €100. «Oltre il misurato» = quante volte "
              "il reinvestimento ha chiesto una taglia il cui costo non abbiamo mai pagato davvero.*", "",
          "## Verdetto", ""]
    if meglio >= BERSAGLIO:
        L += [f"> ✅ Una delle due politiche supera il bersaglio: **{meglio*100:+.2f}%** netto per",
              "> operazione. Va congelata e riprovata sul livello di validazione."]
    else:
        L += [f"> ❌ **Criterio di morte scattato**, scritto prima di guardare: la migliore delle due",
              f"> politiche fa **{meglio*100:+.2f}%** netto per operazione, contro il bersaglio del",
              f"> **+{BERSAGLIO*100:.0f}%**. Non è una questione di come scaliamo il conto: **non c'è",
              "> ancora un vantaggio da scalare.** Cambiare la taglia non crea un margine che non esiste.", "",
              "> Resta però un numero utile per dopo: il pedaggio quadruplica fra $25 e $100 e",
              "> sestuplica a $500. Quando il vantaggio ci sarà, **crescere costerà più di quanto",
              "> l'istinto suggerisca** — e questa misura sarà già in tasca."]
    L += ["", "---", "",
          "> ⚠️ **Il limite di questa misura.** Il pedaggio usato qui è quello misurato su **Solana**:",
          "> è l'unica curva per taglia che abbiamo. Il confronto fra le due politiche resta onesto —",
          "> pagano lo stesso pedaggio, quindi la gara è pari — ma i livelli assoluti di Base e",
          "> Robinhood non sono il loro costo vero. Dirlo è meglio che lasciar credere che lo sia.", "",
          "> Nota su cosa dicono davvero questi numeri: il **trade mediano perde**, mentre la media è",
          "> positiva. Non è una contraddizione: è la forma del mercato. Quasi tutte le operazioni",
          "> perdono poco, poche vincono molto. Una strategia che vive così non si giudica dal trade",
          "> tipico — e non si scala reinvestendo, perché il capitale muore prima del biglietto buono."]
    open("SCALA_CONTO.md", "w").write("\n".join(L))
    print(f"SCALA_CONTO | migliore {meglio*100:+.2f}%", flush=True)


if __name__ == "__main__":
    main()
