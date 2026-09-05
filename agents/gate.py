#!/usr/bin/env python3
"""
GATE — il cancello del LOOP 2 (vedi STRATEGIA_LOOP.md, direttiva Nicolò 31/08).

Il live di una chain si accende SOLO se il LOOP 1 (la ricerca) ha una percentuale ROBUSTA sopra soglia su
abbastanza token. Andare live con il loop 1 negativo significa attuare una strategia che sappiamo gia' essere
perdente e poi stupirsi che perda: e' l'errore del 30-31/08 (demo aperti su Base -3% e Solana -21%).
"""
import json, os

SOGLIA_ROBUSTA = 40.0     # sotto questa percentuale robusta il live resta chiuso
MIN_TOKEN = 150           # e serve un campione abbastanza grande perche' il numero significhi qualcosa
MISURE_CONSECUTIVE = 3    # e deve reggere per PIU' misure di fila: prima bastava un'oscillazione fortunata
                          # sull'ultima riga per aprire il cancello
RICHIEDE_CASSAFORTE = True   # e deve aver superato il giudizio su dati mai visti (validatore.py)


def ultime(chain, n):
    """le ultime n misure della percentuale robusta, per capire se REGGE o è stata un'oscillazione."""
    out = []
    if chain == "robinhood" and os.path.exists("data/edge_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
            out = [(r.get("sel_no3"), r.get("n_tok", 0)) for r in recs[-n:]]
        except Exception: pass
    elif os.path.exists("data/multichain_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/multichain_history.jsonl") if l.strip()]
            recs = [r for r in recs if r.get("chain") == chain]
            out = [(r.get("robusta"), r.get("n", 0)) for r in recs[-n:]]
        except Exception: pass
    return [(v, k) for v, k in out if v is not None]


def validata_in_cassaforte(chain):
    """la proposta di questa chain ha superato il giudizio su dati MAI VISTI dalla ricerca?"""
    if not os.path.exists("data/proposte.json"): return None
    try:
        for p in json.load(open("data/proposte.json")).get("proposte", []):
            if p.get("chain") == chain and p.get("validazione"):
                return p["validazione"].get("robusta", -999) > 0
    except Exception: pass
    return None


def percentuale(chain):
    """la percentuale ROBUSTA piu' recente del LOOP 1 per questa chain (media tolti i 3 colpi migliori)."""
    if chain == "robinhood" and os.path.exists("data/edge_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
            if recs: return recs[-1].get("sel_no3"), recs[-1].get("n_tok", 0)
        except Exception: pass
    if os.path.exists("data/multichain_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/multichain_history.jsonl") if l.strip()]
            recs = [r for r in recs if r.get("chain") == chain]
            if recs: return recs[-1].get("robusta"), recs[-1].get("n", 0)
        except Exception: pass
    return None, 0


def aperto(chain):
    """(aperto?, motivo leggibile). Il live non apre posizioni nuove finche' il cancello e' chiuso."""
    rob, n = percentuale(chain)
    if rob is None:
        return False, "il LOOP 1 non ha ancora una misura per questa chain"
    if n < MIN_TOKEN:
        return False, f"campione troppo piccolo: {n} token (ne servono {MIN_TOKEN})"
    if rob < SOGLIA_ROBUSTA:
        return False, (f"il LOOP 1 e' a **{rob:+.0f}%** robusta, sotto la soglia di **+{SOGLIA_ROBUSTA:.0f}%**: "
                       f"andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare")
    # PERSISTENZA: non basta l'ultima misura. Prima bastava una riga fortunata per aprire il cancello.
    storia = ultime(chain, MISURE_CONSECUTIVE)
    if len(storia) < MISURE_CONSECUTIVE:
        return False, f"solo {len(storia)} misure disponibili: ne servono {MISURE_CONSECUTIVE} di fila sopra soglia"
    sotto = [v for v, _ in storia if v < SOGLIA_ROBUSTA]
    if sotto:
        return False, (f"non regge: nelle ultime {MISURE_CONSECUTIVE} misure e' sceso sotto soglia "
                       f"({min(sotto):+.0f}%). Serve costanza, non un colpo fortunato")
    # CASSAFORTE: e deve aver funzionato su dati che la ricerca non ha mai visto
    if RICHIEDE_CASSAFORTE:
        val = validata_in_cassaforte(chain)
        if val is None:
            return False, "manca il giudizio su dati mai visti (validatore.py): senza quello non si apre"
        if not val:
            return False, ("**bocciata in cassaforte**: sui token che la ricerca non ha mai visto la strategia "
                           "non tiene. Era rumore, non un edge")
    return True, (f"il LOOP 1 e' a {rob:+.0f}% robusta su {n} token, regge da {MISURE_CONSECUTIVE} misure "
                  f"e ha superato la prova su dati mai visti: si puo' andare live")
