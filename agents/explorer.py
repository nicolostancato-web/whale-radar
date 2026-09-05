#!/usr/bin/env python3
"""
EXPLORER — il LOOP 1: la ricerca che non si ferma mai. *"Come faccio ad avere una percentuale più alta?"*

Direttiva Nicolò 31/08 (vedi STRATEGIA_LOOP.md): il loop deve provare STRATEGIE, una per una, e scriverle:
"entro a +6h, stop loss 80%, take profit 2x/3x/4x/5x" → misura sullo storico → esce un numero → "questa non
va, avanti" → un'altra. E ogni volta che il numero sale, tiene la nuova e riparte a cercarne una migliore.
Il goal non finisce mai: anche a +108% la domanda resta come alzarlo ancora.

Prova DUE cose insieme (prima provava solo la prima, cioe' meta' del lavoro):
  1. **la selezione** — quali segnali guardare e con che soglia di ingresso
  2. **la strategia** — quando entrare (entry_h), dove tagliare (hard stop), dove prendere profitto
     (tp1/tp2) e quanto lasciar correre (trailing)
Ogni tentativo e' misurato col walk-forward ONESTO sulla percentuale ROBUSTA (tolti i 3 colpi migliori):
la media e' gonfiata dai mostri, e una strategia che regge solo grazie a un 300x e' una lotteria.

L'EXPLORER PROPONE, NON APPLICA: cambiare la strategia viva e' una decisione umana (DECISIONS.md).
Stato in data/explorer_<chain>.json · verbale in EXPLORER_<chain>.md. €0.
"""
import json, os, gzip, glob, time, random, sys
sys.path.insert(0, "agents")
import multichain_brain as B, learner as L
import holdout as H
import conoscenza as K

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 240))
# Una miglioria conta solo se supera il rumore. Con ~200 trade e forte dispersione, l'errore standard della
# robusta e' ~8 punti: accettare +3 significava promuovere migliorie fantasma. Ora la soglia si calcola dai
# dati (2 x errore standard), con un minimo di 8 punti.
MIGLIORAMENTO_MINIMO = 8.0
now = int(time.time())
t0 = time.time()
STATO = f"data/explorer_{CHAIN}.json"

# lo spazio delle strategie da provare (i valori che Nicolò descrive: entrata, stop, take profit, trailing)
ENTRY_H = [1, 2, 3, 6, 12]
# IL FILTRO D'INGRESSO: la cosa che Robinhood (+34%) ha e le altre chain no. Robinhood non entra su ogni
# token a orario fisso: entra solo quando c'e' abbastanza vita (volume, ore di scambi, un minimo di
# pressione in vendita = qualcuno che monetizza, quindi non e' un pool morto). Sulle altre chain entravamo
# su TUTTO — plausibilmente e' per questo che sono negative. Ora il loop 1 puo' provarlo ovunque.
MIN_VOL = [0, 500, 3000, 10000, 30000]      # volume minimo prima di entrare
MIN_ORE = [0, 2, 4]                          # ore di storia minime prima di entrare
MIN_SELL = [0.0, 0.10, 0.15, 0.30]           # rapporto minimo vendite/acquisti (vitalita' del pool)
TP1 = [2, 3, 4, 5]
TP2 = [6, 8, 12, 15, 25]
TRAIL = [0.3, 0.4, 0.5, 0.6]
HARD = [0.5, 0.6, 0.7, 0.8]


def candele_chain(chain):
    """carica UNA volta le serie di prezzo (candele + pulse); poi ogni strategia si valuta su queste."""
    out = []; nascite = []
    for f in B.serie_files(chain):
        try:
            cs = []; nato = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("t0"): nato = int(d["t0"])
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            if not cs: continue
            cs.sort()
            addr = os.path.basename(f).replace(".jsonl.gz", "")
            nascite.append(nato or cs[0][0])      # PRIMA del filtro: altrimenti il confine slitta indietro
            if len(cs) < B.MIN_CANDLES: continue
            # SPLIT TEMPORALE: la ricerca vede solo i token piu' vecchi. Validazione e conferma sono
            # separate dal TEMPO, non dall'hash: e' l'unico modo di chiedersi "funziona su un mercato
            # che non abbiamo mai visto?"
            if H.in_cassaforte(addr, nato or cs[0][0]): continue
            out.append((addr, cs, nato))
        except Exception: pass
    H.imposta_confine(nascite)      # il confine temporale si fissa una volta sola, mai piu' toccato
    return out


SIZE_RIF = 10.0        # euro per posizione nel demo (10% di un conto da 100): serve a stimare l'impatto


try:
    TRAPPOLE = set(json.load(open("data/trappole.json")).get("pool", {}))
except Exception:
    TRAPPOLE = set()


def _net_liq(m, tr, impatto, fuga=None, vol_ora=None):
    """come L._net, ma con lo slippage maggiorato dall'IMPATTO DI MERCATO.

    Correzione 01/09 (revisione critica #1): usavamo uno slippage fisso del 15% in uscita. Ma su un pool con
    poche migliaia di dollari di volume orario, vendere una posizione a 3x muove il prezzo molto di piu': sei
    tu il mercato. Ora l'attrito cresce quando il pool e' sottile — ed e' proprio nei pool sottili che si
    annidano i rendimenti piu' spettacolari dello storico, quelli che non avremmo mai potuto incassare."""
    if fuga is None: fuga = tr
    ein = (1 + L.ES) * (1 + L.FEE)
    ritardo = L.LAT * (2 if tr else 1)
    # la gamba giusta, e al prezzo della liquidita' VERA di quel momento (03/09).
    # `impatto` restava come termine additivo inventato: ora il costo lo dice la curva misurata, e
    # quel termine serve solo se la curva non e' ancora utilizzabile.
    import metro as _MM
    if _MM.CURVA and vol_ora is not None:
        uscita_slip = min(0.60, _MM.uscita_liquidita(vol_ora, fuga=fuga))
    else:
        uscita_slip = min(0.60, _MM.uscita(fuga) + impatto)
    eout = m * (1 - uscita_slip) * (1 - L.FEE) * (1 - ritardo)
    return eout / ein - 1 - (L.GAS * 2) / SIZE_RIF


def esito(path, tp1, tp2, trail, hard, minimi=None, impatto=0.0, vol_ora=None):
    """rendimento di UN trade: scale-out a tp1/tp2, trailing, stop duro.

    IL RUG INTRABAR (correzione 31/08, dalla revisione critica): le candele sono ORARIE, e finora lo stop
    veniva valutato sulla CHIUSURA. Ma dentro quell'ora il prezzo puo' essere crollato a -95% e risalito a
    -70%: noi vedevamo -70% e uscivamo li'. Nella realta' saremmo usciti molto piu' in basso — o non saremmo
    usciti affatto. Ora lo stop guarda il MINIMO della candela: se il fondo e' stato toccato, e' quello il
    prezzo a cui saremmo usciti davvero. E' il ramo che rende onesti i memecoin che muoiono in un blocco."""
    ep = path[0]; hi = ep; legs = []; h1 = h2 = False; pk = max(path) / ep if path else 1
    for i, v in enumerate(path):
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        basso = (minimi[i] if minimi and i < len(minimi) and minimi[i] else v)
        if not h1 and m >= tp1: legs.append(_net_liq(tp1, False, impatto, vol_ora=vol_ora)); h1 = True
        if not h2 and m >= tp2: legs.append(_net_liq(tp2, False, impatto, vol_ora=vol_ora)); h2 = True
        if not h1:
            if basso <= ep * (1 - hard):
                # si esce al FONDO toccato, non al livello dello stop: in un crollo quel prezzo non esiste
                legs.append(_net_liq(min(basso, ep * (1 - hard)) / ep, False, impatto, fuga=True, vol_ora=vol_ora)); break
        elif basso <= hi * (1 - trail):
            legs.append(_net_liq(min(basso, hi * (1 - trail)) / ep, True, impatto)); break
    while len(legs) < 3:
        legs.append(legs[-1] if legs else _net_liq(path[-1] / ep if path else 1, True, impatto, vol_ora=vol_ora))
    return sum(legs[:3]) / 3, pk


NON_RISOLTI_H = 48      # una serie aggiornata nelle ultime 48h e' ancora VIVA: quel trade non e' chiuso


def costruisci(serie, entry_h, tp1, tp2, trail, hard, min_vol=500, min_ore=0, min_sell=0.0):
    """applica UNA strategia a tutti i token: quando entrare, se entrare (filtro), come uscire.
    I token ancora vivi vengono ESCLUSI: prima venivano chiusi al prezzo corrente e contati come trade
    conclusi — e finivano proprio nella "meta' recente" che doveva fare da verifica."""
    rows = []
    limite_vivo = int(time.time()) - NON_RISOLTI_H * 3600
    for addr, cs, nato in serie:
        t0c = nato or cs[0][0]
        if cs[0][0] > t0c + entry_h * 3600: continue      # preso troppo tardi: la finestra e' persa
        ei = None
        for i, c in enumerate(cs):
            if c[0] >= t0c + entry_h * 3600: ei = i; break
        if ei is None or ei == 0: continue
        pre = cs[:ei + 1]
        if sum((c[5] or 0) for c in pre) < max(B.MIN_VOL, min_vol): continue     # FILTRO: volume minimo
        if min_ore and (pre[-1][0] - pre[0][0]) < min_ore * 3600: continue       # FILTRO: ore di vita minime
        if min_sell:                                                              # FILTRO: il pool e' vivo?
            tr = [t for t in B.load_trades(CHAIN, addr) if t["ts"] <= cs[ei][0]]
            bu = sum(t["usd"] for t in tr if t["kind"] == "buy")
            se = sum(t["usd"] for t in tr if t["kind"] == "sell")
            if se / (bu + 1) < min_sell: continue
        dopo = [c for c in cs[ei:] if c[4]]
        path = [c[4] for c in dopo]
        minimi = [(c[3] if c[3] else c[4]) for c in dopo]     # il minimo della candela: serve al rug intrabar
        if len(path) < 2: continue
        if cs[-1][0] > limite_vivo: continue        # ancora in corsa: non e' un trade chiuso, non si conta
        # IMPATTO: quanto pesa la nostra posizione sul volume orario tipico del pool.
        # Volume alto -> impatto trascurabile. Pool sottile -> l'uscita si mangia il rendimento.
        vols = [(c[5] or 0) for c in pre if c[5]]
        vol_ora = (sum(vols) / len(vols)) if vols else 0.0
        impatto = min(0.45, SIZE_RIF / (vol_ora + 1.0))
        r, _ = esito(path, tp1, tp2, trail, hard, minimi, impatto, vol_ora=vol_ora)
        # TRAPPOLA (03/09): il token esiste, il prezzo esiste, l'uscita no. Il backtest vedeva uno
        # stop a -40% e registrava -40%; nella realta' quel trade e' -100%. Forziamo la perdita
        # totale SOLO se la serie non la mostra gia': cosi' l'aggiustamento e' esatto su questo
        # token, non una probabilita' spalmata su tutti — che sarebbe l'errore del costo medio,
        # ripetuto in un altro punto.
        if addr.lower() in TRAPPOLE and r > -0.95:
            r = -1.0
        # anche le CANDELE si tagliano al ritardo con cui ci arrivano: entrare all'ora giusta
        # guardando un grafico che a quell'ora non avevamo e' la stessa illusione dei trade (04/09).
        _vis = [c for c in pre if c[0] <= cs[ei][0] - B.RITARDO_OSS] or pre[:1]
        feats = B.features(_vis) + B.trade_features(B.load_trades(CHAIN, addr), cs[ei][0])
        rows.append({"ent": cs[ei][0], "xt": cs[-1][0], "f": feats, "ret": r})
    rows.sort(key=lambda r: r["ent"])
    return rows


def porta(rr): return (sum(1 + x for x in rr) / len(rr) - 1) * 100 if rr else 0.0


def _robusta(sel):
    """Toglie il 5% dei risultati migliori, non 3 fissi.
    Perche': con 3 fissi, su 600 trade si toglieva lo 0,5% e su 15 il 20% — e l'ottimizzatore poteva vincere
    semplicemente facendo PIU' trade, cosi' il taglio pesava meno e i mostri sotto il quarto posto restavano
    dentro. In percentuale il taglio e' onesto a qualunque numero di operazioni."""
    if len(sel) < 6: return porta(sel)
    quanti = max(3, int(len(sel) * 0.05))
    return porta(sorted(sel, reverse=True)[quanti:])


def _metriche(sel):
    """LE METRICHE PRIMARIE (consulenza esterna 01/09).

    Fin qui decidevamo sulla 'robusta' = media tolto il 5% migliore. La consulenza l'ha smontata con un
    argomento che regge: quel taglio tiene TUTTA la coda negativa ed elimina quella positiva — ma sui
    memecoin il profitto VIENE dalla coda. Chiedere che una strategia sia positiva senza i suoi mostri,
    con capacita' e costi realistici, e' chiedere tre proprieta' spesso incompatibili fra loro.

    Da ora la 'robusta' resta come STRESS TEST (una seconda condizione), e si decide su:
      · P&L netto atteso per trade (la media vera, code comprese)
      · crescita logaritmica a size fissa (quanto cresce il capitale reinvestendo: penalizza le rovine)
      · CVaR 5% (quanto fa male il 5% peggiore)
      · limite inferiore bootstrap (il numero prudente, non la stima fortunata)"""
    if not sel: return {}
    import math
    n = len(sel)
    media = sum(sel) / n * 100
    peggiori = sorted(sel)[:max(1, n // 20)]
    cvar = sum(peggiori) / len(peggiori) * 100
    # log-growth: quanto cresce il capitale se reinvesti sempre la stessa frazione
    log_g = sum(math.log(max(0.01, 1 + x)) for x in sel) / n * 100
    return {"media": media, "cvar5": cvar, "log_growth": log_g, "n": n}


def _limite_basso(sel, giri=120):
    """Non ci si fida della stima puntuale: si guarda il 5° percentile di un bootstrap.
    Tradotto: 'se ripetessimo questo esperimento, nel 95% dei casi andrebbe almeno cosi'.
    E' il numero su cui si dovrebbe decidere, non la media fortunata di un campione."""
    if len(sel) < 30: return None
    import random as _r
    rnd = _r.Random(12345)          # seme fisso: il risultato non deve cambiare a ogni lettura
    stime = []
    for _ in range(giri):
        camp = [sel[rnd.randrange(len(sel))] for _ in range(len(sel))]
        stime.append(_robusta(camp))
    stime.sort()
    return stime[int(len(stime) * 0.05)]


def valuta(rows, mask, thr, dettaglio=False):
    """walk-forward onesto coi soli segnali accesi.
    Ritorna (PUNTEGGIO, media, n_trade, vinti, robusta_totale, robusta_recente).

    Il PUNTEGGIO non è la robusta su tutto lo storico: è il MINIMO fra la robusta totale e quella sulla
    META' PIU' RECENTE dei token. Motivo (scoperto il 31/08): tutte le chain rendono meno sui token nuovi —
    il mercato si muove. Ottimizzando su tutto lo storico premieremmo strategie che funzionavano un mese fa
    e oggi sono morte. Chiedendo che regga ANCHE sul periodo recente, cerchiamo qualcosa che funzioni domani."""
    idx = [i for i, m in enumerate(mask) if m]
    if not idx or len(rows) < 40: return ([] if dettaglio else None)
    # `dettaglio`: oltre al punteggio, QUALI righe sono state scelte. Serve al test sigillato, che deve
    # raggruppare gli esiti per giornata e creator — e il raggruppamento e' impossibile su una media.
    sel = []; scelte = []; model = None; last_n = 0
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        if len(train) < B.WARMUP: sel.append(r["ret"]); scelte.append(r); continue
        if model is None or len(train) - last_n >= 10:
            y = [1 if q["ret"] > 0 else 0 for q in train]
            if len(set(y)) >= 2:
                model = L.fit_logreg([[q["f"][j] for j in idx] for q in train], y, iters=400); last_n = len(train)
        if model is None: sel.append(r["ret"]); scelte.append(r); continue
        w, b, mu, sd = model
        s = L.sigmoid(sum(w[k] * (r["f"][idx[k]] - mu[k]) / sd[k] for k in range(len(idx))) + b)
        if s >= thr: sel.append(r["ret"]); scelte.append(r)
    if dettaglio: return scelte
    if len(sel) < 10: return None
    vinti = sum(1 for x in sel if x > 0) / len(sel) * 100
    # errore standard della media: serve a sapere quanto e' RUMOROSO questo numero
    m = sum(sel) / len(sel)
    var = sum((x - m) ** 2 for x in sel) / max(1, len(sel) - 1)
    se = (var / len(sel)) ** 0.5 * 100
    m = _metriche(sel)
    rob_tot = _robusta(sel)
    meta = len(sel) // 2
    rob_rec = _robusta(sel[meta:]) if len(sel) >= 24 else rob_tot   # sel e' in ordine di entrata: la coda e' il recente
    return min(rob_tot, rob_rec), porta(sel), len(sel), vinti, rob_tot, rob_rec, se, _limite_basso(sel), m


def descrivi(c):
    filtro = []
    if c.get("min_vol", 0) > 500: filtro.append(f"solo se volume > ${c['min_vol']:,}".replace(",", "."))
    if c.get("min_ore", 0): filtro.append(f"almeno {c['min_ore']}h di scambi")
    if c.get("min_sell", 0): filtro.append(f"vendite/acquisti > {c['min_sell']:.0%}")
    f = (" · " + ", ".join(filtro)) if filtro else ""
    return (f"entra +{c['entry_h']}h{f} · stop -{c['hard']*100:.0f}% · profitto a {c['tp1']}x e {c['tp2']}x "
            f"· trailing -{c['trail']*100:.0f}% · soglia {c['thr']}")


def main():
    serie = candele_chain(CHAIN)
    if len(serie) < 60:
        print(f"EXPLORER | {CHAIN}: solo {len(serie)} serie, si accumula", flush=True); return

    st = json.load(open(STATO)) if os.path.exists(STATO) else {}
    best = st.get("best") or {"entry_h": B.ENTRY_H, "tp1": 3, "tp2": 6, "trail": 0.5, "hard": 0.7,
                              "thr": B.THR, "mask": None, "min_vol": 500, "min_ore": 0, "min_sell": 0.0}
    for k, v in {"min_vol": 500, "min_ore": 0, "min_sell": 0.0}.items(): best.setdefault(k, v)
    scoperte = st.get("scoperte", []); tentativi_tot = st.get("tentativi", 0); provate = st.get("provate", [])

    cache = {}
    def rows_per(c):
        k = (c["entry_h"], c["tp1"], c["tp2"], c["trail"], c["hard"], c["min_vol"], c["min_ore"], c["min_sell"])
        if k not in cache: cache[k] = costruisci(serie, *k)
        return cache[k]

    r0 = rows_per(best)
    nfeat = len(r0[0]["f"]) if r0 else 10
    if not best.get("mask") or len(best["mask"]) != nfeat: best["mask"] = [1] * nfeat
    v0 = valuta(r0, best["mask"], best["thr"])
    if v0 and st.get("robusta") is not None and v0[0] < st["robusta"] - 3:
        # il campione di ieri oggi vale meno: NON e' un dettaglio, e' una strategia che si e' spenta.
        # Va ricordato, altrimenti la ri-eleggiamo campione al prossimo giro.
        K.ricorda(f"strategia:{CHAIN}:{descrivi(best)}", "strategia", CHAIN, False,
                  v0[0] - st["robusta"], len(r0))
    best_val = v0[0] if v0 else None
    best_info = v0

    rnd = random.Random(now // 1800)
    # MULTI-START: una volta ogni 6 giri si riparte da una configurazione a CASO. Cercando sempre a piccoli
    # passi dal migliore, si finisce in un minimo locale e ci si resta per sempre: il salto serve a uscirne.
    # Il campione in carica non si perde: resta salvato, e viene ripreso se il salto non paga.
    giro = st.get("giri", 0) + 1
    if giro % 6 == 0:
        campione = dict(best); campione_val = best_val
        best = {"entry_h": rnd.choice(ENTRY_H), "tp1": rnd.choice(TP1), "tp2": rnd.choice(TP2),
                    "trail": rnd.choice(TRAIL), "hard": rnd.choice(HARD), "thr": rnd.choice([0.2, 0.3, 0.4, 0.5]),
                    "min_vol": rnd.choice(MIN_VOL), "min_ore": rnd.choice(MIN_ORE), "min_sell": rnd.choice(MIN_SELL),
                    "mask": [rnd.randint(0, 1) for _ in range(nfeat)]}
        if sum(best["mask"]) == 0: best["mask"][0] = 1
        rr = rows_per(best)
        vv = valuta(rr, best["mask"], best["thr"]) if len(rr) >= 60 else None
        if vv is None or (campione_val is not None and vv[0] < campione_val):
            best, best_val = campione, campione_val      # il salto non ha pagato: si torna al campione
        else:
            best_val, best_info = vv[0], vv
    provati = 0; migliorie = 0
    while time.time() - t0 < BUDGET - 15:
        c = dict(best)
        mossa = rnd.random()
        if mossa < 0.30:                        # cambia la STRATEGIA di uscita/entrata
            campo = rnd.choice(["entry_h", "tp1", "tp2", "trail", "hard"])
            c[campo] = rnd.choice({"entry_h": ENTRY_H, "tp1": TP1, "tp2": TP2, "trail": TRAIL, "hard": HARD}[campo])
        elif mossa < 0.45:                      # cambia il FILTRO D'INGRESSO (la leva di Robinhood)
            campo = rnd.choice(["min_vol", "min_ore", "min_sell"])
            c[campo] = rnd.choice({"min_vol": MIN_VOL, "min_ore": MIN_ORE, "min_sell": MIN_SELL}[campo])
        elif mossa < 0.75:                      # cambia i SEGNALI guardati
            mask = list(best["mask"]); j = rnd.randrange(nfeat); mask[j] = 1 - mask[j]
            if sum(mask) == 0: continue
            c["mask"] = mask
        elif mossa < 0.90:                      # cambia la soglia d'ingresso
            c["thr"] = round(min(0.75, max(0.15, best["thr"] + rnd.choice([-0.1, -0.05, 0.05, 0.1]))), 2)
        else:                                   # scossa: strategia + segnali insieme
            campo = rnd.choice(["entry_h", "tp1", "tp2", "hard"])
            c[campo] = rnd.choice({"entry_h": ENTRY_H, "tp1": TP1, "tp2": TP2, "hard": HARD}[campo])
            mask = list(best["mask"]); j = rnd.randrange(nfeat); mask[j] = 1 - mask[j]
            if sum(mask): c["mask"] = mask
        if c["tp2"] <= c["tp1"]: continue
        rows = rows_per(c)
        v = valuta(rows, c["mask"], c["thr"])
        provati += 1
        if v is None: continue
        rob, med, ntr, vinti = v[0], v[1], v[2], v[3]
        soglia_rumore = max(MIGLIORAMENTO_MINIMO, 2 * (v[6] if len(v) > 6 else 4))
        provate.append({"ts": now, "s": descrivi(c), "robusta": round(rob, 1)})
        if best_val is None or rob > best_val + soglia_rumore:
            scoperte.append({"ts": now, "da": round(best_val, 1) if best_val is not None else None,
                             "a": round(rob, 1), "media": round(med, 1), "vinti": round(vinti), "n": ntr,
                             "strategia": descrivi(c)})
            # traccia PERMANENTE: imparare vuol dire ricordare anche cosa e' stato provato e poi caduto,
            # altrimenti fra una settimana il team ripesca la stessa strada e ci perde di nuovo tempo
            K.ricorda(f"strategia:{CHAIN}:{descrivi(c)}", "strategia", CHAIN, True, rob, len(rows))
            best_val, best, best_info = rob, c, v
            migliorie += 1

    tentativi_tot += provati
    json.dump({"chain": CHAIN, "ts": now, "best": best, "robusta": round(best_val, 1) if best_val is not None else None,
               "giri": giro, "tentativi": tentativi_tot, "scoperte": scoperte[-40:], "provate": provate[-200:]}, open(STATO, "w"))

    nomi = B.FEAT if len(B.FEAT) == nfeat else [f"f{i}" for i in range(nfeat)]
    accesi = [n for n, m in zip(nomi, best["mask"]) if m]
    if best_info:
        rob, med, ntr, vinti, rob_tot, rob_rec = best_info[:6]
    else:
        rob = med = None; ntr = vinti = rob_tot = rob_rec = 0
    L2 = [f"# 🔬 EXPLORER — LOOP 1: come alzo la percentuale? ({CHAIN})",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {provati} strategie provate in questo ciclo "
          f"· {tentativi_tot} in totale*", ""]
    if best_val is not None:
        mm = best_info[8] if best_info and len(best_info) > 8 else {}
        L2 += [f"## Migliore trovata finora: **{best_val:+.0f}%** (stress test) · "
               f"P&L medio **{mm.get('media', 0):+.0f}%** · crescita composta **{mm.get('log_growth', 0):+.1f}%** "
               f"· 5% peggiore **{mm.get('cvar5', 0):+.0f}%** · {ntr} trade", "",
               "*La percentuale grande è lo STRESS TEST (tolto il 5% migliore): serve a non farsi ingannare",
               "dai colpi fortunati, ma non è il rendimento atteso. Il P&L medio è quello che il conto vedrebbe;",
               "la crescita composta dice se reinvestendo si cresce o ci si rovina.*", "",
               f"*Il punteggio è il **minimo** fra la robusta su tutto lo storico ({rob_tot:+.0f}%) e quella sui "
               f"token più RECENTI ({rob_rec:+.0f}%): cerchiamo qualcosa che funzioni domani, non che abbia "
               f"funzionato un mese fa.*", "",
               f"**La strategia:** {descrivi(best)}", f"**I segnali guardati:** `{', '.join(accesi)}`", "",
               f"- migliorie trovate in questo ciclo: **{migliorie}**",
               f"- il cancello del LIVE si apre a **+40%** robusta → oggi "
               + ("🟢 **APERTO**" if best_val >= 40 else f"🔴 chiuso (mancano {40-best_val:.0f} punti)"), ""]
    if scoperte:
        L2 += ["## Le strategie che hanno alzato la percentuale", "",
               "| quando | da | a | vinti | la strategia |", "|---|---|---|---|---|"]
        for s in scoperte[-8:][::-1]:
            L2.append(f"| {time.strftime('%d/%m %H:%M', time.gmtime(s['ts']))} | "
                      f"{('%+.0f%%' % s['da']) if s['da'] is not None else '—'} | **{s['a']:+.0f}%** | "
                      f"{s.get('vinti','?')}% | {s['strategia']} |")
    if provate:
        L2 += ["", "## Le ultime provate e scartate", "", "| la strategia | risultato |", "|---|---|"]
        for p in provate[-6:][::-1]:
            L2.append(f"| {p['s']} | {p['robusta']:+.0f}% |")
    L2 += ["", "> Il LOOP 1 non si ferma mai: prova strategie e segnali, tiene solo cio' che alza la percentuale",
           f"> ROBUSTA (tolti i 3 colpi migliori) di almeno {MIGLIORAMENTO_MINIMO:.0f} punti, e riparte da li'.",
           "> **Propone, non applica**: cambiare la strategia viva e' una decisione umana (DECISIONS.md)."]
    open(f"EXPLORER_{CHAIN}.md", "w").write("\n".join(L2))
    print(f"EXPLORER | {CHAIN} | {provati} strategie provate | migliore "
          f"{'-' if best_val is None else round(best_val,1)}% | {migliorie} migliorie | totale {tentativi_tot}", flush=True)


if __name__ == "__main__":
    main()
