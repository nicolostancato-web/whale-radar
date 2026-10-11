#!/usr/bin/env python3
"""
VALIDATORE — il giudice. Misura le proposte sui token della CASSAFORTE: quelli che la ricerca non ha mai visto.

Perché è il ruolo più importante di tutti: gli esploratori provano migliaia di configurazioni e tengono la
migliore. Su dati puramente casuali, con 5.000 tentativi la migliore sembra comunque ottima — è il multiple
testing, e nessun walk-forward protegge da questo. L'unico modo di sapere se una scoperta è vera è provarla
su dati che NON hanno partecipato alla ricerca.

Regola: una proposta non è mai "buona" finché il validatore non l'ha vista reggere in cassaforte. Se crolla
lì, non è una strategia: è la forma del rumore su cui abbiamo cercato troppo.
Scrive VALIDAZIONE.md. Sola lettura sui dati. €0.
"""
import json, os, gzip, time, sys
sys.path.insert(0, "agents")
import multichain_brain as B, learner as L, explorer as E, explorer_rh as ERH, holdout as H

now = int(time.time())
CADUTA_MAX = 25.0      # se in cassaforte perde più di 25 punti rispetto a quanto promesso, è rumore


def serie_cassaforte(chain):
    """le serie riservate: stesso caricamento della ricerca, ma SOLO sui token in cassaforte."""
    out = []
    for f in B.serie_files(chain):
        addr = os.path.basename(f).replace(".jsonl.gz", "")
        try:
            cs = []; nato = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("t0"): nato = int(d["t0"])
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            if len(cs) < B.MIN_CANDLES: continue
            cs.sort()
            # solo i token della fascia di VALIDAZIONE (o CONFERMA): quelli che la ricerca non ha visto
            if not H.in_cassaforte(addr, nato or cs[0][0]): continue
            out.append((addr, cs, nato))
        except Exception: pass
    return out


def giudica(chain, cfg):
    """misura una configurazione sui token mai visti. Ritorna (robusta, n_trade, vinti) o None."""
    serie = serie_cassaforte(chain)
    if len(serie) < 60: return None
    E.CHAIN = chain
    rows = E.costruisci(serie, cfg.get("entry_h", 3), cfg.get("tp1", 3), cfg.get("tp2", 6),
                        cfg.get("trail", 0.5), cfg.get("hard", 0.7),
                        cfg.get("min_vol", 500), cfg.get("min_ore", 0), cfg.get("min_sell", 0.0))
    if len(rows) < 40: return None
    nfeat = len(rows[0]["f"])
    v = E.valuta(rows, [1] * nfeat, cfg.get("thr", 0.4))
    if v is None: return None
    return {"robusta": v[4], "recente": v[5], "trade": v[2], "vinti": v[3], "token": len(rows)}


def giudica_robinhood(cfg):
    """stessa prova, sul pipeline completo di Robinhood: solo i token in cassaforte."""
    try:
        cand, flow, fbp, wl, fts = L.load_data()
        reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    except Exception:
        return None
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    byname = {}
    for p in cand:
        if p not in mp: continue
        if not H.in_cassaforte(p, fts.get(p)): continue     # QUI il contrario: solo i riservati
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts[p] < fts[byname[nm]]: byname[nm] = p
    if len(byname) < 40: return None
    c = {"ore_min": cfg.get("ore_min", 4), "vol_min": cfg.get("vol_min", 3000),
         "sell_min": cfg.get("sell_min", 0.15), "entry_h": cfg.get("entry_h", 3),
         "tp1": cfg.get("tp1", 3), "tp2": cfg.get("tp2", 6), "trail": cfg.get("trail", 0.5),
         "hard": cfg.get("hard", 0.7), "thr": cfg.get("thr", 0.4)}
    rows = ERH.costruisci((cand, flow, fbp, wl, fts, byname), c)
    if len(rows) < 30: return None
    v = E.valuta(rows, [1] * len(rows[0]["f"]), c["thr"])
    if v is None: return None
    return {"robusta": v[4], "recente": v[5], "trade": v[2], "vinti": v[3], "token": len(rows)}


def main():
    arch = json.load(open("data/proposte.json")) if os.path.exists("data/proposte.json") else {"proposte": []}
    aperte = [p for p in arch["proposte"] if p.get("stato") == "APERTA" and p.get("tipo") == "configurazione"]
    esiti = []
    for p in aperte:
        chain = p["chain"]
        g = (giudica_robinhood(p.get("dettaglio", {})) if chain == "robinhood"
             else giudica(chain, p.get("dettaglio", {})))
        if not g:
            esiti.append((p, None, "non abbastanza token in cassaforte per giudicare")); continue
        promesso = p.get("a", 0)
        caduta = promesso - g["robusta"]
        if g["robusta"] > 0 and caduta <= CADUTA_MAX:
            verdetto = "✅ **REGGE** — funziona anche su dati mai visti"
        elif g["robusta"] > 0:
            verdetto = f"🟡 **SI SGONFIA** — resta positiva ma perde {caduta:.0f} punti fuori dalla ricerca"
        else:
            verdetto = f"❌ **NON REGGE** — in cassaforte fa {g['robusta']:+.0f}%: era rumore"
        esiti.append((p, g, verdetto))
        p["validazione"] = {"ts": now, "robusta": round(g["robusta"], 1), "trade": g["trade"],
                            "verdetto": verdetto.split("—")[0].strip()}

    json.dump(arch, open("data/proposte.json", "w"))

    L2 = ["# ⚖️ VALIDAZIONE — le proposte messe alla prova su dati MAI VISTI",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · un token su quattro è in cassaforte: "
          f"la ricerca non lo vede, non lo può vedere*", "",
          "> **Perché esiste questo controllo:** gli esploratori provano migliaia di configurazioni e tengono la",
          "> migliore. Su dati puramente casuali, con 5.000 tentativi la migliore sembra comunque ottima. È il",
          "> multiple testing, e nessun walk-forward protegge da questo. L'unico modo di sapere se una scoperta",
          "> è vera è provarla dove non ha cercato.", ""]
    if not esiti:
        L2 += ["Nessuna proposta di configurazione da giudicare in questo momento.", ""]
    else:
        L2 += ["| chain | prometteva | **in cassaforte** | trade | verdetto |", "|---|---|---|---|---|"]
        for p, g, v in esiti:
            if g:
                L2.append(f"| {p['chain']} | {p.get('a', 0):+.0f}% | **{g['robusta']:+.0f}%** | "
                          f"{g['trade']} ({g['token']} token) | {v} |")
            else:
                L2.append(f"| {p['chain']} | {p.get('a', 0):+.0f}% | — | — | {v} |")
        L2 += ["", "> **La regola:** nessuna proposta si applica se non ha superato questo controllo. Una",
               "> configurazione che brilla nella ricerca e crolla in cassaforte non è una strategia: è la forma",
               f"> del rumore su cui abbiamo cercato troppo. Tolleranza massima: {CADUTA_MAX:.0f} punti di calo.", ""]
    open("VALIDAZIONE.md", "w").write("\n".join(L2))
    print(f"VALIDATORE | {len(esiti)} proposte giudicate", flush=True)


if __name__ == "__main__":
    main()
