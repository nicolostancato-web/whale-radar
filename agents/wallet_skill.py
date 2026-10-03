#!/usr/bin/env python3
"""
WALLET_SKILL — l'ULTIMO test sulla wallet intelligence, fatto come si deve.

Il test precedente (lag_wallet) chiudeva il copy-trading, e la consulenza esterna ha confermato la
chiusura "ma per il motivo sbagliato": avevamo bocciato UNA definizione di bravura, non l'idea.
Quella definizione — "ha azzeccato 2 token >= 2x" — non misura bravura: su decine di migliaia di
wallet, moltissimi ne azzeccano due di fila per puro caso. Stavamo scambiando la sopravvivenza
statistica per talento.

Qui la bravura e' definita come chiede la consulenza:
  - non "quanti ne ha azzeccati", ma QUANTO HA FATTO MEGLIO dei token comparabili disponibili
    negli stessi momenti (excess return vs controlli appaiati per eta' e liquidita')
  - con SHRINKAGE: chi ha pochi casi viene schiacciato verso lo zero. Tre successi su tre non
    valgono piu' di settanta su centoventi — valgono MENO, perche' potrebbero essere fortuna.
  - su UNITA' INDIPENDENTI: prima decisione di ogni entita' su ogni token, con i wallet della
    stessa mano fusi in un cluster. Lo stesso wallet che ricompra non e' una nuova prova.
  - a ORIZZONTI MULTIPLI fissati prima (5m/30m/2h/6h/24h): un'informazione che vale mezz'ora
    risultava morta solo perche' guardavamo a 24 ore.
  - con PLACEBO all'indietro: se il "segnale" spiega anche il passato, non e' un segnale.

E soprattutto: **prima si guarda il LORDO.** Se dopo l'acquisto di un wallet selezionato non c'e'
extra-rendimento nemmeno lordo, a nessun orizzonte, il problema non e' lo slippage e non e'
l'uscita: quel wallet non sa niente. I costi si discutono solo dopo, e solo se c'e' qualcosa.

Criterio di morte, fissato ADESSO, prima di vedere i numeri (scritto qui perche' non si possa
cambiare dopo): se il gruppo dei wallet bravi non produce excess return positivo contro i
controlli appaiati, con direzione coerente su almeno DUE orizzonti, in fascia di validazione,
la wallet intelligence si chiude e non si riapre cambiando la soglia.

Scrive WALLET_SKILL.md. Sola lettura. €0.
"""
import json, os, time, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "agents")
import multichain_brain as B
import controlli as C

CHAIN = os.environ.get("CHAIN", "base")
MIN_DECISIONI = 20          # sotto questa soglia non parliamo di bravura (fissata ex ante)
K_SHRINK = 20.0             # forza dello schiacciamento: con 20 casi pesi meta'
MAX_TOKEN = int(os.environ.get("MAX_TOKEN", 900))
now = int(time.time())
try: CONFINE = int(json.load(open("data/holdout_config.json"))["confine_validazione"])
except Exception: CONFINE = 0


def main():
    U = C.Universo(CHAIN, limite=MAX_TOKEN)
    if len(U.cs) < 100:
        print(f"WALLET_SKILL | {CHAIN}: solo {len(U.cs)} serie", flush=True); return

    ent = C.cluster(CHAIN, addrs=list(U.cs), max_token=MAX_TOKEN)
    eventi = []
    for a in U.cs:
        for t in B.load_trades(CHAIN, a):
            if t.get("kind") == "buy" and t.get("w") and t.get("ts"):
                eventi.append((int(t["ts"]), t["w"], a))
    eventi = C.unita_indipendenti(eventi, ent)
    if len(eventi) < 300:
        print(f"WALLET_SKILL | {CHAIN}: solo {len(eventi)} decisioni indipendenti", flush=True); return

    # --- passata 1: la bravura di ogni entita', costruita scorrendo il tempo in avanti
    storia = defaultdict(list)            # entita' -> [excess a 2h dei suoi acquisti passati]
    punteggio_al_momento = []             # (ts, entita', token, punteggio con SOLO il passato)
    for ts, w, addr in eventi:
        e = ent.get(w, w)
        v = storia[e]
        # shrinkage: la media si tira verso zero quanto piu' i casi sono pochi
        p = (sum(v) / (len(v) + K_SHRINK)) if v else 0.0
        punteggio_al_momento.append((ts, e, addr, p, len(v)))
        ctrl = [U.cs[c] for c in U.matched(addr, ts, k=5)]
        ex = C.excess(U.cs[addr], ctrl, ts, [7200]) if ctrl else {}
        if 7200 in ex: storia[e].append(ex[7200])

    # --- passata 2: quando un'entita' GIA' brava compra, il token sovraperforma i controlli?
    res = {f: {h: [] for h in C.ORIZZONTI} for f in ("ricerca", "validazione")}
    plac = {h: [] for h in C.ORIZZONTI}
    usati = fasce = 0
    for ts, e, addr, p, n in punteggio_al_momento:
        if n < MIN_DECISIONI or p <= 0: continue      # bravura vera, misurata solo sul passato
        ctrl = [U.cs[c] for c in U.matched(addr, ts, k=5)]
        if not ctrl: continue
        ex = C.excess(U.cs[addr], ctrl, ts)
        if not ex: continue
        f = "validazione" if (CONFINE and ts >= CONFINE) else "ricerca"
        for h, v in ex.items(): res[f][h].append(v)
        for h, v in C.placebo(U.cs[addr], ts).items(): plac[h].append(v)
        usati += 1

    L = [f"# 🧠 WALLET INTELLIGENCE — l'ultimo test ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(eventi)} decisioni indipendenti "
         f"(prima scelta di ogni entità su ogni token) · {len(set(ent.values()))} entità riconosciute "
         f"fondendo i wallet della stessa mano*", "",
         "> **Come si misura la bravura qui**: non «quanti token ha azzeccato», ma **quanto ha fatto meglio",
         "> dei token comparabili** disponibili negli stessi momenti — e con il punteggio schiacciato verso",
         "> lo zero quando i casi sono pochi. Tre successi su tre non valgono più di settanta su centoventi.", "",
         "> **Numeri LORDI, di proposito.** Prima si guarda se l'informazione esiste. I costi si discutono",
         "> solo dopo, e solo se c'è qualcosa da scontare.", ""]

    if usati < 30:
        L += [f"## Campione insufficiente", "",
              f"Solo **{usati}** acquisti provengono da entità con almeno {MIN_DECISIONI} decisioni alle",
              f"spalle e bravura storica positiva. Non basta per un verdetto: serve più storico.",
              "", "*Nessuna conclusione tratta — meglio nessuna risposta che una sbagliata.*"]
        open("WALLET_SKILL.md", "w").write("\n".join(L))
        print(f"WALLET_SKILL | {CHAIN} | solo {usati} casi qualificati", flush=True); return

    for f, titolo in (("ricerca", "Fascia di ricerca (già vista)"),
                      ("validazione", "🔒 Fascia di validazione (mai vista — decide lei)")):
        righe = []
        for h in C.ORIZZONTI:
            v = res[f][h]
            if len(v) < 20: continue
            m = st.mean(v) * 100; med = st.median(v) * 100
            pos = sum(1 for x in v if x > 0) / len(v) * 100
            righe.append(f"| {C.ETICHETTE[h]} | **{m:+.1f}%** | {med:+.1f}% | {pos:.0f}% | {len(v)} |")
        if not righe:
            L += [f"## {titolo}", "", "*Campione troppo piccolo in questa fascia.*", ""]; continue
        L += [f"## {titolo}", "",
              "| dopo | extra-rendimento medio | mediano | quante volte sopra i controlli | casi |",
              "|---|---|---|---|---|"] + righe + [""]

    pos_val = [h for h in C.ORIZZONTI if len(res["validazione"][h]) >= 20
               and st.mean(res["validazione"][h]) > 0]
    L += ["## Il controllo all'indietro (placebo)", "",
          "*Cos'era successo PRIMA dell'acquisto. Se il segnale «spiega» anche il passato, non sta",
          "prevedendo niente: sta guardando un movimento già avvenuto.*", "",
          "| prima dell'acquisto | rendimento |", "|---|---|"]
    for h in C.ORIZZONTI:
        if len(plac[h]) >= 20: L.append(f"| {C.ETICHETTE[h]} | {st.mean(plac[h])*100:+.1f}% |")
    L += ["", "## Verdetto", ""]
    # ATTENZIONE (corretto 02/09): il criterio di morte puo' scattare SOLO se la fascia di validazione
    # ha davvero abbastanza casi. Dichiarare morta una strategia perche' non abbiamo dati per giudicarla
    # e' lo stesso errore, rovesciato, di dichiararla viva perche' i numeri in ricerca sono belli.
    val_pieni = sum(1 for h in C.ORIZZONTI if len(res["validazione"][h]) >= 20)
    if val_pieni < 2:
        ric = [h for h in C.ORIZZONTI if len(res["ricerca"][h]) >= 20 and st.mean(res["ricerca"][h]) > 0]
        L += ["> ⏸️ **Non ancora giudicabile.** La fascia di validazione non ha abbastanza casi per",
              "> decidere, e il criterio di morte NON scatta su dati insufficienti.", "",
              f"> Quello che si vede in ricerca (extra-rendimento positivo su {len(ric)} orizzonti su "
              f"{len(C.ORIZZONTI)}) **non fa fede**: è la fascia su cui il sistema si è già adattato.",
              "> Il test si rifà da solo quando l'accumulo avrà riempito la validazione."]
    elif len(pos_val) >= 2:
        L += [f"> ✅ **Esiste informazione.** Extra-rendimento positivo su **{len(pos_val)} orizzonti** in",
              "> fascia di validazione. Il criterio di morte fissato prima del test NON è scattato:",
              "> si passa al secondo stadio — questo vantaggio lordo sopravvive ai costi veri?"]
    else:
        L += ["> ❌ **Non esiste informazione.** Il gruppo dei wallet storicamente bravi non batte i",
              "> controlli appaiati nemmeno al LORDO, in fascia mai vista. Non è un problema di costi né",
              "> di uscita: quei wallet non sanno nulla che non sappia il mercato.", "",
              "> **Criterio di morte scattato** (fissato prima di guardare i numeri): la wallet intelligence",
              "> si chiude e non si riapre cambiando la soglia."]
    open("WALLET_SKILL.md", "w").write("\n".join(L))
    print(f"WALLET_SKILL | {CHAIN} | {usati} casi | validazione: {val_pieni} orizzonti pieni, {len(pos_val)} positivi", flush=True)


if __name__ == "__main__":
    main()
