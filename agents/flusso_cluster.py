#!/usr/bin/env python3
"""
FLUSSO_CLUSTER — la seconda pista della consulenza, e cambia la domanda che ci facciamo.

Fin qui abbiamo sempre chiesto: *questo wallet e' bravo?* — ed e' una domanda che non ha risposta,
perche' su decine di migliaia di wallet qualcuno indovina sempre. La consulenza esterna propone di
girarla:

    «non "FrancescoWallet42 e' bravo?", ma: sta entrando capitale INDIPENDENTE in questo token?»

La differenza e' tutta nell'indipendenza. Se in cinque minuti vedi trenta wallet diversi comprare,
sembra domanda: ma se venticinque di quei trenta sono la stessa mano che si e' divisa in venticinque
portafogli, non hai trenta compratori — ne hai sei, e uno sta costruendo l'illusione degli altri.
E' il trucco piu' vecchio del mercato, e finora ci saremmo cascati ogni volta.

Il segnale qui e':

    (dollari comprati da ENTITA' distinte - dollari venduti) / liquidita' disponibile

Non "quanti buy meno quanti sell": quello lo puo' fabbricare chiunque con uno script. Il denominatore
conta perche' 5.000 dollari su un pool da 10.000 sono un'onda, su un pool da un milione sono nulla.

Tutte le cautele della consulenza sono qui dentro:
  - segnale calcolato SOLO fino a T, rendimento misurato dopo T
  - confronto contro controlli appaiati per eta' e liquidita' (non "un token a caso")
  - creator e wallet collegati esclusi: l'insider non e' domanda, e' la controparte
  - PLACEBO ALL'INDIETRO: se il "segnale" spiega anche cos'era successo PRIMA, non sta prevedendo —
    sta descrivendo un movimento gia' avvenuto, e ci saremmo comprati il momentum di ieri

CRITERIO DI MORTE, fissato adesso: se il decile alto del flusso non produce extra-rendimento contro
i controlli appaiati su almeno DUE orizzonti in fascia di validazione, oppure se il placebo
all'indietro e' grande quanto il segnale in avanti, la pista si chiude.

Scrive FLUSSO_CLUSTER.md. Sola lettura. €0.
"""
import json, os, time, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "agents")
import multichain_brain as B
import controlli as C

CHAIN = os.environ.get("CHAIN", "base")
MAX_TOKEN = int(os.environ.get("MAX_TOKEN", 700))
FINESTRA = 900             # il flusso si misura sugli ultimi 15 minuti
PASSO = 1800               # si guarda ogni mezz'ora di vita del token
MIN_ETA = 1800             # non prima di mezz'ora: nei primi minuti e' tutto rumore di lancio
DECILE = 0.90              # "flusso alto" = il 10% piu' alto, soglia fissata prima di guardare
PUMP_GIA_FATTO = 0.50      # oltre +50% nelle 2 ore precedenti, il rialzo e' gia' successo senza di noi
now = int(time.time())
try: CONFINE = int(json.load(open("data/holdout_config.json"))["confine_validazione"])
except Exception: CONFINE = 0


def main():
    U = C.Universo(CHAIN, limite=MAX_TOKEN)
    if len(U.cs) < 80:
        print(f"FLUSSO_CLUSTER | {CHAIN}: solo {len(U.cs)} serie", flush=True); return
    ent = C.cluster(CHAIN, addrs=list(U.cs), max_token=MAX_TOKEN)

    # creator e wallet collegati: fuori. Un insider che compra il proprio token non e' domanda.
    esclusi = set()
    p = f"data/sicurezza/{CHAIN}.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                d = json.loads(l)
                for k in ("creator", "owner"):
                    if d.get(k): esclusi.add(d[k].lower())
            except Exception: pass

    punti = []          # (ts, token, flusso)
    for addr, cs in U.cs.items():
        tr = [t for t in B.load_trades(CHAIN, addr) if t.get("ts") and t.get("w")]
        if len(tr) < 20: continue
        tr.sort(key=lambda t: int(t["ts"]))
        nasce = U.nasce[addr]
        fine = U.muore[addr]
        t = nasce + MIN_ETA
        while t < fine - 7200:
            fin, fout, entita = 0.0, 0.0, set()
            for x in tr:
                ts = int(x["ts"])
                if ts >= t: break
                if ts < t - FINESTRA: continue
                w = (x.get("w") or "").lower()
                if w in esclusi: continue
                u = float(x.get("usd") or 0)
                if x.get("kind") == "buy":
                    e = ent.get(x["w"], x["w"])
                    if e not in entita: fin += u; entita.add(e)   # una entita' conta UNA volta
                else: fout += u
            liq = C.volume_prima(cs, t) + 1.0
            if fin > 0 and len(entita) >= 3:
                punti.append((t, addr, (fin - fout) / liq, len(entita)))
            t += PASSO
    if len(punti) < 200:
        print(f"FLUSSO_CLUSTER | {CHAIN}: solo {len(punti)} osservazioni", flush=True)
        open("FLUSSO_CLUSTER.md", "w").write(
            f"# 🌊 FLUSSO DI ENTITÀ INDIPENDENTI ({CHAIN})\n\n*Solo {len(punti)} osservazioni: troppo poche "
            f"per giudicare. Serve più storico dei trade.*\n"); return

    vals = sorted(x[2] for x in punti)
    soglia = vals[int(len(vals) * DECILE)]
    alti = [x for x in punti if x[2] >= soglia]

    res = {f: {h: [] for h in C.ORIZZONTI} for f in ("ricerca", "validazione")}
    pulito = {f: {h: [] for h in C.ORIZZONTI} for f in ("ricerca", "validazione")}
    plac = {h: [] for h in C.ORIZZONTI}
    usati = 0
    vivi_cache = {}
    for ts, addr, v, ne in alti:
        chiave = ts // 3600
        if chiave not in vivi_cache: vivi_cache[chiave] = U.vivi(ts)
        ctrl = [U.cs[c] for c in U.matched(addr, ts, k=5, candidati=vivi_cache[chiave])]
        if not ctrl: continue
        ex = C.excess(U.cs[addr], ctrl, ts)
        if not ex: continue
        f = "validazione" if (CONFINE and ts >= CONFINE) else "ricerca"
        for h, x in ex.items(): res[f][h].append(x)
        pl = C.placebo(U.cs[addr], ts)
        for h, x in pl.items(): plac[h].append(x)
        # VARIANTE PULITA (aggiunta 02/09): lo stesso segnale, ma solo dove il token NON era gia'
        # esploso. Il placebo ha mostrato +432% PRIMA del segnale: il flusso alto arriva a festa
        # cominciata, e quello che sembrava un vantaggio era il ricordo di un rialzo altrui.
        if pl.get(7200, 0) < PUMP_GIA_FATTO:
            for h, x in ex.items(): pulito[f][h].append(x)
        usati += 1

    L = [f"# 🌊 FLUSSO DI ENTITÀ INDIPENDENTI ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(punti)} osservazioni · "
         f"{usati} nel decile alto · {len(set(ent.values()))} entità riconosciute*", "",
         "> **La domanda è cambiata.** Non «questo wallet è bravo?» — che non ha risposta — ma:",
         "> **sta entrando capitale indipendente in questo token?**", "",
         "> Se trenta wallet diversi comprano in cinque minuti sembra domanda. Se venticinque sono la",
         "> stessa mano divisa in venticinque portafogli, hai sei compratori e uno che fabbrica l'illusione",
         "> degli altri. Qui **ogni entità conta una volta sola**, e creator e proprietari sono esclusi.", ""]
    if usati < 40:
        L += [f"*Solo {usati} casi con controlli appaiati disponibili: non basta per un verdetto.*"]
        open("FLUSSO_CLUSTER.md", "w").write("\n".join(L))
        print(f"FLUSSO_CLUSTER | {CHAIN} | solo {usati} casi", flush=True); return

    for f, titolo in (("ricerca", "Fascia di ricerca (già vista)"),
                      ("validazione", "🔒 Fascia di validazione (mai vista — decide lei)")):
        righe = []
        for h in C.ORIZZONTI:
            v = res[f][h]
            if len(v) < 20: continue
            righe.append(f"| {C.ETICHETTE[h]} | **{st.mean(v)*100:+.1f}%** | {st.median(v)*100:+.1f}% | "
                         f"{sum(1 for x in v if x > 0)/len(v)*100:.0f}% | {len(v)} |")
        if not righe:
            L += [f"## {titolo}", "", "*Campione troppo piccolo in questa fascia.*", ""]; continue
        L += [f"## {titolo}", "",
              "| dopo | extra-rendimento medio | mediano | volte sopra i controlli | casi |",
              "|---|---|---|---|---|"] + righe + [""]

    L += ["## Il controllo all'indietro (placebo)", "",
          "*Se il «segnale» spiega anche cos'era successo PRIMA, non sta prevedendo: sta descrivendo un",
          "movimento già avvenuto — e staremmo comprando il momentum di ieri.*", "",
          "| prima del segnale | rendimento |", "|---|---|"]
    for h in C.ORIZZONTI:
        if len(plac[h]) >= 20: L.append(f"| {C.ETICHETTE[h]} | {st.mean(plac[h])*100:+.1f}% |")

    val_pieni = sum(1 for h in C.ORIZZONTI if len(res["validazione"][h]) >= 20)
    pos = [h for h in C.ORIZZONTI if len(res["validazione"][h]) >= 20 and st.mean(res["validazione"][h]) > 0]
    avanti = st.mean(res["validazione"][7200]) if len(res["validazione"][7200]) >= 20 else None
    indietro = st.mean(plac[7200]) if len(plac[7200]) >= 20 else None
    # confronto avanti/indietro sulla fascia che ha dati: e' la diagnosi piu' importante del test,
    # e non puo' aspettare che la validazione si riempia.
    f_dati = "validazione" if val_pieni >= 2 else "ricerca"
    av = st.mean(res[f_dati][7200]) if len(res[f_dati][7200]) >= 20 else None
    ind = st.mean(plac[7200]) if len(plac[7200]) >= 20 else None
    if av is not None and ind is not None and ind > max(0.10, abs(av) * 2):
        L += ["", f"> 🔴 **Il segnale arriva a festa cominciata.** Nelle 2 ore PRIMA il token aveva già",
              f"> fatto **{ind*100:+.0f}%**; nelle 2 ore DOPO fa **{av*100:+.1f}%**. Non stiamo prevedendo",
              "> un rialzo: stiamo riconoscendo un rialzo altrui e arrivando dopo.", "",
              "> È esattamente ciò che il controllo all'indietro serviva a scoprire — e senza di esso",
              "> avremmo scambiato quel numero positivo per un vantaggio.", ""]
        righe = []
        for h in C.ORIZZONTI:
            v_ = pulito[f_dati][h]
            if len(v_) < 20: continue
            righe.append(f"| {C.ETICHETTE[h]} | **{st.mean(v_)*100:+.1f}%** | {st.median(v_)*100:+.1f}% | {len(v_)} |")
        L += ["### Lo stesso segnale, ma solo dove il rialzo NON era già avvenuto", ""]
        L += (["| dopo | extra-rendimento medio | mediano | casi |", "|---|---|---|---|"] + righe + [""]) if righe \
            else ["*Non restano abbastanza casi «puliti» per misurarla: il flusso alto è quasi sempre", "posteriore al rialzo.*", ""]

    L += ["", "## Verdetto", ""]
    if val_pieni < 2:
        ric = [h for h in C.ORIZZONTI if len(res["ricerca"][h]) >= 20 and st.mean(res["ricerca"][h]) > 0]
        L += ["> ⏸️ **Non ancora giudicabile**: la fascia di validazione non ha abbastanza casi, e il",
              "> criterio di morte non scatta su dati insufficienti.",
              f"> In ricerca il flusso alto batte i controlli su {len(ric)} orizzonti su {len(C.ORIZZONTI)},",
              "> ma quella è la fascia su cui il sistema si è già adattato: **non fa fede**."]
    elif avanti is not None and indietro is not None and indietro > abs(avanti):
        L += ["> ❌ **È momentum, non previsione.** Il movimento PRIMA del segnale è più grande di quello",
              "> dopo: stiamo riconoscendo un rialzo già avvenuto e arrivando a cose fatte."]
    elif len(pos) >= 2:
        L += [f"> ✅ **Esiste informazione**: extra-rendimento positivo su {len(pos)} orizzonti in validazione,",
              "> e il placebo all'indietro non lo spiega. Si passa al secondo stadio: sopravvive ai costi veri?"]
    else:
        L += ["> ❌ **Nessuna informazione**: il flusso di entità indipendenti non batte i controlli appaiati",
              "> in fascia mai vista. **Criterio di morte scattato**, e non si riapre cambiando il decile."]
    open("FLUSSO_CLUSTER.md", "w").write("\n".join(L))
    print(f"FLUSSO_CLUSTER | {CHAIN} | {usati} casi | validazione {val_pieni} orizzonti pieni, {len(pos)} positivi",
          flush=True)


if __name__ == "__main__":
    main()
