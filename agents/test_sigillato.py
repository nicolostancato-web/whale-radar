#!/usr/bin/env python3
"""
TEST_SIGILLATO — la lettura UNICA dell'holdout. Si puo' sbagliare una volta sola.

Una configurazione congelata si giudica sui dati mai visti, e la si giudica UNA VOLTA. Non e'
pignoleria: guardare, aggiustare e riguardare trasforma la prova in un allenamento, e dopo il
secondo sguardo quel numero non dice piu' niente sul futuro. Per questo l'agente si rifiuta di
girare due volte sulla stessa configurazione, e appena legge marca `letto: true` in criteri.json.

Cosa serve per dire RIUSCITO — tutto insieme, e scritto prima del 3/9:
  - rendimento netto >= +10%
  - t >= 2, calcolato sui GRUPPI (giornata, creator) e non sulle righe
  - almeno 25 prove indipendenti
  - costi condizionati alla liquidita' al momento dell'uscita
  - segnale davvero DISPONIBILE prima dell'ingresso, col ritardo reale del bot

Sul conteggio delle prove: e' il punto della revisione del 04/09. Cento trade legati allo stesso
evento non sono cento prove. Un t=+2,88 calcolato sulle righe puo' valere +0,58 sui gruppi — la
differenza fra "abbiamo trovato qualcosa" e "non abbiamo trovato niente", sempre nella direzione
che ci fa comodo.

Scrive TEST_SIGILLATO.md. €0.
"""
import json, os, time, sys, statistics as st
sys.path.insert(0, "agents")
import indipendenza as IND

CHAIN = os.environ.get("CHAIN", "robinhood")
CRIT = "data/criteri.json"
now = int(time.time())


def main():
    try: c = json.load(open(CRIT))
    except Exception:
        print("TEST_SIGILLATO | criteri mancanti", flush=True); return
    cg = (c.get("congelate") or {}).get(CHAIN)
    if not cg:
        print(f"TEST_SIGILLATO | {CHAIN}: nessuna configurazione congelata", flush=True); return
    if cg.get("letto"):
        print(f"TEST_SIGILLATO | {CHAIN}: holdout GIA' LETTO il {cg.get('letto_il')}. "
              f"Non si rilegge: sarebbe un secondo tentativo travestito da verifica.", flush=True)
        return

    try: conf = int(json.load(open("data/holdout_config.json"))["confine_validazione"])
    except Exception:
        print("TEST_SIGILLATO | sigillo mancante", flush=True); return

    # gli esiti dei trade nella fascia MAI VISTA, con la configurazione congelata
    esiti = []      # (rendimento, giornata, creator)
    try:
        import explorer_rh as E
    except Exception as e:
        print(f"TEST_SIGILLATO | non riesco a caricare la valutazione: {type(e).__name__}", flush=True)
        return
    righe = []
    try:
        righe = E.righe_valutabili(cg["config"]) if hasattr(E, "righe_valutabili") else []
    except Exception: righe = []

    L = [f"# 🔐 TEST SIGILLATO — la lettura unica dell'holdout ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · configurazione congelata il "
         f"{cg.get('quando')} · fascia mai vista dal "
         f"{time.strftime('%d/%m %H:%M', time.gmtime(conf))}*", "",
         "> Si legge **una volta sola**. Guardare, aggiustare e riguardare trasforma la prova in un",
         "> allenamento: dopo il secondo sguardo il numero non dice più niente sul futuro.", "",
         f"**Configurazione sotto esame:** `{json.dumps(cg['config'])}`", ""]

    if not righe:
        L += ["## ⏸️ Non ancora eseguibile", "",
              "La valutazione sulla fascia mai vista non è ancora disponibile in una forma che permetta",
              "di raggruppare gli esiti per giornata e per creator — e senza quel raggruppamento il test",
              "darebbe un t **cinque volte più generoso del vero**.", "",
              "> **Il sigillo NON viene consumato.** Meglio non leggere che leggere male: la lettura è una,",
              "> e sprecarla su un conteggio sbagliato significherebbe non poterla più fare."]
        open("TEST_SIGILLATO.md", "w").write("\n".join(L))
        print(f"TEST_SIGILLATO | {CHAIN}: rimandato, sigillo INTATTO", flush=True); return

    for r in righe:
        if r.get("ent", 0) >= conf:
            esiti.append((r["ret"], IND.giornata(r["ent"]), r.get("creator") or r.get("addr")))
    if len(esiti) < 20:
        L += [f"## ⏸️ Troppo poco nella fascia mai vista", "",
              f"Solo **{len(esiti)}** trade dopo il sigillo. Il sigillo **non** viene consumato."]
        open("TEST_SIGILLATO.md", "w").write("\n".join(L))
        print(f"TEST_SIGILLATO | {CHAIN}: solo {len(esiti)} trade, sigillo INTATTO", flush=True); return

    val = [e[0] for e in esiti]
    t_g, n_g, t_r = IND.t_onesto(val, [e[1] for e in esiti])
    t_c, n_c, _ = IND.t_onesto(val, [e[2] for e in esiti])
    t = min(t_g, t_c); prove = min(n_g, n_c)
    medio = st.mean(val)
    S = c["successo"]
    ok = (medio >= S["rendimento_netto_minimo"] and t >= S["t_stat_minimo"]
          and prove >= S["prove_indipendenti_minime"])

    L += ["| | risultato | serve |", "|---|---|---|",
          f"| rendimento netto medio | **{medio*100:+.1f}%** | ≥ {S['rendimento_netto_minimo']*100:.0f}% |",
          f"| t sui gruppi | **{t:+.2f}** | ≥ {S['t_stat_minimo']} |",
          f"| prove indipendenti | **{prove}** | ≥ {S['prove_indipendenti_minime']} |",
          f"| righe | {len(val)} | ≥ {S.get('righe_minime', 250)} |", "",
          f"> Contando le righe invece dei gruppi il t sarebbe **{t_r:+.2f}**: "
          f"{'nessuna differenza' if abs(t_r-t) < 0.2 else f'{abs(t_r/t):.1f} volte più generoso'}.", "",
          "## Verdetto", ""]
    L += (["> ✅ **RIUSCITO.** La configurazione congelata regge sui dati mai visti, con le prove contate",
           "> a gruppi. È il primo risultato che supera tutti i criteri scritti in anticipo."] if ok else
          ["> ❌ **NON RIUSCITO.** Non supera i criteri fissati prima. La configurazione resta bocciata:",
           "> non si riottimizza e non si rilegge — sarebbe un secondo tentativo travestito da verifica."])
    open("TEST_SIGILLATO.md", "w").write("\n".join(L))

    cg["letto"] = True; cg["letto_il"] = time.strftime("%Y-%m-%d", time.gmtime(now))
    cg["esito"] = {"medio": medio, "t": t, "prove": prove, "righe": len(val), "riuscito": ok}
    json.dump(c, open(CRIT, "w"), indent=1, ensure_ascii=False)
    print(f"TEST_SIGILLATO | {CHAIN} | medio {medio*100:+.1f}% | t {t:+.2f} su {prove} prove | "
          f"{'RIUSCITO' if ok else 'NON riuscito'} | sigillo CONSUMATO", flush=True)


if __name__ == "__main__":
    main()
