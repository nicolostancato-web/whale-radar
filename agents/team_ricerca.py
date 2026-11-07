#!/usr/bin/env python3
"""
TEAM · RICERCA — il ruolo che INVENTA segnali nuovi, da solo.

Finora il loop provava combinazioni dei 10 segnali che gli avevamo dato: poteva cercare meglio, non cercare
ALTRO. L'insider su Solana l'ha inventato un umano. Questo ruolo esiste perche' non succeda piu': costruisce
da se' segnali nuovi dai dati grezzi (chi compra, quando, quanto, quante volte), li mette alla prova uno per
uno col walk-forward onesto, e PROMUOVE solo quelli che alzano la percentuale ROBUSTA.

Come "inventa": ha dei mattoni elementari (concentrazione, ricorrenza dei wallet, velocita', dimensione dei
buy, quota dei wallet mai visti prima...) e li calcola sui dati che gia' abbiamo. Non serve un LLM e non
costa nulla: serve dare al sistema abbastanza mattoni e lasciarlo misurare. E' cosi' che si sarebbe scoperto
l'insider da solo: "la quota di soldi che arriva da wallet gia' visti nei token vincenti" e' uno dei mattoni.

Scrive RICERCA.md + data/feature_scoperte.json (le promosse, pronte per il cervello). €0.
"""
import json, os, gzip, time, sys, statistics as st
sys.path.insert(0, "agents")
import multichain_brain as B, learner as L, explorer as E
import conoscenza as K


def _quando_provato(chiave):
    """da quanto tempo non proviamo questa idea (serve a ripescare le più vecchie quando tutto è bloccato)."""
    try:
        return K._carica()["voci"].get(chiave, {}).get("ts", 0)
    except Exception:
        return 0

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 240))
GUADAGNO_MINIMO = 3.0
now = int(time.time()); t0 = time.time()
STATO = f"data/ricerca_{CHAIN}.json"


# ---------------------------------------------------------------- I MATTONI (segnali candidati)
def candidati(trades, pre, entry_ts, storia_wallet):
    """calcola tutti i segnali candidati per UN token. Ognuno e' un'ipotesi su cosa distingue i vincenti."""
    tr = [t for t in trades if t["ts"] <= entry_ts]
    buy = [t for t in tr if t["kind"] == "buy"]
    tot_usd = sum(t["usd"] for t in buy) or 1.0
    per_wallet = {}
    for t in buy: per_wallet[t["w"]] = per_wallet.get(t["w"], 0) + t["usd"]
    quote = sorted(per_wallet.values(), reverse=True)
    durata = (tr[-1]["ts"] - tr[0]["ts"]) / 60 if len(tr) > 1 else 1.0

    # quanto del denaro arriva da wallet gia' visti in ALTRI token andati bene (questo mattone e' l'insider)
    usd_reduci = sum(u for w, u in per_wallet.items() if storia_wallet.get(w, 0) >= 2)
    usd_vincenti = sum(u for w, u in per_wallet.items() if storia_wallet.get(w, 0) >= 1)
    mai_visti = sum(u for w, u in per_wallet.items() if w not in storia_wallet)

    c = {
        "concentrazione_top5": sum(quote[:5]) / tot_usd,
        "concentrazione_top1": (quote[0] / tot_usd) if quote else 0.0,
        "n_compratori": len(per_wallet),
        "buy_medio": tot_usd / max(1, len(buy)),
        "buy_grossi": sum(t["usd"] for t in buy if t["usd"] >= 500) / tot_usd,
        "trade_al_minuto": len(tr) / max(1.0, durata),
        "quota_wallet_reduci": usd_reduci / tot_usd,          # <- l'insider, generato dal mattone
        "quota_wallet_vincenti": usd_vincenti / tot_usd,
        "quota_wallet_nuovi": mai_visti / tot_usd,
        "eta_al_primo_trade": (tr[0]["ts"] - pre[0][0]) / 60 if tr else 999.0,
    }
    # mattoni sui wallet e sul tempo (aggiunti perche' con soli 13 candidati il ricercatore esauriva le idee)
    primi = sorted(buy, key=lambda t: t["ts"])[:20]
    c["usd_primi20"] = sum(t["usd"] for t in primi) / tot_usd
    c["wallet_ripetuti"] = sum(1 for u in per_wallet.values() if u > 0 and len([1 for t in buy if t["usd"] == u]) > 1) / max(1, len(per_wallet))
    c["compra_e_rivende"] = len({t["w"] for t in tr if t["kind"] == "sell"} & set(per_wallet)) / max(1, len(per_wallet))
    c["sbilanciamento"] = (sum(t["usd"] for t in tr if t["kind"] == "buy") -
                           sum(t["usd"] for t in tr if t["kind"] == "sell")) / (tot_usd + 1)
    meta_t = tr[len(tr) // 2]["ts"] if tr else entry_ts
    c["accelerazione_denaro"] = (sum(t["usd"] for t in buy if t["ts"] >= meta_t) /
                                 (sum(t["usd"] for t in buy if t["ts"] < meta_t) + 1))
    # mattoni dalle candele
    chiusure = [x[4] for x in pre if x[4]]
    vol = [(x[5] or 0) for x in pre]
    if len(chiusure) > 2:
        c["ampiezza"] = (max(chiusure) - min(chiusure)) / (st.mean(chiusure) + 1e-12)
        c["drawdown_pre"] = (max(chiusure) - chiusure[-1]) / (max(chiusure) + 1e-12)
        c["volume_ultima_su_media"] = vol[-1] / (st.mean(vol[:-1]) + 1)
    else:
        c["ampiezza"] = c["drawdown_pre"] = 0.0; c["volume_ultima_su_media"] = 1.0
    return c


SPIEGA = {
    "concentrazione_top5": "quanto del denaro iniziale arriva dai 5 compratori più grossi",
    "concentrazione_top1": "quanto pesa il singolo compratore più grosso",
    "n_compratori": "quante persone diverse hanno comprato",
    "buy_medio": "quanto compra in media ciascuno",
    "buy_grossi": "la quota di denaro che arriva da acquisti sopra i 500 dollari",
    "trade_al_minuto": "quanto è frenetico lo scambio",
    "quota_wallet_reduci": "la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider)",
    "quota_wallet_vincenti": "la quota di denaro da wallet con almeno un successo alle spalle",
    "quota_wallet_nuovi": "la quota di denaro da wallet mai visti prima",
    "eta_al_primo_trade": "quanto tempo passa dalla nascita al primo scambio",
    "usd_primi20": "quanto pesano i primissimi 20 acquisti sul totale",
    "wallet_ripetuti": "quanti wallet comprano più di una volta",
    "compra_e_rivende": "quanti di quelli che hanno comprato stanno già rivendendo",
    "sbilanciamento": "quanto il denaro che entra supera quello che esce",
    "accelerazione_denaro": "se i soldi stanno entrando più in fretta adesso che all'inizio",
    "ampiezza": "quanto oscilla il prezzo prima di entrare",
    "drawdown_pre": "quanto è già sceso dal massimo prima di entrare",
    "volume_ultima_su_media": "se il volume sta accelerando proprio adesso",
}


def main():
    serie = E.candele_chain(CHAIN)
    if len(serie) < 80:
        print(f"RICERCA | {CHAIN}: solo {len(serie)} serie, si accumula", flush=True); return

    st_prec = json.load(open(STATO)) if os.path.exists(STATO) else {}
    cfg = st_prec.get("cfg") or {"entry_h": B.ENTRY_H, "tp1": 3, "tp2": 6, "trail": 0.5, "hard": 0.7}
    ex = json.load(open(f"data/explorer_{CHAIN}.json")) if os.path.exists(f"data/explorer_{CHAIN}.json") else {}
    if ex.get("best"): cfg = {k: ex["best"][k] for k in ("entry_h", "tp1", "tp2", "trail", "hard")}
    thr = (ex.get("best") or {}).get("thr", B.THR)

    base_rows = E.costruisci(serie, cfg["entry_h"], cfg["tp1"], cfg["tp2"], cfg["trail"], cfg["hard"])
    if len(base_rows) < 60:
        print(f"RICERCA | {CHAIN}: pochi token utilizzabili", flush=True); return

    # storia dei wallet — LEAK CHIUSO (31/08): prima un wallet veniva marcato "vincente" appena il suo token
    # nasceva, ma il pump di quel token poteva avvenire DOPO l'entrata del token successivo. I memecoin si
    # sovrappongono nel tempo: cosi' il segnale "insider" conosceva il futuro. Ora un esito entra nella storia
    # solo quando e' RISOLTO (xt), e la storia viene consumata in ordine di ENTRATA.
    ordinati = sorted(serie, key=lambda s: (s[2] or s[1][0][0]))
    storia = {}
    esiti = {}; risolti = []
    for addr, cs, nato in ordinati:
        path = [c[4] for c in cs if c[4]]
        if len(path) > 3 and path[0]:
            esiti[addr] = (max(path) / path[0]) >= 2
            risolti.append((cs[-1][0], addr, {t["w"] for t in B.load_trades(CHAIN, addr) if t["kind"] == "buy"}))
    risolti.sort()

    # calcola i candidati per ogni token, aggiornando la storia wallet SOLO col passato
    dati = []
    for addr, cs, nato in ordinati:
        if time.time() - t0 > BUDGET * 0.6: break
        t0c = nato or cs[0][0]
        ei = None
        for i, c in enumerate(cs):
            if c[0] >= t0c + cfg["entry_h"] * 3600: ei = i; break
        if ei is None or ei == 0: continue
        # assorbi nella storia SOLO i token gia' chiusi prima di questa entrata (niente futuro)
        while risolti and risolti[0][0] < cs[ei][0]:
            _, a_ris, compratori = risolti.pop(0)
            if esiti.get(a_ris):
                for w in compratori: storia[w] = storia.get(w, 0) + 1
        tr = B.load_trades(CHAIN, addr)
        c = candidati(tr, cs[:ei + 1], cs[ei][0], storia)
        dati.append((addr, cs[ei][0], c))

    # righe = feature base + segnali candidati, allineate per timestamp d'entrata
    per_ent = {}
    for r in base_rows: per_ent.setdefault(r["ent"], []).append(r)
    righe = []
    for addr, ts, c in dati:
        lst = per_ent.get(ts)
        if not lst: continue
        r = lst.pop()
        righe.append({"ent": r["ent"], "xt": r["xt"], "ret": r["ret"], "f": r["f"], "c": c})
    if len(righe) < 60:
        print(f"RICERCA | {CHAIN}: {len(righe)} righe allineate, troppo poche", flush=True); return
    righe.sort(key=lambda r: r["ent"])

    nomi = list(SPIEGA.keys())
    # SPAZIO CHE NON SI ESAURISCE: quando tutti i mattoni base sono stati bocciati, il ricercatore restava
    # puntuale ma senza niente da provare ("0 segnali provati"). Ora combina i mattoni fra loro: rapporti e
    # prodotti. Da 18 idee si passa a centinaia, e le combinazioni dicono cose che i singoli non dicono
    # (es. "molti soldi da POCHI compratori" = concentrazione x volume).
    base_disponibili = [n for n in nomi if K.da_riprovare(f"segnale:{CHAIN}:{n}:voto", len(righe))[0]]
    if len(base_disponibili) < 6:
        import itertools, random as _rnd
        # SPAZIO INESAURIBILE: le coppie vengono mescolate con un seme che cambia a ogni ciclo, cosi' il
        # ricercatore non ripropone sempre le stesse 40 combinazioni e non resta mai senza lavoro.
        forti = [n for n in nomi if n not in ("eta_al_primo_trade",)]
        coppie = list(itertools.combinations(forti, 2))
        _rnd.Random(now // 3600).shuffle(coppie)
        for a, b in coppie[:40]:
            nomi.append(f"{a} x {b}")
            SPIEGA[f"{a} x {b}"] = f"{SPIEGA.get(a,a)} MOLTIPLICATO per {SPIEGA.get(b,b)}"
            nomi.append(f"{a} / {b}")
            SPIEGA[f"{a} / {b}"] = f"{SPIEGA.get(a,a)} RAPPORTATO a {SPIEGA.get(b,b)}"
    base_val = E.valuta([{"ent": r["ent"], "xt": r["xt"], "ret": r["ret"], "f": r["f"]} for r in righe],
                        [1] * len(righe[0]["f"]), thr)
    if base_val is None:
        print(f"RICERCA | {CHAIN}: base non valutabile", flush=True); return
    partenza = base_val[0]

    # GARANZIA DI LAVORO: se la memoria blocca TUTTO (già provato di recente, dati non ancora cresciuti),
    # il ricercatore restava puntuale e fermo — "0 segnali provati". Inaccettabile: un componente del team
    # non sta mai a mani vuote. In quel caso si riprendono comunque i candidati provati MENO di recente.
    # Meglio riprovare qualcosa con dati un po' diversi che non fare niente per ore.
    disponibili = [n for m in ("voto", "filtro") for n in nomi
                   if K.da_riprovare(f"segnale:{CHAIN}:{n}:{m}", len(righe))[0]]
    forzati = set()
    if not disponibili:
        vecchi = sorted(nomi, key=lambda n: _quando_provato(f"segnale:{CHAIN}:{n}:voto"))[:10]
        forzati = set(vecchi)

    promosse = []; provate = []; saltati = []
    for nome in nomi:
        for modo in ("voto", "filtro"):
            if time.time() - t0 > BUDGET - 20: break
            chiave = f"segnale:{CHAIN}:{nome}:{modo}"
            ok, motivo = K.da_riprovare(chiave, len(righe))
            if not ok and nome in forzati:
                ok, motivo = True, "ripreso comunque: non c'era altro da provare"
            if not ok:
                saltati.append((f"{nome} ({modo})", motivo)); continue
            def valore(r, nm):
                """valore del segnale per un token: i combinati si calcolano al volo dai mattoni."""
                if " x " in nm:
                    a, b = nm.split(" x "); return r["c"].get(a, 0.0) * r["c"].get(b, 0.0)
                if " / " in nm:
                    a, b = nm.split(" / "); return r["c"].get(a, 0.0) / (abs(r["c"].get(b, 0.0)) + 1e-6)
                return r["c"].get(nm, 0.0)
            if modo == "voto":
                # il segnale entra nel modello come uno dei tanti: vale un voto su N
                rr = [{"ent": r["ent"], "xt": r["xt"], "ret": r["ret"],
                       "f": r["f"] + [valore(r, nome)]} for r in righe]
            else:
                # IL SEGNALE COME FILTRO: non si compra affatto cio' che sta sotto la soglia.
                # E' un uso completamente diverso, ed e' quello che ha fatto la differenza su Robinhood:
                # li' il salto e' venuto dal FILTRO d'ingresso, non da un segnale in piu' nel modello.
                # (Su Solana l'insider come voto vale +2 punti, ma come filtro separa 27% da 8% di vincenti.)
                # LEAK CHIUSO: la soglia del filtro si calcola SOLO sul passato, espandendo mano a mano.
                # Prima era il 60° percentile su tutto il campione: dal vivo non l'avresti mai conosciuta.
                rr = []; visti = []
                for r in sorted(righe, key=lambda x: x["ent"]):
                    v = valore(r, nome)
                    if len(visti) >= 40:
                        soglia_f = sorted(visti)[int(len(visti) * 0.6)]
                        if v >= soglia_f:
                            rr.append({"ent": r["ent"], "xt": r["xt"], "ret": r["ret"], "f": r["f"]})
                    visti.append(v)
                if len(rr) < 60: continue
            v = E.valuta(rr, [1] * len(rr[0]["f"]), thr)
            if v is None: continue
            guadagno = v[0] - partenza
            provate.append((f"{nome} ({modo})", v[0], guadagno))
            promosso = guadagno >= GUADAGNO_MINIMO
            K.ricorda(chiave, "segnale", CHAIN, promosso, guadagno, len(righe))
            if promosso: promosse.append((f"{nome} ({modo})", v[0], guadagno))

    promosse.sort(key=lambda x: -x[2]); provate.sort(key=lambda x: -x[2])
    json.dump({"chain": CHAIN, "ts": now, "partenza": round(partenza, 1), "cfg": cfg,
               "promosse": [{"nome": n, "robusta": round(v, 1), "guadagno": round(g, 1)} for n, v, g in promosse],
               "provate": [{"nome": n, "robusta": round(v, 1), "guadagno": round(g, 1)} for n, v, g in provate]},
              open(STATO, "w"))
    if promosse:
        json.dump({"chain": CHAIN, "ts": now, "feature": [p[0] for p in promosse]},
                  open("data/feature_scoperte.json", "w"))

    L = [f"# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(provate)} segnali nuovi messi alla prova "
         f"su {len(righe)} token*", "",
         f"**Punto di partenza:** con i segnali attuali la percentuale robusta è **{partenza:+.0f}%**.", ""]
    if promosse:
        L += [f"## 🎯 {len(promosse)} segnali NUOVI che alzano la percentuale", "",
              "| il segnale | cosa guarda | porta a | guadagno |", "|---|---|---|---|"]
        for n, v, g in promosse:
            L.append(f"| `{n}` | {SPIEGA.get(n.split(' (')[0], '')} | **{v:+.0f}%** | **{g:+.0f} punti** |")
        L += ["", "> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.",
              "> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.", ""]
    else:
        L += ["## Nessun segnale nuovo ha superato la prova in questo giro", "",
              f"Nessuno dei {len(provate)} candidati alza la percentuale di almeno {GUADAGNO_MINIMO:.0f} punti.",
              "Non è un fallimento: è la risposta onesta di oggi. Con più dati gli stessi segnali possono passare.", ""]
    if provate:
        L += ["## Tutti i segnali provati, dal migliore al peggiore", "",
              "| il segnale | cosa guarda | risultato |", "|---|---|---|"]
        for n, v, g in provate:
            L.append(f"| `{n}` | {SPIEGA.get(n.split(' (')[0], '')} | {v:+.0f}% ({g:+.0f}) |")
    if saltati:
        L += ["", "## Non riprovati (la memoria del team dice che è inutile)", ""]
        L += [f"- `{n}` — {m}" for n, m in saltati[:10]]
    L += ["", "> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema",
          "> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio",
          "> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,",
          "> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare."]
    open(f"RICERCA_{CHAIN}.md", "w").write("\n".join(L))
    K.report()
    print(f"RICERCA | {CHAIN} | {len(provate)} provati ({len(saltati)} saltati dalla memoria) | "
          f"{len(promosse)} promossi | base {partenza:+.0f}%", flush=True)


if __name__ == "__main__":
    main()
