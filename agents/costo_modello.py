#!/usr/bin/env python3
"""
COSTO_MODELLO — mettere d'accordo il costo MISURATO con quello USATO nei conti.

La consulenza esterna del 02/09 ha trovato una contraddizione che invalida ogni verdetto dato
finora, in tutte e due le direzioni:

    misurato su Jupiter:  4,0% andata+ritorno su $25   ->  pareggio a 1,04x
    usato nel backtest:  ~33% andata+ritorno           ->  pareggio a 1,52x

Otto volte piu' severo del dato che diciamo di aver misurato. Finche' le due cose non si parlano,
"tutte le chain sono negative" non e' una scoperta: e' un'assunzione travestita da risultato.

Ma il modo giusto di riconciliare NON e' abbassare il 33% al 4%. La consulenza indica la strada:

    «invendibile non e' un costo alto, e' una perdita totale, e va contato a parte»

Sono due macchine diverse, e mescolarle e' l'errore:
  MACCHINA 1  la probabilita' di non poter uscire affatto  ->  perdi tutto, nessuno slippage lo descrive
  MACCHINA 2  quanto costa uscire QUANDO si puo' uscire    ->  e li' il 4-8% misurato e' il numero vero

Un costo medio del 33% e' la fusione sbagliata delle due: punisce ogni trade con un pezzo del
disastro altrui, e insieme sottostima il disastro vero. Cosi' un token buono sembra impraticabile
e un token invendibile sembra solo caro.

Questo agente NON cambia la strategia viva: misura, scrive il verdetto e apre una proposta.
Cambiare il metro con cui si giudica tutto e' una decisione dell'investitore, non un'ottimizzazione.

Scrive COSTO_MODELLO.md + data/costo_modello.json. Sola lettura sul resto. €0.
"""
import json, os, glob, time, statistics as st

ARCH = "data/costi_archivio.json"
USCITA = "data/costo_modello.json"
now = int(time.time())
# quello che il backtest usa oggi (learner.py) — serve solo per il confronto
ES = XS = 0.15; FEE = 0.01; LAT = 0.08
# SOGLIA TRAPPOLA (02/09): "esiste una route" NON vuol dire "puoi uscire". Nelle prime misure, 4 token
# su 6 restituivano lo 0,02% di quanto messo: Jupiter dava regolarmente il prezzo, e quel prezzo era zero.
# Contarli come "vendibili con un costo del 99,9%" e' un modo elegante di nascondere che sono trappole.
# Sopra questa soglia non e' un costo: e' aver perso tutto.
SOGLIA_TRAPPOLA = 0.50


def pareggio(costo_frazione):
    return 1.0 / max(1e-6, 1.0 - costo_frazione)


def main():

    arch = {}
    for x in sorted(glob.glob("data/costi/*.json")) + [ARCH]:
        try: arch.update(json.load(open(x)))
        except Exception: pass
    if not arch:
        print("COSTO_MODELLO | nessun archivio leggibile", flush=True); return
    tok = list(arch.values())
    if not tok:
        print("COSTO_MODELLO | archivio vuoto", flush=True); return

    # --- MACCHINA 1: si puo' uscire? (a ogni taglia, perche' dipende da quanto compri)
    # --- MACCHINA 2: quanto costa, quando si puo'
    per_taglia = {}
    for s in ("25", "100", "500"):
        vend, morti = [], 0
        for t in tok:
            v = t.get("size", {}).get(s) or t.get("size", {}).get(int(s))
            if not isinstance(v, dict): continue
            if "costo_roundtrip_pct" in v:
                c = v["costo_roundtrip_pct"] / 100.0
                if c >= SOGLIA_TRAPPOLA: morti += 1      # route esistente ma restituisce nulla
                else: vend.append(c)
            elif "VENDITA IMPOSSIBILE" in str(v.get("errore", "")): morti += 1
        n = len(vend) + morti
        if n:
            per_taglia[s] = {"vendibili": len(vend), "invendibili": morti, "n": n,
                             "costo_mediano": st.median(vend) if vend else None,
                             "costo_p90": sorted(vend)[int(len(vend) * .9)] if len(vend) >= 5 else None}
            # LE DUE GAMBE SEPARATE (03/09): dividere il roundtrip a meta' era un'assunzione, e i dati
            # dicono il contrario di quello che avrei dedotto — a $25 l'acquisto costa 2,76% e la
            # vendita 1,07%. Il p75 della vendita serve per le uscite in stop: li' il mercato e' un altro.
            acq = [t["size"][s].get("impatto_acquisto_pct") for t in tok
                   if isinstance(t.get("size", {}).get(s), dict)
                   and "costo_roundtrip_pct" in t["size"][s]
                   and t["size"][s]["costo_roundtrip_pct"] / 100.0 < SOGLIA_TRAPPOLA]
            ven = [t["size"][s].get("impatto_vendita_pct") for t in tok
                   if isinstance(t.get("size", {}).get(s), dict)
                   and "costo_roundtrip_pct" in t["size"][s]
                   and t["size"][s]["costo_roundtrip_pct"] / 100.0 < SOGLIA_TRAPPOLA]
            acq = sorted(x / 100.0 for x in acq if x is not None)
            ven = sorted(x / 100.0 for x in ven if x is not None)
            if acq: per_taglia[s]["impatto_acquisto_mediano"] = st.median(acq)
            if ven:
                per_taglia[s]["impatto_vendita_mediano"] = st.median(ven)
                per_taglia[s]["impatto_vendita_p75"] = ven[int(len(ven) * .75)]

    json.dump({"ts": now, "taglie": per_taglia}, open(USCITA, "w"))

    costo_finto = 1 - (1 - XS) * (1 - FEE) * (1 - LAT) / ((1 + ES) * (1 + FEE))
    L = [f"# ⚖️ IL COSTO VERO — mettere d'accordo misura e modello",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(tok)} token misurati su Jupiter · €0*", "",
         "> **Il problema**: diciamo di aver misurato il costo, e poi nei conti ne usiamo un altro,",
         f"> **{costo_finto*100:.0f}%**. Finché le due cose non si parlano, «tutte le chain sono negative»",
         "> non è una scoperta: è un'assunzione travestita da risultato.", "",
         "> **La correzione non è abbassare il 33% al 4%.** Sono due domande diverse, e mescolarle è",
         "> l'errore: *si può uscire?* è una perdita totale, *quanto costa uscire?* è una percentuale.",
         "> Un costo medio le fonde male — punisce ogni trade con un pezzo del disastro altrui, e",
         "> insieme sottostima il disastro vero.", "",
         "| se metti | **trappole** (non esci, o esci con nulla) | costo quando esci davvero | peggiori | pareggio |",
         "|---|---|---|---|---|"]
    for s, d in per_taglia.items():
        if d["costo_mediano"] is None: continue
        q = d["invendibili"] / d["n"] * 100
        p90 = f"{d['costo_p90']*100:.0f}%" if d["costo_p90"] is not None else "—"
        L.append(f"| ${s} | **{q:.0f}%** ({d['invendibili']}/{d['n']}) | **{d['costo_mediano']*100:.1f}%** | "
                 f"{p90} | {pareggio(d['costo_mediano']):.2f}x |")
    L += ["", f"| *quello che usiamo oggi nei conti* | *non modellato* | *{costo_finto*100:.0f}%* | — | "
          f"*{pareggio(costo_finto):.2f}x* |", ""]

    d25 = per_taglia.get("25")
    if d25 and d25["costo_mediano"] is not None and d25["n"] >= 25:
        q = d25["invendibili"] / d25["n"]
        # quanto deve rendere un trade riuscito per coprire ANCHE i casi in cui non si esce
        need = (1 + 0) / max(1e-6, (1 - q)) * pareggio(d25["costo_mediano"])
        L += ["## Cosa cambia davvero", "",
              f"A **$25**, quando si esce davvero, costa **{d25['costo_mediano']*100:.1f}%** — molto meno del "
              f"{costo_finto*100:.0f}% che assumiamo.",
              f"Ma **{q*100:.0f}%** dei token è una **trappola**: o non c'è uscita, o l'uscita restituisce nulla.",
              "Quella non è una percentuale di costo: è tutto il capitale.", "",
              f"Messe insieme: un trade che riesce deve fare almeno **{need:.2f}x** perché il gruppo",
              f"vada in pari. **Non {pareggio(costo_finto):.2f}x, e nemmeno {pareggio(d25['costo_mediano']):.2f}x.**", "",
              "> La taglia conta più di quanto pensassimo: passare da $25 a $100 raddoppia il costo di uscita.",
              "> Se una strategia funziona, funziona **piccola**.", ""]
        L += ["## Proposta aperta", "",
              "> Sostituire nel backtest il costo unico con le due macchine separate: probabilità di non",
              "> uscire (perdita totale) + costo misurato sui casi in cui si esce.",
              "> **Non lo cambio da solo**: è il metro con cui giudichiamo ogni cosa, e cambiarlo di nascosto",
              "> rifarebbe tutti i numeri senza che nessuno abbia deciso niente."]
    else:
        n = d25["n"] if d25 else 0
        L += ["## Non ancora sufficiente", "",
              f"Servono almeno **25 token misurati** per proporre un cambio del metro: adesso sono **{n}**.",
              "L'archivio cresce a ogni giro del motore (25 token ogni ~2 ore), quindi è questione di ore.", "",
              "> Fino ad allora ogni verdetto «negativo al netto» va letto con questa riserva:",
              f"> poggia su un costo assunto del {costo_finto*100:.0f}%, non misurato."]
    L += ["", "> Nota onesta: le quote sono indicative, prese su token vivi in un momento di calma. Non dicono",
          "> quanto costerebbe uscire durante un crollo — che è esattamente quando si vuole uscire."]
    open("COSTO_MODELLO.md", "w").write("\n".join(L))
    print(f"COSTO_MODELLO | {len(tok)} token | taglie {list(per_taglia)}", flush=True)


if __name__ == "__main__":
    main()
