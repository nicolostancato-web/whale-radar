#!/usr/bin/env python3
"""
DISPONIBILITA — il segnale era davvero utilizzabile in quel momento?

Ultimo punto della revisione esterna del 04/09, e l'ultimo modo in cui un risultato puo' essere
falso senza che nessun raggruppamento lo salvi:

    «Per ogni trade bisogna verificare che tutti i dati fossero disponibili PRIMA dell'ingresso, e
     aggiungere il ritardo reale del bot.»

Sono due cose diverse e servono due prove diverse.

PROVA 1 — IL FUTURO NON DEVE CAMBIARE IL PASSATO.
Le feature dichiarano di usare solo il passato. Ma leggere il codice non basta: si legge quello
che si crede di aver scritto. Qui si calcolano le feature a un certo istante DUE volte — una con
tutti i dati che abbiamo oggi, una con i soli dati fino a quell'istante — e si controlla che
vengano identiche. Se un numero cambia, quella feature stava guardando il futuro, punto.

PROVA 2 — QUANTO TARDI ARRIVA IL DATO A NOI.
Anche una feature onesta e' inutilizzabile se il dato lo riceviamo mezz'ora dopo: un bot vero non
puo' agire su una candela che non ha ancora scaricato. Qui si misura la distanza vera fra il
momento a cui una candela si riferisce e il momento in cui l'abbiamo effettivamente in casa.
Quel ritardo va aggiunto all'entrata, altrimenti stiamo comprando col senno di poi di mezz'ora.

Scrive DISPONIBILITA.md + data/ritardo_reale.json. Sola lettura. €0.
"""
import json, os, glob, time, gzip, sys, statistics as st
sys.path.insert(0, "agents")

now = int(time.time())
CHAINS = ("base", "bsc", "solana", "robinhood")


def ritardo_osservazione(chain, max_file=400):
    """quanto tempo passa fra l'ora a cui una candela si riferisce e l'ora in cui l'abbiamo scaricata."""
    ck = {}
    p = f"data/multichain/{chain}/ckpt.json"
    if os.path.exists(p):
        try: ck = json.load(open(p)).get("last_fetch", {})
        except Exception: pass
    if not ck: return []
    ritardi = []
    for f in glob.glob(f"data/multichain/{chain}/candles/*.jsonl.gz")[:max_file]:
        addr = os.path.basename(f).replace(".jsonl.gz", "")
        preso = ck.get(addr)
        if not preso: continue
        try:
            ultimo = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): ultimo = int(d["ts"])
            if ultimo and preso > ultimo: ritardi.append(preso - ultimo)
        except Exception: pass
    return ritardi


def ritardo_pipeline(ritardi):
    """Il ritardo VERO della nostra catena, ripulito da un errore di misura mio (04/09).

    La prima versione prendeva la mediana della distanza fra l'ultima candela e il momento in cui
    l'abbiamo scaricata, e usciva 58 ore. Non era il nostro ritardo: era che gran parte dei token e'
    MORTA, e la loro ultima candela e' vecchia perche' hanno smesso di essere scambiati — non perche'
    noi siamo lenti. Misurando cosi', la morte del token diventava un difetto nostro.
    Il ritardo della catena si legge sui casi in cui il token era ancora vivo quando l'abbiamo preso,
    cioe' nella CODA BASSA della distribuzione: li' la distanza e' dovuta a noi, non al mercato."""
    if len(ritardi) < 20: return None
    r = sorted(ritardi)
    return {"tipico_s": r[int(len(r) * .10)], "buono_s": r[int(len(r) * .05)],
            "lento_s": r[int(len(r) * .25)], "n": len(r)}


def prova_futuro():
    """le feature calcolate a un istante devono venire IDENTICHE con e senza i dati successivi."""
    try:
        import learner as L
    except Exception as e:
        return None, f"non riesco a caricare il calcolo delle feature ({type(e).__name__})"
    try:
        cand, flow, fbp, wl, fts = L.load_data()
    except Exception as e:
        return None, f"dati non disponibili ({type(e).__name__})"
    pool = [p for p in cand if len(cand[p]) >= 12][:60]
    if not pool: return None, "nessun token con abbastanza storia"
    diverse = []; provati = 0
    for p in pool:
        ks = sorted(cand[p])
        ent = ks[len(ks) // 3]                       # un istante a un terzo della vita del token
        pieno = L.features_at_entry(p, ent, cand, flow, fbp, wl, fts)
        if pieno is None: continue
        # ora gli stessi dati, TAGLIATI: come se oggi fosse quell'istante e il resto non esistesse
        cand_t = {q: {t: v for t, v in cand[q].items() if t <= ent} for q in cand}
        flow_t = {q: {h: v for h, v in flow[q].items() if h <= ent} for q in flow}
        wl_t = {w: [l for l in ls if l <= ent] for w, ls in wl.items()}
        fbp_t = {q: v for q, v in fbp.items() if fts.get(q, 0) <= ent}
        tagl = L.features_at_entry(p, ent, cand_t, flow_t, fbp_t, wl_t, fts)
        provati += 1
        if tagl is None:
            diverse.append((p, "col solo passato la feature non si calcola affatto")); continue
        for i, (a, b) in enumerate(zip(pieno, tagl)):
            if abs(a - b) > max(1e-9, abs(a) * 1e-6):
                diverse.append((p, f"feature #{i}: {a:.4f} col futuro, {b:.4f} senza")); break
    return (provati, diverse), None


def main():
    L_ = ["# ⏱️ IL SEGNALE ERA UTILIZZABILE IN QUEL MOMENTO?",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · €0*", "",
          "> Un risultato può essere falso in due modi che nessun raggruppamento salva: se una feature",
          "> guarda il futuro, o se il dato ci arriva **dopo** il momento in cui avremmo dovuto agire.",
          "> Sono due difetti diversi e servono due prove diverse.", ""]

    # --- prova 1
    ris, err = prova_futuro()
    L_ += ["## Prova 1 — il futuro cambia il passato?", "",
           "*Le feature si calcolano due volte allo stesso istante: una con tutti i dati di oggi, una",
           "con i soli dati fino a quell'istante. Devono venire identiche. Leggere il codice non basta:",
           "si legge quello che si crede di aver scritto.*", ""]
    esito1 = None
    if err:
        L_ += [f"> ⏸️ Non eseguibile: {err}"]
    else:
        provati, diverse = ris
        esito1 = not diverse
        if diverse:
            L_ += [f"> ❌ **{len(diverse)} token su {provati} cambiano** quando si toglie il futuro.",
                   "> Quelle feature stanno guardando avanti, e ogni risultato che le usa è falso.", ""]
            L_ += [f"- `{p[:12]}…` — {m}" for p, m in diverse[:5]]
        else:
            L_ += [f"> ✅ **Nessuna differenza su {provati} token.** Le feature usano solo il passato:",
                   "> non è una dichiarazione del codice, è una verifica sui numeri."]

    # --- prova 2
    L_ += ["", "## Prova 2 — quanto tardi arriva il dato a noi", "",
           "*Un bot vero non può agire su una candela che non ha ancora scaricato. Questo ritardo va",
           "aggiunto all'entrata: senza, stiamo comprando col senno di poi.*", "",
           "*Nota di metodo: si legge sulla coda bassa della distribuzione. La mediana direbbe 58 ore,",
           "ma quelle sono i token MORTI — la loro ultima candela è vecchia perché hanno smesso di essere",
           "scambiati, non perché siamo lenti noi. Misurando così, la morte del token diventerebbe un",
           "nostro difetto.*", "",
           "| chain | ritardo tipico | quando andiamo lenti | misure |", "|---|---|---|---|"]
    ritardi = {}
    for ch in CHAINS:
        d = ritardo_pipeline(ritardo_osservazione(ch))
        if not d: continue
        ritardi[ch] = d
        L_.append(f"| {ch} | **{d['tipico_s']/60:.0f} min** | {d['lento_s']/60:.0f} min | {d['n']} |")
    if ritardi:
        peggio = max(v["tipico_s"] for v in ritardi.values())
        L_ += ["", f"> Il ritardo tipico peggiore è di **{peggio/60:.0f} minuti**. Su un memecoin che si",
               "> muove del 5% al minuto, entrare mezz'ora dopo non è la stessa strategia: è un'altra.", ""]
        L_ += ["> ⚠️ **Questo ritardo NON è ancora applicato nei backtest**, e la conseguenza è più grave",
               "> di quanto sembri.", "",
               "> Le nostre strategie entrano 3 o 6 ore dopo il listing. Se i dati ci arrivano con 3-7 ore",
               "> di ritardo, un bot vero a quell'ora avrebbe in mano **quasi solo i dati del momento del",
               "> listing**: entrerebbe alla stessa ora, ma decidendo su informazioni molto più povere.",
               "> Non è la stessa strategia con un handicap — è una strategia diversa.", "",
               "> Finché non lo applichiamo, ogni risultato va letto sapendo che stiamo decidendo con",
               "> informazioni che al momento dell'ingresso non avremmo avuto.", ""]
    else:
        L_ += ["", "*Non abbastanza dati per misurare il ritardo.*", ""]

    json.dump({"ts": now, "ritardi": ritardi, "feature_pulite": esito1},
              open("data/ritardo_reale.json", "w"))
    open("DISPONIBILITA.md", "w").write("\n".join(L_))
    print(f"DISPONIBILITA | feature pulite: {esito1} | ritardi: "
          f"{ {k: round(v['tipico_s']/60) for k, v in ritardi.items()} }", flush=True)


if __name__ == "__main__":
    main()
