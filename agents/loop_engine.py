#!/usr/bin/env python3
"""
LOOP_ENGINE — il SEGRETARIO DEI MEETING + l'ARCHITETTO che verifica che ogni loop giri davvero.

L'idea (Nicolo, 30/08): finora avevamo gente che lavora ma NESSUNO che ogni ora si siede e chiede
"ragazzi, come siamo messi verso il goal?". Cosi' Base e' rimasto fermo 4 giorni senza che nessuno alzasse
la mano. Da qui in poi, a ogni ciclo del motore si tiene UN MEETING PER GOAL:
  1. si misura dove siamo ORA (numero, non opinione)
  2. si confronta col meeting precedente: l'ago si e' mosso?
  3. se e' fermo, qualcuno ALZA LA MANO e si esegue la riparazione nota
  4. se e' fermo da troppo tempo, non si insiste col retry: si SALE LA SCALA (cambio di approccio)
  5. si scrive il verbale, cosi' al meeting dopo si riparte da li'

L'ARCHITETTO (ultima sezione): controlla che ogni loop abbia avuto il suo meeting di recente. Un loop che
smette di riunirsi e' esattamente il guasto che ci e' costato 4 giorni — quindi qui viene detto per nome.
Registro dei loop in data/loops.json · memoria in data/loops_history.jsonl · cruscotto in LOOPS.md. €0.
"""
import json, os, glob, gzip, time, subprocess, sys

sys.path.insert(0, "agents")
import gate
now = int(time.time())
REG = "data/loops.json"
HIST = "data/loops_history.jsonl"
CICLO_H = 0.5                      # un ciclo del motore ~30 min


def carica_storico():
    """ultimo verbale per ogni loop + quante volte di fila e' rimasto fermo."""
    ultimo, righe = {}, []
    if os.path.exists(HIST):
        try:
            righe = [json.loads(l) for l in open(HIST) if l.strip()]
        except Exception: righe = []
    for r in righe:
        ultimo[r["id"]] = r
    return ultimo, righe


# ---------------------------------------------------------------- SENSORI (uno per tipo di loop)
def misura_accumulo(loop):
    ch = loop["chain"]; b = f"data/multichain/{ch}"
    pulse = len(glob.glob(f"{b}/pulse/*.jsonl.gz"))
    cand = len(glob.glob(f"{b}/candles/*.jsonl.gz"))
    pool = 0
    if os.path.exists(f"{b}/pools.json"):
        try: pool = len(json.load(open(f"{b}/pools.json")))
        except Exception: pass
    return {"valore": pulse + cand, "pulse": pulse, "candele": cand, "pool": pool,
            "frase": f"{pulse + cand} token con dati ({pulse} osservati dal vivo, {cand} con storico) su {pool} pool noti"}


def misura_percentuale(loop):
    """la percentuale ROBUSTA (senza i 3 colpi migliori): l'unico numero che conta."""
    ch = loop["chain"]
    rob = med = None; n = 0
    if ch == "robinhood" and os.path.exists("data/edge_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
            if recs:
                r = recs[-1]; med = r.get("sel_port"); rob = r.get("sel_no3"); n = r.get("n_tok", 0)
        except Exception: pass
    elif os.path.exists("data/multichain_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/multichain_history.jsonl") if l.strip()]
            recs = [r for r in recs if r.get("chain") == ch]
            if recs:
                r = recs[-1]; med = r.get("media"); rob = r.get("robusta"); n = r.get("n", 0)
        except Exception: pass
    if rob is None:
        return {"valore": None, "frase": "nessuna misura ancora (il cervello non ha scritto lo storico)"}
    return {"valore": round(rob, 1), "media": med, "robusta": rob, "n": n,
            "frase": f"robusta {rob:+.0f}% (media {med:+.0f}%) su {n} token"}


MIN_TRADE_PER_GIUDICARE = 20   # PAZIENZA: sotto i 20 trade chiusi un live non si giudica. Due trade negativi
                               # non sono un segnale — e' rumore. (direttiva Nicolò 31/08, STRATEGIA_LOOP.md)


def misura_demo(loop):
    """equity + ETA al goal al ritmo attuale: il numero che nessuno calcolava."""
    p = loop["stato"]
    if not os.path.exists(p):
        return {"valore": None, "frase": "conto non ancora aperto"}
    try: st = json.load(open(p))
    except Exception: return {"valore": None, "frase": "stato illeggibile"}
    eq = st.get("bal", 0) + sum(x.get("size", 0) for x in st.get("open", []))
    giorni = max(0.1, (now - st.get("start_ts", now)) / 86400)
    guadagno_giorno = (eq - 100.0) / giorni
    goal = loop.get("goal_eur", 3000)
    if guadagno_giorno <= 0:
        eta = None; eta_txt = "MAI a questo ritmo"
    else:
        eta = (goal - eq) / guadagno_giorno
        eta_txt = f"~{eta/365:.1f} anni" if eta > 400 else f"~{eta:.0f} giorni"
    trade = st.get("closed", 0) + len(st.get("open", []))
    aperto, motivo = gate.aperto(loop["chain"])
    if not aperto:
        return {"valore": round(eq, 2), "equity": round(eq, 2), "trade": trade, "sospeso": True,
                "aperte": len(st.get("open", [])), "eta_giorni": None,
                "frase": f"🔴 SOSPESO dal cancello — {motivo}"}
    if trade < MIN_TRADE_PER_GIUDICARE:
        return {"valore": round(eq, 2), "equity": round(eq, 2), "trade": trade, "giovane": True,
                "aperte": len(st.get("open", [])), "eta_giorni": None,
                "frase": f"€{eq:.0f} · {trade}/{MIN_TRADE_PER_GIUDICARE} trade: troppo presto per giudicare (pazienza)"}
    return {"valore": round(eq, 2), "equity": round(eq, 2), "trade": trade,
            "aperte": len(st.get("open", [])), "eta_giorni": round(eta) if eta else None,
            "frase": f"€{eq:.0f} verso €{goal} · {trade} trade in {giorni:.1f} giorni · arrivo: {eta_txt}"}


SENSORI = {"accumulo": misura_accumulo, "percentuale": misura_percentuale, "demo": misura_demo}


RIMEDI = "data/loops_rimedi.json"


def carica_rimedi():
    if os.path.exists(RIMEDI):
        try: return json.load(open(RIMEDI))
        except Exception: pass
    return {}


def ripara(script, motivo):
    try:
        # 45s e non 240: una riparazione lunga faceva scadere l'INTERO loop_engine (ucciso a 180s dal
        # motore) e il verbale non veniva scritto affatto. Meglio una riparazione parziale che nessun verbale.
        subprocess.run(f"python agents/{script}", shell=True, timeout=45,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"rilanciato **{script}** ({motivo})"
    except Exception:
        return f"tentata riparazione con {script}, fallita"


def scegli_rimedio(lid, fix, rimedi):
    """Prende il primo rimedio non ancora bocciato. Un rimedio che ha fallito 3 volte di fila e' INUTILE per
    questo loop: si smette di riprovarlo. E' l'anti-ripetizione — senza, il loop rilancia lo stesso script
    all'infinito convinto di stare lavorando."""
    for s in fix:
        k = f"{lid}|{s}"
        if rimedi.get(k, {}).get("falliti", 0) < 3:
            return s
    return None


def main():
    if not os.path.exists(REG):
        print("LOOP_ENGINE | manca data/loops.json", flush=True); return
    reg = json.load(open(REG))
    ultimo, righe = carica_storico()
    rimedi = carica_rimedi()
    verbali = []; nuovi = []; azioni = []
    MAX_RIPARAZIONI = 2      # le altre aspettano il prossimo meeting: il verbale viene prima di tutto
    fatte = 0
    # bandiera rossa dell'auditor: se un numero non si spiega, i loop NON salgono di scala
    rossa = False
    if os.path.exists("data/audit_flags.json"):
        try: rossa = json.load(open("data/audit_flags.json")).get("critiche", 0) > 0
        except Exception: pass

    for loop in reg["loops"]:
        lid = loop["id"]
        m = SENSORI[loop["tipo"]](loop)
        prec = ultimo.get(lid)
        val, pval = m["valore"], (prec or {}).get("valore")

        # --- l'ago si e' mosso dall'ultimo meeting? ---
        # Si giudica SOLO se dall'ultimo meeting e' passato tempo vero: due riunioni back-to-back non
        # provano nulla, e farebbero partire riparazioni inutili.
        troppo_presto = bool(prec) and now - prec["ts"] < 1200
        if val is None: mosso = None
        elif pval is None: mosso = True
        else: mosso = val > pval
        if troppo_presto:
            fermo_da = (prec or {}).get("fermo_da", 0)
        else:
            fermo_da = 0 if mosso else (prec or {}).get("fermo_da", 0) + 1

        # --- CHECK -> FIX -> AVANTI ---
        soglia = loop.get("fermo_dopo_cicli", 6)
        azione = ""; rec_rimedio = None
        if m.get("sospeso"):
            azione = "⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale"
            fermo_da = 0
        elif m.get("giovane"):
            azione = "⏳ pazienza: si raccolgono trade, non si tocca niente"
            fermo_da = 0
        elif val is None:
            azione = "in attesa della prima misura"
        elif troppo_presto:
            azione = "meeting ravvicinato: si giudica al prossimo"
        elif mosso:
            azione = "avanti cosi'"
        elif fermo_da >= soglia and rossa:
            azione = "⛔ cambio di approccio SOSPESO: l'auditor ha una bandiera rossa aperta (vedi AUDIT.md)"
        elif fermo_da >= soglia:
            # fermo da troppo: NON si insiste col retry, si sale la scala
            scala = loop.get("escalation", [])
            aperte = {r.get("escalation_aperta") for r in righe if r.get("id") == lid}
            prossima = next((e for e in scala if e not in aperte), None)
            if prossima:
                azione = f"🔺 SCALA: fermo da {fermo_da*CICLO_H:.0f}h → cambiamo approccio"
                azioni.append((lid, loop["domanda"], prossima, fermo_da * CICLO_H))
                nuovi.append({"escalation_aperta": prossima})
            else:
                azione = f"🚨 fermo da {fermo_da*CICLO_H:.0f}h e la scala e' finita: serve una decisione umana"
        else:
            # prima di tutto: il rimedio provato al meeting scorso ha funzionato?
            provato = (prec or {}).get("rimedio")
            if provato:
                k = f"{lid}|{provato}"
                voce = rimedi.setdefault(k, {"ok": 0, "falliti": 0})
                if mosso: voce["ok"] += 1
                else: voce["falliti"] += 1
            fix = loop.get("fix", [])
            scelto = scegli_rimedio(lid, fix, rimedi) if fix else None
            if scelto and fatte < MAX_RIPARAZIONI:
                azione = "✋ mano alzata: " + ripara(scelto, f"fermo da {fermo_da} meeting")
                rec_rimedio = scelto; fatte += 1
            elif scelto:
                azione = f"✋ mano alzata: riparazione rimandata al prossimo meeting (già {fatte} in questo giro)"
                rec_rimedio = None
            elif fix:
                azione = (f"✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte "
                          f"({', '.join(fix)}) → non li ripetiamo, serve cambiare approccio")
                rec_rimedio = None
            else:
                azione = f"✋ mano alzata: fermo da {fermo_da} meeting, nessuna riparazione automatica nota"
                rec_rimedio = None

        rec = {"id": lid, "ts": now, "valore": val, "fermo_da": fermo_da, "azione": azione[:120]}
        if rec_rimedio: rec["rimedio"] = rec_rimedio
        if nuovi and "escalation_aperta" in nuovi[-1] and azioni and azioni[-1][0] == lid:
            rec["escalation_aperta"] = nuovi[-1]["escalation_aperta"]
        verbali.append((loop, m, rec, prec))
        with open(HIST, "a") as fo: fo.write(json.dumps(rec) + "\n")

    json.dump(rimedi, open(RIMEDI, "w"))

    # ---------------------------------------------------------------- L'ARCHITETTO
    # controlla che ogni loop si sia RIUNITO di recente: un loop che smette di riunirsi e' il guasto
    # che ci e' costato 4 giorni su Base. Qui viene detto per nome.
    fermi = []
    for loop, m, rec, prec in verbali:
        if prec and now - prec["ts"] > 3 * 3600:
            fermi.append((loop["id"], (now - prec["ts"]) / 3600))
    salute = "🟢 tutti i loop si stanno riunendo" if not fermi else \
             "🔴 loop che avevano smesso di riunirsi: " + ", ".join(f"{i} ({h:.0f}h)" for i, h in fermi)

    # ---------------------------------------------------------------- VERBALE
    L = ["# 🔁 LOOPS — i meeting del sistema",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · un meeting per goal, a ogni ciclo (~30 min)*", "",
         f"## Architetto: {salute}", "",
         "| loop | la domanda | dove siamo | ago | cosa si fa |", "|---|---|---|---|---|"]
    for loop, m, rec, prec in verbali:
        if rec["valore"] is None: ago = "—"
        elif rec["fermo_da"] == 0: ago = "📈 si muove"
        else:
            ore = rec["fermo_da"] * CICLO_H
            ago = f"⏸ fermo da {ore:.0f}h" if ore >= 1 else "⏸ fermo dall'ultimo meeting"
        L.append(f"| `{loop['id']}` | {loop['domanda']} | {m['frase']} | {ago} | {rec['azione']} |")
    L += [""]
    if azioni:
        L += ["## 🔺 Cambi di approccio aperti (serve implementarli)", ""]
        for lid, dom, prossima, ore in azioni:
            L.append(f"- **{lid}** — fermo da {ore:.0f}h su *\"{dom}\"* → prossima mossa: **{prossima}**")
        L += [""]
    # priorita': chi e' fermo da piu' tempo pesa di piu', e un demo che non arriva MAI al goal viene prima
    punteggi = []
    for loop, m, rec, prec in verbali:
        p = rec["fermo_da"] * 2
        if loop["tipo"] == "demo":
            if m.get("sospeso") or m.get("giovane"): p = 0        # non e' un problema: e' la regola / la pazienza
            else: p += 10 if m.get("eta_giorni") is None else (5 if m["eta_giorni"] > 365 else 0)
        if loop["tipo"] == "percentuale" and rec["valore"] is not None:
            p += 8 if rec["valore"] < 0 else (4 if rec["valore"] < 40 else 0)   # il vero lavoro e' qui
        if rec["valore"] is None: p += 3
        punteggi.append((p, loop, m, rec))
    punteggi.sort(key=lambda x: -x[0])
    top = [x for x in punteggi if x[0] > 0][:3]
    if top:
        L += ["## 🎯 Le 3 cose che contano adesso", ""]
        for i, (p, loop, m, rec) in enumerate(top, 1):
            perche = ("non arriva al goal a questo ritmo" if loop["tipo"] == "demo" and m.get("eta_giorni") is None
                      else f"fermo da {rec['fermo_da']*CICLO_H:.0f}h" if rec["fermo_da"]
                      else "senza misura")
            L.append(f"{i}. **{loop['id']}** — {perche}. {m['frase']}")
        L += [""]
    if rossa:
        L += ["## ⛔ Bandiera rossa dell'auditor", "",
              "Un numero non si spiega (vedi `AUDIT.md`). Finche' non e' chiarito i loop **non salgono di scala**:",
              "prima si capisce se stiamo barando, poi si va avanti.", ""]
    L += ["> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.",
          "> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).",
          "> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md."]
    open("LOOPS.md", "w").write("\n".join(L))
    print(f"LOOP_ENGINE | {len(verbali)} meeting | {salute[:40]} | {len(azioni)} cambi di approccio", flush=True)


if __name__ == "__main__":
    main()
