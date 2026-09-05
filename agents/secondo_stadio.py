#!/usr/bin/env python3
"""
SECONDO_STADIO — fra i token che sopravvivono, quale si compra?

E' il buco piu' grande del progetto, e lo dice la consulenza esterna senza girarci intorno:

    «Il creator gate ci dice soprattutto quali token EVITARE. Non dimostra che quelli che superano
     il filtro facciano guadagnare. Serve un secondo segnale indipendente che scelga cosa comprare
     fra i token sopravvissuti.»

Un filtro anti-truffa perfetto porta il rendimento da -40% a -10%. E' un enorme miglioramento e
non e' un guadagno: senza un secondo stadio, LOOP 1 non puo' aumentare la percentuale, puo' solo
smettere di perderla. Qui si prova a costruire quel secondo stadio.

DUE STADI, in quest'ordine:
  STADIO 1 (cancello)  il token e' vendibile, non e' una trappola, il creator non e' marchiato
  STADIO 2 (segnale)   fra i sopravvissuti, c'e' qualcosa che anticipa chi sale?

I QUATTRO CANDIDATI, scelti perche' hanno una ragione economica, non perche' correlano:
  1. ACCELERAZIONE — il volume degli ultimi minuti contro l'ora precedente. Domanda che ARRIVA,
     non domanda gia' arrivata (che e' il momentum che ci ha gia' fregato una volta).
  2. AMPIEZZA — quante ENTITA' distinte comprano, non quanti dollari. Dieci mani diverse valgono
     piu' di una mano che compra dieci volte: quella e' una persona che si sta parlando addosso.
  3. SQUILIBRIO — dollari comprati meno venduti, rapportati alla liquidita'. Non il numero di
     scambi: quello lo fabbrica chiunque con uno script.
  4. FACCE NUOVE — quanti compratori non avevano mai toccato quel token. Il contrario dello
     sciame: gente che arriva, non gente che rigira.

MOLTI TEST INSIEME, e va dichiarato: 4 segnali x 5 orizzonti = 20 prove. Con venti prove qualcosa
sembra buono per forza. Per questo un candidato passa solo se e' positivo su ALMENO DUE orizzonti,
in fascia di validazione, E il placebo all'indietro non lo spiega. Tre condizioni insieme, non una.

CRITERIO DI MORTE, scritto adesso: se nessuno dei quattro supera quelle tre condizioni, con questi
dati un secondo stadio non esiste — e il cancello da solo non e' una strategia. Non si aggiungono
altri candidati per tentativi: si dice che non c'e'.

Scrive SECONDO_STADIO.md. Sola lettura. €0.
"""
import json, os, time, sys, statistics as st
sys.path.insert(0, "agents")
import multichain_brain as B
import controlli as C

CHAIN = os.environ.get("CHAIN", "base")
MAX_TOKEN = int(os.environ.get("MAX_TOKEN", 700))
FINESTRA = 900          # "ultimi minuti" = 15
PASSO = 1800            # si guarda ogni mezz'ora di vita
MIN_ETA = 1800
DECILE = 0.90           # "alto" = il 10% piu' alto, fissato prima
now = int(time.time())
try: CONFINE = int(json.load(open("data/holdout_config.json"))["confine_validazione"])
except Exception: CONFINE = 0


def cancello(chain):
    """STADIO 1: chi NON si tocca. Trappole dichiarate + creator marchiati."""
    fuori = set()
    try:
        fuori |= {p.lower() for p in json.load(open("data/trappole.json")).get("pool", {})}
    except Exception: pass
    marchiati = set()
    p = f"data/sicurezza/{chain}.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                d = json.loads(l)
                if str(d.get("creator_gia_honeypot") or "") == "1" and d.get("token"):
                    marchiati.add(d["token"].lower())
            except Exception: pass
    try:
        tm = json.load(open(f"data/multichain/{chain}/token_map.json"))
        fuori |= {pa.lower() for pa, tk in tm.items() if (tk or "").lower() in marchiati}
    except Exception: pass
    return fuori


def segnali(tr, t, cs, ent, storici):
    """i quattro candidati, calcolati SOLO con quello che si sapeva prima di t."""
    fin = fout = 0.0
    entita = set(); nuove = 0
    for x in tr:
        ts = int(x["ts"])
        if ts >= t: break
        if ts < t - FINESTRA: continue
        w = x.get("w")
        u = float(x.get("usd") or 0)
        if x.get("kind") == "buy":
            fin += u
            e = ent.get(w, w)
            if e not in entita:
                entita.add(e)
                if w not in storici: nuove += 1
        else: fout += u
    vol_prima = C.volume_prima(cs, t - FINESTRA, 3600) + 1.0
    vol_ora = C.volume_prima(cs, t, FINESTRA) + 1.0
    liq = C.volume_prima(cs, t, 3600) + 1.0
    return {
        "accelerazione": (vol_ora / FINESTRA) / max(1e-9, vol_prima / 3600.0),
        "ampiezza": float(len(entita)),
        "squilibrio": (fin - fout) / liq,
        "facce_nuove": float(nuove),
    }


def main():
    U = C.Universo(CHAIN, limite=MAX_TOKEN)
    if len(U.cs) < 80:
        print(f"SECONDO_STADIO | {CHAIN}: solo {len(U.cs)} serie", flush=True); return
    fuori = cancello(CHAIN)
    dentro = [a for a in U.cs if a.lower() not in fuori]
    ent = C.cluster(CHAIN, addrs=dentro, max_token=MAX_TOKEN)

    NOMI = ["accelerazione", "ampiezza", "squilibrio", "facce_nuove"]
    punti = {k: [] for k in NOMI}
    for addr in dentro:
        cs = U.cs[addr]
        tr = sorted((x for x in B.load_trades(CHAIN, addr) if x.get("ts") and x.get("w")),
                    key=lambda x: int(x["ts"]))
        if len(tr) < 20: continue
        storici = set()
        t = U.nasce[addr] + MIN_ETA
        while t < U.muore[addr] - 7200:
            s = segnali(tr, t, cs, ent, storici)
            for k in NOMI: punti[k].append((t, addr, s[k]))
            for x in tr:
                if int(x["ts"]) < t and x.get("w"): storici.add(x["w"])
            t += PASSO

    L = [f"# 🎯 IL SECONDO STADIO — fra i sopravvissuti, cosa si compra? ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(dentro)} token passano il "
         f"cancello su {len(U.cs)} · {len(fuori)} scartati*", "",
         "> Un filtro anti-truffa perfetto porta il rendimento da −40% a −10%. È un enorme",
         "> miglioramento e **non è un guadagno**: senza un secondo stadio LOOP 1 può solo smettere",
         "> di perdere, non iniziare a guadagnare.", "",
         "> **Quattro candidati, venti prove in tutto.** Con venti prove qualcosa sembra buono per",
         "> forza: per questo un candidato passa solo se è positivo su **almeno due orizzonti**, in",
         "> **fascia di validazione**, **e** il placebo all'indietro non lo spiega. Tre condizioni insieme.", ""]

    if not any(len(v) >= 200 for v in punti.values()):
        L += [f"*Osservazioni insufficienti ({max((len(v) for v in punti.values()), default=0)}): "
              f"serve più storico dei trade.*"]
        open("SECONDO_STADIO.md", "w").write("\n".join(L))
        print(f"SECONDO_STADIO | {CHAIN}: osservazioni insufficienti", flush=True); return

    vivi_cache = {}
    esiti = {}
    for k in NOMI:
        v = punti[k]
        if len(v) < 200: continue
        soglia = sorted(x[2] for x in v)[int(len(v) * DECILE)]
        alti = [x for x in v if x[2] >= soglia]
        res = {"ricerca": {h: [] for h in C.ORIZZONTI}, "validazione": {h: [] for h in C.ORIZZONTI}}
        plac = {h: [] for h in C.ORIZZONTI}
        for ts, addr, _ in alti:
            key = ts // 3600
            if key not in vivi_cache: vivi_cache[key] = U.vivi(ts)
            ctrl = [U.cs[c] for c in U.matched(addr, ts, k=5, candidati=vivi_cache[key])]
            if not ctrl: continue
            ex = C.excess(U.cs[addr], ctrl, ts)
            if not ex: continue
            f = "validazione" if (CONFINE and ts >= CONFINE) else "ricerca"
            for h, x in ex.items(): res[f][h].append(x)
            for h, x in C.placebo(U.cs[addr], ts).items(): plac[h].append(x)
        esiti[k] = (res, plac, len(alti))

    ETICHETTE = {"accelerazione": "il volume sta ACCELERANDO",
                 "ampiezza": "comprano MOLTE MANI diverse",
                 "squilibrio": "si compra molto più di quanto si venda",
                 "facce_nuove": "arrivano compratori MAI VISTI su quel token"}
    passati = []
    for k, (res, plac, n) in esiti.items():
        L += [f"## {ETICHETTE[k]}", ""]
        f_dati = "validazione" if sum(1 for h in C.ORIZZONTI if len(res["validazione"][h]) >= 20) >= 2 else "ricerca"
        righe = []
        for h in C.ORIZZONTI:
            v = res[f_dati][h]
            if len(v) < 20: continue
            righe.append(f"| {C.ETICHETTE[h]} | **{st.mean(v)*100:+.1f}%** | {st.median(v)*100:+.1f}% | {len(v)} |")
        if not righe:
            L += ["*campione troppo piccolo*", ""]; continue
        L += [f"*fascia: {'🔒 validazione (mai vista)' if f_dati=='validazione' else 'ricerca (già vista, non fa fede)'}*", "",
              "| dopo | extra-rendimento medio | **mediano** | casi |", "|---|---|---|---|"] + righe + \
             ["", "> Su queste distribuzioni **conta la mediana**: la media la muove un token solo.", ""]
        # MEDIA **E** MEDIANA (corretto al primo giro, 04/09). I primi due candidati mostravano
        # +70% di media con mediana +0,0%: pochi mostri tiravano su tutto mentre il caso tipico non
        # guadagnava niente. Promuovere su quella media significherebbe costruire una strategia che
        # funziona solo se becchi il mostro — cioe' una lotteria con un nome tecnico.
        # E' lo stesso errore che avevo gia' visto su BSC (media +4911%, mediana -41%) e che il mio
        # criterio non aveva imparato a evitare.
        pos = [h for h in C.ORIZZONTI if len(res[f_dati][h]) >= 20
               and st.mean(res[f_dati][h]) > 0 and st.median(res[f_dati][h]) > 0]
        av = st.mean(res[f_dati][7200]) if len(res[f_dati][7200]) >= 20 else None
        ind = st.mean(plac[7200]) if len(plac[7200]) >= 20 else None
        momentum = av is not None and ind is not None and ind > max(0.10, abs(av) * 2)
        if momentum:
            L += ["", f"> ❌ **È momentum**: prima del segnale il token aveva già fatto {ind*100:+.0f}%, "
                      f"dopo fa {av*100:+.1f}%. Riconosce un rialzo altrui, non lo prevede.", ""]
        elif len(pos) >= 2 and f_dati == "validazione":
            L += ["", f"> ✅ **Passa**: positivo su {len(pos)} orizzonti in fascia mai vista, e il placebo "
                      "non lo spiega.", ""]
            passati.append(k)
        elif len(pos) >= 2:
            L += ["", f"> ⏸️ Positivo (media **e** mediana) su {len(pos)} orizzonti, ma **in fascia di "
                      "ricerca**: non fa fede. Da rivedere quando la validazione avrà abbastanza casi.", ""]
        else:
            medie_ok = [h for h in C.ORIZZONTI if len(res[f_dati][h]) >= 20 and st.mean(res[f_dati][h]) > 0]
            if len(medie_ok) >= 2:
                L += ["", "> ❌ **Media positiva ma mediana no**: guadagnano pochi token estremi, il caso",
                      "> tipico non guadagna niente. È una lotteria, non un segnale.", ""]
            else:
                L += ["", "> ❌ Non batte i controlli appaiati.", ""]

    L += ["## Verdetto", ""]
    if passati:
        L += [f"> ✅ **Un secondo stadio esiste**: {', '.join(ETICHETTE[k] for k in passati)}.",
              "> Prossimo passo: unirlo al cancello e misurare la coppia, non i due pezzi separati."]
    else:
        L += ["> ⏸️ **Nessun candidato ha ancora passato le tre condizioni insieme.**", "",
              "> Il criterio di morte scatta solo quando la fascia di validazione ha abbastanza casi:",
              "> bocciare per mancanza di dati sarebbe lo stesso errore, rovesciato, di promuovere per",
              "> numeri belli in ricerca."]
    open("SECONDO_STADIO.md", "w").write("\n".join(L))
    print(f"SECONDO_STADIO | {CHAIN} | {len(dentro)} token dentro, {len(fuori)} fuori | "
          f"candidati passati: {len(passati)}", flush=True)


if __name__ == "__main__":
    main()
