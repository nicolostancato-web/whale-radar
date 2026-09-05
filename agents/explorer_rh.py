#!/usr/bin/env python3
"""
EXPLORER_RH — la ricerca sul pipeline COMPLETO di Robinhood (la chain più vicina al cancello).

Buco scoperto il 31/08: l'esploratore lavorava sul pipeline multichain, ma il numero vero di Robinhood
(+34% robusta) viene da un pipeline diverso e più ricco (candele + flusso + first-buyers + score dei wallet).
Risultato: stavamo cercando ovunque tranne che sulla chain messa meglio.
Peggio: il suo FILTRO D'INGRESSO (almeno 4h di scambi, $3.000 di volume, 15% di vendite) non è mai stato
ottimizzato — sono tre numeri scritti a mano una volta e mai più toccati. Qui vengono messi in discussione.

Prova: filtro d'ingresso · entrata · uscita (tp/trail/stop) · quali segnali guardare · soglia.
Punteggio = MINIMO fra robusta totale e robusta sui token più recenti (deve funzionare domani, non un mese fa).
PROPONE, non applica. Scrive EXPLORER_ROBINHOOD.md. €0.
"""
import json, os, time, random, sys
sys.path.insert(0, "agents")
import learner as L, explorer as E
import holdout as H
import conoscenza as K

BUDGET = int(os.environ.get("BUDGET_SEC", 300))
MIGLIORAMENTO_MINIMO = 3.0
now = int(time.time()); t0 = time.time()
STATO = "data/explorer_rh.json"

ORE_MIN = [2, 3, 4, 6, 8]          # ore di flusso richieste prima di entrare
VOL_MIN = [1000, 3000, 6000, 12000, 25000]
SELL_MIN = [0.05, 0.10, 0.15, 0.25, 0.40]
ENTRY_H = [1, 2, 3, 6]
TP1 = [2, 3, 4, 5]; TP2 = [6, 8, 12, 20]
TRAIL = [0.3, 0.4, 0.5, 0.6]; HARD = [0.5, 0.6, 0.7, 0.8]



# CONGELAMENTO (03/09): una configurazione congelata non si riottimizza piu' sugli stessi dati.
# Non e' pignoleria burocratica: continuare a cercare finche' il numero diventa bello trasforma
# la prova in un allenamento, e a quel punto quel numero non dice piu' niente sul futuro.
def _congelata():
    """True se questa chain e' congelata in attesa del verdetto.

    ATTENZIONE (corretto subito dopo averlo introdotto): la prima versione usciva con SystemExit
    all'IMPORT del modulo. Cosi' non fermava solo l'ottimizzazione: uccideva chiunque importasse
    questo file — e il Giudice lo importa. Risultato, il controllo che doveva proteggere la
    validazione impediva alla validazione di girare. Un guardiano che blocca anche chi sta dalla
    sua parte non e' un guardiano: e' un guasto con una buona intenzione.
    Ora il blocco vale SOLO quando l'agente viene eseguito per ottimizzare."""
    try:
        import json as _j
        c = _j.load(open("data/criteri.json")).get("congelate", {})
        return "robinhood" in c and not c["robinhood"].get("letto"), c.get("robinhood", {}).get("quando", "?")
    except Exception:
        return False, "?"


def costruisci(dati, c):
    """applica una configurazione COMPLETA (filtro + entrata + uscita) e produce le righe da valutare."""
    cand, flow, fbp, wl, fts, byname = dati
    tp1, tp2, trail, hard = c["tp1"], c["tp2"], c["trail"], c["hard"]

    def esito(cs, ent, ep, minimi=None):
        """RUG INTRABAR anche su Robinhood (01/09): finora questa chain veniva misurata sulla CHIUSURA
        mentre le altre tre erano gia' passate al minimo della candela — e Robinhood e' proprio quella con
        la proposta piu' vicina al live. Misurare la chain candidata con il metro piu' generoso delle altre
        e' il modo migliore per farsi male."""
        ser = [(t, cs[t]) for t in sorted(cs) if t >= ent and cs[t] > 0]
        hi = ep; legs = []; h1 = h2 = False; xt = ser[-1][0] if ser else ent
        for t, v in ser:
            hi = max(hi, v); m = v / ep
            basso = (minimi or {}).get(t) or v
            if not h1 and m >= tp1: legs.append(L._net(tp1)); h1 = True
            if not h2 and m >= tp2: legs.append(L._net(tp2)); h2 = True
            if not h1:
                if basso <= ep * (1 - hard):
                    legs.append(L._net(min(basso, ep * (1 - hard)) / ep)); xt = t; break
            elif basso <= hi * (1 - trail):
                legs.append(L._net(min(basso, hi * (1 - trail)) / ep, True)); xt = t; break
        while len(legs) < 3: legs.append(legs[-1] if legs else L._net(ser[-1][1] / ep if ser else 1, True))
        return sum(legs[:3]) / 3, xt

    rows = []
    for nm, p in byname.items():
        lt = fts[p]; base = lt + c["entry_h"] * 3600; fl = flow.get(p, {}); ent = ep = None
        for t in sorted(cand[p]):
            if t < base: continue
            past = [v for h, v in fl.items() if h <= t]
            hrs = len(past); bu = sum(v[0] for v in past); su = sum(v[1] for v in past)
            if hrs >= c["ore_min"] and bu + su >= c["vol_min"] and su / (bu + 1) >= c["sell_min"]:
                ent, ep = t, cand[p][t]; break
        if ent is None or not ep: continue
        f = L.features_at_entry(p, ent, cand, flow, fbp, wl, fts)
        if f is None: continue
        r, xt = esito(cand[p], ent, ep, L.MINIMI.get(p))
        rows.append({"ent": ent, "xt": xt, "f": f, "ret": r, "addr": p})
    rows.sort(key=lambda r: r["ent"])
    return rows


def righe_valutabili(config):
    """Applica UNA configurazione gia' decisa ai soli token della fascia di VALIDAZIONE, e restituisce
    le righe con quanto serve per raggrupparle: quando si e' entrati, quanto ha reso, su quale token,
    di chi era.

    Non cerca, non ottimizza, non confronta: quello sarebbe un secondo tentativo travestito da verifica.
    Serve al test sigillato, che deve contare le PROVE (giornate, creator) e non le righe — cento trade
    legati allo stesso evento non sono cento prove.

    Attenzione al rovescio: la ricerca ESCLUDE la cassaforte, qui si tiene SOLO quella. E' lo stesso
    filtro girato al contrario, ed e' il motivo per cui questa funzione vive separata dal ciclo di
    ricerca invece di essere un suo parametro: un interruttore che apre la cassaforte, messo dentro
    l'agente che ottimizza, prima o poi verrebbe acceso per sbaglio."""
    cand, flow, fbp, wl, fts = L.load_data()
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    byname = {}
    for p_ in cand:
        if p_ not in mp: continue
        if H.livello(fts.get(p_)) != "validazione": continue     # SOLO i mai visti
        nm = (mp[p_] or "").split(" ")[0]
        if nm not in byname or fts[p_] < fts[byname[nm]]: byname[nm] = p_
    if not byname: return []
    rows = costruisci((cand, flow, fbp, wl, fts, byname), config)

    creatori = {}
    try:
        import glob as _g
        for f in _g.glob("data/sicurezza/*.jsonl"):
            for l in open(f):
                try:
                    d = json.loads(l)
                    if d.get("token") and d.get("creator"):
                        creatori[d["token"].lower()] = d["creator"].lower()
                except Exception: pass
    except Exception: pass

    # la selezione usa la STESSA logica della ricerca (modello allenato camminando nel tempo), non una
    # soglia semplice: se il test sigillato selezionasse in modo diverso, misurerebbe un'altra strategia.
    mask, thr = config.get("mask"), config.get("thr")
    scelte = rows
    if mask and thr is not None:
        try:
            d = E.valuta(rows, mask, thr, dettaglio=True)
            if d: scelte = d
        except Exception: pass
    fuori = []
    for r in scelte:
        a = (r.get("addr") or "").lower()
        fuori.append({"ent": r["ent"], "ret": r["ret"], "addr": a, "creator": creatori.get(a) or a})
    return fuori


def descrivi(c):
    return (f"entra dopo {c['ore_min']}h di scambi, solo se volume > ${c['vol_min']:,} e vendite/acquisti > "
            f"{c['sell_min']:.0%} · attesa +{c['entry_h']}h · stop -{c['hard']*100:.0f}% · profitto a {c['tp1']}x "
            f"e {c['tp2']}x · trailing -{c['trail']*100:.0f}% · soglia {c['thr']}").replace(",", ".")


def main():
    fermo, quando = _congelata()
    if fermo:
        print(f"EXPLORER_RH | configurazione CONGELATA il {quando}: non si riottimizza. "
              "Aspetta il verdetto sull'holdout.", flush=True)
        return
    cand, flow, fbp, wl, fts = L.load_data()
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    byname = {}
    for p in cand:
        if p not in mp: continue
        # su Robinhood la data di nascita e' fts[p] (primo timestamp): senza passarla il filtro temporale
        # non morderebbe affatto e la ricerca vedrebbe anche validazione e conferma
        if H.in_cassaforte(p, fts.get(p)): continue
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts[p] < fts[byname[nm]]: byname[nm] = p
    dati = (cand, flow, fbp, wl, fts, byname)

    st = json.load(open(STATO)) if os.path.exists(STATO) else {}
    S = json.load(open("data/strategy.json")) if os.path.exists("data/strategy.json") else {}
    best = st.get("best") or {"ore_min": 4, "vol_min": 3000, "sell_min": 0.15, "entry_h": S.get("entry_h", 3),
                              "tp1": S.get("tp1", 3), "tp2": S.get("tp2", 6), "trail": S.get("trail", 0.5),
                              "hard": S.get("hard", 0.7), "thr": 0.40, "mask": None}
    scoperte = st.get("scoperte", []); tot = st.get("tentativi", 0); provate = st.get("provate", [])

    cache = {}
    def rows_per(c):
        k = (c["ore_min"], c["vol_min"], c["sell_min"], c["entry_h"], c["tp1"], c["tp2"], c["trail"], c["hard"])
        if k not in cache: cache[k] = costruisci(dati, c)
        return cache[k]

    r0 = rows_per(best)
    if len(r0) < 60:
        _verbale_di_errore(f"solo {len(r0)} token utilizzabili con la configurazione attuale (ne servono 60)")
        print(f"EXPLORER_RH | solo {len(r0)} token con la configurazione attuale", flush=True); return
    nfeat = len(r0[0]["f"])
    if not best.get("mask") or len(best["mask"]) != nfeat: best["mask"] = [1] * nfeat
    v0 = E.valuta(r0, best["mask"], best["thr"])
    if v0 and st.get("robusta") is not None and v0[0] < st["robusta"] - 3:
        # il campione di ieri oggi vale meno: NON e' un dettaglio, e' una strategia che si e' spenta.
        # Va ricordato, altrimenti la ri-eleggiamo campione al prossimo giro.
        K.ricorda("strategia:robinhood:" + descrivi(best), "strategia", "robinhood", False,
                  v0[0] - st["robusta"], len(r0))
    best_val = v0[0] if v0 else None; best_info = v0

    # QUANTO VALE, COL METRO SEVERO, LA CONFIGURAZIONE CHE GIRA DAVVERO OGGI (non la migliore trovata finora):
    # è l'unico confronto onesto per dire "questa proposta vale N punti in più di quello che facciamo adesso".
    live = {"ore_min": 4, "vol_min": 3000, "sell_min": 0.15,          # il filtro storico, scritto a mano
            "entry_h": S.get("entry_h", 3), "tp1": S.get("tp1", 3), "tp2": S.get("tp2", 6),
            "trail": S.get("trail", 0.5), "hard": S.get("hard", 0.7), "thr": 0.40}
    try:
        rl = rows_per(live)
        vl = E.valuta(rl, [1] * nfeat, live["thr"]) if len(rl) >= 60 else None
        partenza = vl[0] if vl else None
    except Exception:
        partenza = None

    rnd = random.Random(now // 1800)
    # MULTI-START: una volta ogni 6 giri si riparte da una configurazione a CASO. Cercando sempre a piccoli
    # passi dal migliore, si finisce in un minimo locale e ci si resta per sempre: il salto serve a uscirne.
    # Il campione in carica non si perde: resta salvato, e viene ripreso se il salto non paga.
    giro = st.get("giri", 0) + 1
    if giro % 6 == 0:
        campione = dict(best); campione_val = best_val
        best = {"ore_min": rnd.choice(ORE_MIN), "vol_min": rnd.choice(VOL_MIN),
                    "sell_min": rnd.choice(SELL_MIN), "entry_h": rnd.choice(ENTRY_H), "tp1": rnd.choice(TP1),
                    "tp2": rnd.choice(TP2), "trail": rnd.choice(TRAIL), "hard": rnd.choice(HARD),
                    "thr": rnd.choice([0.2, 0.3, 0.4, 0.5]), "mask": [rnd.randint(0, 1) for _ in range(nfeat)]}
        if sum(best["mask"]) == 0: best["mask"][0] = 1
        rr = rows_per(best)
        vv = E.valuta(rr, best["mask"], best["thr"]) if len(rr) >= 60 else None
        if vv is None or (campione_val is not None and vv[0] < campione_val):
            best, best_val = campione, campione_val      # il salto non ha pagato: si torna al campione
        else:
            best_val, best_info = vv[0], vv

    provati = 0; migliorie = 0
    while time.time() - t0 < BUDGET - 20:
        c = dict(best); m = rnd.random()
        if m < 0.40:                                   # IL FILTRO D'INGRESSO (mai ottimizzato prima)
            campo = rnd.choice(["ore_min", "vol_min", "sell_min"])
            c[campo] = rnd.choice({"ore_min": ORE_MIN, "vol_min": VOL_MIN, "sell_min": SELL_MIN}[campo])
        elif m < 0.70:                                 # entrata/uscita
            campo = rnd.choice(["entry_h", "tp1", "tp2", "trail", "hard"])
            c[campo] = rnd.choice({"entry_h": ENTRY_H, "tp1": TP1, "tp2": TP2, "trail": TRAIL, "hard": HARD}[campo])
        elif m < 0.90:                                 # quali segnali guardare
            mask = list(best["mask"]); j = rnd.randrange(nfeat); mask[j] = 1 - mask[j]
            if sum(mask) == 0: continue
            c["mask"] = mask
        else:
            c["thr"] = round(min(0.75, max(0.15, best["thr"] + rnd.choice([-0.1, -0.05, 0.05, 0.1]))), 2)
        if c["tp2"] <= c["tp1"]: continue
        rows = rows_per(c)
        if len(rows) < 60: continue
        v = E.valuta(rows, c["mask"], c["thr"])
        provati += 1
        if v is None: continue
        provate.append({"ts": now, "s": descrivi(c), "punteggio": round(v[0], 1), "n": v[2]})
        if best_val is None or v[0] > best_val + MIGLIORAMENTO_MINIMO:
            scoperte.append({"ts": now, "da": round(best_val, 1) if best_val is not None else None,
                             "a": round(v[0], 1), "tot": round(v[4], 1), "rec": round(v[5], 1),
                             "vinti": round(v[3]), "n": v[2], "strategia": descrivi(c)})
            K.ricorda(f"strategia:robinhood:{descrivi(c)}", "strategia", "robinhood", True, v[0], v[2])
            best_val, best, best_info = v[0], c, v; migliorie += 1

    tot += provati
    json.dump({"ts": now, "best": best, "punteggio": round(best_val, 1) if best_val is not None else None,
               "giri": giro, "tentativi": tot, "partenza": round(partenza, 1) if partenza is not None else None,
               "scoperte": scoperte[-40:], "provate": provate[-200:]}, open(STATO, "w"))

    attuale = None
    if os.path.exists("data/edge_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
            if recs: attuale = recs[-1].get("sel_no3")
        except Exception: pass
    # [:6] e non l'intera tupla: valuta() restituisce anche errore standard e limite bootstrap, aggiunti
    # dopo. Senza questo taglio l'agente CRASHAVA a ogni giro — muto per 7 ore, perche' non scriveva
    # nemmeno il motivo. Ora il verbale di errore c'e' comunque (vedi _verbale_di_errore).
    pu, med, ntr, vin, rtot, rrec = best_info[:6] if best_info else (None, None, 0, 0, 0, 0)
    L2 = ["# 🔬 EXPLORER — Robinhood (pipeline completo, la chain più vicina al live)",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {provati} configurazioni provate in questo "
          f"ciclo · {tot} in totale*", ""]
    if best_val is not None:
        L2 += [f"## Migliore trovata: **{best_val:+.0f}%** (storico {rtot:+.0f}%, recente {rrec:+.0f}%, "
               f"vinti {vin:.0f}%, {ntr} trade)", "",
               f"**La configurazione:** {descrivi(best)}", ""]
        if partenza is not None:
            d = best_val - partenza
            L2 += [f"**Confronto onesto, stesso metro:** la configurazione in uso oggi vale **{partenza:+.0f}%**, "
                   f"questa vale **{best_val:+.0f}%** → **{d:+.0f} punti**.", "",
                   f"*(Il +{attuale:.0f}% che vedi altrove è misurato solo sullo storico, senza chiedere che "
                   f"regga anche sui token recenti: è un metro più generoso. Qui usiamo quello severo.)*" if attuale
                   else "", ""]
            if d > MIGLIORAMENTO_MINIMO:
                L2 += ["> 🎯 **PROPOSTA all'investitore**: adottare questa configurazione. È una DECISIONE: "
                       "va approvata e scritta in DECISIONS.md.", ""]
        L2 += [f"- al cancello del live (+40%) " +
               ("✅ **ci siamo**" if best_val >= 40 else f"mancano **{40-best_val:.0f} punti**"), ""]
    if scoperte:
        L2 += ["## Le configurazioni che hanno alzato il numero", "",
               "| quando | da | a | storico/recente | la configurazione |", "|---|---|---|---|---|"]
        for s in scoperte[-6:][::-1]:
            L2.append(f"| {time.strftime('%d/%m %H:%M', time.gmtime(s['ts']))} | "
                      f"{('%+.0f%%' % s['da']) if s['da'] is not None else '—'} | **{s['a']:+.0f}%** | "
                      f"{s['tot']:+.0f}% / {s['rec']:+.0f}% | {s['strategia']} |")
    L2 += ["", "> Qui si mette in discussione anche il **filtro d'ingresso** (quante ore di scambi, quanto volume,",
           "> quanta pressione in vendita): erano tre numeri scritti a mano una volta e mai più toccati, ed è",
           "> proprio il filtro che distingue Robinhood dalle altre chain."]
    open("EXPLORER_ROBINHOOD.md", "w").write("\n".join(L2))
    print(f"EXPLORER_RH | {provati} configurazioni | migliore {'-' if best_val is None else round(best_val,1)}% "
          f"| {migliorie} migliorie | totale {tot}", flush=True)


def _verbale_di_errore(err):
    """Se qualcosa va storto, si scrive COMUNQUE un verbale che lo dice.
    Perche' (31/08): questo agente e' rimasto muto 7 ore — veniva eseguito a ogni giro ma non scriveva nulla,
    e nessuno poteva sapere perche'. Un componente che fallisce in silenzio e' peggio di uno che fallisce
    rumorosamente: il secondo lo aggiusti, il primo non lo vedi nemmeno."""
    import traceback
    L = ["# 🔬 EXPLORER — Robinhood (pipeline completo)",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(int(time.time())))} · 0 configurazioni provate*", "",
         "## ⚠️ Questo giro è fallito", "",
         f"**Errore:** `{err}`", "",
         "```", traceback.format_exc()[-1200:], "```", "",
         "> Il verbale viene scritto lo stesso, apposta: un agente che tace non si distingue da uno che non",
         "> esiste. Così l'ispezione lo vede e sappiamo dove guardare."]
    try:
        open("EXPLORER_ROBINHOOD.md", "w").write("\n".join(L))
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _verbale_di_errore(f"{type(e).__name__}: {e}")
        print(f"EXPLORER_RH | FALLITO: {type(e).__name__}: {e}", flush=True)
