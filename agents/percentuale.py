#!/usr/bin/env python3
"""
PERCENTUALE — il report per l'INVESTITORE: non solo QUANTO fa una chain, ma COM'E' FATTO quel numero.

Direttiva Nicolò 31/08: "mi parli di questo 34%: è un 34% molto casuale in cui avevamo tutti trade a zero e
poi due colpi di fortuna? Allora è poco robusto e stiamo cercando di renderlo robusto."
Quindi qui si misura la ROBUSTEZZA, non solo la media:
  - quanti trade sono in guadagno (se vince 1 su 10, la media la fanno i mostri)
  - quanto pesa il colpo migliore sul totale (se da' tutto lui, non e' una strategia: e' una lotteria)
  - cosa resta togliendo i 3 migliori
  - quanto manca al cancello del live (+40%)
Scrive PERCENTUALE.md. Sola lettura. €0.
"""
import json, os, time, sys
sys.path.insert(0, "agents")
import multichain_brain as B, gate

CHAINS = ["robinhood", "base", "solana", "bsc"]
now = int(time.time())


def porta(rr): return (sum(1 + x for x in rr) / len(rr) - 1) * 100 if rr else 0.0


def da_edge_history():
    """Robinhood ha un pipeline suo, piu' ricco (filtro d'ingresso su volume/flusso + feature del learner):
    il suo numero VERO sta in edge_history, non nel multichain. Usare la fonte sbagliata dava -23% invece
    di +34% — un errore che all'investitore non si puo' raccontare."""
    if not os.path.exists("data/edge_history.jsonl"): return None
    try:
        recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
        if not recs: return None
    except Exception: return None
    r = recs[-1]
    return {"n": r.get("n_tok", 0), "trade": r.get("sel_n", 0), "media": r.get("sel_port", 0),
            "robusta": r.get("sel_no3", 0), "vinti": r.get("sel_win", 0),
            "peso_top1": r.get("peso_top1", 0), "peso_top3": r.get("peso_top3", 0),
            "migliore": r.get("migliore", 0), "mediana": r.get("mediana", 0), "fonte": "pipeline completo"}


def analizza(chain):
    """rifà la selezione walk-forward e guarda COME è fatto il risultato, trade per trade."""
    if chain == "robinhood":
        a = da_edge_history()
        if a: return a
    try:
        rows = B.load_rows(chain)
    except Exception:
        return None
    if len(rows) < 40: return None
    sel = B.walkforward(rows)
    if len(sel) < 10: return None
    s = sorted(sel, reverse=True)
    tot = sum(1 + x for x in sel)                       # capitale finale se mettessimo 1 su ognuno
    guadagno_top = (1 + s[0]) if s else 0
    return {
        "n": len(rows), "trade": len(sel),
        "media": porta(sel), "robusta": porta(s[3:]),
        "vinti": sum(1 for x in sel if x > 0) / len(sel) * 100,
        "peso_top1": guadagno_top / tot * 100 if tot else 0,
        "peso_top3": sum(1 + x for x in s[:3]) / tot * 100 if tot else 0,
        "migliore": s[0] * 100, "mediana": s[len(s) // 2] * 100, "fonte": "pipeline multichain",
    }


def stabilita(chain):
    """IL TEST CHE CONTA DAVVERO: la percentuale regge anche nel PERIODO PIU' RECENTE?
    Un numero costruito su token vecchi puo' essere gia' morto: il mercato cambia. Dividiamo i token in due
    meta' nel tempo e misuriamo separatamente. Se la meta' recente crolla, quella percentuale non e' un edge:
    e' un ricordo. (E' il controllo che vorremmo aver avuto prima del paper da €323k.)"""
    try:
        rows = B.load_rows(chain)
    except Exception:
        return None
    if len(rows) < 120: return None
    rows.sort(key=lambda r: r["ent"])
    meta = len(rows) // 2
    out = []
    for parte in (rows[:meta], rows[meta:]):
        sel = B.walkforward(parte)
        if len(sel) < 10: return None
        out.append(porta(sorted(sel, reverse=True)[3:]))
    vecchia, recente = out
    return {"vecchia": vecchia, "recente": recente, "tiene": recente >= min(0.0, vecchia - 15)}


def giudizio(a):
    """la frase che spiega all'investitore che tipo di numero è."""
    if a["robusta"] >= 40:
        return "🟢 **SOLIDA** — regge anche togliendo i colpi migliori: qui si può parlare di live"
    if a["robusta"] > 0 and a["peso_top3"] < 50:
        return "🟡 **POSITIVA MA NON ANCORA SOLIDA** — guadagna, ma serve alzarla prima di rischiare soldi"
    if a["robusta"] > 0:
        return (f"🟠 **FRAGILE** — il numero è positivo ma i 3 colpi migliori pesano il {a['peso_top3']:.0f}% "
                f"del risultato: togli quelli e resta poco. È fortuna concentrata, non una strategia")
    return "🔴 **NEGATIVA** — con questa strategia si perde: il loop 1 deve continuare a cercare"


def main():
    L = ["# 📊 LA PERCENTUALE — com'è fatta, chain per chain",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · walk-forward onesto · "
         f"il cancello del live si apre a +{gate.SOGLIA_ROBUSTA:.0f}% robusta su {gate.MIN_TOKEN}+ token*", "",
         "| chain | media | **robusta** | trade in guadagno | peso dei 3 colpi migliori | giudizio |",
         "|---|---|---|---|---|---|"]
    dettagli = []
    stab = {}
    for ch in CHAINS:
        a = analizza(ch)
        if not a:
            L.append(f"| {ch} | — | — | — | — | dati insufficienti |"); continue
        g = giudizio(a)
        L.append(f"| **{ch}** | {a['media']:+.0f}% | **{a['robusta']:+.0f}%** | {a['vinti']:.0f}% "
                 f"({a['trade']} trade) | {a['peso_top3']:.0f}% | {g.split('—')[0].strip()} |")
        dettagli.append((ch, a, g))
        stab[ch] = stabilita(ch)
    L += [""]
    for ch, a, g in dettagli:
        manca = gate.SOGLIA_ROBUSTA - a["robusta"]
        L += [f"## {ch}", "", g, "",
              f"- su **{a['n']} token** il modello ne sceglie **{a['trade']}**, e ne vanno bene il **{a['vinti']:.0f}%**"
              + (f"  *(fonte: {a['fonte']})*" if a.get("fonte") else ""),
              f"- il colpo migliore ha fatto **{a['migliore']:+.0f}%** e da solo pesa il **{a['peso_top1']:.0f}%** del risultato",
              f"- il trade mediano fa **{a['mediana']:+.0f}%** (è questo che succede *di solito*)",
              f"- togliendo i 3 colpi migliori resta **{a['robusta']:+.0f}%** ← il numero su cui decidiamo",
              (f"- al cancello del live mancano **{manca:.0f} punti**" if manca > 0
               else "- ✅ **sopra il cancello**: si può proporre di aprire il live")]
        s = stab.get(ch)
        if s:
            L += [f"- **tiene nel tempo?** prima metà dei token **{s['vecchia']:+.0f}%**, metà più recente "
                  f"**{s['recente']:+.0f}%** → " +
                  ("✅ regge" if s["tiene"] else
                   "⚠️ **NO: sta peggiorando**. Un numero che funziona solo sui token vecchi è un ricordo, "
                   "non un edge — il mercato è cambiato e la strategia va rifatta")]
        L += [""]
    L += ["> **Perché guardiamo la robusta e non la media:** la media la fanno i mostri. Se una chain fa +100%",
          "> ma il 90% arriva da un solo token che ha fatto 300x, quella non è una strategia ripetibile: è una",
          "> lotteria vinta una volta. Il numero su cui si decide è quello che resta togliendo i colpi migliori.",
          "> **Il LOOP 1 lavora per alzare proprio quello.**"]
    open("PERCENTUALE.md", "w").write("\n".join(L))
    print("PERCENTUALE | " + " · ".join(f"{ch} {a['robusta']:+.0f}%" for ch, a, _ in dettagli), flush=True)


if __name__ == "__main__":
    main()
