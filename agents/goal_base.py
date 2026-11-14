#!/usr/bin/env python3
"""
GOAL_BASE — il GUARDIANO del goal "aprire trade su Base ed essere in profitto".
Nasce dal 30/08: il demo Base era a 0 trade da 4 giorni e per capire perche' e' servito uno scavo a mano di ore
(erano TRE anelli rotti in fila). Mai piu': la catena che porta al trade viene misurata a OGNI ciclo, stadio per
stadio, e il primo stadio a zero viene indicato per nome. Se il forward si ferma, il sistema dice DOVE si e' rotto.
Non si limita a guardare: se un anello e' rotto e ha una RIPARAZIONE nota, la esegue subito (rilancia il reparto
che manca) e lo scrive. Tiene lo storico in data/goal_base_history.jsonl per vedere se l'ago si muove: se lo
stesso anello resta rotto per ore nonostante le riparazioni, alza un ALLARME (li' serve una testa, non un retry).
Scrive GOAL_BASE.md. €0.
"""
import gzip, json, glob, os, time, sys, datetime, subprocess
sys.path.insert(0, "agents")
import multichain_brain as B

CHAIN = "base"
EH = 2                      # la strategia Base entra a +2h dalla nascita
now = int(time.time())
S = json.load(open("data/strategy_base.json")) if os.path.exists("data/strategy_base.json") else {}
EH = S.get("entry_h", EH)


def age_h(p):
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    return (now - p.get("seen", now)) / 3600


def main():
    base = f"data/multichain/{CHAIN}"
    pools = json.load(open(f"{base}/pools.json")) if os.path.exists(f"{base}/pools.json") else {}

    # --- STADIO 1: conosciamo token appena nati? (se no: la scoperta e' ferma) ---
    freschi = sum(1 for p in pools.values() if age_h(p) <= 4)

    # --- STADIO 2: li stiamo guardando? (se no: il pulse non gira) ---
    pf = glob.glob(f"{base}/pulse/*.jsonl.gz")
    n_pulse = len(pf)

    # --- STADIO 3: quanti hanno abbastanza punti E sono stati presi IN TEMPO? ---
    # (preso in tempo = il primo campione arriva prima della finestra d'entrata: altrimenti il trade e' finto)
    pronti = tardi = pochi = 0
    ultimo_punto = 0
    for f in pf:
        try:
            cs = []; nato = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("t0"): nato = int(d["t0"])
                if d.get("cl"): cs.append(int(d["ts"]))
            if not cs: continue
            cs.sort(); ultimo_punto = max(ultimo_punto, cs[-1])
            t0 = nato or cs[0]
            if len(cs) < B.MIN_CANDLES: pochi += 1
            elif cs[0] > t0 + EH * 3600: tardi += 1
            else: pronti += 1
        except Exception: pass

    # --- STADIO 4-5: il demo ha comprato? e come va? ---
    st = json.load(open("data/demo_live_base_state.json")) if os.path.exists("data/demo_live_base_state.json") else {}
    aperte = len(st.get("open", [])); chiuse = st.get("closed", 0)
    bal = st.get("bal", 100.0); equity = bal + sum(x.get("size", 0) for x in st.get("open", []))
    visti = len(st.get("entered", []))
    giorni = (now - st.get("start_ts", now)) / 86400

    # --- l'anello rotto = il primo stadio a zero ---
    def ripara(cmd, quando):
        """riparazione nota: rilancia il reparto mancante. Se non basta, il prossimo ciclo lo ridira'."""
        try:
            subprocess.run(f"python agents/{cmd}", shell=True, timeout=220,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"✅ riparazione tentata: rilanciato **{cmd}** ({quando})"
        except Exception:
            return f"⚠️ riparazione fallita: {cmd}"

    catena = [("1. token nuovi scoperti", freschi, "la scoperta pool e' ferma → guarda multichain_collector"),
              ("2. token sotto osservazione", n_pulse, "il pulse non scrive → guarda agents/pulse.py nei log del motore"),
              ("3. token pronti da valutare", pronti, f"nessuno ha ancora {B.MIN_CANDLES} punti presi in tempo → servono ~{B.MIN_CANDLES//2}h di motore"),
              ("4. token valutati dal modello", visti, "il demo non li vede → controlla serie_files() e la finestra d'entrata"),
              ("5. trade aperti o chiusi", aperte + chiuse, "il modello li vede ma li scarta tutti → soglia P(win) troppo alta o strategia da rivedere")]
    rotto = next((c for c in catena if c[1] == 0), None)

    # --- STORICO: l'ago si muove? (serve a distinguere "sta maturando" da "e' inchiodato") ---
    hf = "data/goal_base_history.jsonl"
    prima = None
    if os.path.exists(hf):
        try:
            righe = [json.loads(l) for l in open(hf) if l.strip()]
            if righe: prima = righe[-1]
        except Exception: pass
    ora = {"ts": now, "freschi": freschi, "pulse": n_pulse, "pronti": pronti, "pochi": pochi,
           "visti": visti, "trade": aperte + chiuse, "equity": round(equity, 2)}
    with open(hf, "a") as fo: fo.write(json.dumps(ora) + "\n")

    # --- CHECK → FIX → AVANTI: se e' rotto e sappiamo come, si ripara SUBITO ---
    azione = ""
    if rotto:
        stadio = rotto[0][0]
        # "fermo" solo se e' passato davvero del tempo dall'ultimo controllo: due run ravvicinati non provano nulla
        fermo = (prima and now - prima.get("ts", now) > 1200
                 and prima.get("pulse") == n_pulse and prima.get("pochi") == pochi)
        if stadio == "1":
            azione = ripara("multichain_collector.py", "la scoperta pool era ferma")
        elif stadio == "2" or (stadio == "3" and fermo):
            azione = ripara("pulse.py", "nessun campione nuovo dal ciclo scorso")
        elif stadio == "4":
            azione = ripara("demo_live_base.py", "il demo non aveva ancora valutato i token pronti")
        elif stadio == "3":
            azione = "⏳ nessuna riparazione serve: i token stanno maturando (servono ~2h di campioni)"
        elif stadio == "5":
            azione = ("🧠 il modello vede i token e li scarta TUTTI: non e' un guasto, e' una scelta di soglia. "
                      "Va decisa da noi (strategy_base.json), non aggiustata di nascosto da un retry.")

    # allarme se lo stesso anello resiste da ore
    allarme = ""
    if rotto and os.path.exists(hf):
        try:
            righe = [json.loads(l) for l in open(hf) if l.strip()][-8:]
            if len(righe) >= 8 and all(r.get("trade", 0) == 0 for r in righe) and rotto[0][0] in ("1", "2", "4", "5"):
                allarme = ("🚨 **ALLARME**: stesso anello rotto da 8 cicli (~4h) nonostante le riparazioni. "
                           "Qui serve una diagnosi, non un altro retry.")
        except Exception: pass

    fresco_min = (now - ultimo_punto) / 60 if ultimo_punto else 999
    stato = ("🟢 IN PROFITTO" if equity > 100 and chiuse else
             "🟡 OPERATIVO (trade aperti, esito da vedere)" if aperte else
             "🔴 FERMO: " + rotto[0] if rotto else "🟡 IN ATTESA del primo trade")

    L = [f"# 🎯 GOAL BASE — aprire trade ed essere in profitto",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · conto attivo da {giorni:.1f} giorni*", "",
         f"## Stato: {stato}", "",
         f"**Saldo: €{equity:.2f}** ({equity-100:+.2f} vs partenza) · {aperte} posizioni aperte · {chiuse} trade chiusi", "",
         "## La catena che porta al trade", "",
         "| stadio | quanti | |", "|---|---|---|"]
    for nome, n, _ in catena:
        L.append(f"| {nome} | **{n}** | {'✅' if n else '❌ ROTTO QUI'} |")
    L += ["", f"- token con pochi punti (stanno maturando): **{pochi}**",
          f"- token presi troppo tardi (finestra +{EH}h persa, giustamente scartati): **{tardi}**",
          f"- ultimo campione raccolto: **{fresco_min:.0f} minuti fa** " +
          ("✅" if fresco_min < 90 else "⚠️ il pulse potrebbe essersi fermato"), ""]
    if rotto:
        L += [f"## ⚠️ Anello rotto: {rotto[0]}", f"> {rotto[2]}", ""]
        if azione: L += [f"**Riparazione automatica:** {azione}", ""]
        if allarme: L += [allarme, ""]
    else:
        L += ["## ✅ Catena integra: il forward gira da solo", ""]
    if prima:
        L += ["## L'ago si muove?", "", "| | ciclo scorso | ora |", "|---|---|---|",
              f"| token osservati | {prima.get('pulse','-')} | {n_pulse} |",
              f"| pronti da valutare | {prima.get('pronti','-')} | {pronti} |",
              f"| trade | {prima.get('trade','-')} | {aperte + chiuse} |", ""]
    L += ["> Questo file si riscrive a ogni ciclo del motore. Se il forward si ferma, qui c'e' scritto DOVE.",
          "> Goal: trade aperti su Base e saldo sopra €100 guadagnato in avanti (nessuno storico, nessuna illusione)."]
    open("GOAL_BASE.md", "w").write("\n".join(L))
    print(f"GOAL_BASE | {stato} | catena: " + " ".join(str(c[1]) for c in catena) +
          (f" | {azione[:60]}" if azione else ""), flush=True)


if __name__ == "__main__":
    main()
