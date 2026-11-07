#!/usr/bin/env python3
"""
LOOP SPERIMENTALE — dove si provano le idee FUORI dal recinto.

Nasce il 06/09 da un'osservazione di Nicolo' che vale piu' di qualsiasi ottimizzazione:

    «Vi ho dato un recinto — loop 0, loop 1 — ma il castello perfetto potrebbe costruirsi fuori.
     Il goal non e' far funzionare il loop 1: e' trovare qualcosa che fa soldi.»

Aveva ragione, e il recinto l'avevo costruito io. LOOP 1 poggia su un assunto mai messo in
discussione: che la risposta stia in un database di prezzi e trade che accumuliamo noi, filtrato
meglio. Nessuno ha mai chiesto se fosse la strada giusta o solo la prima che ci era venuta in mente.

Qui si prova quello che LOOP 1 non puo' vedere, con le stesse regole di rigore ma senza il vincolo
di partire dal nostro filtraggio. Ogni esperimento nasce con:
  - un'intuizione ECONOMICA (perche' dovrebbe funzionare, non che correla)
  - un criterio di morte scritto PRIMA di guardare i numeri
  - e muore in fretta se non regge: qui si brucia, non si coltiva

ESPERIMENTO 1 — IL GEMELLO SULL'ALTRA CHAIN
Intuizione: un nome che esplode su una chain crea attenzione che non si ferma al confine. Chi arriva
tardi cerca lo stesso nome dove puo' comprarlo, e sull'altra chain esiste gia' un gemello con lo
stesso nome. Non e' una correlazione statistica: e' un travaso di attenzione fra due mercati
separati, e il secondo mercato non sa ancora cosa e' successo nel primo.
Perche' e' fuori dal recinto: LOOP 1 guarda ogni chain per conto suo. Questo segnale, per
costruzione, e' invisibile a tutti e tre i suoi esploratori.
2.548 nomi vivono su piu' di una chain: il materiale c'e'.

Scrive SPERIMENTALE.md. Sola lettura. €0.
"""
import json, os, glob, time, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "agents")
import multichain_brain as B
import controlli as C

CHAINS = ("base", "solana", "robinhood")
ESPLOSIONE = 2.0        # "e' esploso" = ha raddoppiato in un'ora
INDIETRO = 3          # quante candele indietro per dire "e' esploso"
now = int(time.time())


def nomi_per_chain():
    """{nome: {chain: pool}} — chi vive su piu' mercati con lo stesso nome."""
    out = defaultdict(dict)
    for ch in CHAINS:
        f = f"data/multichain/{ch}/pools.json"
        if not os.path.exists(f): continue
        try: pools = json.load(open(f))
        except Exception: continue
        for a, v in pools.items():
            n = (v.get("name") or "").split("/")[0].strip().upper()
            if len(n) >= 3 and ch not in out[n]: out[n][ch] = a
    return {n: c for n, c in out.items() if len(c) >= 2}


def main():
    gemelli = nomi_per_chain()
    serie = {}
    for ch in CHAINS:
        serie[ch] = C.serie(ch, limite=2500)

    eventi = []      # (quando, nome, chain esplosa, chain gemella, pool gemello)
    for nome, dove in gemelli.items():
        presenti = {ch: p for ch, p in dove.items() if p in serie.get(ch, {})}
        if len(presenti) < 2: continue
        for ch, p in presenti.items():
            cs = serie[ch][p]
            # "esploso" = ha raddoppiato rispetto a POCHE CANDELE FA, non "nell'ultima ora".
            # Prima confrontavo dentro una finestra di 3600 secondi: con candele orarie quella
            # finestra contiene UNA candela, quindi non c'era mai niente con cui confrontare e non
            # rilevava nulla. Zero eventi non significava "il fenomeno non esiste": significava che
            # non stavo guardando. Contare le candele invece dei secondi funziona a qualunque passo.
            for i in range(INDIETRO, len(cs)):
                fin = cs[i][0]
                base_p = cs[i - INDIETRO][4]
                if not base_p or not cs[i][4]: continue
                if cs[i][4] / base_p >= ESPLOSIONE:
                    for ch2, p2 in presenti.items():
                        if ch2 != ch: eventi.append((fin, nome, ch, ch2, p2))
                    break        # una sola esplosione per token: non la stessa contata dieci volte

    L = [f"# 🧪 LOOP SPERIMENTALE — fuori dal recinto",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · €0*", "",
         "> Nasce da un'osservazione che vale più di qualsiasi ottimizzazione: **il recinto — LOOP 0,",
         "> LOOP 1 — l'ho costruito io**, e tutto ciò che c'è dentro poggia su un assunto mai messo in",
         "> discussione: che la risposta stia nel nostro database, filtrato meglio.", "",
         "> Qui si prova quello che LOOP 1 **non può vedere**. Stesse regole di rigore, nessun vincolo",
         "> di partire dal nostro filtraggio. Si brucia in fretta, non si coltiva.", "",
         "## Esperimento 1 — il gemello sull'altra chain", "",
         "**L'intuizione, e non è statistica:** un nome che esplode su una chain crea attenzione che non",
         "si ferma al confine. Chi arriva tardi cerca lo stesso nome dove può comprarlo — e sull'altra",
         "chain esiste già un gemello con lo stesso nome, in un mercato che **non sa ancora** cosa è",
         "successo nel primo.", "",
         "**Perché è fuori dal recinto:** LOOP 1 guarda ogni chain per conto suo. Questo segnale è",
         "invisibile a tutti e tre i suoi esploratori, per costruzione.", "",
         f"**Materiale:** {len(gemelli)} nomi vivono su più di una chain.", ""]

    if len(eventi) < 30:
        L += [f"### ⏸️ Solo {len(eventi)} esplosioni con un gemello osservabile", "",
              "Non bastano per un verdetto. L'esperimento resta aperto: si rifà quando i dati crescono."]
        open("SPERIMENTALE.md", "w").write("\n".join(L))
        print(f"SPERIMENTALE | gemelli {len(gemelli)} | eventi {len(eventi)}: troppo pochi", flush=True); return

    res = {h: [] for h in C.ORIZZONTI}
    U = {ch: C.Universo.__new__(C.Universo) for ch in CHAINS}
    for ch in CHAINS:
        U[ch].cs = serie[ch]
        U[ch].nasce = {a: c[0][0] for a, c in serie[ch].items()}
        U[ch].muore = {a: c[-1][0] for a, c in serie[ch].items()}
        U[ch].ordine = sorted(serie[ch], key=lambda a: U[ch].nasce[a])
    usati = 0
    for ts, nome, ch, ch2, p2 in eventi:
        cs2 = serie[ch2].get(p2)
        if not cs2: continue
        ctrl = [serie[ch2][c] for c in U[ch2].matched(p2, ts, k=5)]
        if not ctrl: continue
        ex = C.excess(cs2, ctrl, ts)
        if not ex: continue
        for h, v in ex.items(): res[h].append(v)
        usati += 1

    if usati < 30:
        L += [f"### ⏸️ Solo {usati} casi con controlli appaiati disponibili", "",
              "Il gemello esiste ma non abbiamo abbastanza confronti onesti. Si rifà più avanti."]
    else:
        L += [f"### Cosa fa il gemello quando l'altro esplode  ({usati} casi)", "",
              "| dopo | extra-rendimento | mediano | quante volte sopra i controlli |",
              "|---|---|---|---|"]
        for h in C.ORIZZONTI:
            v = res[h]
            if len(v) < 20: continue
            L.append(f"| {C.ETICHETTE[h]} | **{st.mean(v)*100:+.1f}%** | {st.median(v)*100:+.1f}% | "
                     f"{sum(1 for x in v if x > 0)/len(v)*100:.0f}% |")
        pos = [h for h in C.ORIZZONTI if len(res[h]) >= 20
               and st.mean(res[h]) > 0 and st.median(res[h]) > 0]
        L += ["", "### Verdetto", ""]
        if len(pos) >= 2:
            L += [f"> ✅ **Il travaso esiste**: positivo su {len(pos)} orizzonti, media **e** mediana.",
                  "> Prossimo passo: verificarlo sulla fascia mai vista e misurarne il ritardo utile."]
        else:
            L += ["> ❌ **Nessun travaso misurabile.** Il gemello non si muove più dei suoi simili quando",
                  "> l'altro esplode. **Criterio di morte scattato**, scritto prima di guardare: non si",
                  "> allarga la finestra né si cambia la soglia per farlo sopravvivere."]
    open("SPERIMENTALE.md", "w").write("\n".join(L))
    print(f"SPERIMENTALE | gemelli {len(gemelli)} | esplosioni {len(eventi)} | valutate {usati}", flush=True)


if __name__ == "__main__":
    main()
